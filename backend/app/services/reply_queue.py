from typing import Dict, Any, List
from datetime import datetime
import uuid


class ReplyQueue:
    """
    In-memory reply queue.

    Later this can be replaced with Redis,
    PostgreSQL, MongoDB, Celery, etc.
    """

    def __init__(self):
        self.queue: List[Dict[str, Any]] = []

        print("Reply Queue Initialized!")

    # =========================================
    # ADD
    # =========================================

    def add(
        self,
        comment: str,
        reply: str,
        analysis: Dict[str, Any],
        status: str,
    ) -> Dict[str, Any]:

        reply_id = str(
            uuid.uuid4()
        )

        item = {
            "reply_id": reply_id,
            "comment": comment,
            "reply": reply,
            "analysis": analysis,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        self.queue.append(item)

        return item

    # =========================================
    # GET ALL
    # =========================================

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self.queue)

    # =========================================
    # GET PENDING
    # =========================================

    def get_pending(self) -> List[Dict[str, Any]]:

        return [
            item
            for item in self.queue
            if item["status"]
            == "waiting_for_creator"
        ]

    # =========================================
    # FIND
    # =========================================

    def get(
        self,
        reply_id: str,
    ) -> Dict[str, Any] | None:

        for item in self.queue:

            if item["reply_id"] == reply_id:
                return item

        return None

    # =========================================
    # UPDATE
    # =========================================

    def update_status(
        self,
        reply_id: str,
        status: str,
    ) -> Dict[str, Any] | None:

        item = self.get(reply_id)

        if item is None:
            return None

        item["status"] = status
        item["updated_at"] = (
            datetime.now().isoformat()
        )

        return item

    # =========================================
    # APPROVE
    # =========================================

    def approve(
        self,
        reply_id: str,
    ) -> Dict[str, Any] | None:

        return self.update_status(
            reply_id,
            "approved",
        )

    # =========================================
    # REJECT
    # =========================================

    def reject(
        self,
        reply_id: str,
    ) -> Dict[str, Any] | None:

        return self.update_status(
            reply_id,
            "rejected",
        )