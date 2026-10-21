import sys
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT / "src"),
)

from MyProject.config import POSE_MODEL_PATH


MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_full/float16/1/"
    "pose_landmarker_full.task"
)


if not POSE_MODEL_PATH.exists():
    print("Скачивание MediaPipe Pose Landmarker...")

    urllib.request.urlretrieve(
        MODEL_URL,
        POSE_MODEL_PATH,
    )

print(f"Модель готова: {POSE_MODEL_PATH}")
