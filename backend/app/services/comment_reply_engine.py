"""
FrameCraft AI
Comment Understanding + Reply Decision Engine

Purpose:
- Analyze incoming comments
- Classify comments
- Decide whether automatic reply is safe
- Generate creator-style replies
- Ask for creator permission for complex/uncertain comments

This module is intentionally independent of the frontend.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


# ============================================================
# DATA MODEL
# ============================================================

@dataclass
class CommentAnalysis:
    comment: str
    category: str
    sentiment: str
    complexity: str
    confidence: float
    requires_permission: bool
    reason: str
    suggested_reply: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# COMMENT REPLY ENGINE
# ============================================================

class CommentReplyEngine:
    """
    Understands comments and decides whether FrameCraft AI
    should automatically respond or request creator approval.
    """

    SIMPLE_CATEGORIES = {
        "positive",
        "question",
        "thanks",
        "greeting",
        "neutral",
    }

    COMPLEX_CATEGORIES = {
        "negative",
        "controversial",
        "sensitive",
        "personal",
        "spam",
        "unknown",
    }

    def __init__(
        self,
        creator_profile: Optional[Dict[str, Any]] = None,
        auto_reply_enabled: bool = True,
        confidence_threshold: float = 0.75,
    ):
        self.creator_profile = creator_profile or {}
        self.auto_reply_enabled = auto_reply_enabled
        self.confidence_threshold = confidence_threshold

        print("Comment Reply Engine Initialized!")

    # ========================================================
    # PUBLIC API
    # ========================================================

    def analyze_comment(self, comment: str) -> CommentAnalysis:
        """
        Analyze a single comment.
        """

        comment = self._clean_comment(comment)

        if not comment:
            return CommentAnalysis(
                comment="",
                category="unknown",
                sentiment="neutral",
                complexity="complex",
                confidence=1.0,
                requires_permission=True,
                reason="Empty comment.",
            )

        category = self._classify_comment(comment)
        sentiment = self._detect_sentiment(comment)

        confidence = self._calculate_confidence(
            comment,
            category,
            sentiment,
        )

        complexity = self._determine_complexity(
            comment,
            category,
            confidence,
        )

        requires_permission = self._requires_permission(
            category,
            complexity,
            confidence,
        )

        reason = self._permission_reason(
            category,
            complexity,
            confidence,
        )

        suggested_reply = None

        if not requires_permission:
            suggested_reply = self.generate_reply(
                comment,
                category=category,
                sentiment=sentiment,
            )

        return CommentAnalysis(
            comment=comment,
            category=category,
            sentiment=sentiment,
            complexity=complexity,
            confidence=confidence,
            requires_permission=requires_permission,
            reason=reason,
            suggested_reply=suggested_reply,
        )

    # ========================================================
    # COMMENT CLASSIFICATION
    # ========================================================

    def _classify_comment(self, comment: str) -> str:
        text = comment.lower().strip()

        # -----------------------------
        # Spam
        # -----------------------------

        spam_patterns = [
            "follow me",
            "follow back",
            "check my profile",
            "dm me",
            "send me money",
            "click the link",
            "buy followers",
            "free followers",
            "crypto",
            "investment opportunity",
        ]

        if any(pattern in text for pattern in spam_patterns):
            return "spam"

        # -----------------------------
        # Sensitive topics
        # -----------------------------

        sensitive_patterns = [
            "suicide",
            "self harm",
            "kill yourself",
            "abuse",
            "harassment",
            "sexual",
            "explicit",
            "medical emergency",
            "diagnosis",
        ]

        if any(pattern in text for pattern in sensitive_patterns):
            return "sensitive"

        # -----------------------------
        # Personal requests
        # -----------------------------

        personal_patterns = [
            "your phone number",
            "where do you live",
            "home address",
            "send me your number",
            "personal number",
            "private number",
            "meet me",
            "date me",
        ]

        if any(pattern in text for pattern in personal_patterns):
            return "personal"

        # -----------------------------
        # Controversial
        # -----------------------------

        controversial_patterns = [
            "politics",
            "political",
            "religion",
            "racist",
            "sexist",
            "you are a liar",
            "fake",
            "scam",
            "fraud",
        ]

        if any(pattern in text for pattern in controversial_patterns):
            return "controversial"

        # -----------------------------
        # Negative
        # -----------------------------

        negative_patterns = [
            "bad",
            "worst",
            "hate",
            "terrible",
            "useless",
            "boring",
            "stupid",
            "dislike",
            "awful",
            "trash",
        ]

        if any(pattern in text for pattern in negative_patterns):
            return "negative"

        # -----------------------------
        # Thanks
        # -----------------------------

        thanks_patterns = [
            "thank you",
            "thanks",
            "thx",
            "appreciate it",
            "much appreciated",
        ]

        if any(pattern in text for pattern in thanks_patterns):
            return "thanks"

        # -----------------------------
        # Greeting
        # -----------------------------

        greeting_patterns = [
            "hello",
            "hi",
            "hey",
            "good morning",
            "good evening",
            "good afternoon",
        ]

        if text in greeting_patterns:
            return "greeting"

        # -----------------------------
        # Positive
        # -----------------------------

        positive_patterns = [
            "love this",
            "loved this",
            "amazing",
            "awesome",
            "great",
            "beautiful",
            "nice",
            "excellent",
            "fantastic",
            "wonderful",
            "perfect",
            "helpful",
            "incredible",
        ]

        if any(pattern in text for pattern in positive_patterns):
            return "positive"

        # -----------------------------
        # Question
        # -----------------------------

        question_words = [
            "what",
            "why",
            "how",
            "when",
            "where",
            "which",
            "who",
            "can",
            "could",
            "does",
            "do",
            "is",
            "are",
        ]

        words = text.split()

        if "?" in text:
            return "question"

        if words and words[0] in question_words:
            return "question"

        # -----------------------------
        # Default
        # -----------------------------

        return "neutral"

    # ========================================================
    # SENTIMENT
    # ========================================================

    def _detect_sentiment(self, comment: str) -> str:
        text = comment.lower()

        positive_words = {
            "love",
            "amazing",
            "awesome",
            "great",
            "beautiful",
            "excellent",
            "fantastic",
            "wonderful",
            "perfect",
            "helpful",
            "nice",
            "good",
        }

        negative_words = {
            "hate",
            "bad",
            "worst",
            "terrible",
            "awful",
            "boring",
            "stupid",
            "useless",
            "trash",
            "fake",
        }

        positive_score = sum(
            1 for word in positive_words if word in text
        )

        negative_score = sum(
            1 for word in negative_words if word in text
        )

        if positive_score > negative_score:
            return "positive"

        if negative_score > positive_score:
            return "negative"

        return "neutral"

    # ========================================================
    # CONFIDENCE
    # ========================================================

    def _calculate_confidence(
        self,
        comment: str,
        category: str,
        sentiment: str,
    ) -> float:

        confidence = 0.70

        if category in self.SIMPLE_CATEGORIES:
            confidence += 0.15

        if category in self.COMPLEX_CATEGORIES:
            confidence -= 0.10

        if "?" in comment:
            confidence += 0.05

        if len(comment.split()) <= 20:
            confidence += 0.05

        if len(comment.split()) > 50:
            confidence -= 0.10

        return round(
            max(0.0, min(0.99, confidence)),
            2,
        )

    # ========================================================
    # COMPLEXITY
    # ========================================================

    def _determine_complexity(
        self,
        comment: str,
        category: str,
        confidence: float,
    ) -> str:

        if category in self.COMPLEX_CATEGORIES:
            return "complex"

        if confidence < self.confidence_threshold:
            return "complex"

        # Long multi-part comments need more careful handling.
        if len(comment.split()) > 60:
            return "complex"

        # Multiple questions can require contextual understanding.
        if comment.count("?") >= 3:
            return "complex"

        return "simple"

    # ========================================================
    # PERMISSION DECISION
    # ========================================================

    def _requires_permission(
        self,
        category: str,
        complexity: str,
        confidence: float,
    ) -> bool:

        if not self.auto_reply_enabled:
            return True

        if complexity == "complex":
            return True

        if category in self.COMPLEX_CATEGORIES:
            return True

        if confidence < self.confidence_threshold:
            return True

        return False

    # ========================================================
    # REASON
    # ========================================================

    def _permission_reason(
        self,
        category: str,
        complexity: str,
        confidence: float,
    ) -> str:

        if category == "sensitive":
            return "Sensitive topic detected."

        if category == "personal":
            return "Personal information/request detected."

        if category == "controversial":
            return "Potentially controversial topic detected."

        if category == "negative":
            return "Negative comment requires creator review."

        if category == "spam":
            return "Possible spam or promotional content detected."

        if complexity == "complex":
            return "Comment is too complex or uncertain for automatic reply."

        if confidence < self.confidence_threshold:
            return "AI confidence is below the automatic-reply threshold."

        return "Automatic reply is safe."

    # ========================================================
    # REPLY GENERATION
    # ========================================================

    def generate_reply(
        self,
        comment: str,
        category: Optional[str] = None,
        sentiment: Optional[str] = None,
    ) -> str:

        category = category or self._classify_comment(comment)
        sentiment = sentiment or self._detect_sentiment(comment)

        language = self._profile_value(
            "language",
            "English",
        )

        tone = self._profile_value(
            "tone",
            "friendly",
        )

        style = self._profile_value(
            "style",
            "casual",
        )

        reply_length = self._profile_value(
            "reply_length",
            "short",
        )

        emoji_preference = self._profile_value(
            "emoji_preference",
            "occasional",
        )

        # --------------------------------
        # Base reply
        # --------------------------------

        if category == "positive":
            reply = self._positive_reply(tone, style)

        elif category == "thanks":
            reply = self._thanks_reply(tone, style)

        elif category == "greeting":
            reply = self._greeting_reply(tone, style)

        elif category == "question":
            reply = self._question_reply(tone, style)

        elif category == "neutral":
            reply = self._neutral_reply(tone, style)

        else:
            # Complex replies should normally not reach here.
            return ""

        # --------------------------------
        # Length
        # --------------------------------

        reply = self._apply_length(
            reply,
            reply_length,
        )

        # --------------------------------
        # Emoji
        # --------------------------------

        reply = self._apply_emoji(
            reply,
            emoji_preference,
        )

        # --------------------------------
        # Language marker
        # --------------------------------

        reply = self._apply_language(
            reply,
            language,
        )

        return reply.strip()

    # ========================================================
    # REPLY TEMPLATES
    # ========================================================

    def _positive_reply(
        self,
        tone: str,
        style: str,
    ) -> str:

        if tone.lower() in {"professional", "formal"}:
            return "Thank you so much for your kind words. I'm glad you enjoyed it."

        if style.lower() in {"enthusiastic", "energetic"}:
            return "Thank you so much! Really happy you enjoyed it!"

        return "Thank you! I'm glad you enjoyed it!"

    def _thanks_reply(
        self,
        tone: str,
        style: str,
    ) -> str:

        if tone.lower() in {"professional", "formal"}:
            return "You're very welcome. I'm glad it was helpful."

        return "You're welcome! Glad it helped!"

    def _greeting_reply(
        self,
        tone: str,
        style: str,
    ) -> str:

        return "Hey! Thanks for stopping by!"

    def _question_reply(
        self,
        tone: str,
        style: str,
    ) -> str:

        return (
            "Thanks for asking! I'll share more details about this soon."
        )

    def _neutral_reply(
        self,
        tone: str,
        style: str,
    ) -> str:

        return "Thanks for watching and sharing your thoughts!"

    # ========================================================
    # PROFILE HELPERS
    # ========================================================

    def _profile_value(
        self,
        key: str,
        default: str,
    ) -> str:

        value = self.creator_profile.get(key)

        if value is None:
            return default

        if isinstance(value, str):
            return value

        return str(value)

    # ========================================================
    # LENGTH
    # ========================================================

    def _apply_length(
        self,
        reply: str,
        reply_length: str,
    ) -> str:

        value = reply_length.lower()

        if value in {"very short", "short"}:
            sentences = re.split(r"(?<=[.!?])\s+", reply)

            return " ".join(sentences[:2])

        return reply

    # ========================================================
    # EMOJI
    # ========================================================

    def _apply_emoji(
        self,
        reply: str,
        preference: str,
    ) -> str:

        value = preference.lower()

        if value in {"none", "never", "no"}:
            return reply

        if value in {"high", "frequent", "many"}:
            return reply + " 😊✨"

        if value in {"occasional", "sometimes", "low"}:
            return reply + " 😊"

        return reply

    # ========================================================
    # LANGUAGE
    # ========================================================

    def _apply_language(
        self,
        reply: str,
        language: str,
    ) -> str:

        # English is currently the safe default.
        #
        # Other language generation will be connected to the
        # language model layer later.

        if language.lower() in {
            "english",
            "en",
        }:
            return reply

        return reply

    # ========================================================
    # CLEANING
    # ========================================================

    def _clean_comment(
        self,
        comment: str,
    ) -> str:

        comment = str(comment)

        # Normalize whitespace.
        comment = re.sub(
            r"\s+",
            " ",
            comment,
        )

        return comment.strip()

    # ========================================================
    # BATCH PROCESSING
    # ========================================================

    def analyze_comments(
        self,
        comments: List[str],
    ) -> List[Dict[str, Any]]:

        results = []

        for comment in comments:
            analysis = self.analyze_comment(comment)

            results.append(
                analysis.to_dict()
            )

        return results

    # ========================================================
    # CREATOR APPROVAL
    # ========================================================

    def approve_reply(
        self,
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:

        """
        Called later by the API/frontend when the creator
        approves a complex reply.

        At this stage we only change the decision state.
        """

        result = dict(analysis)

        result["requires_permission"] = False
        result["creator_approved"] = True

        return result

    def reject_reply(
        self,
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:

        result = dict(analysis)

        result["requires_permission"] = True
        result["creator_approved"] = False
        result["reply_status"] = "rejected"

        return result


# ============================================================
# SIMPLE FUNCTION API
# ============================================================

def analyze_comment(
    comment: str,
    creator_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    engine = CommentReplyEngine(
        creator_profile=creator_profile,
    )

    return engine.analyze_comment(
        comment
    ).to_dict()