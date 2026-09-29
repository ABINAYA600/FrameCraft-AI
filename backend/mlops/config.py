from pathlib import Path
import os


# ============================================================
# FRAMECRAFT MLOPS PATHS
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = BACKEND_DIR / "output"
PROJECTS_DIR = BACKEND_DIR / "projects"

MLOPS_DIR = OUTPUT_DIR / "mlops"
DATASET_DIR = MLOPS_DIR / "datasets"
MODEL_DIR = MLOPS_DIR / "models"
ARTIFACT_DIR = MLOPS_DIR / "artifacts"


for directory in (
    MLOPS_DIR,
    DATASET_DIR,
    MODEL_DIR,
    ARTIFACT_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# STORAGE FILES
# ============================================================

SNAPSHOTS_FILE = MLOPS_DIR / "analytics_snapshots.jsonl"

FEEDBACK_FILE = MLOPS_DIR / "suggestion_feedback.jsonl"

RUNS_FILE = MLOPS_DIR / "training_runs.json"

STATE_FILE = MLOPS_DIR / "state.json"

CANDIDATE_FILE = MLOPS_DIR / "candidate.json"


# ============================================================
# MLFLOW
# ============================================================

EXPERIMENT_NAME = os.getenv(
    "FRAMECRAFT_MLFLOW_EXPERIMENT",
    "FrameCraft-MLOps"
)


# ============================================================
# RETRAINING CONFIGURATION
# ============================================================

RETRAIN_MIN_SAMPLES = int(
    os.getenv(
        "FRAMECRAFT_RETRAIN_MIN_SAMPLES",
        "20"
    )
)

RETRAIN_COOLDOWN_SECONDS = int(
    os.getenv(
        "FRAMECRAFT_RETRAIN_COOLDOWN",
        "3600"
    )
)

DRIFT_THRESHOLD = float(
    os.getenv(
        "FRAMECRAFT_DRIFT_THRESHOLD",
        "0.20"
    )
)

PERFORMANCE_DROP_THRESHOLD = float(
    os.getenv(
        "FRAMECRAFT_PERFORMANCE_DROP",
        "0.10"
    )
)


# ============================================================
# LIVE MONITORING
# ============================================================

MONITOR_INTERVAL_SECONDS = int(
    os.getenv(
        "FRAMECRAFT_MLOPS_INTERVAL",
        "300"
    )
)