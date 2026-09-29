from pathlib import Path
import csv

from mlops.store import read_jsonl

from mlops.config import (
    SNAPSHOTS_FILE,
    DATASET_DIR,
)

from mlops.features import (
    build_training_rows,
    FEATURE_NAMES,
)


snapshots = read_jsonl(
    SNAPSHOTS_FILE,
    10000
)


rows = build_training_rows(
    snapshots
)


DATASET_DIR.mkdir(
    parents=True,
    exist_ok=True
)


output = (
    DATASET_DIR /
    "engagement_training.csv"
)


fields = (
    FEATURE_NAMES
    +
    [
        "target_engagement",
        "timestamp"
    ]
)


with output.open(
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fields
    )

    writer.writeheader()

    writer.writerows(
        rows
    )


print(
    f"Wrote {len(rows)} "
    f"training rows to {output}"
)