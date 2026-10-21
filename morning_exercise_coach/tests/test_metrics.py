import numpy as np

from myproject_models.pose_metrics import (
    cosine_similarity,
    weighted_distance,
)


def test_cosine_similarity_same_pose():
    pose = np.array(
        [
            [0.0, 0.0],
            [1.0, 1.0],
        ]
    )

    result = cosine_similarity(
        pose,
        pose,
    )

    assert np.isclose(
        result,
        1.0,
    )


def test_weighted_distance_same_pose():
    pose = np.array(
        [
            [0.0, 0.0],
            [1.0, 1.0],
        ]
    )

    confidence = np.array(
        [
            1.0,
            1.0,
        ]
    )

    result = weighted_distance(
        pose,
        pose,
        confidence,
    )

    assert np.isclose(
        result,
        0.0,
    )
