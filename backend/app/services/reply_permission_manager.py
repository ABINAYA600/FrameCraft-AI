from typing import Dict, Any


class ReplyPermissionManager:
    """
    Controls whether a reply can be sent automatically.

    Complex, sensitive, personal, controversial,
    negative, spam, or low-confidence comments require
    creator approval.
    """

    APPROVAL_REQUIRED_CATEGORIES = {
        "complex",
        "sensitive",
        "personal",
        "controversial",
        "negative",
        "spam",
        "unknown",
    }

    def __init__(
        self,
        confidence_threshold: float = 0.75,
    ):
        self.confidence_threshold = (
            confidence_threshold
        )

        print("Reply Permission Manager Initialized!")

    def check(
        self,
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:

        category = str(
            analysis.get(
                "category",
                "unknown",
            )
        ).lower()

        complexity = str(
            analysis.get(
                "complexity",
                "complex",
            )
        ).lower()

        confidence = float(
            analysis.get(
                "confidence",
                0.0,
            )
        )

        # --------------------------------
        # Sensitive/complex categories
        # --------------------------------

        if category in self.APPROVAL_REQUIRED_CATEGORIES:
            return self._approval(
                "Category requires creator approval."
            )

        # --------------------------------
        # Complex comments
        # --------------------------------

        if complexity == "complex":
            return self._approval(
                "Comment is classified as complex."
            )

        # --------------------------------
        # Low confidence
        # --------------------------------

        if confidence < self.confidence_threshold:
            return self._approval(
                "AI confidence is below the required threshold."
            )

        return {
            "allowed": True,
            "requires_permission": False,
            "status": "auto_approved",
            "reason": "Comment is safe for automatic reply.",
        }

    def _approval(
        self,
        reason: str,
    ) -> Dict[str, Any]:

        return {
            "allowed": False,
            "requires_permission": True,
            "status": "waiting_for_creator",
            "reason": reason,
        }

    def approve(
        self,
        reply_id: str,
    ) -> Dict[str, Any]:

        return {
            "reply_id": reply_id,
            "allowed": True,
            "requires_permission": False,
            "status": "approved",
            "reason": "Creator approved the reply.",
        }

    def reject(
        self,
        reply_id: str,
    ) -> Dict[str, Any]:

        return {
            "reply_id": reply_id,
            "allowed": False,
            "requires_permission": True,
            "status": "rejected",
            "reason": "Creator rejected the reply.",
        }