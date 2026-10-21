import numpy as np


def normalize_pose(pose: np.ndarray):
    if np.isnan(pose).any():
        return None

    shoulder_center = (
        pose[11] + pose[12]
    ) / 2

    hip_center = (
        pose[23] + pose[24]
    ) / 2

    center = (
        shoulder_center + hip_center
    ) / 2

    scale = max(
        np.linalg.norm(
            pose[11] - pose[12]
        ),
        1e-6,
    )

    return (pose - center) / scale
