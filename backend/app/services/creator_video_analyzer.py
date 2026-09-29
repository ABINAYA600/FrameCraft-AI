"""
FrameCraft AI - Creator Video Analyzer

Analyzes a creator's previous videos to build a creator profile.

Pipeline:
    Previous Videos
          ↓
    FFmpeg Audio Extraction
          ↓
    Whisper Transcription
          ↓
    Transcript Analysis
          ↓
    Creator Style Profile
          ↓
    JSON Profile

Profile fields:
    - tone
    - language
    - style
    - reply_length
    - emoji_preference
    - auto_reply_setting
    - topics_to_avoid
    - confidence
    - analyzed_videos
"""

import os
import re
import json
import subprocess
from pathlib import Path
from collections import Counter

import imageio_ffmpeg
import whisper


# ============================================================
# FFmpeg CONFIGURATION
# ============================================================

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

if not os.path.exists(FFMPEG_PATH):
    raise FileNotFoundError(
        f"FFmpeg executable was not found:\n{FFMPEG_PATH}"
    )

FFMPEG_DIR = str(Path(FFMPEG_PATH).parent)

# Put the bundled FFmpeg directory at the beginning of PATH.
os.environ["PATH"] = (
    FFMPEG_DIR
    + os.pathsep
    + os.environ.get("PATH", "")
)

# Useful for libraries that look for this variable.
os.environ["FFMPEG_BINARY"] = FFMPEG_PATH


# ============================================================
# CREATOR STYLE ANALYZER
# ============================================================


