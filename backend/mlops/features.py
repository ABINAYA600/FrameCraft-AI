from __future__ import annotations

import json
import math
import uuid

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .config import (
    PROJECTS_DIR,
    OUTPUT_DIR,
)

from .store import append_jsonl


# ============================================================
# EXISTING FRAMECRAFT DATA
# ============================================================

COMMENT_FILE = (
    OUTPUT_DIR /
    "live_comment_events.json"
)

PUBLISHING_FILE = (
    OUTPUT_DIR /
    "publishing.json"
)


# ============================================================
# HELPERS
# ============================================================

def _read_json(
    path,
    default
):

    try:

        if not path.exists():
            return default

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return default


def _safe_number(
    value,
    default=0.0
):

    try:

        return float(value)

    except Exception:

        return default


# ============================================================
# PROJECTS
# ============================================================

def _projects():

    projects = []

    if not PROJECTS_DIR.exists():
        return projects

    for path in PROJECTS_DIR.glob(
        "*/project.json"
    ):

        try:

            project = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

            if isinstance(
                project,
                dict
            ):

                projects.append(
                    project
                )

        except Exception:

            pass

    return projects


# ============================================================
# COMMENTS
# ============================================================

def _comments():

    data = _read_json(
        COMMENT_FILE,
        []
    )

    return (
        data
        if isinstance(data, list)
        else []
    )


# ============================================================
# PUBLISHING
# ============================================================

def _posts():

    data = _read_json(
        PUBLISHING_FILE,
        []
    )

    return (
        data
        if isinstance(data, list)
        else []
    )


# ============================================================
# COLLECT ANALYTICS SNAPSHOT
# ============================================================

def collect_snapshot():

    projects = _projects()

    comments = _comments()

    posts = _posts()


    total_views = 0.0

    total_likes = 0.0

    total_videos = 0

    published_videos = 0


    # --------------------------------------------------------
    # PROJECT DATA
    # --------------------------------------------------------

    for project in projects:

        total_views += _safe_number(
            project.get("views")
        )

        total_likes += _safe_number(
            project.get("likes")
        )


        generated = (
            project.get("generated")
            or
            project.get("generated_videos")
            or
            []
        )

        videos = (
            project.get("videos")
            or
            []
        )


        if isinstance(
            generated,
            list
        ):

            total_videos += len(
                generated
            )


        if isinstance(
            videos,
            list
        ):

            for video in videos:

                total_views += _safe_number(
                    video.get("views")
                )

                total_likes += _safe_number(
                    video.get("likes")
                )


        published_videos += sum(

            1

            for post in posts

            if (
                post.get("project_id")
                == project.get("id")
            )

            and
            (
                str(
                    post.get(
                        "status",
                        ""
                    )
                ).lower()
                == "published"
            )

        )


    # --------------------------------------------------------
    # COMMENT ANALYSIS
    # --------------------------------------------------------

    sentiments = Counter()

    categories = Counter()


    for event in comments:

        analysis = (
            event.get("analysis")
            or {}
        )


        if isinstance(
            analysis,
            dict
        ):

            sentiment = str(
                analysis.get(
                    "sentiment",
                    "neutral"
                )
            ).lower()


            category = str(
                analysis.get(
                    "category",
                    "unknown"
                )
            ).lower()


            sentiments[
                sentiment
            ] += 1


            categories[
                category
            ] += 1


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    total_comments = sum(
        sentiments.values()
    )


    positive = sentiments.get(
        "positive",
        0
    )

    negative = sentiments.get(
        "negative",
        0
    )

    neutral = sentiments.get(
        "neutral",
        0
    )


    positive_rate = (

        positive /
        total_comments

        if total_comments

        else 0.0

    )


    negative_rate = (

        negative /
        total_comments

        if total_comments

        else 0.0

    )


    comment_rate = (

        total_comments /
        max(total_views, 1.0)

    )


    # --------------------------------------------------------
    # ENGAGEMENT SCORE
    # --------------------------------------------------------

    engagement_score = (

        0.50 *
        min(
            math.log1p(
                total_views
            ) / 12.0,
            1.0
        )

        +

        0.30 *
        min(
            math.log1p(
                total_comments
            ) / 8.0,
            1.0
        )

        +

        0.20 *
        positive_rate

    )


    # --------------------------------------------------------
    # SNAPSHOT
    # --------------------------------------------------------

    now = datetime.now(
        timezone.utc
    ).isoformat()


    snapshot = {

        "id":
            f"snapshot_{uuid.uuid4().hex[:12]}",

        "timestamp":
            now,

        "projects":
            len(projects),

        "videos_generated":
            total_videos,

        "published_videos":
            published_videos,

        "views":
            total_views,

        "likes":
            total_likes,

        "comments":
            total_comments,

        "positive_comments":
            positive,

        "negative_comments":
            negative,

        "neutral_comments":
            neutral,

        "positive_rate":
            round(
                positive_rate,
                6
            ),

        "negative_rate":
            round(
                negative_rate,
                6
            ),

        "comment_rate":
            round(
                comment_rate,
                8
            ),

        "category_count":
            len(categories),

        "pending_comments":
            sum(

                1

                for event
                in comments

                if event.get(
                    "reply_source"
                )
                in (
                    None,
                    "pending"
                )

            ),

        "engagement_score":
            round(
                engagement_score,
                6
            ),

    }


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    append_jsonl(
        OUTPUT_DIR /
        "mlops" /
        "analytics_snapshots.jsonl",

        snapshot
    )


    return snapshot


# ============================================================
# TRAINING ROWS
# ============================================================

def build_training_rows(
    snapshots
):

    rows = []

    ordered = sorted(
        snapshots,
        key=lambda x:
            x.get(
                "timestamp",
                ""
            )
    )


    # Current snapshot predicts
    # next snapshot's engagement.

    for current, future in zip(
        ordered,
        ordered[1:]
    ):

        rows.append({

            "views":
                _safe_number(
                    current.get(
                        "views"
                    )
                ),

            "likes":
                _safe_number(
                    current.get(
                        "likes"
                    )
                ),

            "comments":
                _safe_number(
                    current.get(
                        "comments"
                    )
                ),

            "positive_rate":
                _safe_number(
                    current.get(
                        "positive_rate"
                    )
                ),

            "negative_rate":
                _safe_number(
                    current.get(
                        "negative_rate"
                    )
                ),

            "comment_rate":
                _safe_number(
                    current.get(
                        "comment_rate"
                    )
                ),

            "published_videos":
                _safe_number(
                    current.get(
                        "published_videos"
                    )
                ),

            "pending_comments":
                _safe_number(
                    current.get(
                        "pending_comments"
                    )
                ),

            "target_engagement":
                _safe_number(
                    future.get(
                        "engagement_score"
                    )
                ),

            "timestamp":
                future.get(
                    "timestamp"
                ),

        })


    return rows


# ============================================================
# FEATURE NAMES
# ============================================================

FEATURE_NAMES = [

    "views",

    "likes",

    "comments",

    "positive_rate",

    "negative_rate",

    "comment_rate",

    "published_videos",

    "pending_comments",

]


def current_feature_vector(
    snapshot
):

    return [

        _safe_number(
            snapshot.get(
                name
            )
        )

        for name
        in FEATURE_NAMES

    ]