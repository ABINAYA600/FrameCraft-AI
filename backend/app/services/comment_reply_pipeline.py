from typing import Dict, Any, Optional

from app.services.comment_reply_engine import (
    CommentReplyEngine,
)

from app.services.reply_generation_model import (
    ReplyGenerationModel,
)

from app.services.reply_permission_manager import (
    ReplyPermissionManager,
)

from app.services.reply_queue import (
    ReplyQueue,
)


class CommentReplyPipeline:
    """
    Complete backend pipeline:

    Comment
       ↓
    Comment Analysis
       ↓
    Permission Decision
       ↓
    Reply Generation
       ↓
    Reply Queue
    """

    def __init__(
        self,
        creator_profile: Optional[Dict[str, Any]] = None,
        auto_reply_enabled: bool = True,
    ):

        self.creator_profile = (
            creator_profile or {}
        )

        self.analyzer = CommentReplyEngine(
            creator_profile=self.creator_profile,
            auto_reply_enabled=auto_reply_enabled,
        )

        self.generator = (
            ReplyGenerationModel()
        )

        self.permission_manager = (
            ReplyPermissionManager()
        )

        self.queue = ReplyQueue()

        print(
            "Comment Reply Pipeline Initialized!"
        )

    # =========================================
    # PROCESS COMMENT
    # =========================================

    def process_comment(
        self,
        comment: str,
    ) -> Dict[str, Any]:

        # -------------------------------------
        # 1. Analyze
        # -------------------------------------

        analysis = (
            self.analyzer.analyze_comment(
                comment
            )
        )

        analysis_dict = (
            analysis.to_dict()
        )

        # -------------------------------------
        # 2. Permission
        # -------------------------------------

        permission = (
            self.permission_manager.check(
                analysis_dict
            )
        )

        # -------------------------------------
        # 3. Generate reply
        # -------------------------------------

        reply = ""

        if permission["allowed"]:

            reply = (
                self.generator.generate(
                    comment=comment,
                    creator_profile=(
                        self.creator_profile
                    ),
                    category=(
                        analysis.category
                    ),
                )
            )

            status = "auto_approved"

        else:

            # For complex comments we still
            # prepare a suggested reply only
            # when a safe template exists.

            if analysis.category in {
                "positive",
                "thanks",
                "greeting",
                "question",
                "neutral",
            }:

                reply = (
                    self.generator.generate(
                        comment=comment,
                        creator_profile=(
                            self.creator_profile
                        ),
                        category=(
                            analysis.category
                        ),
                    )
                )

            status = "waiting_for_creator"

        # -------------------------------------
        # 4. Add to queue
        # -------------------------------------

        queued = self.queue.add(
            comment=comment,
            reply=reply,
            analysis=analysis_dict,
            status=status,
        )

        return {
            "success": True,
            "reply_id": queued["reply_id"],
            "comment": comment,
            "category": analysis.category,
            "sentiment": analysis.sentiment,
            "complexity": analysis.complexity,
            "confidence": analysis.confidence,
            "reply": reply,
            "status": status,
            "requires_permission": (
                status
                == "waiting_for_creator"
            ),
            "reason": permission["reason"],
        }

    # =========================================
    # APPROVE
    # =========================================

    def approve(
        self,
        reply_id: str,
    ) -> Dict[str, Any]:

        item = self.queue.get(
            reply_id
        )

        if item is None:
            return {
                "success": False,
                "error": "Reply not found.",
            }

        result = (
            self.permission_manager.approve(
                reply_id
            )
        )

        self.queue.approve(
            reply_id
        )

        return {
            "success": True,
            **result,
        }

    # =========================================
    # REJECT
    # =========================================

    def reject(
        self,
        reply_id: str,
    ) -> Dict[str, Any]:

        item = self.queue.get(
            reply_id
        )

        if item is None:
            return {
                "success": False,
                "error": "Reply not found.",
            }

        result = (
            self.permission_manager.reject(
                reply_id
            )
        )

        self.queue.reject(
            reply_id
        )

        return {
            "success": True,
            **result,
        }

    # =========================================
    # PENDING
    # =========================================

    def pending_replies(self):

        return self.queue.get_pending()

    # =========================================
    # ALL
    # =========================================

    def all_replies(self):

        return self.queue.get_all()