
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import (
    Company,
    PlacementDrive,
    Topic,
    Question,
    RecruitmentRound,
    EligibilityCriteria,
    PlacementDriveTopic,
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
    db: Session = Depends(get_db),
    drive_id: int | None = None,
):
    if drive_id is not None and db.query(PlacementDrive).filter_by(id=drive_id).first() is None:
        raise HTTPException(status_code=404, detail="Placement drive not found")

    questions_query = db.query(
        Question.topic_id.label("topic_id"),
        func.sum(Question.occurrence_count).label("total_occurrences"),
    ).filter(Question.topic_id.isnot(None))
    if drive_id is not None:
        questions_query = questions_query.filter(
            Question.placement_drive_id == drive_id
        )
    occurrence_query = (
        questions_query.group_by(Question.topic_id).subquery()
    )
    associations_query = db.query(PlacementDriveTopic.id).filter(
        PlacementDriveTopic.topic_id == Topic.id
    )
    if drive_id is not None:
        associations_query = associations_query.filter(
            PlacementDriveTopic.placement_drive_id == drive_id
        )

    query = (
        db.query(
            Topic.name,
            Topic.category,
            func.coalesce(occurrence_query.c.total_occurrences, 0).label(
                "total_occurrences"
            ),
        )
        .outerjoin(occurrence_query, occurrence_query.c.topic_id == Topic.id)
        .filter(associations_query.exists())
        .order_by(
            func.coalesce(occurrence_query.c.total_occurrences, 0).desc(),
            Topic.name,
        )
    )
    results = query.all()

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
    db: Session = Depends(get_db),
    drive_id: int | None = None,
):
    query = db.query(Question)
    if drive_id is not None:
        if db.query(PlacementDrive).filter_by(id=drive_id).first() is None:
            raise HTTPException(status_code=404, detail="Placement drive not found")
        query = query.filter(Question.placement_drive_id == drive_id)
    questions = query.order_by(Question.occurrence_count.desc()).all()

    return [
        {
            "id": question.id,
            "question": question.question_text,
            "occurrence_count": question.occurrence_count,
            "difficulty": question.difficulty,
            "confidence_score": question.confidence_score,
            "verification_status": question.verification_status,
            "source_message_id": question.source_message_id,
            "round_id": question.round_id,
            "topic_id": question.topic_id,
            "topic_category": question.preparation_category,
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
    db: Session = Depends(get_db),
    drive_id: int | None = None,
):

    # --------------------------------------------------------
    # Find company
    # --------------------------------------------------------

    company = db.query(
        Company
    ).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    # --------------------------------------------------------
    # Find placement drives for this company
    # --------------------------------------------------------

    drives = db.query(
        PlacementDrive
    ).filter(
        PlacementDrive.company_id == company_id
    ).order_by(
        PlacementDrive.id.desc()
    ).all()

    if not drives:
        return {
            "company": company.name,
            "industry": company.industry,
            "website": company.website,
            "placement_drives": 0,
            "available_drives": [],
            "drive_id": None,
            "questions": 0,
            "topics": [],
            "recruitment_date": None,
            "year": None,
            "batch": None,
            "job_role": None,
            "package": None,
            "number_of_rounds": None,
            "difficulty": None,
            "eligibility": None,
            "rounds": [],
            "preparation_topics": [],
            "frequent_questions": []
        }

    available_drives = [
        {
            "id": item.id,
            "job_role": item.job_role,
            "recruitment_date": item.recruitment_date,
            "year": item.year,
            "batch": item.batch,
            "package": item.package,
            "number_of_rounds": item.number_of_rounds,
            "difficulty": item.overall_difficulty,
        }
        for item in drives
    ]

    if drive_id is None:
        drive = drives[0]
    else:
        drive = next((item for item in drives if item.id == drive_id), None)
        if drive is None:
            raise HTTPException(
                status_code=404,
                detail="Placement drive not found for this company",
            )

    # --------------------------------------------------------
    # Fetch questions for the latest drive
    # --------------------------------------------------------

    questions = db.query(
        Question
    ).filter(
        Question.placement_drive_id == drive.id
    ).order_by(
        Question.occurrence_count.desc()
    ).all()

    # --------------------------------------------------------
    # Fetch topics once and create lookup
    # --------------------------------------------------------

    topic_lookup = {
        topic.id: topic
        for topic in db.query(Topic).all()
    }

    # --------------------------------------------------------
    # Prepare company-wise topic statistics
    # --------------------------------------------------------

    topic_data = {}

    preparation_topic_rows = (
        db.query(PlacementDriveTopic, Topic)
        .join(Topic, Topic.id == PlacementDriveTopic.topic_id)
        .filter(PlacementDriveTopic.placement_drive_id == drive.id)
        .order_by(
            PlacementDriveTopic.category,
            PlacementDriveTopic.round_id,
            Topic.name,
        )
        .all()
    )
    for association, topic in preparation_topic_rows:
        topic_data.setdefault(
            topic.id,
            {
                "id": topic.id,
                "topic": topic.name,
                "category": association.category,
                "occurrence_count": 0,
            },
        )

    for question in questions:

        topic = topic_lookup.get(question.topic_id)

        if not topic:
            continue

        if topic.id not in topic_data:
            topic_data[topic.id] = {
                "id": topic.id,
                "topic": topic.name,
                "category": question.preparation_category or topic.category,
                "occurrence_count": 0
            }

        topic_data[topic.id]["occurrence_count"] += (
            question.occurrence_count or 0
        )

    # --------------------------------------------------------
    # Recruitment rounds
    # --------------------------------------------------------

    rounds = db.query(
        RecruitmentRound
    ).filter(
        RecruitmentRound.placement_drive_id == drive.id
    ).order_by(
        RecruitmentRound.round_number.is_(None),
        RecruitmentRound.round_number,
        RecruitmentRound.id,
    ).all()

    round_data = []

    for round_item in rounds:

        round_data.append({
            "id": round_item.id,
            "round_number": round_item.round_number,
            "round_type": round_item.round_type,
            "description": round_item.description,
            "difficulty": round_item.difficulty
        })

    preparation_topic_data = [
        {
            "id": topic.id,
            "topic_id": topic.id,
            "topic": topic.name,
            "category": association.category,
            "round_id": association.round_id,
            "occurrence_count": topic_data.get(topic.id, {}).get(
                "occurrence_count",
                0,
            ),
        }
        for association, topic in preparation_topic_rows
    ]
    preparation_category_lookup = {
        (association.topic_id, association.round_id): association.category
        for association, _ in preparation_topic_rows
    }

    # --------------------------------------------------------
    # Eligibility
    # --------------------------------------------------------

    eligibility = db.query(
        EligibilityCriteria
    ).filter(
        EligibilityCriteria.placement_drive_id == drive.id
    ).order_by(
        EligibilityCriteria.id.desc()
    ).first()

    eligibility_data = None

    if eligibility:

        eligibility_data = {
            "minimum_cgpa": eligibility.minimum_cgpa,
            "maximum_backlogs": eligibility.maximum_backlogs,
            "branch_eligibility": eligibility.branch_eligibility,
            "other_criteria": eligibility.other_criteria
        }

    # --------------------------------------------------------
    # Questions with round and topic mapping
    # --------------------------------------------------------

    question_data = []

    for question in questions:

        topic = topic_lookup.get(question.topic_id)

        question_data.append({
            "id": question.id,
            "question": question.question_text,
            "occurrence_count": question.occurrence_count,
            "difficulty": question.difficulty,
            "confidence_score": question.confidence_score,
            "verification_status": question.verification_status,
            "source_message_id": question.source_message_id,

            # Roadmap mapping
            "round_id": question.round_id,
            "topic_id": question.topic_id,

            # Topic details
            "topic": topic.name if topic else None,
            "topic_category": question.preparation_category
            or preparation_category_lookup.get(
                (question.topic_id, question.round_id)
            )
            or (topic.category if topic else None),
        })

    # --------------------------------------------------------
    # Complete company response
    # --------------------------------------------------------

    return {
        "company": company.name,
        "industry": company.industry,
        "website": company.website,

        "placement_drives": len(drives),
        "available_drives": available_drives,
        "drive_id": drive.id,
        "questions": len(questions),

        "recruitment_date": drive.recruitment_date,
        "year": drive.year,
        "batch": drive.batch,
        "job_role": drive.job_role,
        "package": drive.package,
        "number_of_rounds": drive.number_of_rounds,
        "difficulty": drive.overall_difficulty,

        "eligibility": eligibility_data,

        "rounds": round_data,
        "preparation_topics": preparation_topic_data,

        "topics": sorted(
            topic_data.values(),
            key=lambda x: x["occurrence_count"],
            reverse=True
        ),

        "frequent_questions": question_data
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
