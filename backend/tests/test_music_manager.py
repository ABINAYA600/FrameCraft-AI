from app.services.music_manager import MusicManager


print("Starting Music Manager Test...")


manager = MusicManager()


# =========================================
# STEP 1: AI RECOMMENDATION
# =========================================

print("\n========== AI RECOMMENDATION ==========")

recommendations = manager.recommend_music(
    mood="peaceful",
    energy="low"
)


for track in recommendations:

    print(
        f"🎵 {track['title']} "
        f"| Match: {track['match_score']}%"
    )


# =========================================
# STEP 2: USER ACCEPTS
# =========================================

if recommendations:

    selected = manager.accept_recommendation(
        recommendations[0]
    )

    print("\n========== ACCEPTED ==========")

    print(
        "Selected:",
        selected["track"]["title"]
    )

    print(
        "Audio:",
        selected["audio_path"]
    )


# =========================================
# STEP 3: USER REJECTS
# =========================================

print("\n========== MANUAL SEARCH ==========")


results = manager.search_music(
    "Perfect"
)


for track in results:

    print(
        "Found:",
        track["title"]
    )


print("\nMusic Manager Test Completed!")