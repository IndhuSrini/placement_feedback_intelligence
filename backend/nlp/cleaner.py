import re


def clean_message(text: str) -> str:
    """
    Clean raw placement message text.
    """
    if not text:
        return ""

    text = str(text)

    # Normalize invisible Unicode characters and non-breaking spaces
    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("\ufeff", "")

    # Standardize fancy quote marks to standard quotes
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")

    # Standardize en-dash, em-dash, and horizontal bars to standard hyphen-minus
    text = text.replace("–", "-").replace("—", "-").replace("―", "-").replace("−", "-")

    # Standardize bullet symbols to hyphens for uniform list parsing
    text = re.sub(r"(^|[\n\r\s])[•●▪▫✦★■◆]\s*", r"\1- ", text)

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # Preserve natural Telegram line breaks for question lists while collapsing repeated spaces.
    text = re.sub(r"[ \t]*\r?\n[ \t]*", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()
