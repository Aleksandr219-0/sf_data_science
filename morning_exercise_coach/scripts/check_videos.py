import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT / "src"),
)

from MyProject.config import (
    ORIGINAL_DIR,
    REFERENCE_DIR,
)

from MyProject.utils import find_video

from myproject_data.video_loader import (
    get_video_metadata,
)


for name, folder in [
    ("Видео пользователя", ORIGINAL_DIR),
    ("Эталонное видео", REFERENCE_DIR),
]:
    video = find_video(folder)

    print(f"\n{name}:")
    print(video)

    print("Метаданные:")
    print(get_video_metadata(video))
