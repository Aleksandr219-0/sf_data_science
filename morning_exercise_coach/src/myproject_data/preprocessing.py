import numpy as np


def resample_array(
    array: np.ndarray,
    target_len: int,
) -> np.ndarray:
    if len(array) == target_len:
        return array.copy()

    old_idx = np.linspace(
        0,
        1,
        len(array),
    )

    new_idx = np.linspace(
        0,
        1,
        target_len,
    )

    result = np.empty(
        (target_len,) + array.shape[1:],
        dtype=array.dtype,
    )

    for point_id in range(array.shape[1]):
        for coordinate_id in range(array.shape[2]):
            result[
                :,
                point_id,
                coordinate_id,
            ] = np.interp(
                new_idx,
                old_idx,
                array[
                    :,
                    point_id,
                    coordinate_id,
                ],
            )

    return result
