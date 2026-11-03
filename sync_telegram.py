from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")

# ============================================================
# EXISTING PROJECT MODULES
# ============================================================

from database import SessionLocal
from models import RawMessage
from nlp.raw_message_processor import process_raw_message_record
from telegram.client import create_client, get_authorized_chat_ids
from telegram.collector import (
    _already_saved,
    get_telegram_chat_id,
    prepare_raw_message_record,
)


# ============================================================
# MAIN SYNC
# ============================================================

async def main():

    print()
    print("=" * 60)
    print("        PLACEMENT FEEDBACK - TELEGRAM SYNC")
    print("=" * 60)
    print()

    db = SessionLocal()
    client = create_client()

    fetched_count = 0
    inserted_count = 0
    duplicate_count = 0
    processing_success = 0
    processing_failure = 0

    created_raw_ids = []

    try:

        # --------------------------------------------------------
        # CONNECT TELEGRAM
        # --------------------------------------------------------

        print("Connecting to Telegram...")

        await client.connect()

        if not await client.is_user_authorized():

            print()
            print("Telegram session is not authorized.")
            print("Please complete the Telegram login first.")
            return

        print("Telegram connected successfully.")
        print()

        # --------------------------------------------------------
        # GET AUTHORIZED CHATS
        # --------------------------------------------------------

        chat_ids = get_authorized_chat_ids()

        if not chat_ids:

            print("No authorized Telegram chat IDs configured.")
            return

        print(f"Authorized chats found: {len(chat_ids)}")
        print()

        # --------------------------------------------------------
        # STEP 1: FETCH NEW TELEGRAM MESSAGES
        # --------------------------------------------------------

        for chat_id in chat_ids:

            print(f"Checking Telegram chat: {chat_id}")

            try:
                entity = await client.get_entity(chat_id)

                messages = await client.get_messages(
                    entity,
                    limit=50
                )

            except Exception as exc:

                print(
                    f"Could not fetch chat {chat_id}: {exc}"
                )

                continue

            fetched_count += len(messages)

            for message in messages:

                if message is None:
                    continue

                message_text = (
                    getattr(message, "raw_text", None)
                    or getattr(message, "message", None)
                    or getattr(message, "text", None)
                )

                if not message_text:
                    continue

                telegram_message_id = str(
                    getattr(message, "id", None)
                )

                if not telegram_message_id:
                    continue

                # ------------------------------------------------
                # SKIP ALREADY SAVED TELEGRAM MESSAGE
                # ------------------------------------------------

                if _already_saved(
                    db,
                    telegram_message_id,
                    get_telegram_chat_id(message),
                ):

                    duplicate_count += 1
                    continue

                # ------------------------------------------------
                # SAVE RAW TELEGRAM MESSAGE
                # ------------------------------------------------

                payload = prepare_raw_message_record(
                    message,
                    placement_drive_id=None
                )

                raw_message = RawMessage(
                    **payload
                )

                db.add(raw_message)
                db.flush()

                created_raw_ids.append(
                    raw_message.id
                )

                inserted_count += 1

                print(
                    f"  + New message saved: "
                    f"Telegram ID {telegram_message_id}"
                )

        db.commit()

        print()
        print(
            f"New messages inserted: {inserted_count}"
        )

        # --------------------------------------------------------
        # STEP 2: PROCESS NEW MESSAGES WITH NLP
        # --------------------------------------------------------

        print()
        print("Processing new messages with NLP...")
        print()

        if not created_raw_ids:

            print("No new messages to process.")

        else:

            raw_messages = (
                db.query(RawMessage)
                .filter(
                    RawMessage.id.in_(created_raw_ids)
                )
                .all()
            )

            for raw_message in raw_messages:

                try:

                    print(
                        f"Processing RawMessage "
                        f"{raw_message.id}..."
                    )

                    response = process_raw_message_record(
                        db=db,
                        raw_message_id=raw_message.id,
                    )
                    db.commit()
                    processing_success += 1
                    result = response.get("nlp_result") or {}
                    info = result.get("extracted_information") or {}
                    company_name = response.get("company") or info.get("company")

                    # --------------------------------------------
                    # DISPLAY WHAT WAS EXTRACTED
                    # --------------------------------------------

                    print(
                        f"  ✓ Company: {company_name}"
                    )

                    if info.get("job_role"):
                        print(
                            f"  ✓ Role: "
                            f"{info.get('job_role')}"
                        )

                    if info.get("minimum_cgpa") is not None:
                        print(
                            f"  ✓ CGPA: "
                            f"{info.get('minimum_cgpa')}"
                        )

                    if info.get("maximum_backlogs") is not None:
                        print(
                            f"  ✓ Backlogs: "
                            f"{info.get('maximum_backlogs')}"
                        )

                    rounds = info.get("rounds")

                    if isinstance(rounds, list):
                        print(
                            f"  ✓ Rounds extracted: "
                            f"{len(rounds)}"
                        )

                    questions = info.get("questions")

                    if isinstance(questions, list):
                        print(
                            f"  ✓ Questions extracted: "
                            f"{len(questions)}"
                        )

                    topics = info.get("topics")

                    if isinstance(topics, list):
                        print(
                            f"  ✓ Topics extracted: "
                            f"{len(topics)}"
                        )

                    print()

                except Exception as exc:

                    db.rollback()

                    processing_failure += 1

                    print(
                        f"  ✗ Processing failed for "
                        f"RawMessage {raw_message.id}: "
                        f"{exc}"
                    )

        # --------------------------------------------------------
        # FINAL SUMMARY
        # --------------------------------------------------------

        print()
        print("=" * 60)
        print("              TELEGRAM SYNC COMPLETE")
        print("=" * 60)

        print(
            f"Telegram messages fetched : {fetched_count}"
        )

        print(
            f"New messages inserted     : {inserted_count}"
        )

        print(
            f"Duplicate messages skipped: {duplicate_count}"
        )

        print(
            f"Processing successful     : {processing_success}"
        )

        print(
            f"Processing failed        : {processing_failure}"
        )

        print("=" * 60)
        print()

        if inserted_count > 0 and processing_success > 0:

            print(
                "✓ New Telegram feedback has been added "
                "to PostgreSQL."
            )

            print(
                "✓ Refresh the React dashboard to see it."
            )

        elif inserted_count == 0:

            print(
                "No new Telegram messages were found."
            )

        print()

    except Exception as exc:

        db.rollback()

        print()
        print(
            f"Telegram sync failed: {exc}"
        )
        print()

    finally:

        try:
            await client.disconnect()
        except Exception:
            pass

        db.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())