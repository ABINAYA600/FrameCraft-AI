import json
import os


class MusicCatalog:

    def __init__(self, metadata_path="datasets/music/music_metadata.json"):

        self.metadata_path = metadata_path

        with open(self.metadata_path, "r", encoding="utf-8") as file:
            self.tracks = json.load(file)

        print(f"Music Catalog Loaded: {len(self.tracks)} tracks")

    # -----------------------------------------
    # Get all tracks
    # -----------------------------------------

    def get_all_tracks(self):
        return self.tracks

    # -----------------------------------------
    # Search by song / artist
    # -----------------------------------------

    def search(self, query):

        query = query.lower().strip()

        results = []

        for track in self.tracks:

            title = track["title"].lower()
            artist = track["artist"].lower()

            if query in title or query in artist:

                results.append(track)

        return results

    # -----------------------------------------
    # Search by mood
    # -----------------------------------------

    def search_by_mood(self, mood):

        mood = mood.lower().strip()

        results = []

        for track in self.tracks:

            moods = [
                m.lower()
                for m in track.get("mood", [])
            ]

            if mood in moods:

                results.append(track)

        return results

    # -----------------------------------------
    # Get audio path
    # -----------------------------------------

    def get_audio_path(self, track):

        return os.path.join(
            "datasets",
            "music",
            track["filename"]
        )