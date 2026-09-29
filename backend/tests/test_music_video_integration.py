from ml_models.video_composer import VideoComposer
from app.services.music_manager import MusicManager
from app.services.music_decision_engine import MusicDecisionEngine


print("Starting Music + Video Integration Test...")


# ==================================================
# 1. INITIALIZE COMPONENTS
# ==================================================

music_manager = MusicManager()

decision_engine = MusicDecisionEngine()

composer = VideoComposer()


# ==================================================
# 2. STORYBOARD
# ==================================================

storyboard = [

    {
        "scene_number": 1,
        "scene": "Organic farm",
        "media_type": "video",
        "media_path": "datasets/clips/video1_clip001.mp4",
        "duration": 5,
        "has_speech": False,
        "importance": "normal"
    },

    {
        "scene_number": 2,
        "scene": "Farmer explaining organic farming",
        "media_type": "video",
        "media_path": "datasets/clips/video2_clip001.mp4",
        "duration": 5,
        "has_speech": True,
        "importance": "normal"
    },

    {
        "scene_number": 3,
        "scene": "Important farming explanation",
        "media_type": "video",
        "media_path": "datasets/clips/video4_clip001.mp4",
        "duration": 5,
        "has_speech": True,
        "importance": "high"
    },

    {
        "scene_number": 4,
        "scene": "Beautiful farm B-roll",
        "media_type": "video",
        "media_path": "datasets/clips/video3_clip001.mp4",
        "duration": 5,
        "has_speech": False,
        "importance": "normal"
    }
]


# ==================================================
# 3. GET AI MUSIC RECOMMENDATIONS
# ==================================================

print("\n================================")
print("AI MUSIC RECOMMENDATION")
print("================================")


recommendations = music_manager.recommend_music(
    mood="peaceful",
    energy="low"
)


if not recommendations:

    print("❌ No music recommendations found.")

    raise SystemExit


for track in recommendations:

    print(
        f"🎵 {track['title']} "
        f"| Match: {track['match_score']}%"
    )


# ==================================================
# 4. SIMULATE USER ACCEPTING
#    THE AI RECOMMENDATION
# ==================================================

selected_track = recommendations[0]


print("\n================================")
print("USER ACCEPTED RECOMMENDATION")
print("================================")


selected_music = music_manager.accept_recommendation(
    selected_track
)


print(
    "Selected Music:",
    selected_music["track"]["title"]
)

print(
    "Music Path:",
    selected_music["audio_path"]
)


# ==================================================
# 5. AI MUSIC DECISION
# ==================================================

print("\n================================")
print("AI MUSIC DECISION")
print("================================")


music_timeline = decision_engine.decide(
    storyboard
)


for item in music_timeline:

    print(
        f"Scene {item['scene_number']} "
        f"→ {item['music_state']} "
        f"→ Volume: {item['volume']}"
    )


# ==================================================
# 6. CURRENT COMPOSER
# ==================================================

print("\n================================")
print("VIDEO COMPOSITION")
print("================================")


output = composer.compose(
    storyboard=storyboard,
    music_path=selected_music["audio_path"],
    music_timeline=music_timeline,
    output_name="music_scene_control_test.mp4"
)

# ==================================================
# 7. RESULT
# ==================================================

print("\n================================")
print("INTEGRATION TEST COMPLETED")
print("================================")

print(
    "Final Video:",
    output
)

print(
    "\n⚠️ NOTE:"
)

print(
    "The current VideoComposer adds the selected "
    "music as one continuous track."
)

print(
    "Scene-level ON/DUCK/OFF control will be "
    "implemented in the next step."
)