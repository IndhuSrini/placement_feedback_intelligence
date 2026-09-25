import re


def clean_message(text: str) -> str:
    """
    Clean raw placement message text.
    """

    text = text.strip()

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # Preserve natural Telegram line breaks for question lists while collapsing repeated spaces.
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text