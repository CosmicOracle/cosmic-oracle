# app/repositories/chakra_repository.py
"""
Chakra Repository

This module handles all direct database interactions for Chakra-related data.
It encapsulates SQLAlchemy queries, providing a clean interface for the service layer.
This is an implementation of the Repository Pattern.
"""
from sqlalchemy.orm import Session
from typing import List, Optional

# Assuming your models are defined in app.models.orm_models
# and a UserChakraAssessment class exists there.
from app.models.orm_models import UserChakraAssessment

def create_assessment(
    db: Session, 
    user_id: int, 
    chakra_key: str, 
    balance_score: int, 
    notes: Optional[str] = None
) -> UserChakraAssessment:
    """Creates and saves a new chakra assessment record in the database."""
    new_assessment = UserChakraAssessment(
        user_id=user_id,
        chakra_key=chakra_key,
        balance_score=balance_score,
        notes=notes
    )
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)
    return new_assessment

def get_assessment_history(
    db: Session, 
    user_id: int, 
    chakra_key: Optional[str] = None
) -> List[UserChakraAssessment]:
    """Retrieves a user's assessment history, optionally filtered by a specific chakra."""
    query = db.query(UserChakraAssessment).filter(UserChakraAssessment.user_id == user_id)
    if chakra_key:
        query = query.filter(UserChakraAssessment.chakra_key == chakra_key)
    return query.order_by(UserChakraAssessment.assessment_date.desc()).all()

def get_latest_assessments_for_all_chakras(db: Session, user_id: int) -> Dict[str, UserChakraAssessment]:
    """
    Efficiently retrieves only the most recent assessment for each of the 7 chakras for a user.
    """
    # This is a more advanced query that uses a subquery to find the latest record for each chakra
    # which is more efficient than fetching all records and processing in Python.
    from sqlalchemy import func

    subquery = db.query(
        UserChakraAssessment.chakra_key,
        func.max(UserChakraAssessment.assessment_date).label('max_date')
    ).filter(UserChakraAssessment.user_id == user_id).group_by(UserChakraAssessment.chakra_key).subquery()

    latest_records_query = db.query(UserChakraAssessment).join(
        subquery,
        (UserChakraAssessment.chakra_key == subquery.c.chakra_key) &
        (UserChakraAssessment.assessment_date == subquery.c.max_date)
    )

    latest_records = latest_records_query.all()
    return {record.chakra_key: record for record in latest_records}