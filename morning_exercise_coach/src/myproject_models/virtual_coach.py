import numpy as np


def get_coach_message(
    similarity: float,
    distance: float,
    confidence: float,
) -> str:
    if confidence < 0.4:
        return "Low pose confidence"

    if not np.isfinite(similarity):
        return "Pose not detected"

    if similarity >= 0.90 and distance <= 0.15:
        return "Excellent movement"

    if similarity >= 0.75 and distance <= 0.30:
        return "Good, move more precisely"

    if similarity >= 0.60:
        return "Check arms and legs position"

    return "Repeat the exercise slower"
