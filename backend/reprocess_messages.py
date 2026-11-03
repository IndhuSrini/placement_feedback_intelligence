from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import func, inspect as inspect_database

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")

from database import SessionLocal
from models import (
    Company,
    EligibilityCriteria,
    PlacementDrive,
    PlacementDriveTopic,
    Question,
    QuestionSourceMessage,
    RawMessage,
    RecruitmentRound,
    Topic,
)
from nlp.extractor import normalize_company_name
from nlp.processor import process_message
from nlp.storage import (
    find_matching_placement_drive,
    infer_job_role_from_message,
    normalize_job_role,
)
from routes.messages import process_raw_message


def _drive_counts(db, drive_id):
    if drive_id is None:
        return {
            "rounds": 0,
            "topics": 0,
            "questions": 0,
            "question_sources": 0,
            "eligibility": 0,
        }
    return {
        "rounds": db.query(RecruitmentRound)
        .filter_by(placement_drive_id=drive_id)
        .count(),
        "topics": db.query(PlacementDriveTopic)
        .filter_by(placement_drive_id=drive_id)
        .count(),
        "questions": db.query(Question)
        .filter_by(placement_drive_id=drive_id)
        .count(),
        "question_sources": db.query(QuestionSourceMessage)
        .join(Question, Question.id == QuestionSourceMessage.question_id)
        .filter(
            Question.placement_drive_id == drive_id,
            QuestionSourceMessage.raw_message_id.isnot(None),
        )
        .count(),
        "eligibility": db.query(EligibilityCriteria)
        .filter_by(placement_drive_id=drive_id)
        .count(),
    }


def _drive_snapshot(db, drive_id):
    if drive_id is None:
        return {
            "rounds": [],
            "topics": [],
            "questions": [],
        }

    rounds = (
        db.query(RecruitmentRound)
        .filter_by(placement_drive_id=drive_id)
        .order_by(RecruitmentRound.round_number, RecruitmentRound.id)
        .all()
    )
    round_by_id = {item.id: item for item in rounds}
    topic_rows = (
        db.query(
            PlacementDriveTopic.category,
            PlacementDriveTopic.round_id,
            Topic.name,
        )
        .join(Topic, Topic.id == PlacementDriveTopic.topic_id)
        .filter(PlacementDriveTopic.placement_drive_id == drive_id)
        .order_by(PlacementDriveTopic.category, Topic.name)
        .all()
    )
    question_columns = [
        Question.id.label("id"),
        Question.question_text.label("question"),
        Question.topic_id.label("topic_id"),
        Question.round_id.label("round_id"),
        Question.difficulty.label("difficulty"),
        Question.occurrence_count.label("occurrence_count"),
        Question.source_message_id.label("source_message_id"),
        RecruitmentRound.round_type.label("round_type"),
        Topic.name.label("topic"),
        Topic.category.label("topic_category"),
    ]
    question_table_columns = {
        column["name"]
        for column in inspect_database(db.get_bind()).get_columns("questions")
    }
    has_preparation_category = (
        "preparation_category" in question_table_columns
    )
    if has_preparation_category:
        question_columns.append(
            Question.preparation_category.label("preparation_category")
        )
    question_rows = (
        db.query(*question_columns)
        .outerjoin(RecruitmentRound, RecruitmentRound.id == Question.round_id)
        .outerjoin(Topic, Topic.id == Question.topic_id)
        .filter(Question.placement_drive_id == drive_id)
        .order_by(Question.id)
        .all()
    )

    return {
        "rounds": [
            {
                "id": item.id,
                "round_number": item.round_number,
                "round_type": item.round_type,
                "difficulty": item.difficulty,
            }
            for item in rounds
        ],
        "topics": [
            {
                "topic": topic_name,
                "category": category,
                "round_id": round_id,
                "round_type": (
                    round_by_id[round_id].round_type
                    if round_id in round_by_id
                    else None
                ),
            }
            for category, round_id, topic_name in topic_rows
        ],
        "questions": [
            {
                "id": row.id,
                "question": row.question,
                "topic": row.topic,
                "category": (
                    getattr(row, "preparation_category", None)
                    or row.topic_category
                ),
                "round_id": row.round_id,
                "round_type": row.round_type,
                "difficulty": row.difficulty,
                "occurrence_count": row.occurrence_count,
                "source_message_id": row.source_message_id,
            }
            for row in question_rows
        ],
    }


