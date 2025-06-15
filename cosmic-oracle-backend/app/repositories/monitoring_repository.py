# app/repositories/monitoring_repository.py
"""
Repository for Subscription Monitoring and Analytics.

This module encapsulates all direct database queries required to fetch metrics
for the subscription monitoring dashboard.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.models.orm_models import UserSubscription, SubscriptionMetrics, PaymentFailure, CeleryTaskRun # Assuming these models exist

def get_current_subscription_counts(db: Session) -> Dict[str, int]:
    """Retrieves counts of subscriptions by their current status."""
    active_count = db.query(UserSubscription).filter(UserSubscription.status == 'active').count()
    trial_count = db.query(UserSubscription).filter(UserSubscription.status == 'trialing').count()
    past_due_count = db.query(UserSubscription).filter(UserSubscription.status == 'past_due').count()
    return {
        "active": active_count,
        "trialing": trial_count,
        "past_due": past_due_count
    }

def get_subscription_changes(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, int]:
    """Retrieves counts of new subscriptions and cancellations within a date range."""
    new_subs_count = db.query(UserSubscription).filter(UserSubscription.created_at.between(start_date, end_date)).count()
    cancelled_count = db.query(UserSubscription).filter(UserSubscription.status == 'canceled', UserSubscription.cancelled_at.between(start_date, end_date)).count()
    return {
        "new_subscriptions": new_subs_count,
        "cancellations": cancelled_count
    }

def get_payment_failure_stats(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, int]:
    """Retrieves counts of total and recovered payment failures within a date range."""
    total_failures = db.query(PaymentFailure).filter(PaymentFailure.created_at.between(start_date, end_date)).count()
    resolved_failures = db.query(PaymentFailure).filter(
        and_(
            PaymentFailure.created_at.between(start_date, end_date),
            PaymentFailure.resolved_at.isnot(None)
        )
    ).count()
    return {
        "total_failures": total_failures,
        "resolved_failures": resolved_failures
    }

def get_average_feature_usage(db: Session, start_date: datetime, end_date: datetime) -> float:
    """Calculates the average feature usage count within a date range."""
    avg_usage = db.query(func.avg(SubscriptionMetrics.feature_usage_count)).filter(
        SubscriptionMetrics.created_at.between(start_date, end_date)
    ).scalar()
    return float(avg_usage or 0.0)

def get_latest_task_runs(db: Session) -> List[CeleryTaskRun]:
    """
    Retrieves the most recent run record for each distinct background task.
    This assumes a CeleryTaskRun model tracks task executions.
    """
    # This advanced query finds the latest run for each task name
    subquery = db.query(
        CeleryTaskRun.task_name,
        func.max(CeleryTaskRun.run_at).label('max_run_at')
    ).group_by(CeleryTaskRun.task_name).subquery()

    latest_runs_query = db.query(CeleryTaskRun).join(
        subquery,
        and_(
            CeleryTaskRun.task_name == subquery.c.task_name,
            CeleryTaskRun.run_at == subquery.c.max_run_at
        )
    )
    return latest_runs_query.all()