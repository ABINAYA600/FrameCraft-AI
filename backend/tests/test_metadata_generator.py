import os
import sys
import json

# Ensure backend root is in sys.path
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.services.metadata_generator import MetadataGenerator, LocalMetadataStrategy


def run_metadata_generator_test():
    print("================================")
    print("AI METADATA GENERATION TEST")
    print("================================")

    # 1. Initialize MetadataGenerator
    generator = MetadataGenerator(output_folder="output")

    storyboard = [
        {
            "scene_number": 1,
            "scene": "Organic farming and sustainable agriculture"
        },
        {
            "scene_number": 2,
            "scene": "Fresh vegetables growing on a modern farm"
        },
        {
            "scene_number": 3,
            "scene": "Modern tractors and smart farming technology"
        },
        {
            "scene_number": 4,
            "scene": "Farmers using technology to improve crop production"
        }
    ]

    # 2. Test Storyboard Text Extraction
    extracted_scenes = generator.extract_storyboard_text(storyboard)
    assert len(extracted_scenes) == 4, f"Expected 4 scenes, got: {len(extracted_scenes)}"
    assert "Organic farming" in extracted_scenes[0]

    # 3. Generate Metadata (Default / Auto Title)
    metadata = generator.generate_metadata(
        storyboard=storyboard,
        requested_title=None,
        platform="youtube"
    )

    title = metadata.get("title")
    description = metadata.get("description")
    hashtags = metadata.get("hashtags", [])

    assert title and len(title) > 0, "Title is empty"
    assert description and len(description) > 0, "Description is empty"
    assert len(description) <= 5000, "Description exceeds 5000 characters"
    assert isinstance(hashtags, list) and len(hashtags) > 0, "Hashtags are missing"
    assert "#FrameCraftAI" in hashtags, "Hashtags missing #FrameCraftAI"
    assert len(hashtags) <= 10, f"Too many hashtags: {len(hashtags)}"
    # Verify no duplicates
    assert len(hashtags) == len(set(h.lower() for h in hashtags)), "Duplicate hashtags found"

    # 4. Test requested_title override
    custom_title = "Future of Organic AgriTech"
    meta_custom = generator.generate_metadata(
        storyboard=storyboard,
        requested_title=custom_title,
        platform="youtube"
    )
    assert meta_custom["title"] == custom_title, f"Expected {custom_title}, got: {meta_custom['title']}"

    # 5. Test Platform Support
    meta_shorts = generator.generate_metadata(
        storyboard=storyboard,
        platform="youtube_shorts"
    )
    assert meta_shorts["platform"] == "youtube_shorts"
    assert "youtube_shorts" in meta_shorts["platform"]

    meta_insta = generator.generate_metadata(
        storyboard=storyboard,
        platform="instagram"
    )
    assert meta_insta["platform"] == "instagram"

    # 6. Test Edge Cases (Empty storyboard, strings, missing fields)
    meta_empty = generator.generate_metadata(storyboard=[])
    assert meta_empty["title"] == "FrameCraft AI Video"
    assert "#FrameCraftAI" in meta_empty["hashtags"]

    raw_script = "Robotics in agriculture. Automated crop harvesting. AI powered greenhouse."
    meta_script = generator.generate_metadata(storyboard=raw_script)
    assert len(meta_script["hashtags"]) > 0

    # 7. Save Metadata to File
    output_filename = "framecraft_metadata.json"
    saved_path = generator.save_metadata(
        metadata=metadata,
        output_name=output_filename
    )

    assert os.path.exists(saved_path), f"Saved metadata file not found at: {saved_path}"

    with open(saved_path, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    assert loaded_data["title"] == title
    assert loaded_data["description"] == description
    assert loaded_data["hashtags"] == hashtags
    assert loaded_data["generator"] == "FrameCraft AI Metadata Generator"

    # Print output matching requirements
    print("\nTitle:")
    print(title)

    print("\nDescription:")
    print(description)

    print("\nHashtags:")
    print(" ".join(hashtags))

    print("\nMetadata:")
    print(saved_path)

    print("\n================================")
    print("METADATA TEST PASSED")
    print("================================")


if __name__ == "__main__":
    run_metadata_generator_test()
