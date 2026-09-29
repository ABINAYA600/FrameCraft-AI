from fastapi import (
    APIRouter,
    HTTPException
)

from pydantic import BaseModel


from .service import (
    status,
    snapshot_and_monitor,
    manual_retrain,
    record_suggestion_feedback,
)


from .model import (
    approve_candidate,
    reject_candidate,
    predict,
)


from .features import (
    collect_snapshot,
)


from .recommendations import (
    get_live_suggestions,
)


router = APIRouter(
    prefix="/mlops",
    tags=["MLOps"]
)


# ============================================================
# REQUEST MODELS
# ============================================================

class RetrainRequest(
    BaseModel
):

    reason: str = "manual"


class DecisionRequest(
    BaseModel
):

    version: str | None = None


class SuggestionFeedbackRequest(
    BaseModel
):

    suggestion: str

    outcome: str

    video_id: str | None = None

    project_id: str | None = None

    before_views: float | None = None

    after_views: float | None = None

    notes: str = ""


# ============================================================
# STATUS
# ============================================================

@router.get(
    "/status"
)
def mlops_status():

    return status()


# ============================================================
# SNAPSHOT
# ============================================================

@router.post(
    "/snapshot"
)
def mlops_snapshot():

    try:

        return snapshot_and_monitor()

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "MLOps snapshot failed: "
                f"{error}"
            )

        )


# ============================================================
# RETRAIN
# ============================================================

@router.post(
    "/retrain"
)
def mlops_retrain(
    request: RetrainRequest
):

    try:

        return {

            "success":
                True,

            "candidate":
                manual_retrain(
                    request.reason
                ),

        }

    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error)

        )

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "Retraining failed: "
                f"{error}"
            )

        )


# ============================================================
# APPROVE
# ============================================================

@router.post(
    "/approve"
)
def mlops_approve(
    request: DecisionRequest
):

    try:

        return {

            "success":
                True,

            **approve_candidate(
                request.version
            ),

        }

    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error)

        )

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "Approval failed: "
                f"{error}"
            )

        )


# ============================================================
# REJECT
# ============================================================

@router.post(
    "/reject"
)
def mlops_reject(
    request: DecisionRequest
):

    try:

        return {

            "success":
                True,

            **reject_candidate(
                request.version
            ),

        }

    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error)

        )

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "Rejection failed: "
                f"{error}"
            )

        )


# ============================================================
# PREDICTION
# ============================================================

@router.get(
    "/predict"
)
def mlops_predict():

    try:

        snapshot = (
            collect_snapshot()
        )


        return {

            "success":
                True,

            **predict(
                snapshot
            ),

        }

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "Prediction failed: "
                f"{error}"
            )

        )


# ============================================================
# LIVE SUGGESTIONS
# ============================================================

@router.get(
    "/suggestions"
)
def mlops_suggestions():

    try:

        return get_live_suggestions()

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "Suggestion generation failed: "
                f"{error}"
            )

        )


# ============================================================
# SUGGESTION FEEDBACK
# ============================================================

@router.post(
    "/feedback"
)
def mlops_feedback(
    request: SuggestionFeedbackRequest
):

    try:

        return {

            "success":
                True,

            "feedback":
                record_suggestion_feedback(

                    suggestion=
                        request.suggestion,

                    outcome=
                        request.outcome,

                    video_id=
                        request.video_id,

                    project_id=
                        request.project_id,

                    before_views=
                        request.before_views,

                    after_views=
                        request.after_views,

                    notes=
                        request.notes,

                ),

        }

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "Feedback save failed: "
                f"{error}"
            )

        )