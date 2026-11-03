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
from models import RawMessage
from nlp.raw_message_processor import process_raw_message_record
from telegram.client import create_client, get_authorized_chat_ids
from telegram.collector import (
    _already_saved,
    get_telegram_chat_id,
    prepare_raw_message_record,
)


def process_new_raw_message(db, raw_message: RawMessage):
    """Extract and store one new Telegram message atomically."""
    response = process_raw_message_record(
        db=db,
        raw_message_id=raw_message.id,
    )
    result = response.get("nlp_result") or {}
    return result.get("extracted_information") or {}


async def main() -> None:
    """Fetch recent Telegram messages and process only new messages."""
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
            print(
                "Telegram session is not authorized. "
                "Please complete the existing login flow first."
            )
            return

        configured_chat_ids = get_authorized_chat_ids()

        if not configured_chat_ids:
            print("No authorized Telegram chat IDs are configured.")
            return

        target_chat_id = configured_chat_ids[0]

        try:
            entity = await client.get_entity(target_chat_id)
        except ValueError:
            print(
                f"Configured Telegram chat is invalid or inaccessible: "
                f"{target_chat_id}"
            )
            return
        except Exception as exc:
            print(
                f"Unable to resolve Telegram chat {target_chat_id}: {exc}"
            )
            return

        try:
            messages = await client.get_messages(entity, limit=20)
        except Exception as exc:
            print(
                f"Telegram message retrieval failed for chat "
                f"{target_chat_id}: {exc}"
            )
            return

        fetched_count = len(messages)

        # ---------------------------------------------------------
        # STEP 1: Save new Telegram messages
        # ---------------------------------------------------------
        for message in messages:
            if message is None:
                continue

            message_text = (
                getattr(message, "raw_text", None)
                or getattr(message, "message", None)
            )

            if message_text is None and getattr(message, "text", None) is None:
                continue

            telegram_message_id = str(getattr(message, "id", None))

            if not telegram_message_id:
                continue

            if _already_saved(
                db,
                telegram_message_id,
                get_telegram_chat_id(message),
            ):
                duplicate_count += 1
                continue

            payload = prepare_raw_message_record(
                message,
                placement_drive_id=None,
            )

            raw_message = RawMessage(**payload)

            db.add(raw_message)
            db.flush()

            created_raw_ids.append(raw_message.id)
            inserted_count += 1

        db.commit()

        # ---------------------------------------------------------
        # STEP 2: Process each new message
        # ---------------------------------------------------------
        raw_messages = (
            db.query(RawMessage)
            .filter(RawMessage.id.in_(created_raw_ids))
            .all()
        )

        for raw_message in raw_messages:
            try:
                with db.begin_nested():
                    info = process_new_raw_message(db, raw_message)

                processing_success += 1

                company_name = info.get("company")
                if company_name and company_name not in extracted_summary["companies"]:
                    extracted_summary["companies"].append(company_name)

                # -------------------------------------------------
                # Summary information
                # -------------------------------------------------
                if info.get("minimum_cgpa") is not None:
                    extracted_summary["cgpa_eligibility"].append(
                        f"CGPA >= {info['minimum_cgpa']}"
                    )

                if info.get("maximum_backlogs") is not None:
                    extracted_summary["backlog_criteria"].append(
                        f"Backlogs <= {info['maximum_backlogs']}"
                    )

                if info.get("rounds"):
                    for item in info["rounds"]:
                        if isinstance(item, dict):
                            round_value = (
                                item.get("round_type")
                                or item.get("description")
                                or "Unknown"
                            )

                            if (
                                str(round_value)
                                not in extracted_summary[
                                    "recruitment_rounds"
                                ]
                            ):
                                extracted_summary[
                                    "recruitment_rounds"
                                ].append(str(round_value))

                if info.get("difficulty"):
                    for item in info["difficulty"]:
                        value = str(item)

                        if (
                            value
                            not in extracted_summary["difficulty_values"]
                        ):
                            extracted_summary[
                                "difficulty_values"
                            ].append(value)

                questions = info.get("questions", [])

                if isinstance(questions, list):
                    for question in questions:
                        q_text = str(question)

                        if (
                            q_text
                            not in extracted_summary["questions"]
                        ):
                            extracted_summary["questions"].append(
                                q_text
                            )

                topics = info.get("topics", [])

                if isinstance(topics, list):
                    for topic in topics:
                        topic_name = str(topic)

                        if (
                            topic_name
                            not in extracted_summary["topics"]
                        ):
                            extracted_summary["topics"].append(
                                topic_name
                            )

            except Exception as exc:
                processing_failure += 1

                print(
                    f"Processing failed for RawMessage "
                    f"{raw_message.id}: {exc}"
                )

        db.commit()

        # ---------------------------------------------------------
        # FINAL SUMMARY
        # ---------------------------------------------------------
        print()
        print("Telegram collection test summary")
        print("---------------------------------")
        print(f"Telegram messages fetched: {fetched_count}")
        print(
            f"New RawMessage records inserted: {inserted_count}"
        )
        print(
            f"Duplicate messages skipped: {duplicate_count}"
        )
        print(
            f"Processing success: {processing_success}"
        )
        print(
            f"Processing failure: {processing_failure}"
        )

        print()
        print("Extracted placement information:")

        print(
            f"Companies found: "
            f"{extracted_summary['companies']}"
        )

        print(
            f"CGPA/eligibility information found: "
            f"{extracted_summary['cgpa_eligibility']}"
        )

        print(
            f"Backlog criteria found: "
            f"{extracted_summary['backlog_criteria']}"
        )

        print(
            f"Recruitment rounds found: "
            f"{extracted_summary['recruitment_rounds']}"
        )

        print(
            f"Difficulty values found: "
            f"{extracted_summary['difficulty_values']}"
        )

        print(
            f"Questions found: "
            f"{len(extracted_summary['questions'])}"
        )

        print(
            f"Topics/categories found: "
            f"{extracted_summary['topics']}"
        )

    except Exception as exc:
        db.rollback()
        print(
            f"Telegram collection test failed: {exc}"
        )

    finally:
        try:
            await client.disconnect()
        except Exception:
            pass

        db.close()


if __name__ == "__main__":
    asyncio.run(main())