"""
FrameCraft AI - YouTube Publisher

Responsible for:
- Uploading an existing FrameCraft MP4 to YouTube.
- Publishing immediately.
- Uploading and scheduling a video for a future YouTube publish time.
- Reading the status of an uploaded YouTube video.

OAuth/account connection is handled by youtube_service.py.
This module only consumes the saved OAuth connection produced by that service.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


# ------------------------------------------------------------------
# Environment
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


YOUTUBE_CONNECTIONS_FILE = (
    BASE_DIR / "data" / "youtube_connections.json"
)

DEFAULT_TOKEN_URI = "https://oauth2.googleapis.com/token"

YOUTUBE_UPLOAD_SCOPE = (
    "https://www.googleapis.com/auth/youtube.upload"
)

YOUTUBE_READONLY_SCOPE = (
    "https://www.googleapis.com/auth/youtube.readonly"
)

YOUTUBE_FORCE_SSL_SCOPE = (
    "https://www.googleapis.com/auth/youtube.force-ssl"
)


# ------------------------------------------------------------------
# Generic helpers
# ------------------------------------------------------------------

def _load_connections() -> dict:
    if not YOUTUBE_CONNECTIONS_FILE.exists():
        raise RuntimeError(
            "YouTube connection file was not found: "
            f"{YOUTUBE_CONNECTIONS_FILE}"
        )

    try:
        with YOUTUBE_CONNECTIONS_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except Exception as error:
        raise RuntimeError(
            "Could not read YouTube connection data: "
            f"{error}"
        ) from error

    if not isinstance(data, dict):
        raise RuntimeError(
            "YouTube connection data must be a JSON object."
        )

    return data


def _save_connections(data: dict) -> None:
    YOUTUBE_CONNECTIONS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = YOUTUBE_CONNECTIONS_FILE.with_suffix(
        ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary.replace(
        YOUTUBE_CONNECTIONS_FILE
    )


def _looks_like_credentials(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    keys = set(value.keys())

    credential_keys = {
        "token",
        "access_token",
        "refresh_token",
        "token_uri",
        "client_id",
        "client_secret",
    }

    return bool(keys.intersection(credential_keys))


def _find_user_connection(
    data: dict,
    user_id: str,
) -> tuple[dict, dict]:
    """
    Return:
        (connection_container, credential_dict)

    Supports the common structures used by the FrameCraft OAuth service,
    including:

    {
        "demo_user": {
            "credentials": {...}
        }
    }

    and:

    {
        "users": {
            "demo_user": {
                "credentials": {...}
            }
        }
    }

    and structures where the credential fields are directly under the
    user record.
    """

    def search(
        node: Any,
        parent: dict | None = None,
        key: str | None = None,
    ):
        if isinstance(node, dict):

            # Direct user-id match.
            if key == user_id:

                if _looks_like_credentials(node):
                    return node, node

                credentials = node.get(
                    "credentials"
                )

                if isinstance(
                    credentials,
                    dict,
                ):
                    return node, credentials

                token_data = node.get(
                    "token"
                )

                if isinstance(
                    token_data,
                    dict,
                ) and _looks_like_credentials(
                    token_data
                ):
                    return node, token_data

            # Search children.
            for child_key, child_value in node.items():

                result = search(
                    child_value,
                    node,
                    child_key,
                )

                if result is not None:
                    return result

        elif isinstance(node, list):

            for item in node:
                result = search(
                    item,
                    parent,
                    key,
                )

                if result is not None:
                    return result

        return None

    result = search(data)

    if result is None:
        raise RuntimeError(
            f"No YouTube OAuth connection found for user '{user_id}'. "
            "Connect the YouTube account first."
        )

    return result


def _credential_value(
    credentials: dict,
    *names: str,
):
    for name in names:
        value = credentials.get(name)

        if value not in (
            None,
            "",
        ):
            return value

    return None


def _build_credentials(
    user_id: str,
) -> tuple[Credentials, dict, dict]:
    connections = _load_connections()

    connection, stored = _find_user_connection(
        connections,
        user_id,
    )

    client_id = (
        _credential_value(
            stored,
            "client_id",
        )
        or _credential_value(
            connection,
            "client_id",
        )
        or os.getenv(
            "GOOGLE_CLIENT_ID"
        )
    )

    client_secret = (
        _credential_value(
            stored,
            "client_secret",
        )
        or _credential_value(
            connection,
            "client_secret",
        )
        or os.getenv(
            "GOOGLE_CLIENT_SECRET"
        )
    )

    refresh_token = (
        _credential_value(
            stored,
            "refresh_token",
        )
        or _credential_value(
            connection,
            "refresh_token",
        )
    )

    access_token = (
        _credential_value(
            stored,
            "token",
        )
        or _credential_value(
            stored,
            "access_token",
        )
        or _credential_value(
            connection,
            "token",
        )
        or _credential_value(
            connection,
            "access_token",
        )
    )

    token_uri = (
        _credential_value(
            stored,
            "token_uri",
        )
        or _credential_value(
            connection,
            "token_uri",
        )
        or DEFAULT_TOKEN_URI
    )

    scopes = (
        _credential_value(
            stored,
            "scopes",
        )
        or _credential_value(
            connection,
            "scopes",
        )
        or [
            YOUTUBE_UPLOAD_SCOPE,
            YOUTUBE_READONLY_SCOPE,
            YOUTUBE_FORCE_SSL_SCOPE,
        ]
    )

    expiry = (
        _credential_value(
            stored,
            "expiry",
        )
        or _credential_value(
            connection,
            "expiry",
        )
    )

    if not client_id:
        raise RuntimeError(
            "GOOGLE_CLIENT_ID is missing."
        )

    if not client_secret:
        raise RuntimeError(
            "GOOGLE_CLIENT_SECRET is missing."
        )

    if not refresh_token and not access_token:
        raise RuntimeError(
            "No YouTube OAuth token was found for this user. "
            "Reconnect the YouTube account."
        )

    credentials = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes,
    )

    if expiry:
        try:
            credentials.expiry = datetime.fromisoformat(
                str(expiry).replace(
                    "Z",
                    "+00:00",
                )
            )
        except Exception:
            pass

    if not credentials.valid:

        if credentials.expired and credentials.refresh_token:

            credentials.refresh(
                Request()
            )

        elif not credentials.token:

            raise RuntimeError(
                "YouTube OAuth credentials are invalid. "
                "Reconnect the YouTube account."
            )

    # Persist refreshed token/expiry where possible.
    changed = False

    if credentials.token:
        if stored.get("token") != credentials.token:
            stored["token"] = credentials.token
            changed = True

    if credentials.expiry:
        expiry_string = (
            credentials.expiry.astimezone(
                timezone.utc
            ).isoformat()
        )

        if stored.get("expiry") != expiry_string:
            stored["expiry"] = expiry_string
            changed = True

    if changed:
        try:
            _save_connections(
                connections
            )
        except Exception:
            # Token persistence is helpful but must not prevent a valid
            # upload from succeeding.
            pass

    return (
        credentials,
        connection,
        stored,
    )


def _youtube_client(
    user_id: str,
):
    credentials, connection, stored = (
        _build_credentials(user_id)
    )

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials,
        cache_discovery=False,
    )

    return (
        youtube,
        connection,
        stored,
    )


def _validate_video_file(
    video_path: str | Path,
) -> Path:

    path = Path(
        video_path
    ).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"Video file does not exist: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Video path is not a file: {path}"
        )

    if path.suffix.lower() != ".mp4":
        raise ValueError(
            "Only MP4 files are supported for YouTube publishing."
        )

    if path.stat().st_size <= 0:
        raise ValueError(
            f"Video file is empty: {path}"
        )

    return path


def _clean_tags(
    tags: list[str] | None,
) -> list[str]:

    if not tags:
        return []

    cleaned = []

    for tag in tags:

        value = str(tag).strip()

        if not value:
            continue

        if value not in cleaned:
            cleaned.append(value)

    return cleaned[:500]


def _validate_scheduled_at(
    scheduled_at: str,
) -> datetime:

    if not scheduled_at:
        raise ValueError(
            "scheduled_at is required."
        )

    value = scheduled_at.strip()

    try:
        parsed = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )
    except ValueError as error:
        raise ValueError(
            "scheduled_at must be a valid ISO-8601 datetime."
        ) from error

    if parsed.tzinfo is None:
        raise ValueError(
            "scheduled_at must include timezone information."
        )

    parsed = parsed.astimezone(
        timezone.utc
    )

    if parsed <= datetime.now(
        timezone.utc
    ):
        raise ValueError(
            "scheduled_at must be in the future."
        )

    return parsed


def _youtube_url(
    video_id: str,
) -> str:

    return (
        "https://www.youtube.com/watch?v="
        f"{video_id}"
    )


# ------------------------------------------------------------------
# Public publishing functions
# ------------------------------------------------------------------

def publish_video_now(
    *,
    user_id: str,
    video_path: str | Path,
    title: str,
    description: str = "",
    tags: list[str] | None = None,
    category_id: str = "22",
) -> dict:

    path = _validate_video_file(
        video_path
    )

    title = title.strip()

    if not title:
        raise ValueError(
            "YouTube title cannot be empty."
        )

    if len(title) > 100:
        raise ValueError(
            "YouTube title must be 100 characters or fewer."
        )

    youtube, _, _ = _youtube_client(
        user_id
    )

    body = {
        "snippet": {
            "title": title,
            "description": description or "",
            "tags": _clean_tags(tags),
            "categoryId": str(
                category_id or "22"
            ),
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=8 * 1024 * 1024,
    )

    try:

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = request.execute()

    except HttpError as error:

        raise RuntimeError(
            "YouTube upload failed: "
            f"{error}"
        ) from error

    video_id = response.get(
        "id"
    )

    if not video_id:
        raise RuntimeError(
            "YouTube upload completed without returning a video ID."
        )

    return {
        "success": True,
        "video_id": video_id,
        "video_url": _youtube_url(
            video_id
        ),
        "privacy_status": (
            response.get("status", {})
            .get("privacyStatus")
        ),
        "publish_at": (
            response.get("status", {})
            .get("publishAt")
        ),
        "title": (
            response.get("snippet", {})
            .get("title", title)
        ),
    }


def schedule_video(
    *,
    user_id: str,
    video_path: str | Path,
    title: str,
    scheduled_at: str,
    description: str = "",
    tags: list[str] | None = None,
    category_id: str = "22",
) -> dict:

    path = _validate_video_file(
        video_path
    )

    title = title.strip()

    if not title:
        raise ValueError(
            "YouTube title cannot be empty."
        )

    if len(title) > 100:
        raise ValueError(
            "YouTube title must be 100 characters or fewer."
        )

    publish_time = _validate_scheduled_at(
        scheduled_at
    )

    publish_at = publish_time.isoformat()

    youtube, _, _ = _youtube_client(
        user_id
    )

    body = {
        "snippet": {
            "title": title,
            "description": description or "",
            "tags": _clean_tags(tags),
            "categoryId": str(
                category_id or "22"
            ),
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=8 * 1024 * 1024,
    )

    try:

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = request.execute()

    except HttpError as error:

        raise RuntimeError(
            "YouTube scheduled upload failed: "
            f"{error}"
        ) from error

    video_id = response.get(
        "id"
    )

    if not video_id:
        raise RuntimeError(
            "YouTube scheduled upload completed without returning a video ID."
        )

    actual_publish_at = (
        response.get("status", {})
        .get("publishAt")
        or publish_at
    )

    return {
        "success": True,
        "video_id": video_id,
        "video_url": _youtube_url(
            video_id
        ),
        "privacy_status": (
            response.get("status", {})
            .get("privacyStatus")
        ),
        "publish_at": actual_publish_at,
        "title": (
            response.get("snippet", {})
            .get("title", title)
        ),
    }


def get_youtube_video_status(
    *,
    user_id: str,
    video_id: str,
) -> dict:

    video_id = video_id.strip()

    if not video_id:
        raise ValueError(
            "video_id is required."
        )

    youtube, _, _ = _youtube_client(
        user_id
    )

    try:

        response = youtube.videos().list(
            part="snippet,status",
            id=video_id,
        ).execute()

    except HttpError as error:

        raise RuntimeError(
            "Could not read YouTube video status: "
            f"{error}"
        ) from error

    items = response.get(
        "items",
        []
    )

    if not items:
        raise LookupError(
            "YouTube video was not found."
        )

    video = items[0]

    snippet = video.get(
        "snippet",
        {}
    )

    status = video.get(
        "status",
        {}
    )

    return {
        "success": True,
        "video_id": video_id,
        "video_url": _youtube_url(
            video_id
        ),
        "title": snippet.get(
            "title"
        ),
        "description": snippet.get(
            "description"
        ),
        "privacy_status": status.get(
            "privacyStatus"
        ),
        "publish_at": status.get(
            "publishAt"
        ),
        "upload_status": status.get(
            "uploadStatus"
        ),
        "made_for_kids": status.get(
            "selfDeclaredMadeForKids"
        ),
    }


def delete_youtube_video(
    *,
    user_id: str,
    video_id: str,
) -> dict:

    video_id = video_id.strip()

    if not video_id:
        raise ValueError(
            "video_id is required."
        )

    youtube, _, _ = _youtube_client(
        user_id
    )

    try:

        youtube.videos().delete(
            id=video_id
        ).execute()

    except HttpError as error:

        raise RuntimeError(
            "Could not delete YouTube video: "
            f"{error}"
        ) from error

    return {
        "success": True,
        "video_id": video_id,
        "deleted": True,
    }



def get_youtube_video_comments(
    *,
    user_id: str,
    video_id: str,
    max_results: int = 100,
) -> dict:
    """Fetch top-level comments and available replies for a YouTube video."""
    video_id = video_id.strip()
    if not video_id:
        raise ValueError("video_id is required.")

    max_results = max(1, min(int(max_results), 100))
    youtube, _, _ = _youtube_client(user_id)

    comments = []
    next_page_token = None

    try:
        while len(comments) < max_results:
            response = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=min(100, max_results - len(comments)),
                pageToken=next_page_token,
                textFormat="plainText",
            ).execute()

            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                top = snippet.get("topLevelComment", {})
                top_snippet = top.get("snippet", {})
                comment_id = top.get("id") or item.get("id")
                comments.append({
                    "id": comment_id,
                    "author": top_snippet.get("authorDisplayName", ""),
                    "text": top_snippet.get("textDisplay", ""),
                    "like_count": top_snippet.get("likeCount", 0),
                    "published_at": top_snippet.get("publishedAt"),
                    "updated_at": top_snippet.get("updatedAt"),
                    "reply_count": snippet.get("totalReplyCount", 0),
                })
                if len(comments) >= max_results:
                    break

            next_page_token = response.get("nextPageToken")
            if not next_page_token or not response.get("items"):
                break

    except HttpError as error:
        raise RuntimeError(
            "Could not fetch YouTube comments: "
            f"{error}"
        ) from error

    return {
        "success": True,
        "video_id": video_id,
        "count": len(comments),
        "comments": comments,
    }
