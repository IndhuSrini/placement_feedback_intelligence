import re

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import (
    Company,
    EligibilityCriteria,
    Experience,
    PlacementDrive,
    RecruitmentRound,
    Topic,
    Question,
)

from nlp.duplicate_detector import calculate_similarity
from nlp.confidence import calculate_confidence
from nlp.extractor import normalize_company_name


# ============================================================
# GET OR CREATE COMPANY / PLACEMENT DRIVE
# ============================================================

def get_or_create_company(db: Session, company_name: str):
    normalized = normalize_company_name(company_name) or "Unknown Company"
    company = db.query(Company).filter(func.lower(Company.name) == normalized.lower()).first()
    if company:
        return company

    company = Company(name=normalized)
    db.add(company)
    db.flush()
    return company


def infer_job_role_from_message(message_text: str):
    if not message_text:
        return None

    patterns = [
        r"role\s*[:\-]?\s*([A-Za-z0-9/ .&+-]+)",
        r"job\s+role\s*[:\-]?\s*([A-Za-z0-9/ .&+-]+)",
        r"for\s+(?:the\s+)?role\s+of\s+([A-Za-z0-9/ .&+-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, message_text, flags=re.IGNORECASE)
        if match:
            candidate = match.group(1).strip().strip(" .;:-")
            if candidate and not candidate.lower().startswith("round"):
                return candidate
    return None


def find_matching_placement_drive(db: Session, company_id: int, message_text: str = None):
    filters = [PlacementDrive.company_id == company_id]

    role = infer_job_role_from_message(message_text or "")
    if role:
        filters.append(func.lower(PlacementDrive.job_role) == role.lower())

    drive = db.query(PlacementDrive).filter(*filters).order_by(PlacementDrive.id.desc()).first()
    if drive:
        return drive

    if role is None:
        return db.query(PlacementDrive).filter(PlacementDrive.company_id == company_id).order_by(PlacementDrive.id.desc()).first()

    return None


def get_or_create_placement_drive_for_message(db: Session, company_name: str, message_text: str):
    company = get_or_create_company(db, company_name)
    drive = find_matching_placement_drive(db, company.id, message_text)
    if drive is not None:
        return drive

    drive = PlacementDrive(company_id=company.id)
    db.add(drive)
    db.flush()
    return drive


def get_or_create_topic(db: Session, topic_name: str, category: str):
    normalized = str(topic_name).strip()
    if not normalized:
        return None

    topic = db.query(Topic).filter(func.lower(Topic.name) == normalized.lower()).first()
    if topic:
        return topic

    topic = Topic(name=normalized, category=category)
    db.add(topic)
    db.flush()
    return topic


# ============================================================
# FIND DUPLICATE QUESTION
# ============================================================

def find_duplicate_question(db: Session, placement_drive_id: int, question_text: str, threshold: float = 0.75):
    existing_questions = db.query(Question).filter(Question.placement_drive_id == placement_drive_id).all()

    for question in existing_questions:
        if not question.question_text:
            continue

        similarity = calculate_similarity(question_text, question.question_text)
        if similarity >= threshold:
            return question, similarity

    return None, 0.0


def determine_topic_category(topic_name: str):
    normalized = str(topic_name).strip().lower()

    coding_keywords = [
        "array", "string", "linked list", "stack", "queue", "tree", "graph",
        "recursion", "dynamic programming", "sorting", "searching", "hashing",
        "binary search", "greedy", "data structure"
    ]
    technical_keywords = [
        "dbms", "sql", "join", "oop", "operating system", "process", "thread",
        "deadlock", "computer network", "tcp", "http", "api", "java", "python",
        "c++", "os"
    ]
    aptitude_keywords = [
        "aptitude", "percentage", "ratio", "probability", "time and work",
        "logical reasoning", "verbal", "quantitative"
    ]
    hr_keywords = [
        "strength", "weakness", "introduction", "yourself", "relocation",
        "salary", "career goal"
    ]

    if any(keyword in normalized for keyword in coding_keywords):
        return "Coding"
    if any(keyword in normalized for keyword in technical_keywords):
        return "Technical"
    if any(keyword in normalized for keyword in aptitude_keywords):
        return "Aptitude"
    if any(keyword in normalized for keyword in hr_keywords):
        return "HR"
    return "Other"


def find_best_topic(db: Session, question_text: str, candidate_topics: list):
    if not candidate_topics:
        return None

    question_lower = question_text.lower()
    ranked = []

    for topic_name in candidate_topics:
        topic = db.query(Topic).filter(func.lower(Topic.name) == str(topic_name).lower()).first()
        if not topic:
            continue

        score = 0
        if str(topic.name).lower() in question_lower:
            score += 5
        if topic.category == "Technical" and any(word in question_lower for word in ["dbms", "process", "thread", "sql", "java", "network"]):
            score += 2
        if topic.category == "Coding" and any(word in question_lower for word in ["array", "string", "linked list", "stack", "queue", "tree", "graph"]):
            score += 2
        ranked.append((score, topic))

    if not ranked:
        return None

    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[0][1]


# ============================================================
# STORE EXTRACTED INFORMATION
# ============================================================

def store_extracted_information(db: Session, placement_drive_id: int, information: dict, source_message_id: int = None):
        # --------------------------------------------------------
    # Update placement drive details from extracted NLP data
    # --------------------------------------------------------

    placement_drive = db.query(
        PlacementDrive
    ).filter(
        PlacementDrive.id == placement_drive_id
    ).first()

    if placement_drive:

        job_role = information.get("job_role")

        if job_role:
            placement_drive.job_role = job_role

        difficulty_values = information.get("difficulty", [])

        if isinstance(difficulty_values, list) and difficulty_values:
            placement_drive.overall_difficulty = difficulty_values[0]

        elif isinstance(difficulty_values, str) and difficulty_values:
            placement_drive.overall_difficulty = difficulty_values

        rounds = information.get("rounds", [])

        if isinstance(rounds, list) and rounds:
            placement_drive.number_of_rounds = len(rounds)
    
    
    
    cgpa = information.get("minimum_cgpa")
    backlogs = information.get("maximum_backlogs")

    if cgpa is not None or backlogs is not None:
        db.add(EligibilityCriteria(
            placement_drive_id=placement_drive_id,
            minimum_cgpa=cgpa,
            maximum_backlogs=backlogs
        ))

    rounds = information.get("rounds", [])
    if not isinstance(rounds, list):
        rounds = []

    explicit_difficulty = None
    difficulty_values = information.get("difficulty", [])
    if isinstance(difficulty_values, list) and difficulty_values:
        explicit_difficulty = difficulty_values[0]
    elif isinstance(difficulty_values, str) and difficulty_values:
        explicit_difficulty = difficulty_values

    created_rounds = []
    for round_info in rounds:
        if isinstance(round_info, dict):
            round_number = round_info.get("round_number")
            round_type = round_info.get("round_type")
            description = round_info.get("description") or str(round_info)
        else:
            round_number = None
            round_type = None
            description = str(round_info)

        if not description:
            continue

        if round_type is None:
            lower = description.lower()
            if "aptitude" in lower:
                round_type = "Aptitude"
            elif "coding" in lower:
                round_type = "Coding"
            elif "technical" in lower:
                round_type = "Technical"
            elif "hr" in lower:
                round_type = "HR"
            else:
                round_type = "Unknown"

        if round_number is None and round_type in {"Technical", "HR"}:
            round_number = None

        existing_round = db.query(RecruitmentRound).filter(
            RecruitmentRound.placement_drive_id == placement_drive_id,
            RecruitmentRound.round_number == round_number,
            func.lower(RecruitmentRound.round_type) == round_type.lower(),
            func.lower(func.coalesce(RecruitmentRound.description, "")) == description.lower()
        ).first()
        if existing_round:
            created_rounds.append(existing_round)
            continue

        stored_round = RecruitmentRound(
            placement_drive_id=placement_drive_id,
            round_number=round_number,
            round_type=round_type,
            description=description,
            difficulty=explicit_difficulty if explicit_difficulty and round_type not in {"Unknown"} else None
        )
        db.add(stored_round)
        db.flush()
        created_rounds.append(stored_round)

    feedback_entries = information.get("feedback", [])
    if isinstance(feedback_entries, str):
        feedback_entries = [feedback_entries]
    if isinstance(feedback_entries, list):
        for feedback_text in feedback_entries:
            clean_feedback = str(feedback_text).strip()
            if not clean_feedback:
                continue
            source_prefix = f"[source_message_id={source_message_id}] " if source_message_id is not None else ""
            experience_text = f"{source_prefix}{clean_feedback}"
            existing_experience = db.query(Experience).filter(
                Experience.placement_drive_id == placement_drive_id,
                func.lower(Experience.experience_text) == experience_text.lower()
            ).first()
            if existing_experience:
                continue
            db.add(Experience(
                placement_drive_id=placement_drive_id,
                experience_text=experience_text,
                sentiment=None,
                difficulty_rating=None,
                verified=False,
            ))

    topics = information.get("topics", [])
    questions = information.get("questions", [])

    if not isinstance(topics, list):
        topics = []
    if not isinstance(questions, list):
        questions = []

    normalized_topics = []
    for topic_name in topics:
        if not topic_name:
            continue
        clean_name = str(topic_name).strip()
        if clean_name and clean_name not in normalized_topics:
            normalized_topics.append(clean_name)

    topic_records = {}
    for topic_name in normalized_topics:
        category = determine_topic_category(topic_name)
        topic = get_or_create_topic(db, topic_name, category)
        if topic:
            topic_records[topic_name] = topic

    for question_text in questions:
        if not question_text:
            continue

        question_text = question_text.strip()
        if not question_text:
            continue

        # Skip incomplete question fragments
        if len(question_text) < 8:
            continue

        incomplete_patterns = [
            r"^sample\s*q\.?$",
            r"^sample\s*question\.?$",
            r"^write\s+(a\s+)?program\s+to\??$",
            r"^write\s+(an\s+)?sql\s+query\s+to\??$",
            r"^write\s+sql\s+query\s+to\??$",
            r"^explain\s+the\??$",
            r"^explain\s+your\??$",
            r"^how\s+would\s+you\??$",
            r"^s\??$",
            r"^are\s+anagrams\??$",
            r"^are\s+unclear\??$",
            r"^find\s+duplicate\s+records\??$",
        ]

        if any(re.match(pattern, question_text.lower()) for pattern in incomplete_patterns):
            continue

        if source_message_id is not None:
            existing_question = db.query(Question).filter(
                Question.placement_drive_id == placement_drive_id,
                Question.source_message_id == source_message_id,
                func.lower(Question.question_text) == question_text.lower()
            ).first()
            if existing_question:
                continue

        existing_question, similarity = find_duplicate_question(db, placement_drive_id, question_text)
        if existing_question:
            existing_question.occurrence_count += 1
            existing_question.confidence_score = calculate_confidence(
                existing_question.occurrence_count,
                existing_question.verification_status == "verified"
            )
            continue

        matched_topic = find_best_topic(db, question_text, list(topic_records.keys()))

        matched_round = None
        if len(created_rounds) == 1:
            matched_round = created_rounds[0]
        elif created_rounds:
            question_lower = question_text.lower()
            best_match = None
            best_score = -1
            for round_obj in created_rounds:
                round_type = str(round_obj.round_type or "").lower()
                if not round_type:
                    continue
                score = 0
                if round_type in question_lower:
                    score += 3
                if "technical" in round_type and any(word in question_lower for word in ["dbms", "thread", "process", "sql", "java", "network", "oop", "rest api"]):
                    score += 2
                if "coding" in round_type and any(word in question_lower for word in ["array", "string", "reverse", "linked list", "tree", "graph", "substring"]):
                    score += 2
                if "aptitude" in round_type and any(word in question_lower for word in ["ratio", "profit", "percentage", "logical", "verbal"]):
                    score += 2
                if "hr" in round_type and any(word in question_lower for word in ["yourself", "strength", "weakness", "relocation", "salary"]):
                    score += 2
                if score > best_score:
                    best_score = score
                    best_match = round_obj
            if best_score > 0:
                matched_round = best_match

        if matched_round is None and created_rounds:
            matched_round = created_rounds[0]

        db.add(Question(
            placement_drive_id=placement_drive_id,
            round_id=matched_round.id if matched_round else None,
            topic_id=matched_topic.id if matched_topic else None,
            source_message_id=source_message_id,
            question_text=question_text,
            difficulty=explicit_difficulty,
            occurrence_count=1,
            confidence_score=35.0,
            verification_status="unverified"
        ))

    db.commit()