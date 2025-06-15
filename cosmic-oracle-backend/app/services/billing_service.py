# app/services/billing_service.py
"""
Billing Service for handling Stripe subscriptions and payments
"""
import os
import logging
import stripe
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BillingService:
    """Service for handling Stripe billing operations."""
    
    def __init__(self):
        """Initialize Stripe configuration."""
        self.stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
        self.stripe_publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        self.stripe_webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        if not self.stripe_secret_key:
            logger.warning("STRIPE_SECRET_KEY not found. Billing functionality will be limited.")
            self.stripe_enabled = False
        else:
            stripe.api_key = self.stripe_secret_key
            self.stripe_enabled = True
            logger.info("Stripe billing service initialized successfully.")
    
    def create_customer(self, email: str, name: str = None, metadata: Dict = None) -> Optional[str]:
        """
        Create a new Stripe customer.
        
        Args:
            email: Customer email address
            name: Customer name
            metadata: Additional metadata to store
            
        Returns:
            Stripe customer ID or None if failed
        """
        if not self.stripe_enabled:
            logger.warning("Stripe not configured. Cannot create customer.")
            return None
            
        try:
            customer_data = {'email': email}
            if name:
                customer_data['name'] = name
            if metadata:
                customer_data['metadata'] = metadata
                
            customer = stripe.Customer.create(**customer_data)
            logger.info(f"Created Stripe customer: {customer.id}")
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return None
    
    def create_checkout_session(self, 
                              customer_id: str, 
                              price_id: str, 
                              success_url: str, 
                              cancel_url: str,
                              metadata: Dict = None) -> Optional[str]:
        """
        Create a Stripe checkout session for subscription.
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID for the subscription
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancellation
            metadata: Additional metadata
            
        Returns:
            Checkout session URL or None if failed
        """
        if not self.stripe_enabled:
            logger.warning("Stripe not configured. Cannot create checkout session.")
            return None
            
        try:
            session_data = {
                'customer': customer_id,
                'payment_method_types': ['card'],
                'mode': 'subscription',
                'line_items': [{
                    'price': price_id,
                    'quantity': 1,
                }],
                'success_url': success_url,
                'cancel_url': cancel_url,
            }
            
            if metadata:
                session_data['metadata'] = metadata
                
            session = stripe.checkout.Session.create(**session_data)
            logger.info(f"Created checkout session: {session.id}")
            return session.url
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            return None
    
    def create_customer_portal_session(self, customer_id: str, return_url: str) -> Optional[str]:
        """
        Create a customer portal session for managing subscription.
        
        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after managing subscription
            
        Returns:
            Portal session URL or None if failed
        """
        if not self.stripe_enabled:
            logger.warning("Stripe not configured. Cannot create portal session.")
            return None
            
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            logger.info(f"Created portal session for customer: {customer_id}")
            return session.url
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating portal session: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating portal session: {e}")
            return None
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Stripe webhook signature.
        
        Args:
            payload: Raw request body
            signature: Stripe signature header
            
        Returns:
            True if signature is valid
        """
        if not self.stripe_enabled or not self.stripe_webhook_secret:
            logger.warning("Stripe webhook secret not configured.")
            return False
            
        try:
            stripe.Webhook.construct_event(
                payload, signature, self.stripe_webhook_secret
            )
            return True
        except ValueError:
            logger.error("Invalid payload")
            return False
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature")
            return False
    
    def process_webhook_event(self, event_data: Dict) -> Dict[str, Any]:
        """
        Process Stripe webhook events.
        
        Args:
            event_data: Stripe event data
            
        Returns:
            Processing result
        """
        event_type = event_data.get('type')
        logger.info(f"Processing webhook event: {event_type}")
        
        try:
            if event_type == 'checkout.session.completed':
                return self._handle_checkout_completed(event_data)
            elif event_type == 'customer.subscription.updated':
                return self._handle_subscription_updated(event_data)
            elif event_type == 'customer.subscription.deleted':
                return self._handle_subscription_deleted(event_data)
            elif event_type == 'invoice.payment_succeeded':
                return self._handle_payment_succeeded(event_data)
            elif event_type == 'invoice.payment_failed':
                return self._handle_payment_failed(event_data)
            else:
                logger.info(f"Unhandled webhook event type: {event_type}")
                return {'status': 'ignored', 'event_type': event_type}
                
        except Exception as e:
            logger.error(f"Error processing webhook event {event_type}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _handle_checkout_completed(self, event_data: Dict) -> Dict[str, Any]:
        """Handle successful checkout completion."""
        session = event_data['data']['object']
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')
        metadata = session.get('metadata', {})
        user_id = metadata.get('user_id')
        
        if user_id:
            # Here you would update your user's subscription status in the database
            logger.info(f"Checkout completed for user {user_id}: customer={customer_id}, subscription={subscription_id}")
            # TODO: Update user subscription in database
            return {
                'status': 'processed',
                'user_id': user_id,
                'customer_id': customer_id,
                'subscription_id': subscription_id
            }
        else:
            logger.warning("No user_id in checkout session metadata")
            return {'status': 'error', 'message': 'No user_id in metadata'}
    
    def _handle_subscription_updated(self, event_data: Dict) -> Dict[str, Any]:
        """Handle subscription updates."""
        subscription = event_data['data']['object']
        customer_id = subscription.get('customer')
        status = subscription.get('status')
        
        logger.info(f"Subscription updated: customer={customer_id}, status={status}")
        # TODO: Update user subscription status in database
        return {'status': 'processed', 'customer_id': customer_id, 'subscription_status': status}
    
    def _handle_subscription_deleted(self, event_data: Dict) -> Dict[str, Any]:
        """Handle subscription cancellation."""
        subscription = event_data['data']['object']
        customer_id = subscription.get('customer')
        
        logger.info(f"Subscription deleted: customer={customer_id}")
        # TODO: Update user subscription status to cancelled in database
        return {'status': 'processed', 'customer_id': customer_id, 'subscription_status': 'cancelled'}
    
    def _handle_payment_succeeded(self, event_data: Dict) -> Dict[str, Any]:
        """Handle successful payment."""
        invoice = event_data['data']['object']
        customer_id = invoice.get('customer')
        amount_paid = invoice.get('amount_paid')
        
        logger.info(f"Payment succeeded: customer={customer_id}, amount={amount_paid}")
        # TODO: Log payment in database
        return {'status': 'processed', 'customer_id': customer_id, 'amount_paid': amount_paid}
    
    def _handle_payment_failed(self, event_data: Dict) -> Dict[str, Any]:
        """Handle failed payment."""
        invoice = event_data['data']['object']
        customer_id = invoice.get('customer')
        
        logger.warning(f"Payment failed: customer={customer_id}")
        # TODO: Handle failed payment (send notification, update status, etc.)
        return {'status': 'processed', 'customer_id': customer_id, 'payment_status': 'failed'}
    
    def get_subscription_status(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription status from Stripe.
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Subscription data or None if not found
        """
        if not self.stripe_enabled:
            return None
            
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving subscription {subscription_id}: {e}")
            return None
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> bool:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: Stripe subscription ID
            at_period_end: Whether to cancel at period end or immediately
            
        Returns:
            True if successful
        """
        if not self.stripe_enabled:
            return False
            
        try:
            if at_period_end:
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                stripe.Subscription.delete(subscription_id)
            
            logger.info(f"Cancelled subscription {subscription_id}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Error cancelling subscription {subscription_id}: {e}")
            return False

# Global instance
billing_service = BillingService()
