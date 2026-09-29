from __future__ import annotations

from datetime import datetime, timezone

import joblib
import numpy as np

from sklearn.ensemble import (
    RandomForestRegressor
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from sklearn.model_selection import (
    train_test_split
)


from .config import (
    MODEL_DIR,
    EXPERIMENT_NAME,
)

from .features import (
    FEATURE_NAMES,
    current_feature_vector,
)

from .store import (
    get_runs,
    save_runs,
    save_candidate,
    get_state,
    save_state,
)


try:

    import mlflow

    import mlflow.sklearn

except Exception:

    mlflow = None


# ============================================================
# MODEL PATH
# ============================================================

def _model_path(
    version
):

    return (
        MODEL_DIR /
        f"{version}.joblib"
    )


# ============================================================
# MLFLOW
# ============================================================

def _mlflow_setup():

    if mlflow is None:
        return None

    try:

        mlflow.set_experiment(
            EXPERIMENT_NAME
        )

        return mlflow

    except Exception:

        return None


# ============================================================
# TRAIN
# ============================================================

def train_candidate(
    rows,
    reason="manual"
):

    if len(rows) < 10:

        raise ValueError(
            "Need at least 10 sequential "
            "training rows."
        )


    X = np.array(

        [
            [
                row[name]
                for name
                in FEATURE_NAMES
            ]

            for row
            in rows
        ],

        dtype=float

    )


    y = np.array(

        [
            row[
                "target_engagement"
            ]

            for row
            in rows
        ],

        dtype=float

    )


    if len(
        set(
            y.tolist()
        )
    ) < 2:

        raise ValueError(
            "Training target has no "
            "variation yet."
        )


    test_size = max(
        2,
        int(
            round(
                len(rows) * 0.2
            )
        )
    )


    if test_size >= len(rows):

        test_size = 2


    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=42
        )
    )


    model = RandomForestRegressor(

        n_estimators=250,

        max_depth=8,

        min_samples_leaf=2,

        random_state=42,

        n_jobs=-1,

    )


    # --------------------------------------------------------
    # MLFLOW
    # --------------------------------------------------------

    with_mlflow = (
        _mlflow_setup()
    )


    run_ctx = (
        with_mlflow.start_run()
        if with_mlflow
        else None
    )


    run_id = None


    try:

        if run_ctx:

            with run_ctx:

                model.fit(
                    X_train,
                    y_train
                )


                predictions = (
                    model.predict(
                        X_test
                    )
                )


                metrics = _metrics(
                    y_test,
                    predictions
                )


                with_mlflow.log_params({

                    "n_estimators":
                        250,

                    "max_depth":
                        8,

                    "min_samples_leaf":
                        2,

                    "training_rows":
                        len(rows),

                    "reason":
                        reason,

                })


                with_mlflow.log_metrics(
                    metrics
                )


        else:

            model.fit(
                X_train,
                y_train
            )


            predictions = (
                model.predict(
                    X_test
                )
            )


            metrics = _metrics(
                y_test,
                predictions
            )


    finally:

        if run_ctx:

            run_id = (
                run_ctx.info.run_id
            )


    # --------------------------------------------------------
    # VERSION
    # --------------------------------------------------------

    version = (
        "engagement-"
        +
        datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d%H%M%S"
        )
    )


    path = _model_path(
        version
    )


    joblib.dump(

        {

            "model":
                model,

            "version":
                version,

            "features":
                FEATURE_NAMES,

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "metrics":
                metrics,

        },

        path

    )


    # --------------------------------------------------------
    # FEATURE IMPORTANCE
    # --------------------------------------------------------

    feature_importance = dict(

        zip(

            FEATURE_NAMES,

            model.feature_importances_
            .round(6)
            .tolist()

        )

    )


    # --------------------------------------------------------
    # RUN RECORD
    # --------------------------------------------------------

    record = {

        "version":
            version,

        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "status":
            "candidate",

        "reason":
            reason,

        "training_rows":
            len(rows),

        "metrics":
            metrics,

        "feature_importance":
            feature_importance,

        "mlflow_run_id":
            run_id,

        "model_path":
            str(path),

    }


    runs = get_runs()

    runs.append(
        record
    )

    save_runs(
        runs
    )


    save_candidate(
        record
    )


    state = get_state()

    state[
        "candidate_version"
    ] = version

    state[
        "last_performance"
    ] = metrics

    save_state(
        state
    )


    return record


