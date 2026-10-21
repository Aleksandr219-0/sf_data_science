import numpy as np


def align_by_normalized_time(reference_poses, user_poses, reference_confidence, user_confidence):
    """Сопоставляет кадры без интерполяции и искусственного растягивания видео.

    Для каждого кадра эталона выбирается ближайший реальный кадр пользователя
    по относительному времени. Кадры и координаты позы не изменяются.
    """
    if len(reference_poses) == 0 or len(user_poses) == 0:
        raise ValueError("Одна из последовательностей поз пуста.")

    reference_ids = np.arange(len(reference_poses))
    user_ids = np.round(
        np.linspace(0, len(user_poses) - 1, len(reference_poses))
    ).astype(int)

    return (
        reference_ids,
        user_ids,
        reference_poses,
        user_poses[user_ids],
        reference_confidence,
        user_confidence[user_ids],
    )
