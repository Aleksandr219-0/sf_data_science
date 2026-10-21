import sys
from pathlib import Path

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT / "src"),
)

from MyProject.config import OUTPUT_VIDEO


if not OUTPUT_VIDEO.exists():
    raise FileNotFoundError(
        f"Итоговое видео не найдено:\n{OUTPUT_VIDEO}"
    )

if OUTPUT_VIDEO.stat().st_size == 0:
    raise RuntimeError(
        "Итоговое видео найдено, но его размер равен нулю."
    )

cap = cv2.VideoCapture(
    str(OUTPUT_VIDEO)
)

if not cap.isOpened():
    raise RuntimeError(
        "OpenCV не смог открыть итоговое видео."
    )

fps = cap.get(
    cv2.CAP_PROP_FPS
)

width = int(
    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
)

height = int(
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
)

frame_count = int(
    cap.get(cv2.CAP_PROP_FRAME_COUNT)
)

ok, first_frame = cap.read()

cap.release()

if not ok:
    raise RuntimeError(
        "Не удалось прочитать первый кадр итогового видео."
    )

expected_width = 1280
expected_height = 635

print("Итоговое видео успешно открыто.")

print("\nФайл:")
print(OUTPUT_VIDEO)

print("\nРазмер файла:")
print(
    round(
        OUTPUT_VIDEO.stat().st_size / 1024 / 1024,
        2,
    ),
    "MB",
)

print("\nПараметры видео:")
print("FPS:", round(fps, 2))
print("Разрешение:", f"{width} x {height}")
print("Кадров:", frame_count)
print("Форма первого кадра:", first_frame.shape)

print("\nОжидаемое разрешение:")
print(
    f"{expected_width} x {expected_height}"
)

valid_width = width == expected_width

valid_height = height in {
    expected_height,
    expected_height - 1,
}

if valid_width and valid_height:
    print(
        "\nПроверка размера пройдена. "
        "Видео создано корректно."
    )

    if height == expected_height - 1:
        print(
            "Высота уменьшена на 1 пиксель кодеком MP4 "
            "для выравнивания размера кадра."
        )
else:
    print(
        "\nВнимание: размер существенно отличается "
        "от ожидаемого."
    )