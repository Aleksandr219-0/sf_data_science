from pathlib import Path
from textwrap import dedent


PROJECT_NAME = "morning_exercise_coach"
PROJECT_ROOT = Path.cwd() / PROJECT_NAME


DIRECTORIES = [
    "data/original",
    "data/reference",
    "data/processed",
    "models",
    "output",
    "examples",
    "images",
    "scripts",
    "tests",
    "src/MyProject",
    "src/myproject_data",
    "src/myproject_models",
]


FILES = {
    "README.md": """
        # Virtual Morning Exercise Coach

        ## Цель проекта

        Виртуальный коуч сравнивает выполнение утренней зарядки
        пользователем с эталонным видео по ключевым точкам тела.

        ## Входные данные

        - `data/original/` — видео пользователя.
        - `data/reference/` — эталонное видео зарядки.
        - `data/processed/` — извлечённые ключевые точки.

        ## Результаты

        После запуска проекта создаются:

        - `output/morning_coach_result.mp4`;
        - `output/morning_coach_metrics.csv`;
        - `output/metrics_plot.png`.

        ## Установка

        ```powershell
        py -3.11 -m pip install -r requirements.txt
        py -3.11 -m pip install -e .
        ```

        ## Запуск

        ```powershell
        py -3.11 scripts/main.py
        ```

        Перед запуском добавьте по одному видео в:

        ```text
        data/original/
        data/reference/
        ```
    """,

    "requirements.txt": """
        numpy==1.26.4
        mediapipe==0.10.14
        opencv-contrib-python==4.10.0.84
        pandas
        matplotlib
        tqdm
        jupyter
        ipykernel
    """,

    "pyproject.toml": """
        [build-system]
        requires = ["setuptools>=61.0"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "morning-exercise-coach"
        version = "0.1.0"
        description = "Virtual coach for pose comparison in morning exercise videos"
        requires-python = ">=3.10"
        dependencies = [
            "numpy==1.26.4",
            "mediapipe==0.10.14",
            "opencv-contrib-python==4.10.0.84",
            "pandas",
            "matplotlib",
            "tqdm",
        ]

        [tool.setuptools.packages.find]
        where = ["src"]
    """,

    ".gitignore": """
        __pycache__/
        *.py[cod]
        .ipynb_checkpoints/
        .venv/
        venv/

        data/original/*
        data/reference/*
        data/processed/*
        models/*.task
        output/*

        !data/original/.gitkeep
        !data/reference/.gitkeep
        !data/processed/.gitkeep
        !models/.gitkeep
        !output/.gitkeep
    """,

    "src/MyProject/__init__.py": '''
        """Общие компоненты проекта виртуального коуча."""
    ''',

    "src/MyProject/config.py": """
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
    """,

    "src/MyProject/constants.py": """
        POSE_CONNECTIONS = [
            (11, 12),
            (11, 13),
            (13, 15),
            (15, 17),
            (15, 19),
            (15, 21),
            (12, 14),
            (14, 16),
            (16, 18),
            (16, 20),
            (16, 22),
            (11, 23),
            (12, 24),
            (23, 24),
            (23, 25),
            (25, 27),
            (27, 29),
            (27, 31),
            (24, 26),
            (26, 28),
            (28, 30),
            (28, 32),
            (0, 11),
            (0, 12),
        ]
    """,

    "src/MyProject/utils.py": """
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
    """,

    "src/MyProject/visualization.py": """
        import cv2
        import numpy as np

        from MyProject.constants import POSE_CONNECTIONS


        def metric_color(similarity: float):
            if not np.isfinite(similarity):
                return (0, 0, 255)

            if similarity < 0.60:
                return (0, 0, 255)

            if similarity < 0.85:
                return (0, 190, 230)

            return (0, 180, 0)


        def draw_pose(
            frame: np.ndarray,
            pose: np.ndarray,
            color: tuple,
            title: str,
        ) -> np.ndarray:
            image = frame.copy()

            height, width = image.shape[:2]

            if pose is not None and not np.isnan(pose).any():
                points = [
                    (
                        int(x * width),
                        int(y * height),
                    )
                    for x, y in pose
                ]

                for first, second in POSE_CONNECTIONS:
                    cv2.line(
                        image,
                        points[first],
                        points[second],
                        color,
                        2,
                        cv2.LINE_AA,
                    )

                for x, y in points:
                    cv2.circle(
                        image,
                        (x, y),
                        4,
                        color,
                        -1,
                        cv2.LINE_AA,
                    )

            cv2.rectangle(
                image,
                (0, 0),
                (width, 45),
                (25, 25, 25),
                -1,
            )

            cv2.putText(
                image,
                title,
                (12, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            return image
    """,

    "src/myproject_data/__init__.py": '''
        """Загрузка и подготовка видеоданных."""
    ''',

    "src/myproject_data/pose_dataset.py": """
        from dataclasses import dataclass

        import numpy as np


        @dataclass
        class PoseVideoDataset:
            frames: list
            poses: np.ndarray
            confidence: np.ndarray
            fps: float
            width: int
            height: int
    """,

    "src/myproject_data/preprocessing.py": """
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
    """,

    "src/myproject_data/video_loader.py": """
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
    """,

    "src/myproject_models/__init__.py": '''
        """Модели определения и сравнения поз."""
    ''',

    "src/myproject_models/pose_normalizer.py": """
        import numpy as np


        def normalize_pose(pose: np.ndarray):
            if np.isnan(pose).any():
                return None

            shoulder_center = (
                pose[11] + pose[12]
            ) / 2

            hip_center = (
                pose[23] + pose[24]
            ) / 2

            center = (
                shoulder_center + hip_center
            ) / 2

            scale = max(
                np.linalg.norm(
                    pose[11] - pose[12]
                ),
                1e-6,
            )

            return (pose - center) / scale
    """,

    "src/myproject_models/pose_metrics.py": """
        import numpy as np


        def cosine_similarity(
            reference_pose: np.ndarray,
            user_pose: np.ndarray,
        ) -> float:
            reference_vector = reference_pose.ravel()
            user_vector = user_pose.ravel()

            denominator = (
                np.linalg.norm(reference_vector)
                * np.linalg.norm(user_vector)
            )

            if denominator <= 1e-9:
                return np.nan

            return float(
                np.dot(
                    reference_vector,
                    user_vector,
                )
                / denominator
            )


        def weighted_distance(
            reference_pose: np.ndarray,
            user_pose: np.ndarray,
            confidence: np.ndarray,
        ) -> float:
            distances = np.linalg.norm(
                reference_pose - user_pose,
                axis=1,
            )

            weights = np.clip(
                confidence,
                0,
                1,
            )

            valid = (
                np.isfinite(distances)
                & (weights > 0)
            )

            if not valid.any():
                return np.nan

            return float(
                np.average(
                    distances[valid],
                    weights=weights[valid],
                )
            )


        def similarity_to_percent(value: float) -> float:
            if not np.isfinite(value):
                return np.nan

            return float(
                np.clip(
                    (value + 1) * 50,
                    0,
                    100,
                )
            )
    """,

    "src/myproject_models/virtual_coach.py": """
        import numpy as np


        def get_coach_message(
            similarity: float,
            distance: float,
            confidence: float,
        ) -> str:
            if confidence < 0.4:
                return "Low pose confidence"

            if not np.isfinite(similarity):
                return "Pose not detected"

            if similarity >= 0.90 and distance <= 0.15:
                return "Excellent movement"

            if similarity >= 0.75 and distance <= 0.30:
                return "Good, move more precisely"

            if similarity >= 0.60:
                return "Check arms and legs position"

            return "Repeat the exercise slower"
    """,

    "src/myproject_models/pose_estimator.py": """
        import cv2
        import mediapipe as mp
        import numpy as np
        from tqdm import tqdm

        from myproject_data.pose_dataset import PoseVideoDataset


        class PoseEstimator:
            def __init__(self, model_path):
                self.model_path = str(model_path)

            def _create_landmarker(self):
                options = (
                    mp.tasks.vision.PoseLandmarkerOptions(
                        base_options=mp.tasks.BaseOptions(
                            model_asset_path=self.model_path
                        ),
                        running_mode=(
                            mp.tasks.vision.RunningMode.VIDEO
                        ),
                        num_poses=1,
                        min_pose_detection_confidence=0.5,
                        min_pose_presence_confidence=0.5,
                        min_tracking_confidence=0.5,
                    )
                )

                return (
                    mp.tasks.vision.PoseLandmarker
                    .create_from_options(options)
                )

            def extract(
                self,
                video_path,
            ) -> PoseVideoDataset:
                cap = cv2.VideoCapture(str(video_path))

                if not cap.isOpened():
                    raise ValueError(
                        f"Не удалось открыть видео: {video_path}"
                    )

                fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

                width = int(
                    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                )

                height = int(
                    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                )

                frame_count = int(
                    cap.get(cv2.CAP_PROP_FRAME_COUNT)
                )

                frames = []
                poses = []
                confidence = []

                with self._create_landmarker() as landmarker:
                    for frame_id in tqdm(
                        range(frame_count),
                        desc=f"Pose: {video_path.name}",
                    ):
                        ok, frame = cap.read()

                        if not ok:
                            break

                        rgb = cv2.cvtColor(
                            frame,
                            cv2.COLOR_BGR2RGB,
                        )

                        image = mp.Image(
                            image_format=mp.ImageFormat.SRGB,
                            data=rgb,
                        )

                        timestamp = int(
                            frame_id * 1000 / fps
                        )

                        result = (
                            landmarker.detect_for_video(
                                image,
                                timestamp,
                            )
                        )

                        if result.pose_landmarks:
                            landmarks = (
                                result.pose_landmarks[0]
                            )

                            pose = np.array(
                                [
                                    [point.x, point.y]
                                    for point in landmarks
                                ],
                                dtype=np.float32,
                            )

                            conf = np.array(
                                [
                                    min(
                                        point.visibility,
                                        point.presence,
                                    )
                                    for point in landmarks
                                ],
                                dtype=np.float32,
                            )
                        else:
                            pose = np.full(
                                (33, 2),
                                np.nan,
                                dtype=np.float32,
                            )

                            conf = np.zeros(
                                33,
                                dtype=np.float32,
                            )

                        frames.append(frame)
                        poses.append(pose)
                        confidence.append(conf)

                cap.release()

                return PoseVideoDataset(
                    frames=frames,
                    poses=np.array(poses),
                    confidence=np.array(confidence),
                    fps=fps,
                    width=width,
                    height=height,
                )
    """,

    "scripts/download_model.py": """
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
    """,

    "scripts/check_videos.py": """
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

            print(f"\\n{name}:")
            print(video)

            print("Метаданные:")
            print(get_video_metadata(video))
    """,

    "scripts/main.py": """
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

        from myproject_data.preprocessing import (
            resample_array,
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

        from myproject_models.virtual_coach import (
            get_coach_message,
        )


        def create_result_video(
            reference,
            user,
            reference_poses,
            user_poses,
            metrics,
        ):
            writer = cv2.VideoWriter(
                str(OUTPUT_VIDEO),
                cv2.VideoWriter_fourcc(*"mp4v"),
                reference.fps,
                (
                    DISPLAY_WIDTH * 2,
                    DISPLAY_HEIGHT,
                ),
            )

            if not writer.isOpened():
                raise RuntimeError(
                    "Не удалось создать выходное видео."
                )

            for frame_id in range(len(metrics)):
                similarity = metrics.loc[
                    frame_id,
                    "cosine_similarity",
                ]

                similarity_percent = metrics.loc[
                    frame_id,
                    "similarity_percent",
                ]

                distance = metrics.loc[
                    frame_id,
                    "weighted_distance",
                ]

                confidence = metrics.loc[
                    frame_id,
                    "confidence",
                ]

                left_frame = cv2.resize(
                    reference.frames[frame_id],
                    (
                        DISPLAY_WIDTH,
                        DISPLAY_HEIGHT,
                    ),
                )

                user_frame_id = min(
                    frame_id,
                    len(user.frames) - 1,
                )

                right_frame = cv2.resize(
                    user.frames[user_frame_id],
                    (
                        DISPLAY_WIDTH,
                        DISPLAY_HEIGHT,
                    ),
                )

                left = draw_pose(
                    left_frame,
                    reference_poses[frame_id],
                    (255, 120, 0),
                    "SOVIET REFERENCE",
                )

                right = draw_pose(
                    right_frame,
                    user_poses[frame_id],
                    metric_color(similarity),
                    "USER EXERCISE",
                )

                panel = np.hstack(
                    [
                        left,
                        right,
                    ]
                )

                text_lines = [
                    (
                        f"Similarity: "
                        f"{similarity_percent:.1f}%"
                        if np.isfinite(similarity_percent)
                        else "Similarity: n/a"
                    ),
                    (
                        f"Weighted distance: "
                        f"{distance:.4f}"
                        if np.isfinite(distance)
                        else "Weighted distance: n/a"
                    ),
                    f"Confidence: {confidence:.2f}",
                    get_coach_message(
                        similarity,
                        distance,
                        confidence,
                    ),
                ]

                cv2.rectangle(
                    panel,
                    (10, 55),
                    (720, 205),
                    (20, 20, 20),
                    -1,
                )

                for line_id, text in enumerate(text_lines):
                    cv2.putText(
                        panel,
                        text,
                        (25, 85 + line_id * 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

                writer.write(panel)

            writer.release()


        def main():
            user_video = find_video(
                ORIGINAL_DIR
            )

            reference_video = find_video(
                REFERENCE_DIR
            )

            print("Видео пользователя:", user_video)
            print("Эталонное видео:", reference_video)

            estimator = PoseEstimator(
                POSE_MODEL_PATH
            )

            reference = estimator.extract(
                reference_video
            )

            user = estimator.extract(user_video)

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

            n_frames = min(
                len(reference.poses),
                len(user.poses),
            )

            reference_poses = reference.poses[
                :n_frames
            ]

            reference_confidence = reference.confidence[
                :n_frames
            ]

            user_poses = resample_array(
                user.poses,
                n_frames,
            )

            user_confidence = resample_array(
                user.confidence[:, :, None],
                n_frames,
            )[:, :, 0]

            records = []

            for frame_id in range(n_frames):
                reference_pose = normalize_pose(
                    reference_poses[frame_id]
                )

                user_pose = normalize_pose(
                    user_poses[frame_id]
                )

                if (
                    reference_pose is None
                    or user_pose is None
                ):
                    records.append(
                        {
                            "frame": frame_id,
                            "cosine_similarity": np.nan,
                            "weighted_distance": np.nan,
                            "confidence": 0.0,
                        }
                    )

                    continue

                confidence = np.minimum(
                    reference_confidence[frame_id],
                    user_confidence[frame_id],
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
                        "frame": frame_id,
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
                metrics["frame"],
                metrics["similarity_percent"],
                color="green",
            )

            axes[0].set_ylabel("Similarity, %")
            axes[0].grid(alpha=0.3)

            axes[1].plot(
                metrics["frame"],
                metrics["weighted_distance"],
                color="red",
            )

            axes[1].set_xlabel("Frame")
            axes[1].set_ylabel(
                "Weighted distance"
            )

            axes[1].grid(alpha=0.3)

            plt.tight_layout()

            plt.savefig(
                PLOT_PATH,
                dpi=150,
            )

            print("\\nГотово.")

            print("Итоговое видео:")
            print(OUTPUT_VIDEO)

            print("Таблица метрик:")
            print(METRICS_CSV)

            print("График:")
            print(PLOT_PATH)


        if __name__ == "__main__":
            main()
    """,

    "tests/test_metrics.py": """
        import numpy as np

        from myproject_models.pose_metrics import (
            cosine_similarity,
            weighted_distance,
        )


        def test_cosine_similarity_same_pose():
            pose = np.array(
                [
                    [0.0, 0.0],
                    [1.0, 1.0],
                ]
            )

            result = cosine_similarity(
                pose,
                pose,
            )

            assert np.isclose(
                result,
                1.0,
            )


        def test_weighted_distance_same_pose():
            pose = np.array(
                [
                    [0.0, 0.0],
                    [1.0, 1.0],
                ]
            )

            confidence = np.array(
                [
                    1.0,
                    1.0,
                ]
            )

            result = weighted_distance(
                pose,
                pose,
                confidence,
            )

            assert np.isclose(
                result,
                0.0,
            )
    """,

    "tests/test_normalizer.py": """
        import numpy as np

        from myproject_models.pose_normalizer import (
            normalize_pose,
        )


        def test_normalize_pose_returns_correct_shape():
            pose = np.tile(
                np.array(
                    [
                        [0.5, 0.5],
                    ],
                    dtype=np.float32,
                ),
                (33, 1),
            )

            pose[11] = [0.4, 0.4]
            pose[12] = [0.6, 0.4]
            pose[23] = [0.4, 0.7]
            pose[24] = [0.6, 0.7]

            normalized_pose = normalize_pose(pose)

            assert normalized_pose.shape == (
                33,
                2,
            )
    """,
}


