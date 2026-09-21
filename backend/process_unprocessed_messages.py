from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")

from database import SessionLocal
from models import PlacementDrive, RawMessage
from nlp.processor import process_message
from nlp.storage import store_extracted_information


def process_single_message(db, raw_message: RawMessage):
    """Process one raw Telegram message using the existing NLP pipeline."""
    if raw_message is None:
        raise ValueError("Raw message is missing.")

    if raw_message.placement_drive_id is None:
        raise ValueError(f"Message {raw_message.id} has no placement_drive_id assigned.")

    placement_drive = (
        db.query(PlacementDrive)
        .filter(PlacementDrive.id == raw_message.placement_drive_id)
        .first()
    )
    if placement_drive is None:
        raise ValueError(
            f"Message {raw_message.id} references missing placement_drive_id {raw_message.placement_drive_id}."
        )

    if raw_message.message_text is None or not str(raw_message.message_text).strip():
        raise ValueError(f"Message {raw_message.id} has no message text.")

    result = process_message(raw_message.message_text)
    information = result.get("extracted_information", {}) if isinstance(result, dict) else {}

    store_extracted_information(
        db=db,
        placement_drive_id=placement_drive.id,
        information=information,
        source_message_id=raw_message.id,
    )

    raw_message.processed = True
    db.commit()

    return result


def main() -> None:
    db = SessionLocal()
    success_count = 0
    failed_count = 0

    try:
        unprocessed_before = (
            db.query(RawMessage)
            .filter(RawMessage.processed.is_(False))
            .count()
        )

        print(f"Total unprocessed before run: {unprocessed_before}")

        messages = (
            db.query(RawMessage)
            .filter(RawMessage.processed.is_(False))
            .order_by(RawMessage.id.asc())
            .all()
        )

        for raw_message in messages:
            print(f"Processing message ID: {raw_message.id}")
            try:
                process_single_message(db, raw_message)
                success_count += 1
                print("Success")
            except Exception as exc:
                failed_count += 1
                print(f"Failed: {exc}")
                db.rollback()

        remaining_unprocessed = (
            db.query(RawMessage)
            .filter(RawMessage.processed.is_(False))
            .count()
        )

        print("Final summary")
        print(f"Total unprocessed before run: {unprocessed_before}")
        print(f"Successfully processed: {success_count}")
        print(f"Failed: {failed_count}")
        print(f"Remaining unprocessed: {remaining_unprocessed}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
