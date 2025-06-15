# app/services/monitoring_service.py
"""
Subscription Monitoring and Analytics Service
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

# Import the repository to handle all DB interactions
from app.repositories import monitoring_repository

logger = logging.getLogger(__name__)

class MonitoringService:
    """A singleton service for all monitoring-related business logic."""
    _instance = None

    def __init__(self):
        logger.info("Initializing MonitoringService singleton...")
        # Configuration for alert thresholds could be moved to a content file
        self.alert_thresholds = {
            "payment_failure_rate": 0.10, # 10%
            "weekly_churn_rate": 0.05,    # 5%
            "task_stale_hours": 4
        }
        logger.info("MonitoringService initialized successfully.")

    def get_dashboard_metrics(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Generates a full suite of metrics for the monitoring dashboard."""
        logger.info(f"Generating dashboard metrics for the last {days} days.")
        try:
            now = datetime.now(timezone.utc)
            start_date = now - timedelta(days=days)
            
            # 1. Fetch raw data from the repository
            current_counts = monitoring_repository.get_current_subscription_counts(db)
            changes = monitoring_repository.get_subscription_changes(db, start_date, now)
            payment_stats = monitoring_repository.get_payment_failure_stats(db, start_date, now)
            avg_usage = monitoring_repository.get_average_feature_usage(db, start_date, now)

            # 2. Perform business logic calculations
            active_subs = current_counts.get("active", 0)
            
            churn_rate = (changes['cancellations'] / active_subs) if active_subs > 0 else 0
            growth_rate = (changes['new_subscriptions'] / active_subs) if active_subs > 0 else 0
            
            total_payments_attempted = active_subs + current_counts.get("trialing", 0) + changes['cancellations']
            payment_failure_rate = (payment_stats['total_failures'] / total_payments_attempted) if total_payments_attempted > 0 else 0
            payment_recovery_rate = (payment_stats['resolved_failures'] / payment_stats['total_failures']) if payment_stats['total_failures'] > 0 else 1.0

            # 3. Assemble the report
            return {
                "current_status": current_counts,
                "performance_metrics": {
                    "new_subscriptions": changes['new_subscriptions'],
                    "cancellations": changes['cancellations'],
                    "churn_rate_percent": round(churn_rate * 100, 2),
                    "growth_rate_percent": round(growth_rate * 100, 2),
                },
                "payment_health": {
                    "failure_rate_percent": round(payment_failure_rate * 100, 2),
                    "recovery_rate_percent": round(payment_recovery_rate * 100, 2),
                    "total_failures": payment_stats['total_failures']
                },
                "engagement": {
                    "average_feature_usage_per_day": round(avg_usage, 2)
                },
                "timeframe_days": days
            }
        except Exception as e:
            logger.critical(f"Failed to generate dashboard metrics: {e}", exc_info=True)
            return {"error": "An internal server error occurred while generating metrics."}

    def check_system_alerts(self, db: Session) -> Dict[str, Any]:
        """Checks for critical system alerts based on recent data."""
        logger.info("Checking for system health alerts.")
        alerts = []
        now = datetime.now(timezone.utc)
        
        # --- High Payment Failure Rate Alert ---
        payment_stats_24h = monitoring_repository.get_payment_failure_stats(db, now - timedelta(days=1), now)
        active_subs = monitoring_repository.get_current_subscription_counts(db).get("active", 0)
        if active_subs > 0:
            failure_rate = payment_stats_24h['total_failures'] / active_subs
            if failure_rate > self.alert_thresholds['payment_failure_rate']:
                alerts.append({"level": "high", "type": "payment_failures", "message": f"High payment failure rate in last 24h: {failure_rate:.1%}"})

        # --- High Churn Rate Alert ---
        churn_7d = monitoring_repository.get_subscription_changes(db, now - timedelta(days=7), now)['cancellations']
        if active_subs > 0:
            churn_rate = churn_7d / active_subs
            if churn_rate > self.alert_thresholds['weekly_churn_rate']:
                alerts.append({"level": "medium", "type": "churn_rate", "message": f"Elevated weekly churn rate: {churn_rate:.1%}"})

        # --- Stale Task Alert ---
        latest_tasks = monitoring_repository.get_latest_task_runs(db)
        for task in latest_tasks:
            time_since_run = now - task.run_at
            if time_since_run.total_seconds() > self.alert_thresholds['task_stale_hours'] * 3600:
                alerts.append({"level": "high", "type": "task_health", "message": f"Task '{task.task_name}' has not run in {time_since_run.total_seconds() / 3600:.1f} hours."})
            if task.status == 'FAILURE':
                alerts.append({"level": "high", "type": "task_health", "message": f"Task '{task.task_name}' failed on its last run."})

        return {"alerts": alerts, "total_alerts": len(alerts), "checked_at_utc": now.isoformat()}


# --- Create a single, shared instance ---
try:
    monitoring_service_instance = MonitoringService()
except Exception as e:
    logger.critical(f"Could not instantiate MonitoringService: {e}")
    monitoring_service_instance = None