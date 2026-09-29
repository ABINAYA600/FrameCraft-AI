from app.services.music_recommender import MusicRecommender


print("Starting Music Recommendation Test...")


recommender = MusicRecommender()


results = recommender.recommend(
    mood="peaceful",
    energy="low"
)


print("\n========== RECOMMENDATIONS ==========")


for track in results:

    print(
        f"🎵 {track['title']} "
        f"| Match: {track['match_score']}%"
    )


print("\nMusic Recommendation Test Completed!")