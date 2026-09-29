from typing import Dict, Any, Optional


class ReplyGenerationModel:
    """
    Generates replies according to the creator profile.

    The model currently uses deterministic templates.
    A real LLM can be connected later without changing
    the rest of the reply pipeline.
    """

    def __init__(self):
        print("Reply Generation Model Initialized!")

    def generate(
        self,
        comment: str,
        creator_profile: Optional[Dict[str, Any]] = None,
        category: str = "neutral",
    ) -> str:

        profile = creator_profile or {}

        tone = str(
            profile.get("tone", "friendly")
        ).lower()

        style = str(
            profile.get("style", "casual")
        ).lower()

        length = str(
            profile.get("reply_length", "short")
        ).lower()

        emoji = str(
            profile.get(
                "emoji_preference",
                "occasional",
            )
        ).lower()

        # -------------------------------
        # Reply selection
        # -------------------------------

        if category == "positive":
            if tone in {"professional", "formal"}:
                reply = (
                    "Thank you for your kind words. "
                    "I'm glad you enjoyed the video."
                )
            else:
                reply = "Thank you! I'm glad you enjoyed it!"

        elif category == "thanks":
            reply = "You're welcome! Glad it helped!"

        elif category == "greeting":
            reply = "Hey! Thanks for stopping by!"

        elif category == "question":
            reply = (
                "Thanks for asking! I'll share more details "
                "about this soon."
            )

        elif category == "neutral":
            reply = (
                "Thanks for watching and sharing your thoughts!"
            )

        else:
            return ""

        # -------------------------------
        # Short reply
        # -------------------------------

        if length in {"very short", "short"}:
            sentences = reply.split(".")
            reply = sentences[0].strip()

            if reply:
                reply += "!"

        # -------------------------------
        # Emoji preference
        # -------------------------------

        if emoji in {"none", "never", "no"}:
            pass

        elif emoji in {"high", "frequent", "many"}:
            reply += " 😊✨"

        elif emoji in {"occasional", "sometimes", "low"}:
            reply += " 😊"

        # -------------------------------
        # Casual style
        # -------------------------------

        if style == "casual":
            reply = reply.replace(
                "Thank you for your kind words.",
                "Thanks for the kind words!",
            )

        return reply.strip()