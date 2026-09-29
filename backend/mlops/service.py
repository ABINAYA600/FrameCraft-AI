from __future__ import annotations

import uuid

from datetime import (
    datetime,
    timezone
)


from .config import (
    FEEDBACK_FILE,
    SNAPSHOTS_FILE,
)


from .store import (
    append_jsonl,
    read_jsonl,
    get_state,
    get_runs,
    get_candidate,
    save_state,
)


from .features import (
    build_training_rows,
)


from .model import (
    train_candidate,
)


from .monitor import (
    collect_and_monitor,
)


# ============================================================
# STATUS
# ============================================================

def status():

    snapshots = read_jsonl(
        SNAPSHOTS_FILE,
        5000
    )


    rows = build_training_rows(
        snapshots
    )


    return {

        "success":
            True,

        "state":
            get_state(),

        "candidate":
            get_candidate(),

        "runs":
            get_runs()[-20:],

        "snapshots":
            len(snapshots),

        "training_rows":
            len(rows),

    }


# ============================================================
# SNAPSHOT + MONITOR
# ============================================================

def snapshot_and_monitor():

    return collect_and_monitor()


# ============================================================
# MANUAL RETRAIN
# ============================================================

def manual_retrain(
    reason="manual"
):

    snapshots = read_jsonl(
        SNAPSHOTS_FILE,
        5000
    )


    rows = build_training_rows(
        snapshots
    )


    candidate = train_candidate(
        rows,
        reason=reason
    )


    state = get_state()


    state[
        "last_retrain_at"
    ] = datetime.now(
        timezone.utc
    ).isoformat()


    state[
        "status"
    ] = "candidate_ready"


    state[
        "candidate_version"
    ] = candidate[
        "version"
    ]


    save_state(
        state
    )


    return candidate


# ============================================================
# FEEDBACK
# ============================================================

def record_suggestion_feedback(

    suggestion: str,

    outcome: str,

    video_id: str | None = None,

    project_id: str | None = None,

    before_views: float | None = None,

    after_views: float | None = None,

    notes: str = "",

):

    row = {

        "id":
            f"feedback_{uuid.uuid4().hex[:12]}",

        "timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "suggestion":
            suggestion,

        "outcome":
            outcome,

        "video_id":
            video_id,

        "project_id":
            project_id,

        "before_views":
            before_views,

        "after_views":
            after_views,

        "notes":
            notes,

    }


    append_jsonl(
        FEEDBACK_FILE,
        row
    )


    return row