# app/services/chakra_service.py
"""
Chakra Assessment and Healing Plan Service

This service encapsulates the business logic for recording chakra assessments
and generating personalized healing plans based on a user's history.
"""
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

# Import the repository to handle DB operations and the content service
from app.repositories import chakra_repository
from app.services.content_fetch_service import get_chakra_data

logger = logging.getLogger(__name__)

def record_new_assessment(
    db: Session, 
    user_id: int, 
    chakra_key: str, 
    balance_score: int, 
    notes: str = None
):
    """
    Business logic for recording a new chakra assessment.
    It relies on the repository to perform the database write.
    """
    # Here you could add more complex business rules, e.g.,
    # "a user can only assess a chakra once per day".
    logger.info(f"Recording new assessment for user {user_id}, chakra {chakra_key}.")
    return chakra_repository.create_assessment(
        db=db,
        user_id=user_id,
        chakra_key=chakra_key,
        balance_score=balance_score,
        notes=notes
    )

def get_assessment_history_for_user(db: Session, user_id: int, chakra_key: str = None):
    """Retrieves a user's assessment history via the repository."""
    logger.info(f"Fetching assessment history for user {user_id}.")
    return chakra_repository.get_assessment_history(db=db, user_id=user_id, chakra_key=chakra_key)

def generate_healing_plan(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Generates a personalized healing plan by identifying the most imbalanced chakras.
    """
    logger.info(f"Generating personalized healing plan for user {user_id}.")
    try:
        static_chakras = get_chakra_data()
        if not static_chakras:
            return {"error": "Chakra definition content not found. Cannot generate plan."}

        # Fetch only the latest assessment for each chakra efficiently.
        latest_assessments = chakra_repository.get_latest_assessments_for_all_chakras(db=db, user_id=user_id)

        imbalanced_chakras = []
        for chakra_key, assessment in latest_assessments.items():
            # Identify imbalanced chakras (score < 5 is a sample threshold)
            if assessment.balance_score < 5:
                imbalanced_chakras.append({
                    "chakra_key": chakra_key,
                    "score": assessment.balance_score,
                    "notes": assessment.notes,
                    "assessed_on": assessment.assessment_date.isoformat()
                })
        
        # Sort by the lowest scores to prioritize the most critical imbalances.
        imbalanced_chakras.sort(key=lambda x: x['score'])
        
        # Build the healing plan based on the sorted imbalances.
        recommendations = []
        for imbalanced_chakra in imbalanced_chakras:
            chakra_key = imbalanced_chakra['chakra_key']
            chakra_details = static_chakras.get(chakra_key)
            if chakra_details:
                recommendations.append({
                    "focus_chakra": chakra_details["name"],
                    "identified_imbalance_score": imbalanced_chakra['score'],
                    "healing_suggestions": {
                        "affirmation": chakra_details.get("affirmation"),
                        "meditation_focus": f"Visualize a spinning wheel of {chakra_details.get('color')} light at your {chakra_details.get('location')}.",
                        "recommended_crystals": chakra_details.get("crystals", []),
                        "suggested_activities": chakra_details.get("practices", [])
                    }
                })
        
        if not recommendations:
            return {"message": "Your recent chakra assessments indicate a good overall balance! Keep up the great work."}

        return {
            "healing_plan_summary": f"Your plan focuses on the {len(recommendations)} most imbalanced chakras, starting with the area needing the most attention.",
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.critical(f"Failed to generate healing plan for user {user_id}: {e}", exc_info=True)
        return {"error": "An internal server error occurred while generating your healing plan."}