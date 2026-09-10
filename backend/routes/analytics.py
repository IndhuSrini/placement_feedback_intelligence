from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import (
    Company,
    PlacementDrive,
    Topic,
    Question,
    RecruitmentRound,
    EligibilityCriteria
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# ============================================================
# 1. FREQUENT TOPICS
# ============================================================

@router.get("/frequent-topics")
def frequent_topics(
    db: Session = Depends(get_db)
):

    results = (
        db.query(
            Topic.name,
            Topic.category,
            func.sum(
                Question.occurrence_count
            ).label("total_occurrences")
        )
        .join(
            Question,
            Question.topic_id == Topic.id
        )
        .group_by(
            Topic.id,
            Topic.name,
            Topic.category
        )
        .order_by(
            func.sum(
                Question.occurrence_count
            ).desc()
        )
        .all()
    )

    return [
        {
            "topic": row.name,
            "category": row.category,
            "occurrence_count": row.total_occurrences
        }
        for row in results
    ]


# ============================================================
# 2. FREQUENT QUESTIONS
# ============================================================

@router.get("/frequent-questions")
def frequent_questions(
    db: Session = Depends(get_db)
):

    questions = (
        db.query(Question)
        .order_by(
            Question.occurrence_count.desc()
        )
        .all()
    )

    return [
        {
            "id": question.id,
            "question": question.question_text,
            "occurrence_count": question.occurrence_count,
            "difficulty": question.difficulty,
            "confidence_score": question.confidence_score,
            "verification_status": question.verification_status,
            "source_message_id": question.source_message_id
        }
        for question in questions
    ]


# ============================================================
# 3. OVERALL SYSTEM STATISTICS
# ============================================================

@router.get("/overview")
def overview(
    db: Session = Depends(get_db)
):

    total_companies = db.query(
        Company
    ).count()

    total_drives = db.query(
        PlacementDrive
    ).count()

    total_questions = db.query(
        Question
    ).count()

    total_topics = db.query(
        Topic
    ).count()

    total_rounds = db.query(
        RecruitmentRound
    ).count()

    return {
        "total_companies": total_companies,
        "total_placement_drives": total_drives,
        "total_questions": total_questions,
        "total_topics": total_topics,
        "total_recruitment_rounds": total_rounds
    }


# ============================================================
# 4. COMPANY-WISE ANALYTICS
# ============================================================

@router.get("/company/{company_id}")
def company_analytics(
    company_id: int,
    db: Session = Depends(get_db)
):

    company = db.query(
        Company
    ).filter(
        Company.id == company_id
    ).first()

    if not company:

        return {
            "error": "Company not found"
        }

    drives = db.query(
        PlacementDrive
    ).filter(
        PlacementDrive.company_id == company_id
    ).all()

    drive_ids = [
        drive.id
        for drive in drives
    ]

    if not drive_ids:

        return {
            "company": company.name,
            "placement_drives": 0,
            "questions": 0,
            "topics": []
        }

    questions = db.query(
        Question
    ).filter(
        Question.placement_drive_id.in_(
            drive_ids
        )
    ).all()

    topic_data = {}

    for question in questions:

        if question.topic_id is None:
            continue

        topic = db.query(
            Topic
        ).filter(
            Topic.id == question.topic_id
        ).first()

        if not topic:
            continue

        if topic.name not in topic_data:

            topic_data[topic.name] = {
                "topic": topic.name,
                "category": topic.category,
                "occurrence_count": 0
            }

        topic_data[
            topic.name
        ]["occurrence_count"] += (
            question.occurrence_count
        )

    return {
        "company": company.name,
        "placement_drives": len(drives),
        "questions": len(questions),
        "topics": sorted(
            topic_data.values(),
            key=lambda x: x["occurrence_count"],
            reverse=True
        )
    }


# ============================================================
# 5. CATEGORY ANALYTICS
# ============================================================

@router.get("/categories")
def category_analytics(
    db: Session = Depends(get_db)
):

    results = (
        db.query(
            Topic.category,
            func.sum(
                Question.occurrence_count
            ).label("occurrences")
        )
        .join(
            Question,
            Question.topic_id == Topic.id
        )
        .group_by(
            Topic.category
        )
        .order_by(
            func.sum(
                Question.occurrence_count
            ).desc()
        )
        .all()
    )

    return [
        {
            "category": row.category,
            "occurrence_count": row.occurrences
        }
        for row in results
    ]


# ============================================================
# 6. CONFIDENCE ANALYTICS
# ============================================================

@router.get("/confidence")
def confidence_analytics(
    db: Session = Depends(get_db)
):

    questions = db.query(
        Question
    ).all()

    total = len(questions)

    if total == 0:

        return {
            "total_questions": 0,
            "average_confidence": 0,
            "verified_questions": 0,
            "unverified_questions": 0
        }

    total_confidence = sum(
        question.confidence_score or 0
        for question in questions
    )

    verified = sum(
        1
        for question in questions
        if question.verification_status == "verified"
    )

    return {
        "total_questions": total,
        "average_confidence": round(
            total_confidence / total,
            2
        ),
        "verified_questions": verified,
        "unverified_questions": total - verified
    }


# ============================================================
# 7. YEAR-WISE PLACEMENT ANALYTICS
# ============================================================

@router.get("/year-wise")
def year_wise_analytics(
    db: Session = Depends(get_db)
):

    results = (
        db.query(
            PlacementDrive.year,
            func.count(
                PlacementDrive.id
            ).label("drive_count")
        )
        .filter(
            PlacementDrive.year.isnot(None)
        )
        .group_by(
            PlacementDrive.year
        )
        .order_by(
            PlacementDrive.year
        )
        .all()
    )

    return [
        {
            "year": row.year,
            "placement_drives": row.drive_count
        }
        for row in results
    ]


# ============================================================
# 8. ELIGIBILITY ANALYTICS
# ============================================================

@router.get("/eligibility")
def eligibility_analytics(
    db: Session = Depends(get_db)
):

    results = (
        db.query(
            Company.name,
            PlacementDrive.year,
            EligibilityCriteria.minimum_cgpa,
            EligibilityCriteria.maximum_backlogs
        )
        .join(
            PlacementDrive,
            PlacementDrive.company_id == Company.id
        )
        .join(
            EligibilityCriteria,
            EligibilityCriteria.placement_drive_id
            == PlacementDrive.id
        )
        .order_by(
            PlacementDrive.year
        )
        .all()
    )

    return [
        {
            "company": row.name,
            "year": row.year,
            "minimum_cgpa": row.minimum_cgpa,
            "maximum_backlogs": row.maximum_backlogs
        }
        for row in results
    ]