import cv2
import numpy as np

from MyProject.constants import POSE_CONNECTIONS


def metric_color(similarity: float):
    if not np.isfinite(similarity):
        return (0, 0, 255)

    if similarity < 0.60:
        return (0, 0, 255)

    if similarity < 0.85:
        return (0, 190, 230)

    return (0, 180, 0)


def draw_pose(
    frame: np.ndarray,
    pose: np.ndarray,
    color: tuple,
    title: str,
) -> np.ndarray:
    image = frame.copy()

    height, width = image.shape[:2]

    if pose is not None and not np.isnan(pose).any():
        points = [
            (
                int(x * width),
                int(y * height),
            )
            for x, y in pose
        ]

        for first, second in POSE_CONNECTIONS:
            cv2.line(
                image,
                points[first],
                points[second],
                color,
                2,
                cv2.LINE_AA,
            )

        for x, y in points:
            cv2.circle(
                image,
                (x, y),
                4,
                color,
                -1,
                cv2.LINE_AA,
            )

    cv2.rectangle(
        image,
        (0, 0),
        (width, 45),
        (25, 25, 25),
        -1,
    )

    cv2.putText(
        image,
        title,
        (12, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    return image
