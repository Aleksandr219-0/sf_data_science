import numpy as np

from myproject_models.pose_normalizer import (
    normalize_pose,
)


def test_normalize_pose_returns_correct_shape():
    pose = np.tile(
        np.array(
            [
                [0.5, 0.5],
            ],
            dtype=np.float32,
        ),
        (33, 1),
    )

    pose[11] = [0.4, 0.4]
    pose[12] = [0.6, 0.4]
    pose[23] = [0.4, 0.7]
    pose[24] = [0.6, 0.7]

    normalized_pose = normalize_pose(pose)

    assert normalized_pose.shape == (
        33,
        2,
    )
