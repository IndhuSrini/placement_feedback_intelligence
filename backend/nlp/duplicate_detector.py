import re

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    _HAS_SEMANTIC = True
except Exception:  # pragma: no cover
    SentenceTransformer = None
    cosine_similarity = None
    _HAS_SEMANTIC = False


model = SentenceTransformer("all-MiniLM-L6-v2") if _HAS_SEMANTIC else None


def _normalize_for_similarity(text: str) -> str:
    cleaned = str(text).lower()
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def calculate_similarity(text1: str, text2: str) -> float:
    if _HAS_SEMANTIC and model is not None:
        try:
            embeddings = model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except Exception:
            pass

    a = _normalize_for_similarity(text1)
    b = _normalize_for_similarity(text2)
    if not a or not b:
        return 0.0

    a_words = set(a.split())
    b_words = set(b.split())
    if not a_words or not b_words:
        return 0.0

    overlap = len(a_words & b_words)
    union = len(a_words | b_words)
    if union == 0:
        return 0.0

    return float(overlap / union)


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