def inspect_message(db, message):
    result = process_message(message.message_text)
    information = result.get("extracted_information") or {}
    company_name = information.get("company")
    role = information.get("job_role") or infer_job_role_from_message(
        message.message_text
    )
    drive = None
    validation_error = None

    if message.placement_drive_id is not None:
        drive = db.query(PlacementDrive).filter_by(
            id=message.placement_drive_id
        ).first()
        if drive is None:
            validation_error = (
                f"Message links to missing placement drive "
                f"{message.placement_drive_id}."
            )
        if drive is not None and company_name:
            normalized = normalize_company_name(company_name)
            company = db.query(Company).filter(
                func.lower(Company.name) == normalized.lower()
            ).first()
            if company is None or company.id != drive.company_id:
                validation_error = (
                    "Extracted company does not match the linked placement drive."
                )
        if (
            drive is not None
            and role
            and drive.job_role
            and normalize_job_role(role) != normalize_job_role(drive.job_role)
        ):
            validation_error = (
                f"Extracted role '{role}' does not match linked drive role "
                f"'{drive.job_role}'."
            )
    elif company_name:
        normalized = normalize_company_name(company_name)
        company = db.query(Company).filter(
            func.lower(Company.name) == normalized.lower()
        ).first()
        if company is not None:
            drive = find_matching_placement_drive(
            db,
            company.id,
            message.message_text,
            information=information,
        )
    else:
        validation_error = "Company not detected; no placement drive can be linked."

    question_details = information.get("question_details") or []
    proposed = {
        "rounds": information.get("rounds") or [],
        "topics": information.get("topic_details") or [],
        "questions": question_details or [
            {"question": question}
            for question in information.get("questions") or []
        ],
    }
    return {
        "nlp_result": result,
        "company": company_name,
        "job_role": role,
        "candidate_drive_id": drive.id if drive else None,
        "candidate_drive_role": drive.job_role if drive else None,
        "would_create_drive": drive is None,
        "validation_error": validation_error,
        "proposed": proposed,
        "extracted_rounds": len(information.get("rounds") or []),
        "extracted_topics": len(information.get("topic_details") or []),
        "extracted_questions": len(information.get("questions") or []),
        "before": _drive_counts(db, drive.id if drive else None),
        "current": _drive_snapshot(db, drive.id if drive else None),
    }


def _audit_record(message, result, mode):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "message_id": message.id,
        "message_sha256": hashlib.sha256(
            message.message_text.encode("utf-8")
        ).hexdigest(),
        **result,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Preview or explicitly reprocess selected raw messages. "
            "The default is read-only dry-run."
        )
    )
    parser.add_argument(
        "--message-id",
        type=int,
        action="append",
        required=True,
        help="RawMessage database ID; repeat this option to select several messages.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply reprocessing instead of performing a dry run.",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required together with --apply to confirm database writes.",
    )
    parser.add_argument(
        "--audit-file",
        type=Path,
        help="Append JSONL before/after records here when applying changes.",
    )
    args = parser.parse_args(argv)

    if args.apply and (not args.confirm or args.audit_file is None):
        parser.error("--apply requires both --confirm and --audit-file.")
    if not args.apply and args.confirm:
        parser.error("--confirm is only valid with --apply.")
    if args.audit_file is not None and not args.apply:
        parser.error("--audit-file is only used when applying reprocessing.")
    if args.apply:
        try:
            with args.audit_file.open("a", encoding="utf-8"):
                pass
        except OSError as exc:
            parser.error(f"Cannot open audit file: {exc}")

    db = SessionLocal()
    try:
        for message_id in args.message_id:
            message = db.query(RawMessage).filter_by(id=message_id).first()
            inspection = None
            if message is None:
                record = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "mode": "apply" if args.apply else "dry-run",
                    "message_id": message_id,
                    "status": "failed",
                    "error": "Raw message not found.",
                }
            else:
                try:
                    inspection = inspect_message(db, message)
                    record = _audit_record(
                        message,
                        inspection,
                        "apply" if args.apply else "dry-run",
                    )
                    record["status"] = "preview"
                    record.pop("nlp_result", None)
                    if inspection["validation_error"]:
                        record["status"] = "failed"
                        record["error"] = inspection["validation_error"]
                    elif args.apply:
                        applied = process_raw_message(
                            message.id,
                            reprocess=True,
                            db=db,
                        )
                        db.refresh(message)
                        record["status"] = "processed"
                        record["placement_drive_id"] = applied[
                            "placement_drive_id"
                        ]
                        record["processed"] = message.processed
                        record["after"] = _drive_counts(
                            db, message.placement_drive_id
                        )
                except Exception as exc:
                    db.rollback()
                    record = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "mode": "apply" if args.apply else "dry-run",
                        "message_id": message_id,
                        "status": "failed",
                        "error": str(exc),
                    }
                    if inspection is not None:
                        record.update(
                            {
                                key: value
                                for key, value in inspection.items()
                                if key != "nlp_result"
                            }
                        )

            serialized = json.dumps(record, default=str)
            print(serialized)
            if args.apply:
                with args.audit_file.open("a", encoding="utf-8") as audit:
                    audit.write(serialized + "\n")
    finally:
        db.close()


if __name__ == "__main__":
    main()
