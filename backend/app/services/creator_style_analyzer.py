import os
import json
import re
from collections import Counter


class CreatorStyleAnalyzer:

    def __init__(
        self,
        output_path="output/creator_profile.json"
    ):

        self.output_path = output_path

        directory = os.path.dirname(
            self.output_path
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        print(
            "Creator Style Analyzer Initialized!"
        )

    # ==================================================
    # BASIC TEXT CLEANING
    # ==================================================

    def clean_text(self, text):

        if not text:
            return ""

        text = str(text)

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # ==================================================
    # LANGUAGE ANALYSIS
    # ==================================================

    def analyze_language(
        self,
        texts
    ):

        combined_text = " ".join(
            self.clean_text(text)
            for text in texts
        ).lower()

        if not combined_text:

            return {
                "value": "unknown",
                "confidence": 0.0
            }

        # Simple local language indicators.
        # This is intentionally lightweight.

        english_words = {
            "the",
            "and",
            "is",
            "are",
            "this",
            "that",
            "with",
            "for",
            "from",
            "you",
            "your",
            "we",
            "our",
            "today",
            "welcome",
            "how",
            "what",
            "why"
        }

        words = re.findall(
            r"\b[a-zA-Z]+\b",
            combined_text
        )

        if not words:

            return {
                "value": "unknown",
                "confidence": 0.0
            }

        english_matches = sum(
            1
            for word in words
            if word in english_words
        )

        confidence = min(
            english_matches / 5,
            1.0
        )

        if confidence >= 0.4:

            language = "English"

        else:

            language = "Unknown"

        return {
            "value": language,
            "confidence": round(
                confidence,
                3
            )
        }

    # ==================================================
    # TONE ANALYSIS
    # ==================================================

    def analyze_tone(
        self,
        texts
    ):

        combined = " ".join(
            self.clean_text(text)
            for text in texts
        ).lower()

        scores = {
            "friendly": 0,
            "professional": 0,
            "educational": 0,
            "enthusiastic": 0,
            "inspirational": 0,
            "casual": 0
        }

        friendly_words = [
            "hey",
            "hello",
            "hi",
            "welcome",
            "thanks",
            "thank",
            "everyone",
            "friends",
            "😊",
            "❤️",
            "welcome"
        ]

        professional_words = [
            "therefore",
            "analysis",
            "research",
            "according",
            "professional",
            "industry",
            "methodology"
        ]

        educational_words = [
            "learn",
            "explain",
            "explained",
            "how",
            "why",
            "step",
            "guide",
            "tutorial",
            "understand",
            "knowledge"
        ]

        enthusiastic_words = [
            "amazing",
            "awesome",
            "exciting",
            "great",
            "incredible",
            "wow",
            "love"
        ]

        inspirational_words = [
            "believe",
            "dream",
            "success",
            "motivation",
            "inspire",
            "journey",
            "never give up",
            "keep going"
        ]

        casual_words = [
            "gonna",
            "wanna",
            "yeah",
            "guys",
            "stuff",
            "cool",
            "okay",
            "ok"
        ]

        for word in friendly_words:

            scores["friendly"] += combined.count(
                word
            )

        for word in professional_words:

            scores["professional"] += combined.count(
                word
            )

        for word in educational_words:

            scores["educational"] += combined.count(
                word
            )

        for word in enthusiastic_words:

            scores["enthusiastic"] += combined.count(
                word
            )

        for word in inspirational_words:

            scores["inspirational"] += combined.count(
                word
            )

        for word in casual_words:

            scores["casual"] += combined.count(
                word
            )

        best_tone = max(
            scores,
            key=scores.get
        )

        total = sum(
            scores.values()
        )

        if total == 0:

            return {
                "value": "neutral",
                "confidence": 0.3
            }

        confidence = (
            scores[best_tone]
            /
            total
        )

        return {
            "value": best_tone,
            "confidence": round(
                confidence,
                3
            )
        }

    # ==================================================
    # WRITING STYLE
    # ==================================================

    def analyze_writing_style(
        self,
        texts
    ):

        cleaned = [
            self.clean_text(text)
            for text in texts
            if self.clean_text(text)
        ]

        if not cleaned:

            return {
                "value": "unknown",
                "confidence": 0.0
            }

        words = []

        for text in cleaned:

            words.extend(
                text.split()
            )

        average_words = (
            len(words)
            /
            len(cleaned)
        )

        question_count = sum(
            text.count("?")
            for text in cleaned
        )

        exclamation_count = sum(
            text.count("!")
            for text in cleaned
        )

        # ----------------------------------------------
        # Determine style
        # ----------------------------------------------

        if average_words < 60:

            style = "concise"

        elif average_words < 150:

            style = "simple"

        else:

            style = "detailed"

        if (
            question_count
            >
            len(cleaned)
        ):

            style = "conversational"

        confidence = min(
            average_words / 150,
            1.0
        )

        if style in [
            "concise",
            "simple"
        ]:

            confidence = max(
                confidence,
                0.65
            )

        return {
            "value": style,
            "confidence": round(
                confidence,
                3
            ),
            "average_words_per_content": round(
                average_words,
                2
            ),
            "questions_detected": question_count,
            "exclamations_detected": exclamation_count
        }

    # ==================================================
    # REPLY LENGTH
    # ==================================================

    def analyze_reply_length(
        self,
        texts
    ):

        if not texts:

            return {
                "value": "short",
                "confidence": 0.0
            }

        word_counts = []

        for text in texts:

            words = self.clean_text(
                text
            ).split()

            if words:

                word_counts.append(
                    len(words)
                )

        if not word_counts:

            return {
                "value": "short",
                "confidence": 0.0
            }

        average = (
            sum(word_counts)
            /
            len(word_counts)
        )

        if average < 50:

            length = "short"

        elif average < 120:

            length = "medium"

        else:

            length = "long"

        confidence = min(
            average / 120,
            1.0
        )

        return {
            "value": length,
            "confidence": round(
                confidence,
                3
            ),
            "average_words": round(
                average,
                2
            )
        }

    # ==================================================
    # EMOJI ANALYSIS
    # ==================================================

    def analyze_emoji_usage(
        self,
        texts
    ):

        emoji_pattern = re.compile(
            "["
            "\U0001F300-\U0001F64F"
            "\U0001F680-\U0001F6FF"
            "\U0001F700-\U0001F77F"
            "\U0001F780-\U0001F7FF"
            "\U0001F800-\U0001F8FF"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FAFF"
            "\U00002700-\U000027BF"
            "]+",
            flags=re.UNICODE
        )

        total_emojis = 0

        total_texts = 0

        for text in texts:

            cleaned = self.clean_text(
                text
            )

            if not cleaned:
                continue

            total_texts += 1

            matches = emoji_pattern.findall(
                cleaned
            )

            total_emojis += sum(
                len(match)
                for match in matches
            )

        if total_texts == 0:

            return {
                "value": "unknown",
                "confidence": 0.0
            }

        average = (
            total_emojis
            /
            total_texts
        )

        if average == 0:

            usage = "none"

        elif average <= 2:

            usage = "low"

        elif average <= 5:

            usage = "moderate"

        else:

            usage = "high"

        confidence = min(
            total_texts / 10,
            1.0
        )

        return {
            "value": usage,
            "confidence": round(
                confidence,
                3
            ),
            "average_emojis_per_content": round(
                average,
                2
            )
        }

    # ==================================================
    # COMMON PHRASES
    # ==================================================

    def analyze_common_phrases(
        self,
        texts,
        limit=10
    ):

        phrases = Counter()

        for text in texts:

            words = re.findall(
                r"\b[a-zA-Z]+\b",
                self.clean_text(text).lower()
            )

            # ------------------------------------------
            # Bigrams
            # ------------------------------------------

            for i in range(
                len(words) - 1
            ):

                phrase = (
                    words[i]
                    +
                    " "
                    +
                    words[i + 1]
                )

                phrases[phrase] += 1

        common = []

        for phrase, count in phrases.most_common(
            limit
        ):

            if count >= 2:

                common.append(
                    {
                        "phrase": phrase,
                        "count": count
                    }
                )

        return common

    # ==================================================
    # TOPIC / NICHE ANALYSIS
    # ==================================================

    def analyze_topics(
        self,
        texts,
        limit=10
    ):

        stop_words = {

            "the",
            "and",
            "this",
            "that",
            "with",
            "from",
            "into",
            "about",
            "your",
            "their",
            "there",
            "which",
            "will",
            "have",
            "has",
            "are",
            "was",
            "were",
            "for",
            "you",
            "they",
            "them",
            "then",
            "than",
            "also",
            "using",
            "today",
            "welcome",
            "video"
        }

        counter = Counter()

        for text in texts:

            words = re.findall(
                r"\b[a-zA-Z][a-zA-Z0-9-]{2,}\b",
                self.clean_text(text).lower()
            )

            for word in words:

                if word in stop_words:
                    continue

                counter[word] += 1

        return [
            {
                "topic": word,
                "frequency": count
            }

            for word, count
            in counter.most_common(
                limit
            )
        ]

    # ==================================================
    # ANALYZE ALL CONTENT
    # ==================================================

    def analyze(
        self,
        previous_videos
    ):

        print(
            "\n================================"
        )

        print(
            "CREATOR STYLE ANALYSIS"
        )

        print(
            "================================"
        )

        if not previous_videos:

            raise ValueError(
                "No previous video content provided."
            )

        texts = []

        video_count = 0

        for video in previous_videos:

            if isinstance(
                video,
                str
            ):

                text = video

            elif isinstance(
                video,
                dict
            ):

                text_parts = []

                for key in [
                    "script",
                    "transcript",
                    "caption",
                    "description",
                    "title"
                ]:

                    value = video.get(
                        key
                    )

                    if value:

                        text_parts.append(
                            str(value)
                        )

                text = " ".join(
                    text_parts
                )

                video_count += 1

            else:

                continue

            text = self.clean_text(
                text
            )

            if text:

                texts.append(
                    text
                )

        if not texts:

            raise ValueError(
                "No usable text found "
                "in previous videos."
            )

        # ==================================================
        # ANALYZE
        # ==================================================

        language = self.analyze_language(
            texts
        )

        tone = self.analyze_tone(
            texts
        )

        style = self.analyze_writing_style(
            texts
        )

        reply_length = (
            self.analyze_reply_length(
                texts
            )
        )

        emoji_usage = (
            self.analyze_emoji_usage(
                texts
            )
        )

        common_phrases = (
            self.analyze_common_phrases(
                texts
            )
        )

        topics = (
            self.analyze_topics(
                texts
            )
        )

        # ==================================================
        # PROFILE
        # ==================================================

        profile = {

            "creator_name": "",

            "niche": [
                item["topic"]
                for item in topics[:5]
            ],

            "language": language,

            "tone": tone,

            "style": style,

            "reply_length": reply_length,

            "emoji_usage": emoji_usage,

            "common_phrases": common_phrases,

            "topics": topics,

            # ------------------------------------------
            # IMPORTANT:
            # These remain creator-controlled.
            # ------------------------------------------

            "auto_reply_enabled": False,

            "require_permission_for_complex": True,

            "topics_to_avoid": [],

            "analysis": {

                "videos_analyzed":
                    video_count,

                "content_samples":
                    len(texts),

                "method":
                    "Local statistical content analysis"
            }
        }

        return profile

    # ==================================================
    # SAVE PROFILE
    # ==================================================

    def save_profile(
        self,
        profile
    ):

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
            "\n✅ Creator profile saved:"
        )

        print(
            self.output_path
        )

        return self.output_path

    # ==================================================
    # ANALYZE + SAVE
    # ==================================================

    def analyze_and_save(
        self,
        previous_videos
    ):

        profile = self.analyze(
            previous_videos
        )

        path = self.save_profile(
            profile
        )

        return (
            profile,
            path
        )