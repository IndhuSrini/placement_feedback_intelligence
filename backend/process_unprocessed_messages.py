from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")

from database import SessionLocal
from models import RawMessage
from nlp.raw_message_processor import process_raw_message_record


def process_single_message(db, raw_message: RawMessage):
    """Process one raw Telegram message using the existing NLP pipeline."""
    if raw_message is None:
        raise ValueError("Raw message is missing.")

    raw_message = (
        db.query(RawMessage)
        .with_for_update()
        .populate_existing()
        .filter(RawMessage.id == raw_message.id)
        .first()
    )
    if raw_message is None:
        raise ValueError("Raw message no longer exists.")

    try:
        result = process_raw_message_record(
            db=db,
            raw_message_id=raw_message.id,
        )
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


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
