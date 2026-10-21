import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT / "src"),
)


import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


from MyProject.config import (
    ORIGINAL_DIR,
    REFERENCE_DIR,
    PROCESSED_DIR,
    POSE_MODEL_PATH,
    OUTPUT_VIDEO,
    METRICS_CSV,
    PLOT_PATH,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
)

from MyProject.utils import find_video

from MyProject.visualization import (
    draw_pose,
    metric_color,
)

from myproject_data.temporal_alignment import (
    align_by_normalized_time,
)

from myproject_models.pose_estimator import (
    PoseEstimator,
)

from myproject_models.pose_normalizer import (
    normalize_pose,
)

from myproject_models.pose_metrics import (
    cosine_similarity,
    weighted_distance,
    similarity_to_percent,
)


# Файл шрифта Windows с поддержкой кириллицы.
FONT_PATH = Path("C:/Windows/Fonts/arial.ttf")

# Высота нижней области для метрик и русской рекомендации.
METRICS_PANEL_HEIGHT = 205

# Ширина результата: два видео по DISPLAY_WIDTH.
OUTPUT_WIDTH = DISPLAY_WIDTH * 2

# Высота результата: видео и нижняя информационная панель.
OUTPUT_HEIGHT = DISPLAY_HEIGHT + METRICS_PANEL_HEIGHT


def get_font(size: int):
    """
    Возвращает шрифт с поддержкой кириллицы.
    """

    if not FONT_PATH.exists():
        raise FileNotFoundError(
            f"Не найден шрифт: {FONT_PATH}"
        )

    return ImageFont.truetype(
        str(FONT_PATH),
        size,
    )


def draw_russian_text(
    image: np.ndarray,
    text: str,
    position: tuple,
    color_bgr: tuple,
    font_size: int,
) -> np.ndarray:
    """
    Рисует текст на русском языке через Pillow.

    OpenCV использует BGR, Pillow использует RGB,
    поэтому цвет преобразуется перед рисованием.
    """

    image_rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB,
    )

    pil_image = Image.fromarray(
        image_rgb
    )

    drawer = ImageDraw.Draw(
        pil_image
    )

    b, g, r = color_bgr

    drawer.text(
        position,
        text,
        font=get_font(font_size),
        fill=(r, g, b),
    )

    return cv2.cvtColor(
        np.array(pil_image),
        cv2.COLOR_RGB2BGR,
    )


def get_similarity_recommendation(
    similarity_percent: float,
    confidence: float,
) -> tuple[str, tuple]:
    """
    Возвращает русскую рекомендацию коуча
    и цвет в формате BGR.
    """

    if not np.isfinite(similarity_percent):
        return (
            "Поза не распознана",
            (0, 0, 255),
        )

    if confidence < 0.40:
        return (
            "Отойдите дальше от камеры: тело плохо видно",
            (0, 140, 255),
        )

    if similarity_percent >= 95:
        return (
            "Отлично! Движение почти полностью совпадает с эталоном",
            (0, 200, 0),
        )

    if similarity_percent >= 85:
        return (
            "Очень хорошо! Сохраняйте технику выполнения",
            (0, 220, 0),
        )

    if similarity_percent >= 75:
        return (
            "Хорошо. Старайтесь точнее повторять движение",
            (0, 220, 220),
        )

    if similarity_percent >= 60:
        return (
            "Обратите внимание на положение рук, ног и корпуса",
            (0, 140, 255),
        )

    return (
        "Повторите упражнение медленнее и точнее",
        (0, 0, 255),
    )


def get_similarity_status(
    similarity_percent: float,
) -> str:
    """
    Возвращает короткий русский статус.
    """

    if not np.isfinite(similarity_percent):
        return "СТАТУС: НЕТ ДАННЫХ"

    if similarity_percent >= 95:
        return "СТАТУС: ОТЛИЧНО"

    if similarity_percent >= 85:
        return "СТАТУС: ОЧЕНЬ ХОРОШО"

    if similarity_percent >= 75:
        return "СТАТУС: ХОРОШО"

    if similarity_percent >= 60:
        return "СТАТУС: НУЖНА КОРРЕКЦИЯ"

    return "СТАТУС: ПОВТОРИТЕ УПРАЖНЕНИЕ"


