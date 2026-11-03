from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from telethon import events

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")

# Existing project modules
from database import SessionLocal
from models import RawMessage

from telegram.client import (
    create_client,
    connect_client,
    get_authorized_chat_ids,
)

from telegram.collector import (
    _already_saved,
    get_telegram_chat_id,
    prepare_raw_message_record,
)

from nlp.raw_message_processor import process_raw_message_record


async def main():

    print("=" * 55)
    print("       PLACEMENT FEEDBACK - REAL-TIME LISTENER")
    print("=" * 55)

    client = create_client()
    chat_ids = get_authorized_chat_ids()

    # Prevent simultaneous database processing
    processing_lock = asyncio.Lock()

    await connect_client(client)

    print("Telegram connected successfully.")
    print(f"Monitoring {len(chat_ids)} authorized chat(s).")
    print("Waiting for new messages...")
    print("Press Ctrl+C to stop.")
    print()

    async def handle_new_message(event):

        async with processing_lock:

            db = SessionLocal()

            try:
                message = event.message

                message_text = (
                    getattr(message, "raw_text", None) or ""
                ).strip()

                if not message_text:
                    return

                telegram_message_id = str(message.id)

                # Skip messages already stored
                if _already_saved(
                    db,
                    telegram_message_id,
                    get_telegram_chat_id(message),
                ):
                    print(f"Duplicate skipped: {telegram_message_id}")
                    return

                # Save the raw Telegram message
                payload = prepare_raw_message_record(
                    message,
                    placement_drive_id=None,
                )

                raw_message = RawMessage(**payload)

                db.add(raw_message)
                db.commit()

                print(f"New message received: {telegram_message_id}")

                response = process_raw_message_record(
                    db=db,
                    raw_message_id=raw_message.id,
                )
                db.commit()

                print(
                    "Saved and processed: "
                    f"{response.get('placement_drive_id')}"
                )
                print(f"Raw message ID: {raw_message.id}")
                print()

            except Exception as exc:

                db.rollback()

                print(f"Message processing failed: {exc}")

            finally:
                db.close()

    client.add_event_handler(
        handle_new_message,
        events.NewMessage(chats=chat_ids),
    )

    try:
        await client.run_until_disconnected()

    finally:
        await client.disconnect()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nReal-time Telegram listener stopped.")