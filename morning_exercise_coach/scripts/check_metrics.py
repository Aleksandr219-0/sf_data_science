import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT / "src"),
)

from MyProject.config import METRICS_CSV


if not METRICS_CSV.exists():
    raise FileNotFoundError(
        f"Файл метрик не найден:\n{METRICS_CSV}"
    )

metrics = pd.read_csv(
    METRICS_CSV
)

required_columns = {
    "alignment_id",
    "reference_frame",
    "user_frame",
    "cosine_similarity",
    "weighted_distance",
    "confidence",
    "similarity_percent",
}

missing_columns = (
    required_columns
    - set(metrics.columns)
)

if missing_columns:
    raise ValueError(
        f"В CSV нет колонок: {missing_columns}"
    )

print("CSV-метрики успешно прочитаны.")

print("\nЧисло сопоставленных пар:")
print(len(metrics))

print("\nКолонки:")
print(metrics.columns.tolist())

print("\nПервые пять строк:")
print(metrics.head())

print("\nСредние значения:")
print(
    metrics[
        [
            "similarity_percent",
            "weighted_distance",
            "confidence",
        ]
    ].mean()
)

print("\nДиапазон кадров эталона:")
print(
    metrics["reference_frame"].min(),
    "—",
    metrics["reference_frame"].max(),
)

print("\nДиапазон кадров пользователя:")
print(
    metrics["user_frame"].min(),
    "—",
    metrics["user_frame"].max(),
)

print("\nПропущенные значения:")
print(metrics.isna().sum())