import re

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import (
    Company,
    EligibilityCriteria,
    Experience,
    PlacementDrive,
    PlacementDriveTopic,
    PlacementDriveTopicSourceMessage,
    RecruitmentRound,
    RecruitmentRoundSourceMessage,
    Topic,
    Question,
    QuestionSourceMessage,
    EligibilitySourceMessage,
)

from nlp.duplicate_detector import calculate_similarity
from nlp.confidence import calculate_confidence
from nlp.extractor import (
    extract_backlogs,
    extract_batch,
    extract_branch_eligibility,
    extract_cgpa,
    extract_package,
    extract_role,
    extract_year,
    normalize_company_name,
)


# ============================================================
# GET OR CREATE COMPANY / PLACEMENT DRIVE
# ============================================================

class DriveMatchAmbiguous(ValueError):
    """Raised when a source message cannot safely identify one drive."""


def get_or_create_company(db: Session, company_name: str):
    normalized = normalize_company_name(company_name)
    if not normalized:
        raise ValueError("A company name is required to create a placement drive.")

    company = (
        db.query(Company)
        .filter(func.lower(Company.name) == normalized.lower())
        .with_for_update()
        .first()
    )
    if company:
        return company

    company = Company(name=normalized)
    db.add(company)
    db.flush()
    return company


def infer_job_role_from_message(message_text: str):
    return extract_role(message_text)


def normalize_job_role(role: str):
    if not role:
        return None
    return re.sub(r"[^a-z0-9]+", " ", str(role).casefold()).strip()


def _normalized_context_value(value):
    return re.sub(r"\s+", " ", str(value or "").casefold()).strip()


def _message_context(message_text: str, information: dict = None):
    information = information or {}
    return {
        "job_role": information.get("job_role") or extract_role(message_text or ""),
        "batch": information.get("batch") or extract_batch(message_text or ""),
        "year": information.get("year") or extract_year(message_text or ""),
        "package": information.get("package") or extract_package(message_text or ""),
        "minimum_cgpa": information.get("minimum_cgpa")
        if "minimum_cgpa" in information
        else extract_cgpa(message_text or ""),
        "maximum_backlogs": information.get("maximum_backlogs")
        if "maximum_backlogs" in information
        else extract_backlogs(message_text or ""),
        "branch_eligibility": information.get("branch_eligibility")
        or extract_branch_eligibility(message_text or ""),
    }


def _drive_context_conflicts(db: Session, drive: PlacementDrive, context: dict):
    for field in ("batch", "year", "package"):
        incoming = context.get(field)
        existing = getattr(drive, field, None)
        if incoming is not None and existing is not None:
            if _normalized_context_value(incoming) != _normalized_context_value(existing):
                return True

    criteria = db.query(EligibilityCriteria).filter_by(
        placement_drive_id=drive.id
    ).all()
    for incoming_field in (
        "minimum_cgpa",
        "maximum_backlogs",
        "branch_eligibility",
    ):
        incoming = context.get(incoming_field)
        if incoming is None:
            continue
        for existing in criteria:
            stored = getattr(existing, incoming_field, None)
            if stored is None:
                continue
            if incoming_field == "branch_eligibility":
                matches = _normalized_context_value(incoming) == _normalized_context_value(stored)
            else:
                matches = incoming == stored
            if not matches:
                return True

    return False


def _drive_context_evidence(db: Session, drive: PlacementDrive, context: dict):
    score = 0
    for field in ("batch", "year", "package"):
        incoming = context.get(field)
        existing = getattr(drive, field, None)
        if incoming is not None and existing is not None and (
            _normalized_context_value(incoming) == _normalized_context_value(existing)
        ):
            score += 1

    criteria = db.query(EligibilityCriteria).filter_by(
        placement_drive_id=drive.id
    ).all()
    for field in ("minimum_cgpa", "maximum_backlogs", "branch_eligibility"):
        incoming = context.get(field)
        if incoming is None:
            continue
        if any(
            getattr(existing, field, None) is not None
            and (
                _normalized_context_value(incoming)
                == _normalized_context_value(getattr(existing, field))
            )
            for existing in criteria
        ):
            score += 1
    return score


