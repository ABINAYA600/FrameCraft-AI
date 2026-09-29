import os
import cv2


class FrameExtractor:
    """
    FrameCraft AI
    --------------
    Extracts a representative frame from every video clip.

    Input:
        datasets/clips/*.mp4

    Output:
        datasets/frames/*.jpg
    """

    def __init__(self):
        print("Frame Extractor Initialized!")

    # ---------------------------------------------------
    # Extract middle frame from one video
    # ---------------------------------------------------

    def extract_middle_frame(self, video_path, output_folder):

        os.makedirs(output_folder, exist_ok=True)

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"❌ Cannot open: {video_path}")
            return None

        total_frames = int(
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        if total_frames <= 0:
            print(f"❌ No frames found: {video_path}")
            cap.release()
            return None

        # Select middle frame
        middle_frame = total_frames // 2

        cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            middle_frame
        )

        success, frame = cap.read()

        cap.release()

        if not success:
            print(
                f"❌ Could not extract frame: "
                f"{video_path}"
            )
            return None

        video_name = os.path.splitext(
            os.path.basename(video_path)
        )[0]

        output_name = video_name + ".jpg"

        output_path = os.path.join(
            output_folder,
            output_name
        )

        cv2.imwrite(
            output_path,
            frame
        )

        print(
            f"✅ Extracted: {output_name}"
        )

        return output_path

    # ---------------------------------------------------
    # Process all clips
    # ---------------------------------------------------

    def process(self, clips_folder, frames_folder):

        os.makedirs(
            frames_folder,
            exist_ok=True
        )

        supported_extensions = (
            ".mp4",
            ".avi",
            ".mov",
            ".mkv"
        )

        clips = [
            file
            for file in os.listdir(clips_folder)
            if file.lower().endswith(
                supported_extensions
            )
        ]

        clips.sort()

        print(
            f"\nFound {len(clips)} video clips.\n"
        )

        if len(clips) == 0:

            print(
                "❌ No video clips found!"
            )

            return

        extracted = 0

        for clip in clips:

            video_path = os.path.join(
                clips_folder,
                clip
            )

            result = self.extract_middle_frame(
                video_path,
                frames_folder
            )

            if result is not None:
                extracted += 1

        print("\n================================")
        print("Frame Extraction Completed!")
        print("================================")
        print(
            f"Clips processed : {len(clips)}"
        )
        print(
            f"Frames extracted: {extracted}"
        )