class CreatorStyleAnalyzer:
    """
    Analyzes transcripts and generates a creator style profile.
    """

    def __init__(self):
        print("Creator Style Analyzer Initialized!")

    # --------------------------------------------------------
    # Tone
    # --------------------------------------------------------

    def analyze_tone(self, text):
        text_lower = text.lower()

        scores = {
            "friendly": 0,
            "professional": 0,
            "casual": 0,
            "energetic": 0,
            "educational": 0,
            "emotional": 0,
            "motivational": 0,
        }

        friendly_words = [
            "welcome",
            "thank you",
            "thanks",
            "hello",
            "hi",
            "friends",
            "guys",
            "hope",
            "enjoy",
        ]

        professional_words = [
            "therefore",
            "however",
            "important",
            "information",
            "professional",
            "process",
            "technology",
            "analysis",
        ]

        casual_words = [
            "guys",
            "okay",
            "yeah",
            "basically",
            "actually",
            "cool",
            "awesome",
            "let's",
        ]

        energetic_words = [
            "amazing",
            "awesome",
            "exciting",
            "incredible",
            "wow",
            "powerful",
            "great",
            "fantastic",
        ]

        educational_words = [
            "learn",
            "explain",
            "how",
            "why",
            "step",
            "steps",
            "tutorial",
            "guide",
            "example",
            "understand",
        ]

        emotional_words = [
            "feel",
            "love",
            "heart",
            "sad",
            "happy",
            "emotional",
            "memories",
        ]

        motivational_words = [
            "believe",
            "success",
            "never give up",
            "keep going",
            "motivation",
            "achieve",
            "goal",
            "dream",
        ]

        for word in friendly_words:
            if word in text_lower:
                scores["friendly"] += 1

        for word in professional_words:
            if word in text_lower:
                scores["professional"] += 1

        for word in casual_words:
            if word in text_lower:
                scores["casual"] += 1

        for word in energetic_words:
            if word in text_lower:
                scores["energetic"] += 1

        for word in educational_words:
            if word in text_lower:
                scores["educational"] += 1

        for word in emotional_words:
            if word in text_lower:
                scores["emotional"] += 1

        for word in motivational_words:
            if word in text_lower:
                scores["motivational"] += 1

        # Exclamation marks indicate energetic communication.
        scores["energetic"] += text.count("!")

        best_tone = max(
            scores,
            key=scores.get
        )

        if scores[best_tone] == 0:
            best_tone = "neutral"

        return {
            "value": best_tone,
            "scores": scores,
        }

    # --------------------------------------------------------
    # Language
    # --------------------------------------------------------

    def analyze_language(self, text):
        if not text.strip():
            return "unknown"

        tamil_chars = len(
            re.findall(
                r"[\u0B80-\u0BFF]",
                text
            )
        )

        hindi_chars = len(
            re.findall(
                r"[\u0900-\u097F]",
                text
            )
        )

        english_chars = len(
            re.findall(
                r"[A-Za-z]",
                text
            )
        )

        total = (
            tamil_chars
            + hindi_chars
            + english_chars
        )

        if total == 0:
            return "unknown"

        tamil_ratio = tamil_chars / total
        hindi_ratio = hindi_chars / total
        english_ratio = english_chars / total

        if tamil_ratio > 0.30:
            return "Tamil"

        if hindi_ratio > 0.30:
            return "Hindi"

        if english_ratio > 0.60:
            return "English"

        # Mixed-language creator.
        if tamil_chars > 0 and english_chars > 0:
            return "Tamil-English"

        if hindi_chars > 0 and english_chars > 0:
            return "Hindi-English"

        return "Mixed"

    # --------------------------------------------------------
    # Style
    # --------------------------------------------------------

    def analyze_style(self, text):
        text_lower = text.lower()

        scores = {
            "storytelling": 0,
            "educational": 0,
            "informational": 0,
            "conversational": 0,
            "tutorial": 0,
            "entertainment": 0,
        }

        storytelling_words = [
            "story",
            "once",
            "when I",
            "then",
            "after",
            "before",
            "experience",
            "happened",
        ]

        educational_words = [
            "learn",
            "explain",
            "understand",
            "because",
            "how",
            "why",
        ]

        informational_words = [
            "information",
            "facts",
            "important",
            "details",
            "according",
            "data",
        ]

        conversational_words = [
            "you",
            "your",
            "guys",
            "we",
            "let's",
            "I think",
            "what do you think",
        ]

        tutorial_words = [
            "step 1",
            "step 2",
            "first",
            "second",
            "next",
            "finally",
            "tutorial",
            "guide",
        ]

        entertainment_words = [
            "fun",
            "funny",
            "joke",
            "laugh",
            "awesome",
            "challenge",
        ]

        groups = {
            "storytelling": storytelling_words,
            "educational": educational_words,
            "informational": informational_words,
            "conversational": conversational_words,
            "tutorial": tutorial_words,
            "entertainment": entertainment_words,
        }

        for style, words in groups.items():
            for word in words:
                if word.lower() in text_lower:
                    scores[style] += 1

        best_style = max(
            scores,
            key=scores.get
        )

        if scores[best_style] == 0:
            best_style = "conversational"

        return {
            "value": best_style,
            "scores": scores,
        }

    # --------------------------------------------------------
    # Reply length
    # --------------------------------------------------------

    def analyze_reply_length(self, text):
        words = text.split()

        word_count = len(words)

        if word_count < 150:
            return "short"

        if word_count < 500:
            return "medium"

        return "long"

    # --------------------------------------------------------
    # Emoji preference
    # --------------------------------------------------------

    def analyze_emoji_preference(self, text):
        emoji_pattern = re.compile(
            "["
            "\U0001F300-\U0001F6FF"
            "\U0001F900-\U0001F9FF"
            "\U00002700-\U000027BF"
            "\U0001FA70-\U0001FAFF"
            "]"
        )

        emojis = emoji_pattern.findall(text)

        count = len(emojis)

        if count == 0:
            return {
                "value": "none",
                "count": 0,
                "examples": [],
            }

        emoji_counts = Counter(emojis)

        examples = [
            emoji
            for emoji, _ in emoji_counts.most_common(5)
        ]

        words = max(
            len(text.split()),
            1
        )

        emoji_ratio = count / words

        if emoji_ratio > 0.02:
            preference = "high"
        elif emoji_ratio > 0.005:
            preference = "moderate"
        else:
            preference = "low"

        return {
            "value": preference,
            "count": count,
            "examples": examples,
        }

    # --------------------------------------------------------
    # Topics
    # --------------------------------------------------------

    def analyze_topics(self, text):
        text_lower = text.lower()

        topic_keywords = {
            "technology": [
                "technology",
                "computer",
                "software",
                "ai",
                "artificial intelligence",
                "coding",
                "programming",
            ],
            "agriculture": [
                "farm",
                "farming",
                "agriculture",
                "crop",
                "tractor",
                "vegetable",
                "organic",
            ],
            "education": [
                "education",
                "student",
                "college",
                "school",
                "learn",
                "study",
            ],
            "travel": [
                "travel",
                "trip",
                "tour",
                "hotel",
                "flight",
                "beach",
                "mountain",
            ],
            "food": [
                "food",
                "recipe",
                "cook",
                "cooking",
                "restaurant",
                "taste",
            ],
            "fitness": [
                "fitness",
                "gym",
                "workout",
                "exercise",
                "health",
            ],
            "finance": [
                "money",
                "finance",
                "investment",
                "stock",
                "bank",
                "loan",
            ],
            "entertainment": [
                "movie",
                "music",
                "song",
                "game",
                "entertainment",
            ],
        }

        detected = {}

        for topic, keywords in topic_keywords.items():

            score = 0

            for keyword in keywords:
                if keyword in text_lower:
                    score += 1

            if score > 0:
                detected[topic] = score

        return detected

    # --------------------------------------------------------
    # Full profile
    # --------------------------------------------------------

    def analyze_transcripts(self, transcripts):

        valid_transcripts = [
            item
            for item in transcripts
            if item
            and item.get("text")
        ]

        if not valid_transcripts:
            raise RuntimeError(
                "No valid transcripts available for style analysis."
            )

        combined_text = "\n".join(
            item["text"]
            for item in valid_transcripts
        )

        tone = self.analyze_tone(
            combined_text
        )

        language = self.analyze_language(
            combined_text
        )

        style = self.analyze_style(
            combined_text
        )

        reply_length = self.analyze_reply_length(
            combined_text
        )

        emoji_preference = self.analyze_emoji_preference(
            combined_text
        )

        topics = self.analyze_topics(
            combined_text
        )

        profile = {
            "tone": tone["value"],
            "tone_scores": tone["scores"],

            "language": language,

            "style": style["value"],
            "style_scores": style["scores"],

            "reply_length": reply_length,

            "emoji_preference": emoji_preference,

            # This is inferred as a recommendation.
            # It does NOT automatically enable replying.
            "auto_reply_setting": "permission_required",

            # Topics are detected from the creator's videos.
            # They are NOT automatically forbidden.
            "topics_detected": topics,

            "topics_to_avoid": [],

            "analyzed_videos": len(
                valid_transcripts
            ),

            "confidence": self._calculate_confidence(
                len(valid_transcripts),
                len(combined_text.split())
            ),
        }

        return profile

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    def _calculate_confidence(
        self,
        video_count,
        word_count
    ):

        video_score = min(
            video_count / 5,
            1.0
        )

        word_score = min(
            word_count / 2000,
            1.0
        )

        confidence = (
            video_score * 0.4
            + word_score * 0.6
        )

        return round(
            confidence,
            2
        )


