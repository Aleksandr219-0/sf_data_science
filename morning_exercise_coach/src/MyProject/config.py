from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

ORIGINAL_DIR = DATA_DIR / "original"
REFERENCE_DIR = DATA_DIR / "reference"
PROCESSED_DIR = DATA_DIR / "processed"

MODELS_DIR = PROJECT_ROOT / "models"
OUTPUT_DIR = PROJECT_ROOT / "output"

POSE_MODEL_PATH = MODELS_DIR / "pose_landmarker_full.task"

OUTPUT_VIDEO = OUTPUT_DIR / "morning_coach_result.mp4"
METRICS_CSV = OUTPUT_DIR / "morning_coach_metrics.csv"
PLOT_PATH = OUTPUT_DIR / "metrics_plot.png"

VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".webm",
}

DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 480


for directory in [
    ORIGINAL_DIR,
    REFERENCE_DIR,
    PROCESSED_DIR,
    MODELS_DIR,
    OUTPUT_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)
