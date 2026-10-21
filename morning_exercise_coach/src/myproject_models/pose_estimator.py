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
