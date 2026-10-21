import numpy as np


def cosine_similarity(
    reference_pose: np.ndarray,
    user_pose: np.ndarray,
) -> float:
    reference_vector = reference_pose.ravel()
    user_vector = user_pose.ravel()

    denominator = (
        np.linalg.norm(reference_vector)
        * np.linalg.norm(user_vector)
    )

    if denominator <= 1e-9:
        return np.nan

    return float(
        np.dot(
            reference_vector,
            user_vector,
        )
        / denominator
    )


def weighted_distance(
    reference_pose: np.ndarray,
    user_pose: np.ndarray,
    confidence: np.ndarray,
) -> float:
    distances = np.linalg.norm(
        reference_pose - user_pose,
        axis=1,
    )

    weights = np.clip(
        confidence,
        0,
        1,
    )

    valid = (
        np.isfinite(distances)
        & (weights > 0)
    )

    if not valid.any():
        return np.nan

    return float(
        np.average(
            distances[valid],
            weights=weights[valid],
        )
    )


def similarity_to_percent(value: float) -> float:
    if not np.isfinite(value):
        return np.nan

    return float(
        np.clip(
            (value + 1) * 50,
            0,
            100,
        )
    )