def create_result_video(
    reference,
    user,
    reference_frame_ids,
    user_frame_ids,
    reference_poses,
    user_poses,
    metrics,
):
    writer = cv2.VideoWriter(
        str(OUTPUT_VIDEO),
        cv2.VideoWriter_fourcc(*"mp4v"),
        reference.fps,
        (
            OUTPUT_WIDTH,
            OUTPUT_HEIGHT,
        ),
    )

    if not writer.isOpened():
        raise RuntimeError(
            "Не удалось создать выходное видео."
        )

    for alignment_id in range(len(metrics)):
        reference_frame_id = int(
            reference_frame_ids[alignment_id]
        )

        user_frame_id = int(
            user_frame_ids[alignment_id]
        )

        similarity = metrics.loc[
            alignment_id,
            "cosine_similarity",
        ]

        similarity_percent = metrics.loc[
            alignment_id,
            "similarity_percent",
        ]

        distance = metrics.loc[
            alignment_id,
            "weighted_distance",
        ]

        confidence = metrics.loc[
            alignment_id,
            "confidence",
        ]

        left_frame = cv2.resize(
            reference.frames[
                reference_frame_id
            ],
            (
                DISPLAY_WIDTH,
                DISPLAY_HEIGHT,
            ),
        )

        right_frame = cv2.resize(
            user.frames[
                user_frame_id
            ],
            (
                DISPLAY_WIDTH,
                DISPLAY_HEIGHT,
            ),
        )

        # Скелет эталонного движения.
        left = draw_pose(
            left_frame,
            reference_poses[alignment_id],
            (255, 120, 0),
            "REFERENCE",
        )

        # Скелет пользователя.
        right = draw_pose(
            right_frame,
            user_poses[alignment_id],
            metric_color(similarity),
            "USER",
        )

        video_panel = np.hstack(
            [
                left,
                right,
            ]
        )

        metrics_panel = np.full(
            (
                METRICS_PANEL_HEIGHT,
                OUTPUT_WIDTH,
                3,
            ),
            (20, 20, 20),
            dtype=np.uint8,
        )

        recommendation, recommendation_color = (
            get_similarity_recommendation(
                similarity_percent,
                confidence,
            )
        )

        status = get_similarity_status(
            similarity_percent
        )

        similarity_text = (
            f"Сходство: {similarity_percent:.1f}%"
            if np.isfinite(similarity_percent)
            else "Сходство: нет данных"
        )

        distance_text = (
            f"Взвешенное расстояние: {distance:.4f}"
            if np.isfinite(distance)
            else "Взвешенное расстояние: нет данных"
        )

        confidence_text = (
            f"Достоверность: {confidence:.2f}"
        )

        reference_frame_text = (
            f"Кадр эталона: {reference_frame_id}"
        )

        user_frame_text = (
            f"Кадр пользователя: {user_frame_id}"
        )

        # Левая колонка: метрики.
        metrics_panel = draw_russian_text(
            metrics_panel,
            similarity_text,
            (25, 15),
            (255, 255, 255),
            27,
        )

        metrics_panel = draw_russian_text(
            metrics_panel,
            distance_text,
            (25, 55),
            (255, 255, 255),
            24,
        )

        metrics_panel = draw_russian_text(
            metrics_panel,
            confidence_text,
            (25, 95),
            (255, 255, 255),
            24,
        )

        # Правая колонка: статус и номера кадров.
        metrics_panel = draw_russian_text(
            metrics_panel,
            status,
            (650, 15),
            recommendation_color,
            24,
        )

        metrics_panel = draw_russian_text(
            metrics_panel,
            reference_frame_text,
            (650, 55),
            (255, 255, 255),
            22,
        )

        metrics_panel = draw_russian_text(
            metrics_panel,
            user_frame_text,
            (650, 90),
            (255, 255, 255),
            22,
        )

        # Большая строка с рекомендацией.
        metrics_panel = draw_russian_text(
            metrics_panel,
            f"СОВЕТ ТРЕНЕРА: {recommendation}",
            (25, 145),
            recommendation_color,
            22,
        )

        result_frame = np.vstack(
            [
                video_panel,
                metrics_panel,
            ]
        )

        writer.write(result_frame)

    writer.release()


