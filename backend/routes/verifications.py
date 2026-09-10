from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Question, VerificationRecord


router = APIRouter(
    prefix="/verifications",
    tags=["Verifications"]
)


@router.post("/questions/{question_id}")
def verify_question(
    question_id: int,
    verified_by: str,
    notes: str = "",
    db: Session = Depends(get_db)
):
    """
    Verify a question extracted from placement feedback.
    """

    question = db.query(Question).filter(
        Question.id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    # Update question
    question.verification_status = "verified"

    question.confidence_score = 100.0

    # Create verification history
    verification = VerificationRecord(
        entity_type="question",
        entity_id=question.id,
        verified=True,
        confidence_score=100.0,
        verified_by=verified_by,
        notes=notes
    )

    db.add(verification)

    db.commit()

    db.refresh(question)

    return {
        "message": "Question verified successfully",
        "question_id": question.id,
        "verification_status": question.verification_status,
        "confidence_score": question.confidence_score,
        "verified_by": verified_by
    }