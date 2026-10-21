from dataclasses import dataclass

import numpy as np


@dataclass
class PoseVideoDataset:
    frames: list
    poses: np.ndarray
    confidence: np.ndarray
    fps: float
    width: int
    height: int