def find_matching_placement_drive(
    db: Session,
    company_id: int,
    message_text: str | None = None,
    information: dict | None = None,
) -> PlacementDrive | None:
    context = _message_context(message_text or "", information)
    drives = (
        db.query(PlacementDrive)
        .filter(PlacementDrive.company_id == company_id)
        .order_by(PlacementDrive.id.desc())
        .all()
    )
    if not drives:
        return None

    role = context["job_role"]
    if not role:
        if len(drives) == 1 and not drives[0].job_role:
            return drives[0]
        raise DriveMatchAmbiguous(
            "The message does not identify a role, and the company has multiple "
            "or role-specific placement drives. Link the message to a drive "
            "explicitly before processing."
        )

    normalized_role = normalize_job_role(role)
    role_matches = [
        drive
        for drive in drives
        if normalize_job_role(drive.job_role) == normalized_role
    ]
    if not role_matches:
        return None

    compatible = [
        drive
        for drive in role_matches
        if not _drive_context_conflicts(db, drive, context)
    ]
    if not compatible:
        return None
    if len(compatible) == 1:
        return compatible[0]

    scored = [
        (_drive_context_evidence(db, drive, context), drive)
        for drive in compatible
    ]
    best_score = max(score for score, _ in scored)
    best_matches = [drive for score, drive in scored if score == best_score]
    if best_score > 0 and len(best_matches) == 1:
        return best_matches[0]

    raise DriveMatchAmbiguous(
        f"More than one {role!r} placement drive matches the company, and "
        "the message does not contain enough batch, year, package, or "
        "eligibility details to distinguish them."
    )


def validate_placement_drive_context(
    db: Session,
    drive: PlacementDrive,
    message_text: str,
    information: dict | None = None,
):
    context = _message_context(message_text or "", information)
    if (
        context["job_role"]
        and drive.job_role
        and normalize_job_role(context["job_role"])
        != normalize_job_role(drive.job_role)
    ):
        raise ValueError(
            f"Extracted role '{context['job_role']}' does not match placement "
            f"drive role '{drive.job_role}'."
        )
    if _drive_context_conflicts(db, drive, context):
        raise ValueError(
            "The extracted batch, year, package, or eligibility details conflict "
            "with the explicitly linked placement drive."
        )


def get_or_create_placement_drive_for_message(
    db: Session,
    company_name: str,
    message_text: str,
    information: dict | None = None,
):
    company = get_or_create_company(db, company_name)
    context = _message_context(message_text or "", information)
    drive = find_matching_placement_drive(
        db,
        company.id,
        message_text,
        information=information,
    )
    if drive is not None:
        return drive

    drive = PlacementDrive(
        company_id=company.id,
        job_role=context["job_role"],
        batch=context["batch"],
        year=context["year"],
        package=context["package"],
    )
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

def find_duplicate_question(
    db: Session,
    placement_drive_id: int,
    question_text: str,
    threshold: float = 0.75,
    round_id: int | None = None,
    topic_id: int | None = None,
    category: str | None = None,
):
    existing_questions = (
        db.query(Question)
        .filter(
            Question.placement_drive_id == placement_drive_id,
            Question.round_id == round_id
            if round_id is not None
            else Question.round_id.is_(None),
            Question.topic_id == topic_id
            if topic_id is not None
            else Question.topic_id.is_(None),
            Question.preparation_category == category
            if category is not None
            else Question.preparation_category.is_(None),
        )
        .all()
    )

    for question in existing_questions:
        if not question.question_text:
            continue

        similarity = calculate_similarity(question_text, question.question_text)
        if similarity >= threshold:
            return question, similarity

    return None, 0.0


def _record_source_message(db: Session, model, filters: dict, source_message_id):
    if source_message_id is None:
        return

    if db.query(model).filter_by(**filters).filter_by(
        raw_message_id=source_message_id
    ).first() is None:
        db.add(model(**filters, raw_message_id=source_message_id))


