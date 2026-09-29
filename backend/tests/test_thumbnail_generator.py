import os
import sys
import json
from PIL import Image

# Ensure backend root is in sys.path
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.services.thumbnail_generator import ThumbnailGenerator


def run_thumbnail_generator_test():
    print("================================")
    print("AI THUMBNAIL GENERATION TEST")
    print("================================")

    # 1. Initialize ThumbnailGenerator
    generator = ThumbnailGenerator(
        output_folder="output",
        quality_weight=0.30,
        semantic_weight=0.50,
        diversity_weight=0.20,
        enable_clip=True,
    )

    clip_status = "AVAILABLE" if generator.clip_available else "UNAVAILABLE"
    device_status = generator.device.upper()
    print(f"CLIP: {clip_status}")
    print(f"Device: {device_status}")

    video_path = "output/music_scene_control_test.mp4"
    if not os.path.isabs(video_path):
        video_path = os.path.join(BACKEND_ROOT, video_path)

    if not os.path.exists(video_path):
        raise FileNotFoundError(
            f"Test video not found at: {video_path}. Please generate it first."
        )

    # 2. Test candidate frame extraction and scoring
    generator.thumbnail_title = "Modern Farming Technology"
    candidates = generator.extract_candidate_frames(video_path, candidate_count=12)
    print(f"\nCandidate frames: {len(candidates)}")

    for cand in candidates:
        print(f"\nFrame:\n{cand['timestamp']:.2f}s")
        print(f"Quality: {cand['quality_score']:.3f}")
        print(f"CLIP: {cand.get('clip_score', 0.0):.3f}")
        print(f"Combined: {cand['combined_score']:.3f}")

    # 3. Test layout decision
    layout = generator.decide_layout(candidates)
    print(f"\nSelected layout: {layout.upper()}")

    # 4. Test frame selection
    layout_frames_map = {
        "single": 1,
        "split": 2,
        "collage_3": 3,
        "collage_4": 4,
    }
    requested_count = layout_frames_map.get(layout, 1)
    selected_frames = generator.select_diverse_frames(candidates, requested_count)

    print("\nSelected frames:")
    for frame in selected_frames:
        print(
            f"  {frame['timestamp']:.2f}s"
            f" | Quality: {frame['quality_score']:.3f}"
            f" | CLIP: {frame.get('clip_score', 0.0):.3f}"
            f" | Combined: {frame['combined_score']:.3f}"
        )

    # 5. Full end-to-end thumbnail creation
    output_thumbnail = generator.create_thumbnail(
        video_path=video_path,
        output_name="framecraft_thumbnail.jpg",
        title="Modern Farming Technology",
        candidate_count=12,
    )

    metadata_path = os.path.join(generator.output_folder, "thumbnail_metadata.json")

    # 6. Verify generated image artifact
    assert os.path.exists(output_thumbnail), f"Thumbnail not created at {output_thumbnail}"
    with Image.open(output_thumbnail) as img:
        assert img.size == (1280, 720), f"Unexpected thumbnail dimensions: {img.size}"
        assert img.format in ("JPEG", "JPG"), f"Unexpected image format: {img.format}"

    # 7. Verify generated metadata artifact
    assert os.path.exists(metadata_path), f"Metadata not created at {metadata_path}"
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert "layout" in meta, "Metadata missing 'layout'"
    assert "frame_count" in meta, "Metadata missing 'frame_count'"
    assert "selection_method" in meta, "Metadata missing 'selection_method'"
    assert "title" in meta, "Metadata missing 'title'"
    assert "thumbnail" in meta, "Metadata missing 'thumbnail'"
    assert "frames" in meta, "Metadata missing 'frames'"
    assert len(meta["frames"]) == meta["frame_count"], "Frame count mismatch in metadata"

    # 8. Test fallback behavior without CLIP
    print("\nTesting CLIP fallback behavior...")
    fallback_generator = ThumbnailGenerator(output_folder="output", enable_clip=False)
    fallback_generator.thumbnail_title = "Modern Farming Technology"
    fallback_candidates = fallback_generator.extract_candidate_frames(video_path, candidate_count=4)
    assert len(fallback_candidates) == 4, "Fallback candidate extraction failed"
    for fc in fallback_candidates:
        assert fc["clip_score"] == 0.0, "Fallback should have 0.0 clip score"
        assert fc["combined_score"] == fc["quality_score"], "Fallback combined score should equal quality score"
    fallback_selected = fallback_generator.select_diverse_frames(fallback_candidates, 2)
    assert len(fallback_selected) == 2, "Fallback diverse selection failed"
    print("✅ Fallback behavior verified successfully.")

    print("\nThumbnail:")
    print("output/framecraft_thumbnail.jpg")
    print("\nMetadata:")
    print("output/thumbnail_metadata.json")
    print("\n================================")
    print("TEST PASSED")
    print("================================")


if __name__ == "__main__":
    run_thumbnail_generator_test()