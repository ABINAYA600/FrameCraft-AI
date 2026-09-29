from app.services.music_catalog import MusicCatalog


class MusicRecommender:

    def __init__(self):

        self.catalog = MusicCatalog()

        print("Music Recommender Initialized!")

    # -----------------------------------------
    # Recommend music
    # -----------------------------------------

    def recommend(self, mood, energy=None):

        tracks = self.catalog.get_all_tracks()

        results = []

        mood = mood.lower()

        for track in tracks:

            score = 0

            track_moods = [
                m.lower()
                for m in track.get("mood", [])
            ]

            # Mood match
            if mood in track_moods:

                score += 70

            # Energy match
            if energy:

                if track.get("energy", "").lower() == energy.lower():

                    score += 30

            if score > 0:

                result = track.copy()

                result["match_score"] = score

                results.append(result)

        results.sort(
            key=lambda x: x["match_score"],
            reverse=True
        )

        return results