for directory in DIRECTORIES:
    full_directory = PROJECT_ROOT / directory
    full_directory.mkdir(
        parents=True,
        exist_ok=True,
    )


for relative_path, content in FILES.items():
    file_path = PROJECT_ROOT / relative_path

    if file_path.exists():
        print(
            "Пропущен существующий файл:",
            file_path.relative_to(PROJECT_ROOT),
        )
        continue

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_text(
        dedent(content).lstrip(),
        encoding="utf-8",
    )

    print(
        "Создан:",
        file_path.relative_to(PROJECT_ROOT),
    )


gitkeep_files = [
    "data/original/.gitkeep",
    "data/reference/.gitkeep",
    "data/processed/.gitkeep",
    "models/.gitkeep",
    "output/.gitkeep",
    "examples/.gitkeep",
    "images/.gitkeep",
]


for relative_path in gitkeep_files:
    file_path = PROJECT_ROOT / relative_path

    file_path.touch(
        exist_ok=True,
    )


print("\n" + "=" * 60)
print("Проект успешно создан.")
print("=" * 60)

print("\nПуть к проекту:")
print(PROJECT_ROOT)

print("\nДальше сделайте следующее:")

print("\n1. Поместите своё видео в:")
print(PROJECT_ROOT / "data" / "original")

print("\n2. Поместите эталонное видео в:")
print(PROJECT_ROOT / "data" / "reference")

print("\n3. Откройте PowerShell и выполните:")

print(f'''
cd "{PROJECT_ROOT}"
py -3.11 -m pip install -e .
py -3.11 scripts/main.py
''')