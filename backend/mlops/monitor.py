from __future__ import annotations

from datetime import datetime, timezone

from statistics import mean


from .config import (
    RETRAIN_MIN_SAMPLES,
    RETRAIN_COOLDOWN_SECONDS,
    DRIFT_THRESHOLD,
    PERFORMANCE_DROP_THRESHOLD,
    SNAPSHOTS_FILE,
)


from .store import (
    get_state,
    save_state,
    read_jsonl,
)


from .features import (
    build_training_rows,
    collect_snapshot,
)


from .model import (
    train_candidate,
)


# ============================================================
# TIME
# ============================================================

def _seconds_since(
    value
):

    if not value:

        return float(
            "inf"
        )


    try:

        then = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )


        return (

            datetime.now(
                timezone.utc
            )

            - then

        ).total_seconds()


    except Exception:

        return float(
            "inf"
        )


# ============================================================
# DATA DRIFT
# ============================================================

def _drift(
    rows
):

    if len(rows) < 10:

        return 0.0


    half = max(
        3,
        len(rows) // 2
    )


    old = rows[:-half]

    new = rows[-half:]


    values = [

        "views",

        "likes",

        "comments",

        "positive_rate",

        "negative_rate",

        "comment_rate",

        "pending_comments",

    ]


    scores = []


    for key in values:

        old_value = mean(

            [
                float(
                    item.get(
                        key,
                        0
                    )
                )

                for item
                in old

            ]

        )


        new_value = mean(

            [
                float(
                    item.get(
                        key,
                        0
                    )
                )

                for item
                in new

            ]

        )


        denominator = max(
            abs(old_value),
            1e-6
        )


        score = min(

            abs(
                new_value
                -
                old_value
            )
            /
            denominator,

            1.0

        )


        scores.append(
            score
        )


    return round(
        mean(scores),
        6
    )


# ============================================================
# CHECK RETRAINING
# ============================================================

def check_retraining_trigger():

    snapshots = read_jsonl(

        SNAPSHOTS_FILE,

        5000

    )


    rows = build_training_rows(
        snapshots
    )


    drift = _drift(
        snapshots
    )


    state = get_state()


    reason = None


    if len(rows) >= RETRAIN_MIN_SAMPLES:

        if drift >= DRIFT_THRESHOLD:

            reason = (
                f"data_drift:"
                f"{drift:.3f}"
            )


        else:

            production = (
                state.get(
                    "last_performance"
                )
                or {}
            )


            r2 = production.get(
                "r2"
            )


            if (
                r2 is not None
                and
                r2 < PERFORMANCE_DROP_THRESHOLD
            ):

                reason = (
                    "performance_gate:"
                    f"r2={r2:.3f}"
                )


    # --------------------------------------------------------
    # RETRAIN
    # --------------------------------------------------------

    if (

        reason

        and

        _seconds_since(
            state.get(
                "last_retrain_at"
            )
        )
        >=
        RETRAIN_COOLDOWN_SECONDS

    ):

        state[
            "last_trigger"
        ] = reason

        state[
            "last_drift"
        ] = drift

        state[
            "status"
        ] = "retraining"


        save_state(
            state
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
            "last_drift"
        ] = drift


        save_state(
            state
        )


        return {

            "triggered":
                True,

            "reason":
                reason,

            "candidate":
                candidate,

        }


    # --------------------------------------------------------
    # NORMAL
    # --------------------------------------------------------

    state[
        "last_drift"
    ] = drift


    if state.get(
        "status"
    ) == "retraining":

        state[
            "status"
        ] = "healthy"


    save_state(
        state
    )


    return {

        "triggered":
            False,

        "reason":
            reason,

        "training_rows":
            len(rows),

        "drift":
            drift,

        "status":
            state.get(
                "status",
                "healthy"
            ),

    }


# ============================================================
# COLLECT + MONITOR
# ============================================================

def collect_and_monitor():

    snapshot = (
        collect_snapshot()
    )


    state = get_state()


    state[
        "last_snapshot_at"
    ] = snapshot[
        "timestamp"
    ]


    save_state(
        state
    )


    result = (
        check_retraining_trigger()
    )


    return {

        "snapshot":
            snapshot,

        "monitor":
            result,

    }