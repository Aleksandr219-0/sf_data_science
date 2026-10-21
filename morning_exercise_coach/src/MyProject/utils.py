from pathlib import Path

from MyProject.config import VIDEO_EXTENSIONS


def find_video(folder: Path) -> Path:
    videos = sorted(
        file
        for file in folder.iterdir()
        if file.is_file()
        and file.suffix.lower() in VIDEO_EXTENSIONS
    )

    if not videos:
        raise FileNotFoundError(
            f"В папке нет видео: {folder}. "
            "Добавьте видео пользователя в data/original/, "
            "а эталонное видео в data/reference/."
        )

    if len(videos) > 1:
        print(
            f"В папке {folder} найдено несколько видео. "
            f"Используется: {videos[0].name}"
        )

    return videos[0]
