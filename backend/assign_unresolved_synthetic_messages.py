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


# This utility is only for synthetic development/test data.
# The assignment does not represent company information extracted from the original message.

def main() -> None:
    db = SessionLocal()

    try:
        synthetic_drives = (
            db.query(PlacementDrive)
            .order_by(PlacementDrive.id.asc())
            .all()
        )

        if not synthetic_drives:
            print("eligible unresolved non-empty messages: 0")
            print("messages assigned: 0")
            print("empty messages skipped: 0")
            print("remaining unresolved messages: 0")
            return

        unresolved_messages = (
            db.query(RawMessage)
            .filter(RawMessage.source == "telegram")
            .filter(RawMessage.processed.is_(False))
            .filter(RawMessage.placement_drive_id.is_(None))
            .order_by(RawMessage.id.asc())
            .all()
        )

        eligible_non_empty = []
        empty_messages = 0

        for message in unresolved_messages:
            text = (message.message_text or "").strip()
            if not text:
                empty_messages += 1
                continue

            if "Company: not mentioned" in text:
                continue

            eligible_non_empty.append(message)

        total_eligible = len(eligible_non_empty)
        assigned_count = 0
        drive_ids = [drive.id for drive in synthetic_drives]

        for index, message in enumerate(eligible_non_empty):
            drive_id = drive_ids[index % len(drive_ids)]
            if message.placement_drive_id is not None:
                continue
            message.placement_drive_id = drive_id
            db.add(message)
            assigned_count += 1

        db.commit()

        remaining_unresolved = (
            db.query(RawMessage)
            .filter(RawMessage.source == "telegram")
            .filter(RawMessage.processed.is_(False))
            .filter(RawMessage.placement_drive_id.is_(None))
            .count()
        )

        print("Final summary")
        print(f"eligible unresolved non-empty messages: {total_eligible}")
        print(f"messages assigned: {assigned_count}")
        print(f"empty messages skipped: {empty_messages}")
        print(f"remaining unresolved messages: {remaining_unresolved}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
