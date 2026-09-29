import json
import re
import os
import tempfile
from collections import Counter
from pathlib import Path


class CreatorProfileAnalyzer:
    """
    Builds a creator communication profile from previously
    analyzed creator content.

    The analyzer is intentionally independent from Whisper.
    It can consume transcripts later when the video transcription
    pipeline is working.
    """

    def __init__(self, output_path="output/creator_profile.json"):

        # ---------------------------------------------------------
        # OUTPUT PATH
        # ---------------------------------------------------------

        # Resolve relative paths from the backend directory.
        # This prevents problems caused by the current working directory.
        backend_dir = Path(__file__).resolve().parents[2]

        requested_path = Path(output_path)

        if requested_path.is_absolute():
            self.output_path = requested_path
        else:
            self.output_path = backend_dir / requested_path

        # Create output directory if it does not exist
        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        print("Creator Profile Analyzer Initialized!")
        print(f"Profile output: {self.output_path}")

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    def analyze(
        self,
        transcripts=None,
        comments=None,
        captions=None,
        creator_settings=None,
    ):

        transcripts = transcripts or []
        comments = comments or []
        captions = captions or []
        creator_settings = creator_settings or {}

        # Combine creator content
        all_text = self._combine_text(
            transcripts,
            captions
        )

        # ---------------------------------------------------------
        # BUILD PROFILE
        # ---------------------------------------------------------

        profile = {
            "profile_version": "1.0",

            "source": {
                "transcripts_analyzed": len(transcripts),
                "captions_analyzed": len(captions),
                "comments_analyzed": len(comments),
            },

            "tone": self._detect_tone(all_text),

            "language": self._detect_language(all_text),

            "style": self._detect_style(all_text),

            "reply_length": self._detect_reply_length(
                comments
            ),

            "emoji_preference": self._detect_emoji_preference(
                all_text,
                comments
            ),

            "auto_reply": self._get_auto_reply_setting(
                creator_settings
            ),

            "topics_to_avoid": self._detect_topics_to_avoid(
                all_text
            ),

            "communication_rules": {
                "use_creator_style": True,
                "do_not_invent_personal_information": True,
                "ask_permission_for_complex_comments": True,
                "preserve_creator_language": True,
                "preserve_creator_tone": True,
            },

            "confidence": self._calculate_confidence(
                transcripts,
                comments,
                captions
            )
        }

        # Save profile
        self.save_profile(profile)

        return profile

    # ---------------------------------------------------------
    # TEXT PROCESSING
    # ---------------------------------------------------------

    def _combine_text(
        self,
        transcripts,
        captions
    ):

        texts = []

        # Transcripts
        for item in transcripts:

            if isinstance(item, dict):
                text = item.get("text", "")
            else:
                text = str(item)

            if text:
                texts.append(text)

        # Captions
        for item in captions:

            if isinstance(item, dict):
                text = item.get("text", "")
            else:
                text = str(item)

            if text:
                texts.append(text)

        return " ".join(texts)

    # ---------------------------------------------------------
    # TONE
    # ---------------------------------------------------------

    def _detect_tone(self, text):

        text_lower = text.lower()

        scores = {
            "friendly": 0,
            "professional": 0,
            "energetic": 0,
            "educational": 0,
            "emotional": 0,
            "casual": 0,
        }

        friendly_words = [
            "hello",
            "hi",
            "welcome",
            "thanks",
            "thank you",
            "friend",
            "guys",
            "everyone",
            "love",
        ]

        professional_words = [
            "therefore",
            "according",
            "analysis",
            "technology",
            "solution",
            "process",
            "industry",
            "professional",
        ]

        energetic_words = [
            "amazing",
            "awesome",
            "great",
            "exciting",
            "wow",
            "let's go",
            "incredible",
            "powerful",
        ]

        educational_words = [
            "learn",
            "explain",
            "how",
            "why",
            "step",
            "tutorial",
            "guide",
            "tip",
            "tips",
        ]

        emotional_words = [
            "feel",
            "heart",
            "love",
            "sad",
            "happy",
            "miss",
            "dream",
            "hope",
        ]

        casual_words = [
            "yeah",
            "okay",
            "really",
            "basically",
            "you know",
            "gonna",
            "wanna",
            "guys",
        ]

        # Count friendly words
        for word in friendly_words:
            scores["friendly"] += text_lower.count(word)

        # Count professional words
        for word in professional_words:
            scores["professional"] += text_lower.count(word)

        # Count energetic words
        for word in energetic_words:
            scores["energetic"] += text_lower.count(word)

        # Count educational words
        for word in educational_words:
            scores["educational"] += text_lower.count(word)

        # Count emotional words
        for word in emotional_words:
            scores["emotional"] += text_lower.count(word)

        # Count casual words
        for word in casual_words:
            scores["casual"] += text_lower.count(word)

        # Empty content
        if not text.strip():
            return {
                "primary": "unknown",
                "scores": scores
            }

        primary = max(
            scores,
            key=scores.get
        )

        if scores[primary] == 0:
            primary = "casual"

        return {
            "primary": primary,
            "scores": scores
        }

    # ---------------------------------------------------------
    # LANGUAGE
    # ---------------------------------------------------------

    def _detect_language(self, text):

        if not text.strip():
            return {
                "primary": "unknown",
                "distribution": {}
            }

        # Tamil Unicode range
        tamil_count = len(
            re.findall(
                r"[\u0B80-\u0BFF]",
                text
            )
        )

        # Hindi Unicode range
        hindi_count = len(
            re.findall(
                r"[\u0900-\u097F]",
                text
            )
        )

        # English alphabet
        english_count = len(
            re.findall(
                r"[A-Za-z]",
                text
            )
        )

        counts = {
            "english": english_count,
            "tamil": tamil_count,
            "hindi": hindi_count,
        }

        total = sum(counts.values())

        if total == 0:
            return {
                "primary": "unknown",
                "distribution": {}
            }

        distribution = {
            language: round(
                count / total,
                3
            )
            for language, count in counts.items()
            if count > 0
        }

        primary = max(
            counts,
            key=counts.get
        )

        return {
            "primary": primary,
            "distribution": distribution
        }

    # ---------------------------------------------------------
    # CONTENT STYLE
    # ---------------------------------------------------------

    def _detect_style(self, text):

        text_lower = text.lower()

        scores = {
            "educational": 0,
            "storytelling": 0,
            "promotional": 0,
            "conversational": 0,
            "motivational": 0,
        }

        educational = [
            "how",
            "why",
            "learn",
            "step",
            "tutorial",
            "guide",
            "explain",
            "tip",
        ]

        storytelling = [
            "story",
            "once",
            "when i",
            "my journey",
            "experience",
            "happened",
            "remember",
        ]

        promotional = [
            "buy",
            "subscribe",
            "follow",
            "offer",
            "available",
            "product",
            "link",
            "discount",
        ]

        conversational = [
            "you",
            "we",
            "guys",
            "let's",
            "what do you think",
            "tell me",
            "comment",
        ]

        motivational = [
            "believe",
            "success",
            "never give up",
            "keep going",
            "achieve",
            "dream",
            "motivation",
        ]

        for word in educational:
            scores["educational"] += text_lower.count(word)

        for word in storytelling:
            scores["storytelling"] += text_lower.count(word)

        for word in promotional:
            scores["promotional"] += text_lower.count(word)

        for word in conversational:
            scores["conversational"] += text_lower.count(word)

        for word in motivational:
            scores["motivational"] += text_lower.count(word)

        primary = max(
            scores,
            key=scores.get
        )

        if scores[primary] == 0:
            primary = "conversational"

        return {
            "primary": primary,
            "scores": scores
        }

    # ---------------------------------------------------------
    # REPLY LENGTH
    # ---------------------------------------------------------

    def _detect_reply_length(self, comments):

        if not comments:
            return {
                "preferred": "medium",
                "average_words": 0
            }

        word_counts = []

        for comment in comments:

            if isinstance(comment, dict):
                text = comment.get(
                    "text",
                    ""
                )
            else:
                text = str(comment)

            words = text.split()

            if words:
                word_counts.append(
                    len(words)
                )

        if not word_counts:
            return {
                "preferred": "medium",
                "average_words": 0
            }

        average = sum(word_counts) / len(word_counts)

        if average <= 8:
            preferred = "short"

        elif average <= 25:
            preferred = "medium"

        else:
            preferred = "detailed"

        return {
            "preferred": preferred,
            "average_words": round(
                average,
                2
            )
        }

    # ---------------------------------------------------------
    # EMOJI
    # ---------------------------------------------------------

    def _detect_emoji_preference(
        self,
        text,
        comments
    ):

        combined = text

        for comment in comments:

            if isinstance(comment, dict):
                combined += " " + comment.get(
                    "text",
                    ""
                )
            else:
                combined += " " + str(comment)

        emoji_pattern = (
            r"[\U0001F300-\U0001FAFF"
            r"\u2600-\u26FF"
            r"\u2700-\u27BF]"
        )

        emojis = re.findall(
            emoji_pattern,
            combined
        )

        words = max(
            len(combined.split()),
            1
        )

        emoji_ratio = len(emojis) / words

        if len(emojis) == 0:
            preference = "none"

        elif emoji_ratio < 0.02:
            preference = "low"

        elif emoji_ratio < 0.06:
            preference = "moderate"

        else:
            preference = "high"

        return {
            "preference": preference,
            "emoji_count": len(emojis),
            "common_emojis": [
                emoji
                for emoji, _ in Counter(
                    emojis
                ).most_common(10)
            ]
        }

    # ---------------------------------------------------------
    # AUTO REPLY
    # ---------------------------------------------------------

    def _get_auto_reply_setting(
        self,
        creator_settings
    ):

        if "auto_reply" in creator_settings:

            return {
                "enabled": bool(
                    creator_settings["auto_reply"]
                ),
                "source": "creator_setting"
            }

        return {
            "enabled": False,
            "source": "default"
        }

    # ---------------------------------------------------------
    # TOPICS TO AVOID
    # ---------------------------------------------------------

    def _detect_topics_to_avoid(self, text):

        text_lower = text.lower()

        sensitive_topics = [
            "politics",
            "religion",
            "personal relationship",
            "family",
            "medical advice",
            "financial advice",
            "password",
            "private information",
        ]

        detected = []

        for topic in sensitive_topics:

            keywords = topic.split()

            if any(
                keyword in text_lower
                for keyword in keywords
            ):
                detected.append(topic)

        return detected

    # ---------------------------------------------------------
    # CONFIDENCE
    # ---------------------------------------------------------

    def _calculate_confidence(
        self,
        transcripts,
        comments,
        captions
    ):

        evidence_count = (
            len(transcripts)
            + len(comments)
            + len(captions)
        )

        if evidence_count == 0:
            return 0.0

        if evidence_count < 3:
            return 0.35

        if evidence_count < 5:
            return 0.55

        if evidence_count < 10:
            return 0.75

        return 0.90

    # ---------------------------------------------------------
    # SAVE PROFILE
    # ---------------------------------------------------------

    def save_profile(self, profile):
        """
        Save creator profile safely.

        Primary location:
            backend/output/creator_profile.json

        If Windows/OneDrive refuses access, a fallback file
        is attempted and finally the system temporary directory
        is used.
        """

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # -----------------------------------------------------
        # PRIMARY SAVE
        # -----------------------------------------------------

        try:

            # Try to make an existing file writable
            if self.output_path.exists():
                try:
                    os.chmod(
                        self.output_path,
                        0o666
                    )
                except OSError:
                    pass

            with open(
                self.output_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    profile,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            print(
                f"Creator profile saved: "
                f"{self.output_path}"
            )

            return str(
                self.output_path
            )

        except PermissionError as error:

            print(
                f"Primary profile save failed: "
                f"{error}"
            )

        # -----------------------------------------------------
        # FALLBACK SAVE
        # -----------------------------------------------------

        fallback_path = (
            self.output_path.parent
            / "creator_profile_latest.json"
        )

        try:

            with open(
                fallback_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    profile,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            print(
                f"Creator profile saved using fallback: "
                f"{fallback_path}"
            )

            # Update active path so load_profile() can use it
            self.output_path = fallback_path

            return str(
                fallback_path
            )

        except PermissionError as error:

            print(
                f"Fallback profile save failed: "
                f"{error}"
            )

        # -----------------------------------------------------
        # FINAL TEMP DIRECTORY FALLBACK
        # -----------------------------------------------------

        temp_dir = Path(
            tempfile.gettempdir()
        )

        temp_path = (
            temp_dir
            / "framecraft_creator_profile.json"
        )

        with open(
            temp_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                profile,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"Creator profile saved to temporary "
            f"location: {temp_path}"
        )

        self.output_path = temp_path

        return str(
            temp_path
        )

    # ---------------------------------------------------------
    # LOAD PROFILE
    # ---------------------------------------------------------

    def load_profile(self):

        if not self.output_path.exists():
            return None

        try:

            with open(
                self.output_path,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except (
            PermissionError,
            json.JSONDecodeError
        ) as error:

            print(
                f"Could not load creator profile: "
                f"{error}"
            )

            return None