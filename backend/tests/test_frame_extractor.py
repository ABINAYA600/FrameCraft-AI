from app.services.frame_extractor import FrameExtractor


print("Starting Frame Extractor Test...")

extractor = FrameExtractor()

extractor.process(
    clips_folder="datasets/clips",
    frames_folder="datasets/frames"
)

print("Test Completed!")