from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from database import SessionLocal
from models import RawMessage
from telegram.client import (
    TelegramChatIdError,
    TelegramConnectionError,
    TelegramMessageFetchError,
    connect_client,
    create_client,
    get_authorized_chat_ids,
)


def prepare_raw_message_record(message: Any, placement_drive_id: Optional[int] = None) -> Dict[str, Any]:
    """Build a payload that matches the existing RawMessage model."""

    message_id = getattr(message, "id", None)
    if message_id is None:
        raise TelegramMessageFetchError("Telegram message has no valid message ID.")

    raw_text = getattr(message, "raw_text", None)
    if raw_text is None:
        raw_text = getattr(message, "message", None)
    if raw_text is None:
        raw_text = ""

    if isinstance(raw_text, str):
        message_text = raw_text
    else:
        message_text = str(raw_text)

    sender = getattr(message, "sender", None)
    sender_name = ""
    if sender is not None:
        parts = [
            getattr(sender, "first_name", None),
            getattr(sender, "last_name", None),
            getattr(sender, "username", None),
        ]
        sender_name = " ".join(part for part in parts if part)

    if not sender_name:
        sender_name = getattr(message, "post_author", None) or "unknown"

    message_date = getattr(message, "date", None)
    if message_date is not None and hasattr(message_date, "date"):
        message_date = message_date.date()

    return {
        "message_id": str(message_id),
        "source": "telegram",
        "sender": sender_name,
        "message_text": message_text,
        "message_date": message_date if isinstance(message_date, date) else None,
        "placement_drive_id": placement_drive_id,
        "processed": False,
    }


def _already_saved(db: Session, telegram_message_id: str) -> bool:
    return (
        db.query(RawMessage)
        .filter(RawMessage.source == "telegram", RawMessage.message_id == telegram_message_id)
        .first()
        is not None
    )


async def collect_telegram_messages(
    db: Optional[Session] = None,
    placement_drive_id: Optional[int] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Collect recent Telegram messages from the configured authorized chats.

    This function does not run automatically. It only executes when the project owner
    explicitly calls it after setting the required environment variables.
    """

    if db is None:
        db = SessionLocal()

    client = create_client()
    saved_records: List[Dict[str, Any]] = []

    try:
        await connect_client(client)
        authorized_chat_ids = get_authorized_chat_ids()

        for chat_id in authorized_chat_ids:
            try:
                entity = await client.get_entity(chat_id)
                messages = await client.get_messages(entity, limit=limit)
            except ValueError as exc:
                raise TelegramChatIdError(f"Invalid Telegram chat ID: {chat_id}") from exc
            except Exception as exc:
                raise TelegramMessageFetchError(
                    f"Unable to fetch messages from chat ID {chat_id}: {exc}"
                ) from exc

            for message in messages:
                if message is None:
                    continue

                text_value = getattr(message, "raw_text", None) or getattr(message, "message", None)
                if text_value is None and getattr(message, "text", None) is None:
                    continue

                telegram_message_id = str(getattr(message, "id", None))
                if not telegram_message_id:
                    continue

                if _already_saved(db, telegram_message_id):
                    continue

                payload = prepare_raw_message_record(message, placement_drive_id)
                raw_message = RawMessage(**payload)
                db.add(raw_message)
                saved_records.append(payload)

        db.commit()
        return saved_records

    except TelegramConfigError:
        raise
    except TelegramConnectionError:
        raise
    except TelegramChatIdError:
        raise
    except TelegramMessageFetchError:
        raise
    except Exception as exc:
        db.rollback()
        raise TelegramMessageFetchError(f"Telegram collection failed: {exc}") from exc
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
        if db is not None and db.is_active:
            db.close()


def collect_telegram_messages_sync(
    db: Optional[Session] = None,
    placement_drive_id: Optional[int] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Synchronous wrapper for running collection from a normal Python script."""

    import asyncio

    return asyncio.run(collect_telegram_messages(db=db, placement_drive_id=placement_drive_id, limit=limit))
