import os
from pathlib import Path
from typing import List

from telethon import TelegramClient


class TelegramConfigError(ValueError):
    """Raised when Telegram credentials or chat IDs are unavailable."""


class TelegramConnectionError(RuntimeError):
    """Raised when the Telegram client cannot connect or is not authorized."""


class TelegramChatIdError(ValueError):
    """Raised when one or more chat IDs are malformed or invalid."""


class TelegramMessageFetchError(RuntimeError):
    """Raised when message retrieval fails for a configured chat."""


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not str(value).strip():
        raise TelegramConfigError(f"Missing required environment variable: {name}")
    return str(value).strip()


def get_telegram_api_id() -> int:
    raw_value = _get_required_env("TELEGRAM_API_ID")
    try:
        return int(raw_value)
    except ValueError as exc:
        raise TelegramConfigError("TELEGRAM_API_ID must be a valid integer.") from exc


def get_telegram_api_hash() -> str:
    value = _get_required_env("TELEGRAM_API_HASH")
    if len(value) < 8:
        raise TelegramConfigError("TELEGRAM_API_HASH looks incomplete.")
    return value


def get_telegram_session() -> str:
    value = _get_required_env("TELEGRAM_SESSION")
    return value


def get_telegram_session_path() -> str:
    """Return a stable session path in the backend/telegram folder.

    Telethon resolves relative session names against the current working directory.
    That makes the session file change depending on where the script is launched.
    To keep Stage 5.3 and Stage 5.4 using the same authenticated session, we
    pin the session file to the same backend/telegram folder used by the project.
    """
    session_name = get_telegram_session()
    session_path = Path(__file__).resolve().parent / session_name
    return str(session_path)


def get_authorized_chat_ids() -> List[int]:
    raw_value = os.getenv("TELEGRAM_CHAT_IDS", "")
    if not raw_value or not raw_value.strip():
        raise TelegramConfigError(
            "TELEGRAM_CHAT_IDS is required. Provide comma-separated chat IDs such as: -1001234567890,-1009876543210"
        )

    chat_ids: List[int] = []
    for piece in raw_value.split(","):
        clean = piece.strip()
        if not clean:
            continue
        try:
            chat_ids.append(int(clean))
        except ValueError as exc:
            raise TelegramChatIdError(
                f"Invalid Telegram chat ID in TELEGRAM_CHAT_IDS: '{clean}'"
            ) from exc

    if not chat_ids:
        raise TelegramChatIdError("No valid Telegram chat IDs were found in TELEGRAM_CHAT_IDS.")

    return chat_ids


def create_client() -> TelegramClient:
    """Create a Telethon client using environment variables only.

    This function does not do any scraping by itself; it just builds the client.
    The app owner is expected to run collection manually after configuration.
    """

    api_id = get_telegram_api_id()
    api_hash = get_telegram_api_hash()
    session_name = get_telegram_session_path()

    try:
        return TelegramClient(session_name, api_id, api_hash)
    except Exception as exc:
        raise TelegramConnectionError(f"Unable to initialize Telegram client: {exc}") from exc


async def connect_client(client: TelegramClient) -> None:
    """Connect the client and confirm authorization.

    The project owner must complete the login flow once before the collector is used.
    """

    try:
        await client.connect()
        if not await client.is_user_authorized():
            raise TelegramConnectionError(
                "Telegram client is not authorized. Complete the login flow first."
            )
    except TelegramConnectionError:
        raise
    except Exception as exc:
        raise TelegramConnectionError(f"Telegram connection failed: {exc}") from exc
