"""Safe Telegram connection smoke test.

This script is intentionally simple and limited to one purpose:
- load Telegram settings from the existing .env file
- create the Telethon client from the project helper module
- connect to Telegram
- complete the normal authentication flow if the app is not already authorized
- print only a safe success message

It does NOT:
- collect messages from groups or channels
- insert data into PostgreSQL
- call the NLP pipeline
- touch the existing analytics or verification logic
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add the backend folder to the Python path so imports like
# `from telegram.client import create_client` work when this script is run directly.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from telegram.client import create_client


async def main() -> None:
    """Connect to Telegram using the project helper and exit cleanly."""
    # Load environment variables from the project's local .env file.
    # This keeps configuration in one place and avoids hardcoding secrets.
    load_dotenv(BACKEND_DIR / ".env")

    client = create_client()

    try:
        # Connect to Telegram. If the app is not already authorized,
        # this triggers the normal login flow (phone code / password flow).
        await client.connect()

        if not await client.is_user_authorized():
            # Let Telethon handle the normal authentication flow.
            # We do not print the phone number, OTP, or password.
            await client.start()

        # Only print a safe confirmation after successful login.
        print("Telegram connection successful")

        # Optional: fetch the account info without exposing any credentials.
        # This is intentionally kept minimal and safe.
        me = await client.get_me()
        username = getattr(me, "username", None)
        if username:
            print(f"Authenticated account: @{username}")

    finally:
        # Disconnect in all cases so the test finishes cleanly.
        try:
            await client.disconnect()
        except Exception:
            # Ignore cleanup failures to keep the test focused on the connection status.
            pass


if __name__ == "__main__":
    asyncio.run(main())
