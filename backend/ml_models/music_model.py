import os


class MusicModel:
    """
    FrameCraft AI Music Model

    Recommends background music from the FrameCraft
    music catalog based on the script context.

    No external music API is required.
    """

    def __init__(self, music_folder="datasets/music"):

        print("Loading Music Model...")

        self.music_folder = music_folder

        self.supported_extensions = (
            ".mp3",
            ".wav",
            ".m4a",
            ".aac",
        )

        self.mood_keywords = {
            "happy": [
                "happy", "joy", "joyful", "fun", "funny", "celebrate",
                "celebration", "festival", "party", "smile", "laugh",
                "exciting", "excited", "success", "victory", "friends",
                "friendship", "memories", "beautiful",
            ],
            "calm": [
                "peaceful", "peace", "calm", "relaxing", "relax", "nature",
                "organic", "meditation", "quiet", "slow", "serene",
            ],
            "technology": [
                "technology", "tech", "artificial intelligence", "ai",
                "innovation", "future", "digital", "software", "computer",
                "robot", "machine learning", "productivity", "smart",
            ],
            "emotional": [
                "sad", "emotional", "emotion", "loss", "memories", "nostalgia",
                "heart", "love", "goodbye", "tears",
            ],
            "cinematic": [
                "cinematic", "story", "journey", "adventure", "dramatic",
                "film", "movie", "documentary", "epic",
            ],
            "inspiring": [
                "inspire", "inspiring", "motivation", "motivational", "dream",
                "achievement", "success", "goal", "growth", "hope", "future",
            ],
        }

        self.energy_keywords = {
            "low": [
                "peaceful", "calm", "relaxing", "meditation", "emotional", "sad", "slow",
            ],
            "medium": [
                "story", "friends", "friendship", "memories", "nature",
                "technology", "inspiring", "beautiful",
            ],
            "high": [
                "exciting", "excited", "fun", "party", "festival", "celebrate",
                "sports", "victory", "adventure", "action",
            ],
        }

        print("Music Model Loaded Successfully!")

    def load_music(self):
        if not os.path.exists(self.music_folder):
            return []

        music_files = []

        for file in os.listdir(self.music_folder):
            if file.lower().endswith(self.supported_extensions):
                music_files.append(file)

        return sorted(music_files)

    def detect_mood(self, text):
        text = (text or "").lower()

        scores = {}

        for mood, keywords in self.mood_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            scores[mood] = score

        best_mood = max(scores, key=scores.get)

        if scores[best_mood] == 0:
            return "neutral"

        return best_mood

    def detect_energy(self, text):
        text = (text or "").lower()

        scores = {
            "low": 0,
            "medium": 0,
            "high": 0,
        }

        for energy, keywords in self.energy_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[energy] += 1

        best_energy = max(scores, key=scores.get)

        if scores[best_energy] == 0:
            return "medium"

        return best_energy

    def analyze_script(self, script):
        return {
            "mood": self.detect_mood(script),
            "energy": self.detect_energy(script),
        }

    def score_track(self, filename, mood, energy):
        filename_lower = filename.lower()

        score = 0
        reasons = []

        if mood in filename_lower:
            score += 60
            reasons.append(f"track matches {mood} mood")

        if energy in filename_lower:
            score += 25
            reasons.append(f"track matches {energy} energy")

        if mood != "neutral" and mood in filename_lower:
            score += 10

        if energy in filename_lower:
            score += 10

        if score == 0:
            score = 20
            reasons.append("general FrameCraft catalog track")

        return score, reasons

    def recommend_music(self, script, limit=5):
        music_files = self.load_music()
        analysis = self.analyze_script(script)

        mood = analysis["mood"]
        energy = analysis["energy"]

        if not music_files:
            return {
                "mood": mood,
                "energy": energy,
                "total_tracks": 0,
                "recommendations": [],
            }

        recommendations = []

        for filename in music_files:
            score, reasons = self.score_track(
                filename,
                mood,
                energy,
            )

            recommendations.append({
                "music": filename,
                "path": os.path.join(self.music_folder, filename),
                "match_score": score,
                "match_reason": ", ".join(reasons),
                "mood": mood,
                "energy": energy,
                "source": "framecraft",
                "usable_in_video": True,
            })

        recommendations.sort(
            key=lambda item: item["match_score"],
            reverse=True,
        )

        recommendations = recommendations[:max(1, min(limit, 20))]

        if recommendations:
            recommendations[0]["recommended"] = True
            for item in recommendations[1:]:
                item["recommended"] = False

        return {
            "mood": mood,
            "energy": energy,
            "total_tracks": len(music_files),
            "recommendations": recommendations,
        }

    def select_music(self, script):
        result = self.recommend_music(script, limit=1)
        recommendations = result["recommendations"]

        if not recommendations:
            return {
                "mood": result["mood"],
                "energy": result["energy"],
                "music": None,
                "path": None,
            }

        selected = recommendations[0]

        return {
            "mood": result["mood"],
            "energy": result["energy"],
            "music": selected["music"],
            "path": selected["path"],
        }