def determine_topic_category(topic_name: str):
    normalized = str(topic_name).strip().lower()

    communication_keywords = [
        "communication", "verbal", "grammar", "listening", "reading comprehension",
        "speaking", "pronunciation", "sentence correction", "vocabulary"
    ]
    coding_keywords = [
        "array", "string", "linked list", "stack", "queue", "tree", "graph",
        "recursion", "dynamic programming", "sorting", "searching", "hashing",
        "binary search", "greedy", "data structure"
    ]
    technical_keywords = [
        "dbms", "sql", "join", "oop", "operating system", "deadlock",
        "computer network", "tcp", "http", "api", "java", "python", "c++"
    ]
    aptitude_keywords = [
        "aptitude", "percentage", "ratio", "probability", "time and work",
        "logical reasoning", "quantitative", "number series", "blood relations"
    ]
    hr_keywords = [
        "strength", "weakness", "introduction", "yourself", "relocation",
        "salary", "career goal", "hobbies"
    ]

    if any(keyword in normalized for keyword in communication_keywords):
        return "Communication"
    if any(keyword in normalized for keyword in coding_keywords):
        return "Coding"
    if any(keyword in normalized for keyword in technical_keywords) or (
        re.search(r"\b(?:os|process|thread)\b", normalized)
        and not re.search(r"\brecruitment\s+process\b", normalized)
    ):
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
    topic_patterns = {
        "arrays": r"\barrays?\b",
        "strings": r"\bstrings?\b",
        "oop": r"\b(?:oops?|object[- ]oriented|method\s+overload\w*|method\s+overrid\w*)\b",
        "dbms": r"\b(?:dbms|normalization|database)\b",
    }

    for topic_name in candidate_topics:
        topic = db.query(Topic).filter(func.lower(Topic.name) == str(topic_name).lower()).first()
        if not topic:
            continue

        normalized_name = str(topic.name).strip().lower()
        pattern = topic_patterns.get(normalized_name)
        if pattern is None:
            escaped_name = re.escape(normalized_name)
            if normalized_name.endswith("s"):
                escaped_name = re.escape(normalized_name[:-1]) + r"s?"
            pattern = rf"\b{escaped_name}\b"

        if re.search(pattern, question_lower):
            ranked.append((len(normalized_name), topic))

    if not ranked:
        return None

    ranked.sort(key=lambda item: item[0], reverse=True)
    if len(ranked) > 1 and ranked[0][0] == ranked[1][0]:
        return None
    return ranked[0][1]


def _round_description_key(description: str):
    normalized = re.sub(r"[^a-z0-9 ]", " ", str(description or "").lower())
    words = [
        word
        for word in normalized.split()
        if word not in {"round", "interview", "stage", "assessment"}
    ]
    return " ".join(words)


def _find_existing_round(db: Session, placement_drive_id: int, round_number, round_type, description):
    existing_rounds = db.query(RecruitmentRound).filter(
        RecruitmentRound.placement_drive_id == placement_drive_id,
        func.lower(RecruitmentRound.round_type) == round_type.lower(),
    ).order_by(RecruitmentRound.id).all()

    incoming_description = _round_description_key(description)
    for existing_round in existing_rounds:
        if existing_round.round_number == round_number:
            return existing_round

        if (
            (round_number is None or existing_round.round_number is None)
            and _round_description_key(existing_round.description) == incoming_description
        ):
            return existing_round

    return None


def _round_for_topic(rounds_by_number, round_number):
    return rounds_by_number.get(round_number) if round_number is not None else None


