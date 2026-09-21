"""Small, controlled Telegram collection test.

This script is intentionally limited to a short verification of the existing
Telegram-to-PostgreSQL flow without redesigning the app.

It does NOT:
- collect the full chat history
- touch the NLP rules or extractor logic
- rewrite the database schema
- change the existing FastAPI endpoints
- create parallel collection logic

The script reuses the existing helpers and the current RawMessage model so it
stays consistent with the rest of the project.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")

from database import SessionLocal
from models import PlacementDrive, RawMessage
from nlp.processor import process_message
from nlp.storage import store_extracted_information
from telegram.client import create_client, get_authorized_chat_ids
from telegram.collector import _already_saved, prepare_raw_message_record


async def main() -> None:
    """Fetch up to 20 recent Telegram messages, save only new ones, and process them."""
    db = SessionLocal()
    client = create_client()

    fetched_count = 0
    inserted_count = 0
    duplicate_count = 0
    processing_success = 0
    processing_failure = 0
    created_raw_ids: list[int] = []

    extracted_summary = {
        "companies": [],
        "cgpa_eligibility": [],
        "backlog_criteria": [],
        "recruitment_rounds": [],
        "difficulty_values": [],
        "questions": [],
        "topics": [],
    }

    try:
        await client.connect()

        if not await client.is_user_authorized():
            print("Telegram session is not authorized. Please complete the existing login flow first.")
            return

        configured_chat_ids = get_authorized_chat_ids()
        target_chat_id = configured_chat_ids[0]

        try:
            entity = await client.get_entity(target_chat_id)
        except ValueError:
            print(f"Configured Telegram chat is invalid or inaccessible: {target_chat_id}")
            return
        except Exception as exc:
            print(f"Unable to resolve Telegram chat {target_chat_id}: {exc}")
            return

        try:
            messages = await client.get_messages(entity, limit=20)
        except Exception as exc:
            print(f"Telegram message retrieval failed for chat {target_chat_id}: {exc}")
            return

        fetched_count = len(messages)

        for message in messages:
            if message is None:
                continue

            message_text = getattr(message, "raw_text", None) or getattr(message, "message", None)
            if message_text is None and getattr(message, "text", None) is None:
                continue

            telegram_message_id = str(getattr(message, "id", None))
            if not telegram_message_id:
                continue

            if _already_saved(db, telegram_message_id):
                duplicate_count += 1
                continue

            payload = prepare_raw_message_record(message, placement_drive_id=None)
            raw_message = RawMessage(**payload)
            db.add(raw_message)
            db.flush()
            created_raw_ids.append(raw_message.id)
            inserted_count += 1

        db.commit()

        placement_drive_id = db.query(PlacementDrive.id).first()
        if placement_drive_id is not None:
            placement_drive_id = placement_drive_id[0]

        for raw_message in db.query(RawMessage).filter(RawMessage.id.in_(created_raw_ids)).all():
            try:
                result = process_message(raw_message.message_text)
                info = result.get("extracted_information", {})

                if placement_drive_id is not None:
                    store_extracted_information(
                        db=db,
                        placement_drive_id=placement_drive_id,
                        information=info,
                        source_message_id=raw_message.id,
                    )

                processing_success += 1

                if info.get("minimum_cgpa") is not None:
                    extracted_summary["cgpa_eligibility"].append(f"CGPA >= {info['minimum_cgpa']}")
                if info.get("maximum_backlogs") is not None:
                    extracted_summary["backlog_criteria"].append(f"Backlogs <= {info['maximum_backlogs']}")

                if info.get("rounds"):
                    for item in info["rounds"]:
                        if isinstance(item, dict):
                            round_value = item.get("round_type") or item.get("description") or "Unknown"
                            if round_value not in extracted_summary["recruitment_rounds"]:
                                extracted_summary["recruitment_rounds"].append(str(round_value))

                if info.get("difficulty"):
                    for item in info["difficulty"]:
                        value = str(item)
                        if value not in extracted_summary["difficulty_values"]:
                            extracted_summary["difficulty_values"].append(value)

                questions = info.get("questions", [])
                if isinstance(questions, list):
                    for question in questions:
                        q_text = str(question)
                        if q_text not in extracted_summary["questions"]:
                            extracted_summary["questions"].append(q_text)

                topics = info.get("topics", [])
                if isinstance(topics, list):
                    for topic in topics:
                        topic_name = str(topic)
                        if topic_name not in extracted_summary["topics"]:
                            extracted_summary["topics"].append(topic_name)

            except Exception:
                processing_failure += 1

        db.commit()

        print("Telegram collection test summary")
        print(f"Telegram messages fetched: {fetched_count}")
        print(f"New RawMessage records inserted: {inserted_count}")
        print(f"Duplicate messages skipped: {duplicate_count}")
        print(f"Processing success: {processing_success}")
        print(f"Processing failure: {processing_failure}")
        print("Extracted placement information:")
        print(f"Companies found: {extracted_summary['companies']}")
        print(f"CGPA/eligibility information found: {extracted_summary['cgpa_eligibility']}")
        print(f"Backlog criteria found: {extracted_summary['backlog_criteria']}")
        print(f"Recruitment rounds found: {extracted_summary['recruitment_rounds']}")
        print(f"Difficulty values found: {extracted_summary['difficulty_values']}")
        print(f"Questions found: {len(extracted_summary['questions'])}")
        print(f"Topics/categories found: {extracted_summary['topics']}")

    except Exception as exc:
        db.rollback()
        print(f"Telegram collection test failed: {exc}")
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
