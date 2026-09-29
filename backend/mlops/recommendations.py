from .features import collect_snapshot
from .model import predict


def build_suggestions(
    snapshot,
    prediction
):

    suggestions = []


    views = float(
        snapshot.get(
            "views",
            0
        )
    )


    comments = float(
        snapshot.get(
            "comments",
            0
        )
    )


    positive_rate = float(
        snapshot.get(
            "positive_rate",
            0
        )
    )


    negative_rate = float(
        snapshot.get(
            "negative_rate",
            0
        )
    )


    comment_rate = float(
        snapshot.get(
            "comment_rate",
            0
        )
    )


    # ========================================================
    # LOW COMMENT RATE
    # ========================================================

    if (
        views > 0
        and
        comment_rate < 0.001
    ):

        suggestions.append({

            "type":
                "engagement",

            "priority":
                "high",

            "title":
                "Increase audience interaction",

            "reason":
                "Views are present but "
                "the comment rate is low.",

            "action":
                "Add a clear question or "
                "call-to-action near the "
                "end of the next video."

        })


    # ========================================================
    # NEGATIVE SENTIMENT
    # ========================================================

    if (
        comments >= 10
        and
        positive_rate < 0.50
    ):

        suggestions.append({

            "type":
                "sentiment",

            "priority":
                "high",

            "title":
                "Address negative audience signals",

            "reason":
                "Less than half of analyzed "
                "comments are positive.",

            "action":
                "Review recurring complaints "
                "and clarify the next video's "
                "explanation or examples."

        })


    # ========================================================
    # HIGH NEGATIVE RATE
    # ========================================================

    if negative_rate >= 0.25:

        suggestions.append({

            "type":
                "content_quality",

            "priority":
                "high",

            "title":
                "Investigate recurring negative feedback",

            "reason":
                "Negative comments are a "
                "significant share of analyzed feedback.",

            "action":
                "Group negative comments by "
                "category and address the most "
                "frequent issue."

        })


    # ========================================================
    # POSITIVE AUDIENCE
    # ========================================================

    if (
        comments >= 20
        and
        positive_rate >= 0.70
    ):

        suggestions.append({

            "type":
                "content_strategy",

            "priority":
                "medium",

            "title":
                "Repeat successful content patterns",

            "reason":
                "Audience sentiment is strongly positive.",

            "action":
                "Reuse the topic, structure or "
                "presentation pattern that generated "
                "this response."

        })


    # ========================================================
    # MODEL PREDICTION
    # ========================================================

    if prediction.get(
        "available"
    ):

        predicted = float(
            prediction[
                "predicted_engagement"
            ]
        )


        if predicted < 0.40:

            suggestions.append({

                "type":
                    "model",

                "priority":
                    "medium",

                "title":
                    "Test a stronger hook",

                "reason":
                    (
                        "The current model predicts "
                        "a relatively low next-period "
                        f"engagement score ({predicted:.3f})."
                    ),

                "action":
                    "Test a shorter opening, clearer "
                    "value proposition and stronger "
                    "first 5–10 seconds."

            })


    # ========================================================
    # DEFAULT
    # ========================================================

    if not suggestions:

        suggestions.append({

            "type":
                "monitoring",

            "priority":
                "low",

            "title":
                "Continue collecting feedback",

            "reason":
                "There is not enough evidence "
                "for a strong intervention.",

            "action":
                "Keep publishing and collecting "
                "views, comments and audience sentiment."

        })


    return suggestions


def get_live_suggestions():

    snapshot = (
        collect_snapshot()
    )


    prediction = predict(
        snapshot
    )


    return {

        "success":
            True,

        "snapshot":
            snapshot,

        "prediction":
            prediction,

        "suggestions":
            build_suggestions(
                snapshot,
                prediction
            ),

    }