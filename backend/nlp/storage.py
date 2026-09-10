from sqlalchemy import func
from sqlalchemy.orm import Session

from models import (
    EligibilityCriteria,
    RecruitmentRound,
    Topic,
    Question
)

from nlp.duplicate_detector import calculate_similarity
from nlp.confidence import calculate_confidence


# ============================================================
# GET OR CREATE TOPIC
# ============================================================

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

        db.add(RecruitmentRound(
            placement_drive_id=placement_drive_id,
            round_number=round_number,
            round_type=round_type,
            description=description
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

        question_text = str(question_text).strip()
        if not question_text:
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
        for round_info in rounds:
            if not isinstance(round_info, dict):
                continue
            round_type = str(round_info.get("round_type") or "").lower()
            question_lower = question_text.lower()
            if round_type and (
                ("technical" in round_type and any(word in question_lower for word in ["dbms", "thread", "process", "sql", "java", "network"])) or
                ("coding" in round_type and any(word in question_lower for word in ["array", "string", "reverse", "linked list", "tree", "graph"])) or
                ("aptitude" in round_type and any(word in question_lower for word in ["ratio", "profit", "percentage", "logical", "verbal"])) or
                ("hr" in round_type and any(word in question_lower for word in ["yourself", "strength", "weakness", "relocation", "salary"]))
            ):
                matched_round = db.query(RecruitmentRound).filter(
                    RecruitmentRound.placement_drive_id == placement_drive_id,
                    RecruitmentRound.round_type == round_info.get("round_type")
                ).order_by(RecruitmentRound.round_number).first()
                if matched_round:
                    break

        if matched_round is None:
            for round_info in rounds:
                if isinstance(round_info, dict):
                    round_type = str(round_info.get("round_type") or "")
                    if round_type:
                        matched_round = db.query(RecruitmentRound).filter(
                            RecruitmentRound.placement_drive_id == placement_drive_id,
                            RecruitmentRound.round_type == round_type
                        ).order_by(RecruitmentRound.round_number).first()
                        if matched_round:
                            break

        db.add(Question(
            placement_drive_id=placement_drive_id,
            round_id=matched_round.id if matched_round else None,
            topic_id=matched_topic.id if matched_topic else None,
            source_message_id=source_message_id,
            question_text=question_text,
            difficulty=None,
            occurrence_count=1,
            confidence_score=35.0,
            verification_status="unverified"
        ))

    db.commit()