# ============================================================
# METRICS
# ============================================================

def _metrics(
    y_true,
    predictions
):

    rmse = float(

        np.sqrt(

            mean_squared_error(
                y_true,
                predictions
            )

        )

    )


    return {

        "mae":
            round(
                float(
                    mean_absolute_error(
                        y_true,
                        predictions
                    )
                ),
                6
            ),

        "rmse":
            round(
                rmse,
                6
            ),

        "r2":
            round(
                float(
                    r2_score(
                        y_true,
                        predictions
                    )
                ),
                6
            ),

    }


# ============================================================
# LOAD MODEL
# ============================================================

def load_model(
    version
):

    path = _model_path(
        version
    )


    if not path.exists():

        raise FileNotFoundError(
            f"Model version not found: {version}"
        )


    return joblib.load(
        path
    )


# ============================================================
# PREDICTION
# ============================================================

def predict(
    snapshot,
    version=None
):

    state = get_state()


    version = (
        version
        or
        state.get(
            "production_version"
        )
    )


    if not version:

        return {

            "available":
                False,

            "reason":
                "No production model "
                "has been approved yet.",

        }


    artifact = load_model(
        version
    )


    value = float(

        artifact[
            "model"
        ].predict(

            np.array(

                [
                    current_feature_vector(
                        snapshot
                    )
                ],

                dtype=float

            )

        )[0]

    )


    return {

        "available":
            True,

        "model_version":
            version,

        "predicted_engagement":
            round(
                value,
                6
            ),

    }


# ============================================================
# APPROVE
# ============================================================

def approve_candidate(
    version=None
):

    state = get_state()

    candidate = None


    if version:

        for item in get_runs():

            if item.get(
                "version"
            ) == version:

                candidate = item

                break


    else:

        candidate = (

            state.get(
                "candidate_version"
            )

            and

            next(

                (
                    x

                    for x
                    in get_runs()

                    if x.get(
                        "version"
                    )
                    ==
                    state[
                        "candidate_version"
                    ]

                ),

                None

            )

        )


    if not candidate:

        raise ValueError(
            "No candidate model "
            "is available."
        )


    if not _model_path(
        candidate[
            "version"
        ]
    ).exists():

        raise ValueError(
            "Candidate model artifact "
            "is missing."
        )


    old = state.get(
        "production_version"
    )


    state[
        "production_version"
    ] = candidate[
        "version"
    ]


    state[
        "candidate_version"
    ] = None


    state[
        "status"
    ] = "healthy"


    state[
        "approved_at"
    ] = datetime.now(
        timezone.utc
    ).isoformat()


    state[
        "previous_production_version"
    ] = old


    save_state(
        state
    )


    runs = get_runs()


    for item in runs:

        if item.get(
            "version"
        ) == candidate[
            "version"
        ]:

            item[
                "status"
            ] = "production"


        elif item.get(
            "status"
        ) == "production":

            item[
                "status"
            ] = "archived"


    save_runs(
        runs
    )


    return {

        "approved":
            True,

        "production_version":
            candidate[
                "version"
            ],

        "previous_production_version":
            old,

    }


# ============================================================
# REJECT
# ============================================================

def reject_candidate(
    version=None
):

    state = get_state()


    target = (

        version

        or

        state.get(
            "candidate_version"
        )

    )


    if not target:

        raise ValueError(
            "No candidate model "
            "is available."
        )


    runs = get_runs()


    for item in runs:

        if item.get(
            "version"
        ) == target:

            item[
                "status"
            ] = "rejected"


    save_runs(
        runs
    )


    if (
        state.get(
            "candidate_version"
        )
        ==
        target
    ):

        state[
            "candidate_version"
        ] = None

        state[
            "status"
        ] = "healthy"

        save_state(
            state
        )


    return {

        "rejected":
            True,

        "version":
            target,

    }