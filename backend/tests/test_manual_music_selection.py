from app.services.music_manager import MusicManager
from ml_models.video_composer import VideoComposer


print("Starting Manual Music Selection Test...")


# ==================================================
# INITIALIZE MUSIC MANAGER
# ==================================================

music_manager = MusicManager()


# ==================================================
# USER ENTERS MUSIC WISH
# ==================================================

user_query = "energetic"


print("\n================================")
print("USER MUSIC SEARCH")
print("================================")

print("User entered:", user_query)


# ==================================================
# SEARCH MUSIC
# ==================================================

results = music_manager.search_music(
    user_query
)


if not results:

    print("❌ No music found.")

    exit()


# ==================================================
# DISPLAY RESULTS
# ==================================================

print("\n================================")
print("SEARCH RESULTS")
print("================================")


for index, track in enumerate(
    results,
    start=1
):

    print(
        f"{index}. "
        f"{track['title']} "
        f"| {track['artist']} "
        f"| {track['genre']} "
        f"| {track['bpm']} BPM"
    )


# ==================================================
# SELECT FIRST RESULT
# ==================================================

selected = results[0]


print("\n================================")
print("USER SELECTED MUSIC")
print("================================")

print(
    "Selected:",
    selected["title"]
)

print(
    "Filename:",
    selected["filename"]
)


# ==================================================
# RESOLVE MUSIC PATH
# ==================================================

music_path = (
    "datasets/music/"
    + selected["filename"]
)


print(
    "Music Path:",
    music_path
)


# ==================================================
# CHECK FILE
# ==================================================

import os


if not os.path.exists(
    music_path
):

    print(
        "❌ Music file does not exist:"
    )

    print(
        music_path
    )

    exit()


print(
    "✅ Music file found"
)


# ==================================================
# VIDEO STORYBOARD
# ==================================================

storyboard = [

    {
        "scene_number": 1,
        "scene": "Organic farm",
        "media_type": "video",
        "media_path":
            "datasets/clips/video1_clip001.mp4",
        "duration": 5
    },

    {
        "scene_number": 2,
        "scene": "Fresh vegetables",
        "media_type": "video",
        "media_path":
            "datasets/clips/video2_clip001.mp4",
        "duration": 5
    },

    {
        "scene_number": 3,
        "scene": "Modern tractors",
        "media_type": "video",
        "media_path":
            "datasets/clips/video4_clip001.mp4",
        "duration": 5
    }

]


# ==================================================
# MUSIC DECISION
# ==================================================

music_timeline = [

    {
        "scene_number": 1,
        "music_state": "ON",
        "volume": 0.30
    },

    {
        "scene_number": 2,
        "music_state": "DUCK",
        "volume": 0.15
    },

    {
        "scene_number": 3,
        "music_state": "OFF",
        "volume": 0.0
    }

]


# ==================================================
# VIDEO COMPOSER
# ==================================================

composer = VideoComposer()


# ==================================================
# COMPOSE VIDEO
# ==================================================

print("\n================================")
print("CREATING VIDEO")
print("================================")


output = composer.compose(

    storyboard=storyboard,

    music_path=music_path,

    music_timeline=music_timeline,

    output_name=
        "manual_music_selection_test.mp4"
)


# ==================================================
# RESULT
# ==================================================

print("\n================================")
print("MANUAL MUSIC TEST COMPLETED")
print("================================")

print(
    "Final Video:",
    output
)