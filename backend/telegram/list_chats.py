"""List available Telegram dialogs without exposing any sensitive data.

This script is intentionally limited to a read-only check of the user's
available chats. It does NOT:
- collect messages
- store anything in PostgreSQL
- connect to the NLP pipeline
- change chat IDs or configuration
- print secret metadata such as API hashes, phone numbers, or session values
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from telegram.client import (
    TelegramConfigError,
    create_client,
)


async def main() -> None:
    """Connect to Telegram and print only a safe summary of available dialogs."""
    # Load the project environment file so the existing Telegram configuration
    # is used without changing any database or NLP code.
    load_dotenv(BACKEND_DIR / ".env")

    client = create_client()

    try:
        await client.connect()

        # If the session has not been authorized yet, Telethon will begin the
        # normal phone/OTP/login flow. We do not print those values.
        if not await client.is_user_authorized():
            await client.start()

        dialogs = await client.get_dialogs(limit=50)

        if not dialogs:
            print("No Telegram dialogs found for this account.")
            return

        print("Telegram dialogs:")
        for index, dialog in enumerate(dialogs, start=1):
            entity = getattr(dialog, "entity", None)
            if entity is None:
                continue

            chat_id = getattr(entity, "id", None)
            title = getattr(entity, "title", None)
            if title is None:
                title = getattr(entity, "first_name", None) or getattr(entity, "username", None) or "Unknown"

            raw_type = getattr(entity, "stringify", None)
            if callable(raw_type):
                chat_type = str(raw_type()).lower()
            else:
                chat_type = str(getattr(entity, "_title", "unknown")).lower()

            # Only show safe metadata: numeric ID, title/name, and type.
            print(f"{index}. ID: {chat_id} | Name: {title} | Type: {chat_type}")

    except TelegramConfigError as exc:
        print(f"Configuration error: {exc}")
    except Exception as exc:
        print(f"Unable to list Telegram dialogs: {exc}")
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
