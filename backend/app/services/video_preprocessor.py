import os
import cv2


class VideoPreprocessor:

    def __init__(self, clip_duration=5):
        self.clip_duration = clip_duration
        print("Video Preprocessor Initialized!")

    def split_video(self, video_path, output_folder):

        os.makedirs(output_folder, exist_ok=True)

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"❌ Cannot open video: {video_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if fps <= 0:
            print(f"❌ Invalid FPS: {video_path}")
            cap.release()
            return

        frames_per_clip = int(fps * self.clip_duration)

        video_name = os.path.splitext(
            os.path.basename(video_path)
        )[0]

        frame_count = 0
        clip_number = 1
        writer = None

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            if frame_count % frames_per_clip == 0:

                if writer is not None:
                    writer.release()

                clip_name = (
                    f"{video_name}_clip"
                    f"{clip_number:03d}.mp4"
                )

                clip_path = os.path.join(
                    output_folder,
                    clip_name
                )

                writer = cv2.VideoWriter(
                    clip_path,
                    cv2.VideoWriter_fourcc(*"mp4v"),
                    fps,
                    (width, height)
                )

                print(f"Creating: {clip_name}")

                clip_number += 1

            writer.write(frame)

            frame_count += 1

        cap.release()

        if writer is not None:
            writer.release()

        print(f"✅ Completed: {video_name}")

    def process(self, video_folder, clips_folder):

        os.makedirs(clips_folder, exist_ok=True)

        supported_extensions = (
            ".mp4",
            ".avi",
            ".mov",
            ".mkv"
        )

        videos = [
            file
            for file in os.listdir(video_folder)
            if file.lower().endswith(supported_extensions)
        ]

        print(f"\nFound {len(videos)} videos.\n")

        if len(videos) == 0:
            print("❌ No videos found!")
            return

        for video in sorted(videos):

            video_path = os.path.join(
                video_folder,
                video
            )

            self.split_video(
                video_path,
                clips_folder
            )

        print("\n================================")
        print("All videos processed successfully!")
        print("================================")