# ============================================================
# CREATOR VIDEO ANALYZER
# ============================================================


class CreatorVideoAnalyzer:

    SUPPORTED_VIDEO_EXTENSIONS = {
        ".mp4",
        ".mov",
        ".mkv",
        ".avi",
        ".webm",
        ".m4v",
    }

    def __init__(
        self,
        model_name="base",
        output_directory="output/creator_analysis",
        **kwargs
    ):
        """
        Initialize creator video analyzer.

        Extra kwargs are accepted for compatibility with older
        test scripts so obsolete constructor parameters don't
        immediately break the analyzer.
        """

        print("Loading Whisper model...")

        self.model_name = model_name

        self.output_directory = Path(
            output_directory
        )

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        # Force CPU-safe transcription.
        self.device = "cpu"

        self.whisper_model = whisper.load_model(
            model_name,
            device=self.device
        )

        print(
            f"Whisper model loaded: {model_name}"
        )

        self.style_analyzer = CreatorStyleAnalyzer()

        print(
            "Creator Video Analyzer Initialized!"
        )

    # --------------------------------------------------------
    # Find videos
    # --------------------------------------------------------

    def find_videos(self, input_directory):

        input_directory = Path(
            input_directory
        ).resolve()

        if not input_directory.exists():
            raise FileNotFoundError(
                f"Video directory does not exist:\n"
                f"{input_directory}"
            )

        videos = []

        for file_path in input_directory.iterdir():

            if not file_path.is_file():
                continue

            if file_path.suffix.lower() in (
                self.SUPPORTED_VIDEO_EXTENSIONS
            ):
                videos.append(
                    file_path
                )

        videos.sort()

        return videos

    # --------------------------------------------------------
    # Verify FFmpeg
    # --------------------------------------------------------

    def verify_ffmpeg(self):

        try:

            result = subprocess.run(
                [
                    FFMPEG_PATH,
                    "-version"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=15,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    "FFmpeg returned a non-zero exit code."
                )

            return True

        except Exception as e:

            raise RuntimeError(
                f"FFmpeg verification failed: {e}"
            )

    # --------------------------------------------------------
    # Extract audio
    # --------------------------------------------------------

    def extract_audio(
        self,
        video_path,
        audio_path
    ):

        video_path = Path(
            video_path
        ).resolve()

        audio_path = Path(
            audio_path
        ).resolve()

        if not video_path.exists():
            raise FileNotFoundError(
                f"Video not found:\n{video_path}"
            )

        audio_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        print("Extracting audio...")

        command = [
            FFMPEG_PATH,
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-acodec",
            "pcm_s16le",
            str(audio_path),
        ]

        try:

            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

        except FileNotFoundError:

            raise RuntimeError(
                "FFmpeg executable could not be started:\n"
                f"{FFMPEG_PATH}"
            )

        except subprocess.CalledProcessError as e:

            print(
                "FFmpeg error:"
            )

            print(
                e.stderr
            )

            raise RuntimeError(
                "FFmpeg failed while extracting audio."
            )

        if not audio_path.exists():

            raise RuntimeError(
                "FFmpeg completed but the audio file "
                "was not created."
            )

        if audio_path.stat().st_size == 0:

            raise RuntimeError(
                "Extracted audio file is empty."
            )

        print(
            "✅ Audio extracted successfully"
        )

        return audio_path

    # --------------------------------------------------------
    # Transcribe one video
    # --------------------------------------------------------

    def transcribe_video(
        self,
        video_path
    ):

        video_path = Path(
            video_path
        ).resolve()

        print()
        print("--------------------------------")
        print(
            f"Transcribing: {video_path}"
        )
        print("Please wait...")

        if not video_path.exists():

            raise FileNotFoundError(
                f"Video does not exist:\n"
                f"{video_path}"
            )

        audio_directory = (
            self.output_directory
            / "audio"
        )

        audio_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        audio_path = (
            audio_directory
            / f"{video_path.stem}.wav"
        )

        # Remove stale audio file.
        if audio_path.exists():

            try:
                audio_path.unlink()

            except Exception:
                pass

        # ----------------------------------------------------
        # Extract audio
        # ----------------------------------------------------

        self.extract_audio(
            video_path,
            audio_path
        )

        # ----------------------------------------------------
        # Whisper
        # ----------------------------------------------------

        print(
            "Running Whisper transcription..."
        )

        try:

            result = self.whisper_model.transcribe(
                str(audio_path),
                fp16=False,
                verbose=False,
            )

        except FileNotFoundError as e:

            raise RuntimeError(
                "Whisper could not start its FFmpeg "
                "subprocess.\n"
                f"FFmpeg configured as:\n{FFMPEG_PATH}\n"
                f"Original error: {e}"
            )

        except Exception as e:

            raise RuntimeError(
                f"Whisper transcription failed: {e}"
            )

        text = (
            result.get(
                "text",
                ""
            )
            .strip()
        )

        language = result.get(
            "language",
            "unknown"
        )

        print(
            "✅ Transcription completed"
        )

        print()
        print("Transcript:")

        if text:
            print(text)
        else:
            print(
                "[No speech detected]"
            )

        return {
            "video": video_path.name,
            "video_path": str(video_path),
            "audio_path": str(audio_path),
            "text": text,
            "language": language,
        }

    # --------------------------------------------------------
    # Transcribe all
    # --------------------------------------------------------

    def transcribe_all(
        self,
        input_directory
    ):

        print()
        print("================================")
        print(
            "PREVIOUS VIDEO TRANSCRIPTION"
        )
        print("================================")

        videos = self.find_videos(
            input_directory
        )

        print(
            f"Videos found: {len(videos)}"
        )

        if not videos:

            raise RuntimeError(
                "No supported videos found."
            )

        transcripts = []

        for index, video in enumerate(
            videos,
            start=1
        ):

            print()
            print(
                f"Video {index}/{len(videos)}"
            )

            try:

                transcript = (
                    self.transcribe_video(
                        video
                    )
                )

                if transcript:

                    transcripts.append(
                        transcript
                    )

            except Exception as e:

                print(
                    f"⚠️ Failed to process "
                    f"{video.name}"
                )

                print(
                    f"Reason: {e}"
                )

        if not transcripts:

            raise RuntimeError(
                "None of the videos could be transcribed."
            )

        return transcripts

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    def save_json(
        self,
        data,
        filename
    ):

        path = (
            self.output_directory
            / filename
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        return path

    # --------------------------------------------------------
    # Analyze videos
    # --------------------------------------------------------

    def analyze_videos(
        self,
        input_directory
    ):

        print()
        print("================================")
        print(
            "CREATOR VIDEO ANALYSIS PIPELINE"
        )
        print("================================")

        input_directory = Path(
            input_directory
        ).resolve()

        print(
            f"Input directory: "
            f"{input_directory}"
        )

        # ----------------------------------------------------
        # Verify FFmpeg
        # ----------------------------------------------------

        print()
        print(
            "Checking FFmpeg..."
        )

        self.verify_ffmpeg()

        print(
            "✅ FFmpeg available"
        )

        print(
            f"FFmpeg: {FFMPEG_PATH}"
        )

        # ----------------------------------------------------
        # Transcription
        # ----------------------------------------------------

        transcripts = self.transcribe_all(
            input_directory
        )

        # ----------------------------------------------------
        # Save transcripts
        # ----------------------------------------------------

        print()
        print("================================")
        print(
            "SAVING TRANSCRIPTS"
        )
        print("================================")

        transcript_file = (
            self.save_json(
                transcripts,
                "transcripts.json"
            )
        )

        print(
            f"✅ Transcripts saved:"
        )

        print(
            transcript_file
        )

        # ----------------------------------------------------
        # Style analysis
        # ----------------------------------------------------

        print()
        print("================================")
        print(
            "CREATOR STYLE ANALYSIS"
        )
        print("================================")

        profile = (
            self.style_analyzer
            .analyze_transcripts(
                transcripts
            )
        )

        # ----------------------------------------------------
        # Save profile
        # ----------------------------------------------------

        profile_file = (
            self.save_json(
                profile,
                "creator_profile.json"
            )
        )

        # ----------------------------------------------------
        # Print result
        # ----------------------------------------------------

        print()
        print("================================")
        print(
            "CREATOR PROFILE"
        )
        print("================================")

        print(
            f"Tone: "
            f"{profile['tone']}"
        )

        print(
            f"Language: "
            f"{profile['language']}"
        )

        print(
            f"Style: "
            f"{profile['style']}"
        )

        print(
            f"Reply Length: "
            f"{profile['reply_length']}"
        )

        print(
            f"Emoji Preference: "
            f"{profile['emoji_preference']['value']}"
        )

        print(
            f"Auto Reply: "
            f"{profile['auto_reply_setting']}"
        )

        print(
            f"Confidence: "
            f"{profile['confidence']}"
        )

        print()
        print(
            "Detected Topics:"
        )

        if profile["topics_detected"]:

            for topic, score in (
                profile[
                    "topics_detected"
                ].items()
            ):

                print(
                    f"  - {topic}: {score}"
                )

        else:

            print(
                "  None detected"
            )

        print()
        print(
            f"Creator profile saved:"
        )

        print(
            profile_file
        )

        # ----------------------------------------------------
        # Final result
        # ----------------------------------------------------

        return {
            "input_directory": str(
                input_directory
            ),

            "videos_analyzed": len(
                transcripts
            ),

            "transcripts": transcripts,

            "creator_profile": profile,

            "transcript_file": str(
                transcript_file
            ),

            "profile_file": str(
                profile_file
            ),
        }


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    analyzer = CreatorVideoAnalyzer(
        model_name="base",
        output_directory=(
            "output/creator_analysis"
        )
    )

    result = analyzer.analyze_videos(
        "datasets/creator_videos"
    )

    print()
    print("================================")
    print(
        "CREATOR VIDEO ANALYSIS COMPLETED"
    )
    print("================================")

    print(
        f"Videos analyzed: "
        f"{result['videos_analyzed']}"
    )

    print(
        f"Profile: "
        f"{result['profile_file']}"
    )