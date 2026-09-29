import json
from pathlib import Path
from typing import Any

from .config import (
    SNAPSHOTS_FILE,
    FEEDBACK_FILE,
    RUNS_FILE,
    STATE_FILE,
    CANDIDATE_FILE,
)


# ============================================================
# JSON
# ============================================================

def read_json(path: Path, default):

    if not path.exists():
        return default

    try:

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return default


def write_json(path: Path, value):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_file = path.with_suffix(
        path.suffix + ".tmp"
    )

    temporary_file.write_text(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            default=str
        ),
        encoding="utf-8"
    )

    temporary_file.replace(path)


# ============================================================
# JSONL
# ============================================================

def append_jsonl(
    path: Path,
    value: dict[str, Any]
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with path.open(
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            json.dumps(
                value,
                ensure_ascii=False,
                default=str
            )
            + "\n"
        )


def read_jsonl(
    path: Path,
    limit: int = 10000
):

    if not path.exists():
        return []

    rows = []

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            if not line.strip():
                continue

            try:

                rows.append(
                    json.loads(line)
                )

            except Exception:

                continue

    return rows[-limit:]


# ============================================================
# TRAINING RUNS
# ============================================================

def get_runs():

    return read_json(
        RUNS_FILE,
        []
    )


def save_runs(runs):

    write_json(
        RUNS_FILE,
        runs[-200:]
    )


# ============================================================
# MLOPS STATE
# ============================================================

def get_state():

    return read_json(
        STATE_FILE,
        {
            "production_version": None,
            "candidate_version": None,
            "last_retrain_at": None,
            "last_snapshot_at": None,
            "last_trigger": None,
            "last_drift": 0.0,
            "last_performance": None,
            "status": "healthy",
        }
    )


def save_state(state):

    write_json(
        STATE_FILE,
        state
    )


# ============================================================
# CANDIDATE MODEL
# ============================================================

def get_candidate():

    return read_json(
        CANDIDATE_FILE,
        None
    )


def save_candidate(candidate):

    write_json(
        CANDIDATE_FILE,
        candidate
    )


def clear_candidate():

    if CANDIDATE_FILE.exists():
        CANDIDATE_FILE.unlink()