"""Verify that the configured Telegram chat is accessible and authorized.

This is a read-only validation step. It checks whether the configured chat ID
can be resolved through the already authenticated Telethon session.

It intentionally does NOT:
- collect messages
- fetch members/participants
- insert data into PostgreSQL
- call the NLP pipeline
- modify the existing application flow
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
    TelegramChatIdError,
    TelegramConfigError,
    create_client,
    get_authorized_chat_ids,
)


async def main() -> None:
    """Resolve the configured authorized Telegram chat and print safe metadata."""
    load_dotenv(BACKEND_DIR / ".env")

    try:
        authorized_chat_ids = get_authorized_chat_ids()
    except (TelegramConfigError, TelegramChatIdError) as exc:
        print(f"Chat configuration error: {exc}")
        return

    if not authorized_chat_ids:
        print("No authorized Telegram chat IDs are configured.")
        return

    chat_id = authorized_chat_ids[0]
    client = create_client()

    try:
        await client.connect()

        if not await client.is_user_authorized():
            print("Telegram session is not authorized. Please complete the existing login flow first.")
            return

        try:
            entity = await client.get_entity(chat_id)
        except ValueError as exc:
            print(f"Invalid or inaccessible Telegram chat ID: {chat_id}")
            print(f"Reason: {exc}")
            return
        except Exception as exc:
            print(f"Unable to resolve configured Telegram chat ID: {chat_id}")
            print(f"Reason: {exc}")
            return

        if entity is None:
            print(f"Configured Telegram chat ID is not accessible: {chat_id}")
            return

        title = getattr(entity, "title", None)
        if not title:
            title = getattr(entity, "first_name", None) or getattr(entity, "username", None) or "Unknown"

        chat_type = getattr(entity, "broadcast", None)
        if chat_type is True:
            chat_type_name = "channel"
        elif getattr(entity, "megagroup", None) is True:
            chat_type_name = "supergroup"
        elif getattr(entity, "is_group", None) is True:
            chat_type_name = "group"
        else:
            chat_type_name = "private"

        print("Authorized Telegram chat verified")
        print(f"Chat ID: {chat_id}")
        print(f"Name: {title}")
        print(f"Type: {chat_type_name}")

    except Exception as exc:
        print(f"Telegram verification failed: {exc}")
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