def _question_key(question_text: str):
    return re.sub(r"[^a-z0-9]", "", str(question_text or "").lower())


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
    ).with_for_update().first()

    if placement_drive is None:
        raise ValueError(f"Placement drive {placement_drive_id} does not exist.")

    if placement_drive:
        job_role = information.get("job_role")
        if (
            job_role
            and placement_drive.job_role
            and normalize_job_role(job_role)
            != normalize_job_role(placement_drive.job_role)
        ):
            raise ValueError(
                f"Extracted role '{job_role}' does not match placement drive "
                f"role '{placement_drive.job_role}'."
            )
        if job_role and not placement_drive.job_role:
            placement_drive.job_role = job_role

        for field in ("batch", "year", "package"):
            incoming = information.get(field)
            existing = getattr(placement_drive, field, None)
            if incoming is None:
                continue
            if existing is not None and (
                _normalized_context_value(existing)
                != _normalized_context_value(incoming)
            ):
                raise ValueError(
                    f"Extracted {field} '{incoming}' does not match placement "
                    f"drive {field} '{existing}'."
                )
            if existing is None:
                setattr(placement_drive, field, incoming)

        difficulty_values = information.get("difficulty", [])

        if isinstance(difficulty_values, list) and difficulty_values:
            placement_drive.overall_difficulty = difficulty_values[0]

        elif isinstance(difficulty_values, str) and difficulty_values:
            placement_drive.overall_difficulty = difficulty_values

        rounds = information.get("rounds", [])
        if (
            placement_drive.number_of_rounds is None
            and isinstance(rounds, list)
            and rounds
        ):
            placement_drive.number_of_rounds = len(rounds)
    
    
    
    cgpa = information.get("minimum_cgpa")
    backlogs = information.get("maximum_backlogs")
    branch_eligibility = information.get("branch_eligibility")
    other_criteria = information.get("other_criteria")

    if any(value is not None for value in (cgpa, backlogs, branch_eligibility, other_criteria)):
        existing_criteria = db.query(EligibilityCriteria).filter_by(
            placement_drive_id=placement_drive_id,
            minimum_cgpa=cgpa,
            maximum_backlogs=backlogs,
            branch_eligibility=branch_eligibility,
            other_criteria=other_criteria,
        ).first()
        if existing_criteria is None:
            existing_criteria = EligibilityCriteria(
                placement_drive_id=placement_drive_id,
                minimum_cgpa=cgpa,
                maximum_backlogs=backlogs,
                branch_eligibility=branch_eligibility,
                other_criteria=other_criteria,
            )
            db.add(existing_criteria)
            db.flush()
        _record_source_message(
            db,
            EligibilitySourceMessage,
            {"eligibility_id": existing_criteria.id},
            source_message_id,
        )

    rounds = information.get("rounds", [])
    if not isinstance(rounds, list):
        rounds = []

    explicit_difficulty = None
    difficulty_values = information.get("difficulty", [])
    if isinstance(difficulty_values, list) and len(difficulty_values) == 1:
        explicit_difficulty = difficulty_values[0]
    elif isinstance(difficulty_values, str) and difficulty_values:
        explicit_difficulty = difficulty_values

    rounds_by_number = {}
    rounds_by_type = {}
    for round_info in rounds:
        if isinstance(round_info, dict):
            round_number = round_info.get("round_number")
            round_type = round_info.get("round_type")
            description = round_info.get("description") or str(round_info)
            round_difficulty = round_info.get("difficulty")
        else:
            round_number = None
            round_type = None
            description = str(round_info)
            round_difficulty = None

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

        existing_round = _find_existing_round(
            db,
            placement_drive_id,
            round_number,
            round_type,
            description,
        )
        if existing_round:
            if existing_round.round_number is None and round_number is not None:
                existing_round.round_number = round_number
            if round_difficulty or explicit_difficulty:
                existing_round.difficulty = round_difficulty or explicit_difficulty
            stored_round = existing_round
        else:
            stored_round = RecruitmentRound(
                placement_drive_id=placement_drive_id,
                round_number=round_number,
                round_type=round_type,
                description=description,
                difficulty=(round_difficulty or explicit_difficulty)
                if (round_difficulty or explicit_difficulty)
                and round_type != "Unknown"
                else None
            )
            db.add(stored_round)
            db.flush()

        _record_source_message(
            db,
            RecruitmentRoundSourceMessage,
            {"round_id": stored_round.id},
            source_message_id,
        )

        if round_number is not None:
            rounds_by_number[round_number] = stored_round
        rounds_by_type.setdefault(round_type.casefold(), []).append(stored_round)

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
    topic_details = information.get("topic_details", [])
    question_details = information.get("question_details", [])

    if not isinstance(topics, list):
        topics = []
    if not isinstance(questions, list):
        questions = []
    if not isinstance(topic_details, list):
        topic_details = []
    if not isinstance(question_details, list):
        question_details = []

    normalized_topic_details = []
    seen_topic_details = set()
    for detail in topic_details:
        if not isinstance(detail, dict):
            continue
        topic_name = str(detail.get("topic") or "").strip()
        if not topic_name:
            continue
        category = str(detail.get("category") or determine_topic_category(topic_name)).strip()
        key = (topic_name.casefold(), category.casefold())
        if key in seen_topic_details:
            continue
        normalized_topic_details.append(
            {
                "topic": topic_name,
                "category": category,
                "round_number": detail.get("round_number"),
            }
        )
        seen_topic_details.add(key)

    for topic_name in topics:
        clean_name = str(topic_name or "").strip()
        if not clean_name:
            continue
        key = (clean_name.casefold(), determine_topic_category(clean_name).casefold())
        if key not in seen_topic_details and not any(
            detail["topic"].casefold() == clean_name.casefold()
            for detail in normalized_topic_details
        ):
            normalized_topic_details.append(
                {
                    "topic": clean_name,
                    "category": determine_topic_category(clean_name),
                    "round_number": None,
                }
            )
            seen_topic_details.add(key)

    topic_records = {}
    for detail in normalized_topic_details:
        topic_name = detail["topic"]
        category = detail["category"]
        topic = get_or_create_topic(db, topic_name, category)
        if not topic:
            continue

        topic_records[topic_name.casefold()] = topic
        associated_round = _round_for_topic(
            rounds_by_number,
            detail.get("round_number"),
        )
        scope_key = (
            f"round:{associated_round.id}"
            if associated_round
            else f"category:{category.casefold()}"
        )
        existing_association = db.query(PlacementDriveTopic).filter_by(
            placement_drive_id=placement_drive_id,
            topic_id=topic.id,
            scope_key=scope_key,
        ).first()
        if existing_association is None:
            existing_association = PlacementDriveTopic(
                    placement_drive_id=placement_drive_id,
                    topic_id=topic.id,
                    round_id=associated_round.id if associated_round else None,
                    category=category,
                    scope_key=scope_key,
                    source_message_id=source_message_id,
                )
            db.add(existing_association)
            db.flush()
        _record_source_message(
            db,
            PlacementDriveTopicSourceMessage,
            {"placement_drive_topic_id": existing_association.id},
            source_message_id,
        )

    question_details_by_key = {
        _question_key(detail.get("question")): detail
        for detail in question_details
        if isinstance(detail, dict) and _question_key(detail.get("question"))
    }

    for question_text in questions:
        if not question_text:
            continue

        question_text = str(question_text).strip()
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

        question_detail = question_details_by_key.get(_question_key(question_text), {})
        topic_name = str(question_detail.get("topic") or "").casefold()
        matched_topic = topic_records.get(topic_name) if topic_name else None
        if matched_topic is None:
            matched_topic = find_best_topic(
                db,
                question_text,
                [detail["topic"] for detail in normalized_topic_details],
            )

        round_number = question_detail.get("round_number")
        round_type = str(question_detail.get("round_type") or "").casefold()
        if round_number is not None:
            matched_round = rounds_by_number.get(round_number)
        elif round_type:
            matching_rounds = rounds_by_type.get(round_type, [])
            matched_round = matching_rounds[0] if len(matching_rounds) == 1 else None
        else:
            matched_round = None

        question_category = question_detail.get("category") or (
            matched_topic.category if matched_topic else None
        )

        if source_message_id is not None:
            source_question_query = (
                db.query(Question)
                .join(
                    QuestionSourceMessage,
                    QuestionSourceMessage.question_id == Question.id,
                )
                .filter(
                    Question.placement_drive_id == placement_drive_id,
                    QuestionSourceMessage.raw_message_id == source_message_id,
                    func.lower(Question.question_text) == question_text.lower(),
                    Question.round_id == matched_round.id
                    if matched_round
                    else Question.round_id.is_(None),
                    Question.topic_id == matched_topic.id
                    if matched_topic
                    else Question.topic_id.is_(None),
                    Question.preparation_category == question_category
                    if question_category
                    else Question.preparation_category.is_(None),
                )
            )
            existing_question = source_question_query.first()
            if existing_question:
                if matched_round is not None or existing_question.round_id is None:
                    existing_question.round_id = (
                        matched_round.id if matched_round else None
                    )
                if matched_topic is not None or existing_question.topic_id is None:
                    existing_question.topic_id = (
                        matched_topic.id if matched_topic else None
                    )
                if question_category is not None or existing_question.preparation_category is None:
                    existing_question.preparation_category = question_category
                question_difficulty = (
                    question_detail.get("difficulty") or explicit_difficulty
                )
                if question_difficulty is not None:
                    existing_question.difficulty = question_difficulty
                existing_source = db.query(QuestionSourceMessage).filter_by(
                    question_id=existing_question.id,
                    raw_message_id=source_message_id,
                ).first()
                if existing_source is None:
                    db.add(
                        QuestionSourceMessage(
                            question_id=existing_question.id,
                            raw_message_id=source_message_id,
                        )
                    )
                continue

        existing_question, _ = find_duplicate_question(
            db,
            placement_drive_id,
            question_text,
            round_id=matched_round.id if matched_round else None,
            topic_id=matched_topic.id if matched_topic else None,
            category=question_category,
        )
        if existing_question:
            if source_message_id is None:
                if matched_round is not None:
                    existing_question.round_id = matched_round.id
                if matched_topic is not None:
                    existing_question.topic_id = matched_topic.id
                if question_category is not None:
                    existing_question.preparation_category = question_category
                existing_question.occurrence_count += 1
                existing_question.confidence_score = calculate_confidence(
                    existing_question.occurrence_count,
                    existing_question.verification_status == "verified",
                )
                continue

            existing_source = db.query(QuestionSourceMessage).filter_by(
                question_id=existing_question.id,
                raw_message_id=source_message_id,
            ).first()
            if existing_source is None:
                db.add(
                    QuestionSourceMessage(
                        question_id=existing_question.id,
                        raw_message_id=source_message_id,
                    )
                )
                if existing_question.source_message_id != source_message_id:
                    existing_question.occurrence_count += 1
                    existing_question.confidence_score = calculate_confidence(
                        existing_question.occurrence_count,
                        existing_question.verification_status == "verified",
                    )

            if (
                existing_source is not None
                or existing_question.source_message_id == source_message_id
            ) and len(question_text) > len(existing_question.question_text or ""):
                existing_question.question_text = question_text

            if existing_question.source_message_id == source_message_id:
                existing_question.round_id = (
                    matched_round.id if matched_round else None
                )
                existing_question.topic_id = (
                    matched_topic.id if matched_topic else None
                )
                category = question_detail.get("category") or (
                    matched_topic.category if matched_topic else None
                )
                if category is not None:
                    existing_question.preparation_category = category
                question_difficulty = (
                    question_detail.get("difficulty") or explicit_difficulty
                )
                if question_difficulty is not None:
                    existing_question.difficulty = question_difficulty
            else:
                if existing_question.round_id is None and matched_round:
                    existing_question.round_id = matched_round.id
                if existing_question.topic_id is None and matched_topic:
                    existing_question.topic_id = matched_topic.id
                if (
                    existing_question.preparation_category is None
                    and question_detail.get("category")
                ):
                    existing_question.preparation_category = question_detail.get(
                        "category"
                    )
                if (
                    existing_question.difficulty is None
                    and (
                        question_detail.get("difficulty")
                        or explicit_difficulty
                    )
                ):
                    existing_question.difficulty = (
                        question_detail.get("difficulty")
                        or explicit_difficulty
                    )
            continue

        question = Question(
            placement_drive_id=placement_drive_id,
            round_id=matched_round.id if matched_round else None,
            topic_id=matched_topic.id if matched_topic else None,
            preparation_category=question_category,
            source_message_id=source_message_id,
            question_text=question_text,
            difficulty=question_detail.get("difficulty") or explicit_difficulty,
            occurrence_count=1,
            confidence_score=35.0,
            verification_status="unverified",
        )
        db.add(question)
        db.flush()

        if source_message_id is not None:
            db.add(
                QuestionSourceMessage(
                    question_id=question.id,
                    raw_message_id=source_message_id,
                )
            )
