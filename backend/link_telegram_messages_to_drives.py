from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import func

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")

from database import SessionLocal
from models import Company, PlacementDrive, RawMessage

COMPANY_NAMES = [
    "TCS",
    "Infosys",
    "Cognizant",
    "Accenture",
    "Capgemini",
    "Wipro",
    "Zoho",
    "Freshworks",
    "HCLTech",
    "IBM",
    "Tech Mahindra",
    "Deloitte",
]

ROLE_NAMES = [
    "Software Engineer",
    "Graduate Engineer Trainee",
    "Programmer Analyst",
    "Software Developer",
    "Associate Software Engineer",
    "System Engineer",
    "Java Developer",
    "Python Developer",
]

ROUND_NAMES = [
    "Aptitude",
    "Coding",
    "Communication",
    "Technical Interview",
    "Managerial Interview",
    "HR",
]

DIFFICULTY_MAP = {
    "easy": "Easy",
    "medium": "Medium",
    "moderate": "Moderate",
    "hard": "Hard",
}


def normalize_name(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def extract_company_name(text: str) -> tuple[Optional[str], str]:
    normalized = text or ""
    candidate_matches = []

    for company in sorted(COMPANY_NAMES, key=len, reverse=True):
        pattern = rf"(?<![A-Za-z]){re.escape(company)}(?![A-Za-z])"
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            candidate_matches.append(company)

    if not candidate_matches:
        return None, "no company information found"

    if len(candidate_matches) > 1:
        # Prefer the longest explicit match when multiple names appear in one message.
        explicit_choice = sorted(candidate_matches, key=len, reverse=True)[0]
        return explicit_choice, "company name ambiguous"

    return candidate_matches[0], ""


def extract_recruitment_date(text: str) -> Optional[str]:
    match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if match:
        return match.group(1)
    return None


def extract_role(text: str) -> Optional[str]:
    lowered = text.lower()
    for role in sorted(ROLE_NAMES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(role.lower())}\b", lowered):
            return role
    return None


def extract_round_count(text: str) -> Optional[int]:
    lower_text = text.lower()
    count = 0
    for round_name in ROUND_NAMES:
        if re.search(rf"\b{re.escape(round_name.lower())}\b", lower_text):
            count += 1
    return count if count > 0 else None


def extract_difficulty(text: str) -> Optional[str]:
    lower_text = text.lower()
    for key, value in DIFFICULTY_MAP.items():
        if re.search(rf"\b{re.escape(key)}\b", lower_text) or re.search(rf"\b{re.escape(value.lower())}\b", lower_text):
            return value
    return None


def get_or_create_company(db, company_name: str) -> tuple[Company, bool]:
    normalized = normalize_name(company_name)
    if not normalized:
        raise ValueError("Company name is required.")

    existing = (
        db.query(Company)
        .filter(func.lower(Company.name) == normalized.lower())
        .first()
    )
    if existing is not None:
        return existing, False

    company = Company(name=normalized)
    db.add(company)
    db.flush()
    return company, True


def build_drive_match_filters(company_id: int, recruitment_date: Optional[str], role: Optional[str]):
    filters = [PlacementDrive.company_id == company_id]
    if recruitment_date:
        try:
            parsed_date = datetime.strptime(recruitment_date, "%Y-%m-%d").date()
        except ValueError:
            parsed_date = None
        if parsed_date is not None:
            filters.append(PlacementDrive.recruitment_date == parsed_date)
    if role:
        filters.append(func.lower(PlacementDrive.job_role) == role.lower())
    return filters


def find_or_create_placement_drive(db, company_name: str, text: str):
    company, created_company = get_or_create_company(db, company_name)

    recruitment_date = extract_recruitment_date(text)
    role = extract_role(text)
    round_count = extract_round_count(text)
    difficulty = extract_difficulty(text)

    conditions = [PlacementDrive.company_id == company.id]
    if recruitment_date:
        try:
            parsed_date = datetime.strptime(recruitment_date, "%Y-%m-%d").date()
        except ValueError:
            parsed_date = None
        if parsed_date is not None:
            conditions.append(PlacementDrive.recruitment_date == parsed_date)
    if role:
        conditions.append(func.lower(PlacementDrive.job_role) == role.lower())

    existing_drive = db.query(PlacementDrive).filter(*conditions).first()
    if existing_drive is not None:
        return existing_drive, created_company, False

    year_value = 2026
    if recruitment_date:
        try:
            year_value = datetime.strptime(recruitment_date, "%Y-%m-%d").year
        except ValueError:
            year_value = 2026

    new_drive = PlacementDrive(
        company_id=company.id,
        recruitment_date=datetime.strptime(recruitment_date, "%Y-%m-%d").date() if recruitment_date else None,
        year=year_value,
        job_role=role,
        number_of_rounds=round_count,
        overall_difficulty=difficulty,
    )
    db.add(new_drive)
    db.flush()
    return new_drive, created_company, True


def main() -> None:
    db = SessionLocal()
    total_eligible = 0
    linked_to_existing = 0
    new_drives_created = 0
    new_companies_created = 0
    unresolved_messages = 0

    try:
        messages = (
            db.query(RawMessage)
            .filter(RawMessage.source == "telegram")
            .filter(RawMessage.processed.is_(False))
            .filter(RawMessage.placement_drive_id.is_(None))
            .order_by(RawMessage.id.asc())
            .all()
        )

        total_eligible = len(messages)
        print(f"Total eligible Telegram messages: {total_eligible}")

        for message in messages:
            print(f"Processing message ID: {message.id}")

            if message.message_text is None or not str(message.message_text).strip():
                unresolved_messages += 1
                print("Unresolved: empty message text")
                continue

            company_name, reason = extract_company_name(message.message_text)
            if not company_name:
                unresolved_messages += 1
                print(f"Unresolved: {reason}")
                continue

            if reason == "company name ambiguous":
                unresolved_messages += 1
                print(f"Unresolved: {reason}")
                continue

            drive, created_company, created_drive = find_or_create_placement_drive(
                db,
                company_name,
                message.message_text,
            )

            if created_company:
                new_companies_created += 1
            if created_drive:
                new_drives_created += 1
            else:
                linked_to_existing += 1

            message.placement_drive_id = drive.id
            db.add(message)
            db.commit()
            print(f"Linked to PlacementDrive ID: {drive.id}")

        remaining_without_drive = (
            db.query(RawMessage)
            .filter(RawMessage.source == "telegram")
            .filter(RawMessage.processed.is_(False))
            .filter(RawMessage.placement_drive_id.is_(None))
            .count()
        )

        print("Final summary")
        print(f"Total eligible Telegram messages: {total_eligible}")
        print(f"Linked to existing drives: {linked_to_existing}")
        print(f"New drives created: {new_drives_created}")
        print(f"New companies created: {new_companies_created}")
        print(f"Unresolved messages: {unresolved_messages}")
        print(f"Remaining without placement_drive_id: {remaining_without_drive}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
