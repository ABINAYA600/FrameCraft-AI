import os
import json
import secrets
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


# ============================================================
# LOAD BACKEND .ENV
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# GOOGLE CONFIGURATION
# ============================================================

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://127.0.0.1:8000/platforms/youtube/callback"
)


# ============================================================
# FILE STORAGE
# ============================================================

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


CONNECTIONS_FILE = (
    DATA_DIR / "youtube_connections.json"
)

OAUTH_STATES_FILE = (
    DATA_DIR / "youtube_oauth_states.json"
)


# ============================================================
# YOUTUBE SCOPES
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


# ============================================================
# JSON HELPERS
# ============================================================

def load_json(
    path: Path,
    default
):
    """
    Load JSON safely.
    """

    if not path.exists():
        return default

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return default


def save_json(
    path: Path,
    data
):
    """
    Save JSON safely.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# GOOGLE CONFIG VALIDATION
# ============================================================

def validate_google_config():

    missing = []

    if not CLIENT_ID:
        missing.append("GOOGLE_CLIENT_ID")

    if not CLIENT_SECRET:
        missing.append("GOOGLE_CLIENT_SECRET")

    if not REDIRECT_URI:
        missing.append("GOOGLE_REDIRECT_URI")

    if missing:

        raise RuntimeError(
            "Missing Google OAuth configuration: "
            + ", ".join(missing)
        )


# ============================================================
# GOOGLE CLIENT CONFIG
# ============================================================

def get_client_config():

    validate_google_config()

    return {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": (
                "https://accounts.google.com/o/oauth2/auth"
            ),
            "token_uri": (
                "https://oauth2.googleapis.com/token"
            ),
            "auth_provider_x509_cert_url": (
                "https://www.googleapis.com/oauth2/v1/certs"
            ),
            "redirect_uris": [
                REDIRECT_URI
            ]
        }
    }


# ============================================================
# CREATE GOOGLE OAUTH FLOW
# ============================================================

def create_flow(
    state: Optional[str] = None
):

    validate_google_config()

    flow = Flow.from_client_config(
        get_client_config(),
        scopes=SCOPES,
        state=state
    )

    flow.redirect_uri = REDIRECT_URI

    return flow


# ============================================================
# CREATE AUTHORIZATION URL
# ============================================================

def create_authorization_url(
    user_id: str
):

    user_id = user_id.strip()

    if not user_id:

        raise ValueError(
            "user_id is required"
        )

    # --------------------------------------------------------
    # Create OAuth flow
    # --------------------------------------------------------

    flow = create_flow()

    # --------------------------------------------------------
    # Generate authorization URL.
    #
    # google-auth-oauthlib generates a PKCE verifier when
    # needed and puts the corresponding challenge in the URL.
    # --------------------------------------------------------

    authorization_url, state = (
        flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
    )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Save BOTH:
    #
    # 1. user_id
    # 2. code_verifier
    #
    # The callback needs the exact verifier used to generate
    # the code_challenge.
    # --------------------------------------------------------

    states = load_json(
        OAUTH_STATES_FILE,
        {}
    )

    states[state] = {
        "user_id": user_id,
        "code_verifier": flow.code_verifier
    }

    save_json(
        OAUTH_STATES_FILE,
        states
    )

    print(
        "\nYouTube OAuth authorization created."
    )

    print(
        f"User: {user_id}"
    )

    print(
        f"State: {state}"
    )

    print(
        "PKCE code verifier stored."
    )

    return authorization_url


# ============================================================
# COMPLETE AUTHORIZATION
# ============================================================

def complete_authorization(
    state: str,
    code: str
):

    if not state:

        raise ValueError(
            "OAuth state is required."
        )

    if not code:

        raise ValueError(
            "OAuth authorization code is required."
        )

    # --------------------------------------------------------
    # Load stored OAuth states
    # --------------------------------------------------------

    states = load_json(
        OAUTH_STATES_FILE,
        {}
    )

    state_data = states.get(state)

    if not state_data:

        raise ValueError(
            "Invalid or expired OAuth state."
        )

    # --------------------------------------------------------
    # Read user ID and PKCE verifier
    # --------------------------------------------------------

    if isinstance(
        state_data,
        dict
    ):

        user_id = state_data.get(
            "user_id"
        )

        code_verifier = state_data.get(
            "code_verifier"
        )

    else:

        # Compatibility with an older state file format.
        user_id = state_data
        code_verifier = None

    if not user_id:

        raise ValueError(
            "OAuth state does not contain user_id."
        )

    if not code_verifier:

        raise ValueError(
            "Missing stored PKCE code verifier. "
            "Please start a new YouTube connection."
        )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Delete state BEFORE exchanging the code.
    #
    # OAuth states are one-time values.
    # --------------------------------------------------------

    del states[state]

    save_json(
        OAUTH_STATES_FILE,
        states
    )

    # --------------------------------------------------------
    # Recreate the exact OAuth flow
    # --------------------------------------------------------

    flow = create_flow(
        state=state
    )

    # --------------------------------------------------------
    # Restore the PKCE verifier.
    #
    # This is the missing piece that caused:
    #
    # invalid_grant: Missing code verifier
    # --------------------------------------------------------

    flow.code_verifier = code_verifier

    # --------------------------------------------------------
    # Exchange authorization code for tokens.
    # --------------------------------------------------------

    flow.fetch_token(
        code=code,
        code_verifier=code_verifier
    )

    credentials = flow.credentials

    if not credentials:

        raise RuntimeError(
            "Google did not return credentials."
        )

    if not credentials.refresh_token:

        raise RuntimeError(
            "Google did not return a refresh token. "
            "Please authorize again with consent."
        )

    # --------------------------------------------------------
    # Create YouTube API client
    # --------------------------------------------------------

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )

    # --------------------------------------------------------
    # Get authenticated YouTube channel
    # --------------------------------------------------------

    response = (
        youtube.channels()
        .list(
            part="snippet,contentDetails",
            mine=True
        )
        .execute()
    )

    channels = response.get(
        "items",
        []
    )

    if not channels:

        raise RuntimeError(
            "No YouTube channel was found "
            "for this Google account."
        )

    channel = channels[0]

    channel_id = channel.get(
        "id"
    )

    snippet = channel.get(
        "snippet",
        {}
    )

    channel_title = snippet.get(
        "title",
        ""
    )

    channel_description = snippet.get(
        "description",
        ""
    )

    thumbnails = snippet.get(
        "thumbnails",
        {}
    )

    # --------------------------------------------------------
    # Store connection
    # --------------------------------------------------------

    connections = load_json(
        CONNECTIONS_FILE,
        {}
    )

    connections[user_id] = {
        "provider": "youtube",
        "connected": True,

        "channel_id": channel_id,
        "channel_title": channel_title,
        "channel_description": channel_description,
        "channel_thumbnail": (
            thumbnails
            .get("default", {})
            .get("url")
        ),

        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,

        "scopes": credentials.scopes,

        "client_id": CLIENT_ID,

        "connected_at": (
            __import__("datetime")
            .datetime.now()
            .isoformat()
        )
    }

    save_json(
        CONNECTIONS_FILE,
        connections
    )

    print(
        "\n============================================================"
    )

    print(
        "YouTube Connected Successfully!"
    )

    print(
        f"User: {user_id}"
    )

    print(
        f"Channel: {channel_title}"
    )

    print(
        f"Channel ID: {channel_id}"
    )

    print(
        "============================================================"
    )

    return {
        "user_id": user_id,
        "provider": "youtube",
        "connected": True,
        "channel_id": channel_id,
        "channel_title": channel_title,
        "channel_description": channel_description,
        "channel_thumbnail": (
            thumbnails
            .get("default", {})
            .get("url")
        )
    }


# ============================================================
# GET CONNECTION
# ============================================================

def get_connection(
    user_id: str
) -> Optional[Dict[str, Any]]:

    connections = load_json(
        CONNECTIONS_FILE,
        {}
    )

    return connections.get(
        user_id
    )


# ============================================================
# GET YOUTUBE CLIENT
# ============================================================

def get_youtube_client(
    user_id: str
):

    connection = get_connection(
        user_id
    )

    if not connection:

        raise ValueError(
            "YouTube account is not connected."
        )

    from google.oauth2.credentials import (
        Credentials
    )

    credentials = Credentials(
        token=connection.get("token"),
        refresh_token=connection.get(
            "refresh_token"
        ),
        token_uri=connection.get(
            "token_uri"
        ),
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=connection.get(
            "scopes"
        ) or SCOPES
    )

    # --------------------------------------------------------
    # Build YouTube client.
    #
    # google-auth can refresh the access token when required.
    # --------------------------------------------------------

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )

    return youtube


# ============================================================
# CONNECTION STATUS
# ============================================================

def get_connection_status(
    user_id: str
):

    connection = get_connection(
        user_id
    )

    if not connection:

        return {
            "provider": "youtube",
            "connected": False,
            "user_id": user_id
        }

    return {
        "provider": "youtube",
        "connected": True,
        "user_id": user_id,

        "channel_id": connection.get(
            "channel_id"
        ),

        "channel_title": connection.get(
            "channel_title"
        ),

        "channel_thumbnail": connection.get(
            "channel_thumbnail"
        ),

        "connected_at": connection.get(
            "connected_at"
        )
    }


# ============================================================
# DISCONNECT YOUTUBE
# ============================================================

def disconnect_youtube(
    user_id: str
):

    connections = load_json(
        CONNECTIONS_FILE,
        {}
    )

    if user_id not in connections:

        return {
            "disconnected": False,
            "message": (
                "YouTube account was not connected."
            )
        }

    del connections[user_id]

    save_json(
        CONNECTIONS_FILE,
        connections
    )

    return {
        "disconnected": True,
        "user_id": user_id
    }


# ============================================================
# IS YOUTUBE CONNECTED
# ============================================================

def is_youtube_connected(
    user_id: str
) -> bool:

    connection = get_connection(
        user_id
    )

    return bool(
        connection
        and connection.get("connected")
    )