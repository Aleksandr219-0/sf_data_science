import cv2


def get_video_metadata(video_path):
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError(
            f"Не удалось открыть видео: {video_path}"
        )

    metadata = {
        "fps": cap.get(cv2.CAP_PROP_FPS) or 30.0,
        "width": int(
            cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        ),
        "height": int(
            cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        ),
        "frame_count": int(
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
        ),
    }

    cap.release()

    return metadata