def main():
    user_video = find_video(
        ORIGINAL_DIR
    )

    reference_video = find_video(
        REFERENCE_DIR
    )

    print("Видео пользователя:")
    print(user_video)

    print("\nЭталонное видео:")
    print(reference_video)

    estimator = PoseEstimator(
        POSE_MODEL_PATH
    )

    reference = estimator.extract(
        reference_video
    )

    user = estimator.extract(
        user_video
    )

    np.save(
        PROCESSED_DIR / "reference_poses.npy",
        reference.poses,
    )

    np.save(
        PROCESSED_DIR / "user_poses.npy",
        user.poses,
    )

    np.save(
        PROCESSED_DIR / "reference_conf.npy",
        reference.confidence,
    )

    np.save(
        PROCESSED_DIR / "user_conf.npy",
        user.confidence,
    )

    (
        reference_frame_ids,
        user_frame_ids,
        reference_poses,
        user_poses,
        reference_confidence,
        user_confidence,
    ) = align_by_normalized_time(
        reference.poses,
        user.poses,
        reference.confidence,
        user.confidence,
    )

    n_frames = len(
        reference_frame_ids
    )

    speed_ratio = (
        len(reference.poses)
        / len(user.poses)
    )

    print("\nСинхронизация без интерполяции поз:")

    print(
        "Кадров эталонного видео:",
        len(reference.poses),
    )

    print(
        "Кадров пользовательского видео:",
        len(user.poses),
    )

    print(
        "Количество сопоставленных пар:",
        n_frames,
    )

    print(
        "Пользователь выполнил движение примерно в",
        round(speed_ratio, 2),
        "раза быстрее эталона.",
    )

    records = []

    for alignment_id in range(n_frames):
        reference_pose = normalize_pose(
            reference_poses[
                alignment_id
            ]
        )

        user_pose = normalize_pose(
            user_poses[
                alignment_id
            ]
        )

        reference_frame_id = int(
            reference_frame_ids[
                alignment_id
            ]
        )

        user_frame_id = int(
            user_frame_ids[
                alignment_id
            ]
        )

        if (
            reference_pose is None
            or user_pose is None
        ):
            records.append(
                {
                    "alignment_id": alignment_id,
                    "reference_frame": reference_frame_id,
                    "user_frame": user_frame_id,
                    "cosine_similarity": np.nan,
                    "weighted_distance": np.nan,
                    "confidence": 0.0,
                }
            )

            continue

        confidence = np.minimum(
            reference_confidence[
                alignment_id
            ],
            user_confidence[
                alignment_id
            ],
        )

        cosine_value = cosine_similarity(
            reference_pose,
            user_pose,
        )

        distance_value = weighted_distance(
            reference_pose,
            user_pose,
            confidence,
        )

        records.append(
            {
                "alignment_id": alignment_id,
                "reference_frame": reference_frame_id,
                "user_frame": user_frame_id,
                "cosine_similarity": cosine_value,
                "weighted_distance": distance_value,
                "confidence": float(
                    confidence.mean()
                ),
            }
        )

    metrics = pd.DataFrame(records)

    metrics["similarity_percent"] = (
        metrics["cosine_similarity"]
        .apply(similarity_to_percent)
    )

    metrics.to_csv(
        METRICS_CSV,
        index=False,
    )

    create_result_video(
        reference,
        user,
        reference_frame_ids,
        user_frame_ids,
        reference_poses,
        user_poses,
        metrics,
    )

    figure, axes = plt.subplots(
        2,
        1,
        figsize=(14, 7),
        sharex=True,
    )

    axes[0].plot(
        metrics["alignment_id"],
        metrics["similarity_percent"],
        color="green",
    )

    axes[0].set_title(
        "Сходство пользователя с эталонной зарядкой"
    )

    axes[0].set_ylabel(
        "Сходство, %",
    )

    axes[0].grid(alpha=0.3)

    axes[1].plot(
        metrics["alignment_id"],
        metrics["weighted_distance"],
        color="red",
    )

    axes[1].set_xlabel(
        "Сопоставленная пара кадров",
    )

    axes[1].set_ylabel(
        "Взвешенное расстояние",
    )

    axes[1].grid(alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        PLOT_PATH,
        dpi=150,
    )

    print("\nГотово.")

    print("\nИтоговое видео:")
    print(OUTPUT_VIDEO)

    print("\nТаблица метрик:")
    print(METRICS_CSV)

    print("\nГрафик:")
    print(PLOT_PATH)


if __name__ == "__main__":
    main()