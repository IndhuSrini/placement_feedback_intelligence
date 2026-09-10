"""Telegram ingestion helpers for placement feedback collection.

This package is intentionally isolated from the existing NLP and analytics flow.
It only prepares and stores Telegram raw messages in the existing RawMessage model.
"""

from .client import (
    TelegramChatIdError,
    TelegramConfigError,
    TelegramConnectionError,
    TelegramMessageFetchError,
    create_client,
    get_authorized_chat_ids,
)
from .collector import collect_telegram_messages, prepare_raw_message_record

__all__ = [
    "TelegramConfigError",
    "TelegramConnectionError",
    "TelegramChatIdError",
    "TelegramMessageFetchError",
    "create_client",
    "get_authorized_chat_ids",
    "collect_telegram_messages",
    "prepare_raw_message_record",
]
