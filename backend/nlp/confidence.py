def calculate_confidence(
    occurrence_count: int,
    verified: bool = False
) -> float:
    """
    Calculate confidence based on number of reports
    and faculty verification.
    """

    if occurrence_count <= 0:
        score = 0

    elif occurrence_count == 1:
        score = 35

    elif occurrence_count == 2:
        score = 45

    elif occurrence_count == 3:
        score = 55

    elif occurrence_count <= 5:
        score = 65

    elif occurrence_count <= 10:
        score = 80

    else:
        score = 90

    # Faculty verification gives additional confidence
    if verified:
        score += 10

    return min(score, 100)