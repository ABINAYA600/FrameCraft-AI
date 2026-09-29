from app.services.creator_video_analyzer import (
    CreatorVideoAnalyzer
)


print("================================")
print("CREATOR VIDEO ANALYZER TEST")
print("================================")


analyzer = CreatorVideoAnalyzer(
    whisper_model="base",
    output_directory="output/creator_analysis",
    transcript_directory="output/creator_analysis/transcripts",
)


result = analyzer.analyze_videos(
    "datasets/creator_videos"
)


print()
print("================================")
print("FINAL CREATOR PROFILE")
print("================================")

profile = result["creator_profile"]

print(
    f"Tone: {profile['tone']}"
)

print(
    f"Language: {profile['language']}"
)

print(
    f"Style: {profile['style']}"
)

print(
    f"Reply Length: "
    f"{profile['reply_length']}"
)

print(
    f"Emoji Preference: "
    f"{profile['emoji_preference']}"
)

print(
    f"Auto Reply: "
    f"{profile['auto_reply']}"
)

print(
    f"Topics to Avoid: "
    f"{profile['topics_to_avoid']}"
)


print()
print("================================")
print("TEST PASSED")
print("================================")