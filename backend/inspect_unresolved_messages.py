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


def main() -> None:
    db = SessionLocal()
    try:
        unresolved = (
            db.query(RawMessage)
            .filter(RawMessage.source == "telegram")
            .filter(RawMessage.processed.is_(False))
            .filter(RawMessage.placement_drive_id.is_(None))
            .order_by(RawMessage.id.asc())
            .all()
        )

        empty_text_count = 0
        non_empty_text_count = 0

        print("Unresolved Telegram RawMessage records")
        for message in unresolved:
            text = message.message_text or ""
            if text.strip():
                non_empty_text_count += 1
            else:
                empty_text_count += 1

            print(f"RawMessage ID: {message.id}")
            print(f"message date: {message.message_date}")
            print(f"message text: {text}")
            print("---")

        print("Final summary")
        print(f"total unresolved messages: {len(unresolved)}")
        print(f"number with empty text: {empty_text_count}")
        print(f"number with non-empty text: {non_empty_text_count}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
