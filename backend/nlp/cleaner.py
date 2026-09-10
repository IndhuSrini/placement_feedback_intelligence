import re


def clean_message(text: str) -> str:
    """
    Clean raw placement message text.
    """

    text = text.strip()

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text