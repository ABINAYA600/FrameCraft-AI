import os
import sys
import json
from PIL import Image

# Ensure backend root is in sys.path
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from ml_models.video_composer import VideoComposer


def run_video_thumbnail_integration_test():
    print("================================")
    print("VIDEO + THUMBNAIL INTEGRATION")
    print("================================")

    composer = VideoComposer()

    storyboard = [
        {
            "scene_number": 1,
            "scene": "Organic farm landscape",
            "media_type": "video",
            "media_path": os.path.join(BACKEND_ROOT, "datasets/clips/video1_clip001.mp4"),
            "duration": 4,
        },
        {
            "scene_number": 2,
            "scene": "Farmer explaining sustainable agriculture",
            "media_type": "video",
            "media_path": os.path.join(BACKEND_ROOT, "datasets/clips/video2_clip001.mp4"),
            "duration": 4,
        },
        {
            "scene_number": 3,
            "scene": "Modern farming machinery in field",
            "media_type": "video",
            "media_path": os.path.join(BACKEND_ROOT, "datasets/clips/video4_clip001.mp4"),
            "duration": 4,
        },
        {
            "scene_number": 4,
            "scene": "Harvested fresh organic produce",
            "media_type": "video",
            "media_path": os.path.join(BACKEND_ROOT, "datasets/clips/video3_clip001.mp4"),
            "duration": 4,
        },
    ]

    music_path = os.path.join(BACKEND_ROOT, "datasets/music/peaceful/peaceful_track_01.mp3")
    if not os.path.exists(music_path):
        music_path = os.path.join(BACKEND_ROOT, "output/music_test.mp3")
    if not os.path.exists(music_path):
        music_path = None

    output_video_name = "video_thumbnail_integration_test.mp4"
    title = "Modern Farming Technology"

    result = composer.compose(
        storyboard=storyboard,
        music_path=music_path,
        output_name=output_video_name,
        generate_thumbnail=True,
        thumbnail_title=title,
        return_metadata=True,
    )

    # Validate result dictionary
    assert isinstance(result, dict), f"Expected dict result, got: {type(result)}"
    video_path = result.get("video")
    thumbnail_path = result.get("thumbnail")
    metadata_path = result.get("thumbnail_metadata")

    assert video_path and os.path.exists(video_path), f"Video file not found: {video_path}"
    assert thumbnail_path and os.path.exists(thumbnail_path), f"Thumbnail file not found: {thumbnail_path}"
    assert metadata_path and os.path.exists(metadata_path), f"Metadata file not found: {metadata_path}"

    # Validate thumbnail image dimensions
    with Image.open(thumbnail_path) as img:
        assert img.size == (1280, 720), f"Unexpected thumbnail dimensions: {img.size}"

    # Validate metadata content
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert "layout" in meta, "Metadata missing 'layout'"
    assert "frame_count" in meta, "Metadata missing 'frame_count'"
    assert "selection_method" in meta, "Metadata missing 'selection_method'"
    assert "frames" in meta and len(meta["frames"]) > 0, "Metadata missing frames data"

    layout_name = str(meta["layout"]).upper()
    selected_frames = meta["frames"]

    print("\n================================")
    print("INTEGRATION TEST SUMMARY")
    print("================================")
    print("\nVideo created:")
    print(video_path.replace("\\", "/"))

    print("\nThumbnail created:")
    print(thumbnail_path.replace("\\", "/"))

    print("\nMetadata created:")
    print(metadata_path.replace("\\", "/"))

    print(f"\nThumbnail layout:\n{layout_name}")

    print("\nSelected frames:")
    for frame in selected_frames:
        print(
            f"  {frame['timestamp']:.2f}s"
            f" | Quality: {frame.get('quality_score', 0):.3f}"
            f" | CLIP: {frame.get('clip_score', 0):.3f}"
            f" | Combined: {frame.get('combined_score', 0):.3f}"
        )

    print("\n================================")
    print("INTEGRATION TEST PASSED")
    print("================================")


if __name__ == "__main__":
    run_video_thumbnail_integration_test()

