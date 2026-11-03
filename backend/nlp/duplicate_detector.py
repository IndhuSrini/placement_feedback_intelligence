import re

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    _HAS_SEMANTIC = True
except Exception:  # pragma: no cover
    SentenceTransformer = None
    cosine_similarity = None
    _HAS_SEMANTIC = False


_model = None


def _get_model():
    global _model
    if _model is None and _HAS_SEMANTIC and SentenceTransformer is not None:
        try:
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _model = None
    return _model


# Backwards compatibility reference
model = None

QUESTION_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "can", "could",
    "does", "do", "did", "explain", "find", "for", "from", "how",
    "in", "is", "it", "me", "of", "on", "or", "please", "should",
    "difference", "differences", "tell", "that", "the", "their", "them",
    "there", "these", "this",
    "to", "was", "we", "were", "what", "when", "where", "which",
    "who", "why", "with", "would", "write", "your",
}


def _normalize_for_similarity(text: str) -> str:
    cleaned = str(text).lower()
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _content_words(text: str) -> set[str]:
    return {
        word
        for word in _normalize_for_similarity(text).split()
        if word not in QUESTION_STOP_WORDS
    }


def calculate_similarity(text1: str, text2: str) -> float:
    words1 = _content_words(text1)
    words2 = _content_words(text2)

    if not words1 or not words2:
        return 0.0

    shared_words = words1 & words2
    union = words1 | words2
    lexical_similarity = len(shared_words) / len(union)

    if words1 == words2:
        return 1.0

    # A common question template or a single shared keyword is not
    # enough evidence that two interview questions are duplicates.
    if len(shared_words) < 2:
        return lexical_similarity

    if _HAS_SEMANTIC and model is not None:
        try:
            embeddings = model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            if lexical_similarity >= 0.5:
                return max(lexical_similarity, float(similarity))
        except Exception:
            pass

    return lexical_similarity


def is_duplicate(
    new_text: str,
    existing_texts: list[str],
    threshold: float = 0.75
):
    for existing_text in existing_texts:
        similarity = calculate_similarity(new_text, existing_text)
        if similarity >= threshold:
            return {
                "duplicate": True,
                "similarity": similarity,
                "matched_text": existing_text
            }

    return {
        "duplicate": False,
        "similarity": 0.0,
        "matched_text": None
    }