# app/services/subscription_service.py
"""
Subscription Service for handling Stripe interactions.
"""
import stripe
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.content_fetch_service import get_subscription_plans_content
from app.repositories import subscription_repository

logger = logging.getLogger(__name__)

class SubscriptionService:
    _instance = None
    
    def __init__(self):
        logger.info("Initializing SubscriptionService singleton...")
        if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_WEBHOOK_SECRET:
            raise RuntimeError("Stripe API keys are not configured in settings.")
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        
        self.plans = get_subscription_plans_content().get("plans", {})
        self.price_id_to_plan_key = {plan['stripe_price_id']: key for key, plan in self.plans.items()}
        if not self.plans:
            raise RuntimeError("Subscription plan content could not be loaded.")
        logger.info("SubscriptionService initialized successfully.")

    def create_checkout_session(self, db: Session, user_id: int, plan_key: str, success_url: str, cancel_url: str) -> str:
        """Creates a Stripe Checkout session for a user to subscribe."""
        user = subscription_repository.find_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found.")
            
        plan_details = self.plans.get(plan_key)
        if not plan_details:
            raise ValueError(f"Invalid plan key: {plan_key}")

        customer_id = user.stripe_customer_id
        if not customer_id:
            customer = stripe.Customer.create(email=user.email, metadata={'user_id': user.id})
            customer_id = customer.id
            user.stripe_customer_id = customer_id
            db.commit()

        try:
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{'price': plan_details['stripe_price_id'], 'quantity': 1}],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                subscription_data={'metadata': {'user_id': user.id}}
            )
            return checkout_session.id
        except Exception as e:
            logger.error(f"Stripe error creating checkout session for user {user_id}: {e}", exc_info=True)
            raise ConnectionError(f"Could not create Stripe checkout session: {e}")

    def create_customer_portal_session(self, db: Session, user_id: int, return_url: str) -> str:
        """Creates a Stripe Customer Portal session for a user to manage their subscription."""
        user = subscription_repository.find_user_by_id(db, user_id)
        if not user or not user.stripe_customer_id:
            raise ValueError("User or Stripe customer ID not found.")
        
        try:
            portal_session = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id,
                return_url=return_url
            )
            return portal_session.url
        except Exception as e:
            logger.error(f"Stripe error creating portal session for user {user_id}: {e}", exc_info=True)
            raise ConnectionError(f"Could not create Stripe customer portal session: {e}")

    def handle_webhook(self, db: Session, payload: bytes, sig_header: str):
        """Verifies and processes a Stripe webhook."""
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, self.webhook_secret)
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise ValueError("Invalid webhook signature.")

        logger.info(f"Received Stripe webhook: {event.type}")
        handler = getattr(self, f"_handle_{event.type.replace('.', '_')}", self._handle_unrecognized_event)
        handler(db, event.data.object)

    def _handle_unrecognized_event(self, db: Session, event_data: Dict):
        logger.info(f"Received unrecognized webhook event type. No action taken.")

    def _handle_checkout_session_completed(self, db: Session, session_data: Dict):
        """Handles successful subscription creation via Stripe Checkout."""
        stripe_sub_id = session_data.get('subscription')
        customer_id = session_data.get('customer')
        user_id = session_data.get('metadata', {}).get('user_id') or session_data.get('client_reference_id')

        if not user_id:
            user = subscription_repository.find_user_by_stripe_customer_id(db, customer_id)
        else:
            user = subscription_repository.find_user_by_id(db, int(user_id))

        if not user:
            logger.error(f"Webhook Error: Could not find user for customer {customer_id}")
            return

        stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)
        price_id = stripe_sub.items.data[0].price.id
        
        sub_details = {
            "stripe_subscription_id": stripe_sub.id,
            "stripe_customer_id": stripe_sub.customer,
            "plan_key": self.price_id_to_plan_key.get(price_id),
            "status": stripe_sub.status,
            "current_period_start": datetime.fromtimestamp(stripe_sub.current_period_start, tz=timezone.utc),
            "current_period_end": datetime.fromtimestamp(stripe_sub.current_period_end, tz=timezone.utc),
            "cancel_at_period_end": False
        }
        subscription_repository.create_or_update_subscription(db, user, sub_details)
        subscription_repository.update_user_access_level(db, user.id, sub_details['plan_key'])
        logger.info(f"Subscription for user {user.id} successfully created via webhook.")

    def _handle_customer_subscription_updated(self, db: Session, sub_data: Dict):
        """Handles subscription updates, like cancellations or plan changes."""
        subscription = subscription_repository.find_subscription_by_stripe_id(db, sub_data['id'])
        if not subscription:
            logger.warning(f"Webhook Update: Received update for unknown subscription {sub_data['id']}")
            return

        price_id = sub_data['items']['data'][0]['price']['id']
        updated_details = {
            "plan_key": self.price_id_to_plan_key.get(price_id),
            "status": sub_data['status'],
            "current_period_end": datetime.fromtimestamp(sub_data['current_period_end'], tz=timezone.utc),
            "cancel_at_period_end": sub_data['cancel_at_period_end'],
            "canceled_at": datetime.fromtimestamp(sub_data['canceled_at'], tz=timezone.utc) if sub_data['canceled_at'] else None
        }
        subscription_repository.create_or_update_subscription(db, subscription.user, updated_details)
        
        # If subscription is now definitively canceled (not just at period end)
        if sub_data['status'] == 'canceled':
            subscription_repository.update_user_access_level(db, subscription.user_id, 'free')
        
        logger.info(f"Subscription for user {subscription.user_id} updated via webhook. New status: {sub_data['status']}")

    def _handle_customer_subscription_deleted(self, db: Session, sub_data: Dict):
        """Handles the final deletion of a subscription at the end of a period."""
        self._handle_customer_subscription_updated(db, sub_data) # The logic is the same

# --- Create a single, shared instance ---
try:
    subscription_service_instance = SubscriptionService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate SubscriptionService: {e}")
    subscription_service_instance = None