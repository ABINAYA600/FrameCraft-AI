from app.services.video_preprocessor import VideoPreprocessor


processor = VideoPreprocessor(
    clip_duration=5
)

processor.process(
    video_folder="datasets/videos",
    clips_folder="datasets/clips"
)