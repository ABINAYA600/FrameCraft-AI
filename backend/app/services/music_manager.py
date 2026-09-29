from app.services.music_catalog import MusicCatalog
from app.services.music_recommender import MusicRecommender


class MusicManager:

    def __init__(self):

        self.catalog = MusicCatalog()
        self.recommender = MusicRecommender()

        print("Music Manager Initialized!")

    # -----------------------------------------
    # AI Recommendation
    # -----------------------------------------

    def recommend_music(self, mood, energy=None):

        return self.recommender.recommend(
            mood=mood,
            energy=energy
        )

    # -----------------------------------------
    # Manual Search
    # -----------------------------------------

    def search_music(self, query):

        return self.catalog.search(query)

    # -----------------------------------------
    # Select Recommended Music
    # -----------------------------------------

    def accept_recommendation(self, track):

        return {
            "source": "ai_recommendation",
            "selected": True,
            "track": track,
            "audio_path": self.catalog.get_audio_path(track)
        }

    # -----------------------------------------
    # Select Manual Music
    # -----------------------------------------

    def select_manual_music(self, track):

        return {
            "source": "manual_selection",
            "selected": True,
            "track": track,
            "audio_path": self.catalog.get_audio_path(track)
        }