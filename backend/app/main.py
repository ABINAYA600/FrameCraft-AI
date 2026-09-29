import json

import re

import shutil

import subprocess

import uuid

from datetime import datetime

from pathlib import Path



from dotenv import load_dotenv

load_dotenv()



from fastapi import (

    FastAPI,

    UploadFile,

    File,

    Form,

    HTTPException,

)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.openapi.utils import get_openapi

from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel



from ml_models.fafm import FAFM

from app.services.creator_knowledge import CreatorKnowledge

from app.services.contextual_comment_intelligence import ContextualCommentIntelligence

# ============================================================
# MLOps
# ============================================================
from mlops.router import router as mlops_router
from mlops.startup import start_background_monitor


# YouTube OAuth integration
from app.services.youtube_service import (
    create_authorization_url,
    complete_authorization,
    get_connection_status,
    disconnect_youtube,
)

# YouTube video publishing / scheduling
from app.services.youtube_publisher import (
    publish_video_now,
    schedule_video,
    get_youtube_video_status,
    get_youtube_video_comments,
)





# ============================================================

# PATHS

# ============================================================



BASE_DIR = Path(__file__).resolve().parent.parent



OUTPUT_DIR = BASE_DIR / "output"

USER_MEDIA_DIR = BASE_DIR / "user_media"

PROJECTS_DIR = BASE_DIR / "projects"



OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

USER_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

PROJECTS_DIR.mkdir(parents=True, exist_ok=True)



CREATOR_PROFILE_FILE = OUTPUT_DIR / "creator_profile.json"

SETTINGS_FILE = OUTPUT_DIR / "framecraft_settings.json"

COMMENT_EVENTS_FILE = OUTPUT_DIR / "live_comment_events.json"

PUBLISHING_FILE = OUTPUT_DIR / "publishing.json"







# ============================================================

# FASTAPI APPLICATION

# ============================================================



app = FastAPI(

    title="FrameCraft AI API",

    description="AI-powered content generation backend",

    version="1.0.0",

)

# ============================================================
# MLOPS ROUTER
# ============================================================
app.include_router(mlops_router)

# ============================================================
# MLOPS BACKGROUND MONITOR
# ============================================================
@app.on_event("startup")
def start_framecraft_mlops():
    start_background_monitor()







# ============================================================

# CORS

# ============================================================



app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)





# ============================================================

# FRAMECRAFT AI FOUNDATION MODEL

# ============================================================



fafm = FAFM()





# ============================================================

# CREATOR KNOWLEDGE

# ============================================================



knowledge = CreatorKnowledge()

knowledge.load()

contextual_intelligence = ContextualCommentIntelligence(knowledge)





# ============================================================

# STATIC FILE SERVING

# ============================================================



app.mount(

    "/media",

    StaticFiles(directory=str(USER_MEDIA_DIR)),

    name="media",

)



app.mount(

    "/output",

    StaticFiles(directory=str(OUTPUT_DIR)),

    name="output",

)



app.mount(

    "/project-files",

    StaticFiles(directory=str(PROJECTS_DIR)),

    name="project-files",

)





# ============================================================

# REQUEST MODELS

# ============================================================



class GenerateRequest(BaseModel):

    script: str

    output_name: str = "framecraft_output.mp4"

    generate_thumbnail: bool = True

    thumbnail_title: str | None = None





class ProjectCreateRequest(BaseModel):

    name: str

    description: str = ""

    script: str = ""

    media_source: str = "both"

    music_mode: str = "ai"

    selected_music_id: str | None = None





class ProjectUpdateRequest(BaseModel):

    name: str | None = None

    description: str | None = None

    script: str | None = None

    media_source: str | None = None

    music_mode: str | None = None

    selected_music_id: str | None = None





class ProjectGenerateRequest(BaseModel):

    generate_thumbnail: bool = True

    thumbnail_title: str | None = None

    output_name: str | None = None





class CommentRequest(BaseModel):

    comment: str

    creator_id: str | None = None

    project_id: str | None = None

    video_id: str | None = None

    occurred_at: str | None = None





class ReplyDecisionRequest(BaseModel):

    reply_id: str





class CreatorProfileRequest(BaseModel):

    name: str = ""

    username: str = ""

    bio: str = ""

    niche: str = ""

    tone: str = "friendly"

    language: str = "English"

    reply_style: str = "short"

    emoji_preference: str = "occasional"





class SettingsRequest(BaseModel):

    auto_reply_enabled: bool = True

    confidence_threshold: float = 0.75

    notifications_enabled: bool = True

    default_music_mode: str = "ai"

    default_media_source: str = "both"





class BatchCommentRequest(BaseModel):

    comments: list[str] = []

    project_id: str | None = None

    video_id: str | None = None





class PublishPostRequest(BaseModel):

    project_id: str | None = None

    title: str

    platform: str

    scheduled_at: str

    status: str = "Scheduled"





class PublishStatusRequest(BaseModel):

    status: str


class YouTubePublishRequest(BaseModel):

    user_id: str = "demo_user"

    project_id: str

    video_id: str | None = None

    title: str

    description: str = ""

    tags: list[str] = []

    category_id: str = "22"


class YouTubeScheduleRequest(BaseModel):

    user_id: str = "demo_user"

    project_id: str

    video_id: str | None = None

    title: str

    description: str = ""

    tags: list[str] = []

    category_id: str = "22"

    scheduled_at: str





# ============================================================

# ALLOWED MEDIA TYPES

# ============================================================



ALLOWED_MEDIA_TYPES = {

    "images": {

        ".jpg",

        ".jpeg",

        ".png",

        ".webp",

    },

    "videos": {

        ".mp4",

        ".mov",

        ".avi",

        ".mkv",

        ".webm",

    },

    "music": {

        ".mp3",

        ".wav",

        ".m4a",

        ".aac",

        ".ogg",

    },

}





# ============================================================

# GENERAL HELPERS

# ============================================================



def now_iso():

    return datetime.now().isoformat()





def normalize_project(project):

    """Make old projects compatible with the new workspace format."""



    if "images" not in project:

        project["images"] = []



    if "videos" not in project:

        project["videos"] = []



    if "music" not in project:

        project["music"] = []



    if "generated" not in project:

        project["generated"] = []



    # Older versions used generated_videos.

    if "generated_videos" in project and not project["generated"]:

        project["generated"] = project["generated_videos"]



    if "script" not in project:

        project["script"] = ""



    if "media_source" not in project:

        project["media_source"] = "both"



    if "created_at" not in project:

        project["created_at"] = now_iso()



    if "updated_at" not in project:

        project["updated_at"] = now_iso()



    return project





def get_all_projects():

    projects = knowledge.data.setdefault("projects", [])



    for project in projects:

        normalize_project(project)



    return projects





def find_project(project_id):

    for project in get_all_projects():

        if project.get("id") == project_id:

            return project



    return None





def get_project_or_404(project_id):

    project = find_project(project_id)



    if project is None:

        raise HTTPException(

            status_code=404,

            detail="Project not found",

        )



    return project





def project_directory(project_id):

    return PROJECTS_DIR / project_id





def project_json_path(project_id):

    return project_directory(project_id) / "project.json"





def create_project_workspace(project_id):

    root = project_directory(project_id)



    (root / "images").mkdir(

        parents=True,

        exist_ok=True,

    )



    (root / "videos").mkdir(

        parents=True,

        exist_ok=True,

    )



    (root / "music").mkdir(

        parents=True,

        exist_ok=True,

    )



    (root / "generated").mkdir(

        parents=True,

        exist_ok=True,

    )



    return root





def save_project_workspace(project):

    project = normalize_project(project)



    project_id = project["id"]



    create_project_workspace(project_id)



    with open(

        project_json_path(project_id),

        "w",

        encoding="utf-8",

    ) as file:

        json.dump(

            project,

            file,

            indent=4,

            ensure_ascii=False,

            default=str,

        )





def save_knowledge():

    knowledge.save()





def create_project_file_url(

    project_id,

    media_type,

    filename,

):

    return (

        f"/project-files/"

        f"{project_id}/"

        f"{media_type}/"

        f"{filename}"

    )





def create_generated_file_url(

    project_id,

    filename,

):

    return (

        f"/project-files/"

        f"{project_id}/"

        f"generated/"

        f"{filename}"

    )





def load_list_file(path: Path):

    data = load_json_file(path, [])

    return data if isinstance(data, list) else []





def save_list_file(path: Path, data):

    save_json_file(path, data)





def get_creator_profile_data():

    profile = load_json_file(CREATOR_PROFILE_FILE, {})

    return profile if isinstance(profile, dict) else {}





def get_live_comment_events():

    return load_list_file(COMMENT_EVENTS_FILE)





def save_live_comment_events(events):

    save_list_file(COMMENT_EVENTS_FILE, events)





def get_publishing_posts():

    return load_list_file(PUBLISHING_FILE)





def save_publishing_posts(posts):

    save_list_file(PUBLISHING_FILE, posts)





def find_video_in_project(project, video_id=None):

    videos = project.get("videos", [])

    if video_id:

        for item in videos:

            if item.get("id") == video_id:

                return item

    return videos[0] if videos else None



def find_generated_video(project, video_id=None):
    """
    Find a generated MP4 video from the project.
    If video_id is provided, only that generated video is considered.
    Otherwise, the newest available generated MP4 is selected.
    """
    normalize_project(project)

    generated = project.get("generated", [])
    if not isinstance(generated, list):
        generated = []

    candidates = []

    for item in generated:
        if not isinstance(item, dict):
            continue

        if item.get("type") != "video":
            continue

        filename = str(item.get("filename") or "")
        path_value = item.get("path")

        if video_id:
            if item.get("id") != video_id and filename != video_id:
                continue

        if not filename.lower().endswith(".mp4") and (
            not path_value or not str(path_value).lower().endswith(".mp4")
        ):
            continue

        if not path_value:
            if filename:
                path_value = project_directory(project["id"]) / "generated" / filename
            else:
                continue

        path = Path(path_value)
        if not path.exists() or not path.is_file():
            continue

        item_copy = dict(item)
        item_copy["path"] = str(path)
        item_copy.setdefault("filename", path.name)
        candidates.append(item_copy)

    if not candidates:
        return None

    if video_id:
        return candidates[0]

    return max(
        candidates,
        key=lambda item: Path(item["path"]).stat().st_mtime,
    )





def analyze_uploaded_video_file(video_path):

    result = {

        "analyzed": False,

        "analysis_method": "metadata",

        "transcript_available": False,

    }

    try:

        import cv2

        capture = cv2.VideoCapture(str(video_path))

        if not capture.isOpened():

            result["error"] = "Video could not be opened."

            return result

        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0)

        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)

        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

        duration = round(frame_count / fps, 2) if fps > 0 else 0

        samples = 0

        brightness = []

        if frame_count > 0:

            for fraction in (0.2, 0.5, 0.8):

                capture.set(cv2.CAP_PROP_POS_FRAMES, min(frame_count - 1, int(frame_count * fraction)))

                ok, frame = capture.read()

                if ok:

                    samples += 1

                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    brightness.append(round(float(gray.mean()), 2))

        capture.release()

        result.update({

            "analyzed": True,

            "duration_seconds": duration,

            "fps": round(fps, 2),

            "frame_count": frame_count,

            "resolution": f"{width}x{height}",

            "sampled_frames": samples,

            "average_sample_brightness": round(sum(brightness) / len(brightness), 2) if brightness else None,

        })

        try:

            import whisper  # optional; lazy import so backend startup is unaffected

            model_name = "base"

            model = whisper.load_model(model_name)

            transcription = model.transcribe(str(video_path), fp16=False)

            text = (transcription.get("text") or "").strip()

            if text:

                result["transcript"] = text

                result["transcript_available"] = True

                result["analysis_method"] = "metadata+whisper"

        except Exception as error:

            result["transcript_note"] = f"Whisper transcription unavailable: {type(error).__name__}"

        return result

    except Exception as error:

        result["error"] = str(error)

        return result





def validate_media_type(media_type):

    if media_type not in ALLOWED_MEDIA_TYPES:

        raise HTTPException(

            status_code=400,

            detail=(

                "Invalid media_type. "

                "Use images, videos, or music."

            ),

        )





def safe_filename(filename):

    return Path(filename).name





def copy_if_exists(source, destination):

    """

    Copy a generated file when the source exists.

    Returns the destination Path or None.

    """

    if not source:

        return None



    try:

        source_path = Path(source)

    except TypeError:

        return None



    if not source_path.exists() or not source_path.is_file():

        return None



    destination.parent.mkdir(

        parents=True,

        exist_ok=True,

    )



    try:

        if source_path.resolve() != destination.resolve():

            shutil.copy2(

                source_path,

                destination,

            )

        return destination

    except Exception as error:

        print(

            "Warning: could not copy generated file:",

            error,

        )

        return None





def find_existing_thumbnail(

    result,

    generated_dir,

):

    candidates = []



    if isinstance(result, dict):

        candidates.extend([

            result.get("thumbnail_path"),

            result.get("thumbnail"),

        ])



    for candidate in candidates:

        if isinstance(candidate, (str, Path)):

            path = Path(candidate)

            if path.exists():

                return path



    # Known FAFM / ThumbnailGenerator output names.

    known_names = [

        "framecraft_thumbnail.jpg",

        "thumbnail.jpg",

    ]



    for name in known_names:

        path = OUTPUT_DIR / name

        if path.exists():

            return path



    for path in generated_dir.glob("*thumbnail*.jpg"):

        if path.is_file():

            return path



    return None





def find_existing_thumbnail_metadata(

    result,

    generated_dir,

):

    candidates = []



    if isinstance(result, dict):

        candidates.extend([

            result.get("thumbnail_metadata_path"),

            result.get("thumbnail_metadata"),

        ])



    for candidate in candidates:

        if isinstance(candidate, (str, Path)):

            path = Path(candidate)

            if path.exists():

                return path



    known_names = [

        "thumbnail_metadata.json",

        "framecraft_thumbnail_metadata.json",

    ]



    for name in known_names:

        path = OUTPUT_DIR / name

        if path.exists():

            return path



    for path in generated_dir.glob("*thumbnail*metadata*.json"):

        if path.is_file():

            return path



    return None





def save_metadata_dictionary(

    metadata,

    destination,

):

    if not isinstance(metadata, dict):

        return None



    destination.parent.mkdir(

        parents=True,

        exist_ok=True,

    )



    with open(

        destination,

        "w",

        encoding="utf-8",

    ) as file:

        json.dump(

            metadata,

            file,

            indent=4,

            ensure_ascii=False,

            default=str,

        )



    return destination





# ============================================================

# ROOT

# ============================================================



@app.get("/")

def root():

    return {

        "message": "FrameCraft AI API is running",

        "status": "success",

    }





# ============================================================

# SYSTEM STATUS

# ============================================================



@app.get("/status")

def status():

    return fafm.get_system_status()





# ============================================================

# LEGACY AI GENERATION

# ============================================================





# ============================================================

# MUSIC SEARCH

# ============================================================





def get_music_catalog():

    """Return searchable metadata for FrameCraft's local/approved music catalog."""



    music_dir = BASE_DIR / "datasets" / "music"

    music_dir.mkdir(parents=True, exist_ok=True)



    supported_extensions = {

        ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac",

    }



    catalog = []



    for file_path in sorted(music_dir.iterdir()):

        if not file_path.is_file() or file_path.suffix.lower() not in supported_extensions:

            continue



        name = file_path.stem.replace("_", " ").replace("-", " ").strip()

        lower = name.lower()

        mood = "neutral"

        genre = "cinematic"

        energy = "medium"



        if any(word in lower for word in ("happy", "joy", "fun", "upbeat")):

            mood, energy = "happy", "high"

        elif any(word in lower for word in ("peace", "peaceful", "calm", "relax")):

            mood, energy = "peaceful", "low"

        elif any(word in lower for word in ("sad", "emotional", "melancholy")):

            mood, energy = "sad", "low"

        elif any(word in lower for word in ("epic", "power", "action", "energetic")):

            mood, energy = "energetic", "high"

        elif any(word in lower for word in ("technology", "tech", "digital", "future")):

            mood, genre, energy = "technology", "electronic", "medium"

        elif any(word in lower for word in ("cinematic", "film", "movie")):

            mood, genre, energy = "cinematic", "cinematic", "medium"



        catalog.append({

            "id": file_path.stem,

            "name": name,

            "filename": file_path.name,

            "path": str(file_path),

            "mood": mood,

            "genre": genre,

            "energy": energy,

            "source": "framecraft",

            "usable_in_video": True,

        })



    return catalog







@app.get("/music/search")

def search_music(

    q: str = "",

    source: str = "framecraft",

    mood: str | None = None,

    genre: str | None = None,

    energy: str | None = None,

):

    """Search only the local FrameCraft music catalog."""



    query = q.strip().lower()

    mood_query = mood.strip().lower() if mood else ""

    genre_query = genre.strip().lower() if genre else ""

    energy_query = energy.strip().lower() if energy else ""



    results = []



    for track in get_music_catalog():

        searchable = " ".join([

            track.get("name", ""),

            track.get("filename", ""),

            track.get("mood", ""),

            track.get("genre", ""),

            track.get("energy", ""),

        ]).lower()



        if query and query not in searchable:

            continue

        if mood_query and track["mood"].lower() != mood_query:

            continue

        if genre_query and track["genre"].lower() != genre_query:

            continue

        if energy_query and track["energy"].lower() != energy_query:

            continue



        public_track = dict(track)

        public_track.pop("path", None)

        results.append(public_track)



    return {

        "success": True,

        "query": q,

        "source": "framecraft",

        "count": len(results),

        "results": results,

    }





class MusicRecommendationRequest(BaseModel):

    script: str

    limit: int = 5





@app.post("/music/recommend")

def recommend_music(request: MusicRecommendationRequest):

    """Recommend FrameCraft catalog music based on the script."""



    if not request.script.strip():

        raise HTTPException(

            status_code=400,

            detail="Script cannot be empty.",

        )



    limit = max(1, min(request.limit, 20))



    try:

        # Use the existing FAFM music manager.

        music_model = fafm.music_manager



        if music_model is None:

            raise RuntimeError("Music Model is not initialized.")



        result = music_model.recommend_music(

            request.script,

            limit=limit,

        )



        return {

            "success": True,

            "script": request.script,

            "mood": result.get("mood"),

            "energy": result.get("energy"),

            "total_tracks": result.get("total_tracks", 0),

            "recommendations": result.get("recommendations", []),

        }



    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=f"Music recommendation failed: {exc}",

        )





@app.post("/generate")

def generate_content(request: GenerateRequest):

    return fafm.generate_content(

        script=request.script,

        output_name=request.output_name,

        generate_thumbnail=request.generate_thumbnail,

        thumbnail_title=request.thumbnail_title,

    )





# ============================================================

# CREATE PROJECT

# ============================================================



@app.post("/projects")

def create_project(request: ProjectCreateRequest):



    if not request.name.strip():

        raise HTTPException(

            status_code=400,

            detail="Project name cannot be empty",

        )



    if request.media_source not in {

        "uploaded",

        "ai",

        "both",

    }:

        raise HTTPException(

            status_code=400,

            detail=(

                "media_source must be "

                "uploaded, ai, or both"

            ),

        )



    project = {

        "id": f"project_{uuid.uuid4().hex[:8]}",

        "name": request.name.strip(),

        "description": request.description,

        "script": request.script,

        "media_source": request.media_source,

        "music_mode": request.music_mode if request.music_mode in {"ai", "uploaded", "search"} else "ai",

        "selected_music_id": request.selected_music_id,

        "images": [],

        "videos": [],

        "music": [],

        "generated": [],

        "created_at": now_iso(),

        "updated_at": now_iso(),

    }



    knowledge.data.setdefault(

        "projects",

        [],

    ).append(project)



    create_project_workspace(

        project["id"]

    )



    save_project_workspace(project)

    save_knowledge()



    return {

        "success": True,

        "project": project,

    }





# ============================================================

# GET ALL PROJECTS

# ============================================================



@app.get("/projects")

def get_projects():



    projects = get_all_projects()



    return {

        "success": True,

        "count": len(projects),

        "projects": projects,

    }





# ============================================================

# GET SINGLE PROJECT

# ============================================================



@app.get("/projects/{project_id}")

def get_project(project_id: str):



    project = get_project_or_404(

        project_id

    )



    normalize_project(project)



    create_project_workspace(

        project_id

    )



    save_project_workspace(project)



    return {

        "success": True,

        "project": project,

    }





# ============================================================

# UPDATE PROJECT

# ============================================================



@app.put("/projects/{project_id}")

def update_project(

    project_id: str,

    request: ProjectUpdateRequest,

):



    project = get_project_or_404(

        project_id

    )



    if request.media_source is not None:



        if request.media_source not in {

            "uploaded",

            "ai",

            "both",

        }:

            raise HTTPException(

                status_code=400,

                detail=(

                    "media_source must be "

                    "uploaded, ai, or both"

                ),

            )



        project[

            "media_source"

        ] = request.media_source



    if request.name is not None:



        if not request.name.strip():

            raise HTTPException(

                status_code=400,

                detail=(

                    "Project name "

                    "cannot be empty"

                ),

            )



        project[

            "name"

        ] = request.name.strip()



    if request.description is not None:

        project[

            "description"

        ] = request.description



    if request.script is not None:

        project[

            "script"

        ] = request.script



    if request.music_mode is not None:

        if request.music_mode not in {

            "ai",

            "uploaded",

            "search",

        }:

            raise HTTPException(

                status_code=400,

                detail=(

                    "music_mode must be ai, uploaded, or search"

                ),

            )

        project["music_mode"] = request.music_mode



    if request.selected_music_id is not None:

        project["selected_music_id"] = request.selected_music_id



    project[

        "updated_at"

    ] = now_iso()



    save_project_workspace(project)

    save_knowledge()



    return {

        "success": True,

        "project": project,

    }





# ============================================================

# UPLOAD PROJECT MEDIA

# ============================================================



@app.post(

    "/projects/{project_id}/media"

)

async def upload_project_media(

    project_id: str,

    media_type: str = Form(...),

    file: UploadFile = File(...),

):



    project = get_project_or_404(

        project_id

    )



    validate_media_type(

        media_type

    )



    if not file.filename:

        raise HTTPException(

            status_code=400,

            detail="No file selected",

        )



    original_name = safe_filename(

        file.filename

    )



    extension = Path(

        original_name

    ).suffix.lower()



    if extension not in ALLOWED_MEDIA_TYPES[

        media_type

    ]:

        raise HTTPException(

            status_code=400,

            detail=(

                f"Unsupported file type "

                f"'{extension}' for "

                f"{media_type}"

            ),

        )



    root = create_project_workspace(

        project_id

    )



    destination_dir = (

        root / media_type

    )



    media_id = (

        f"media_"

        f"{uuid.uuid4().hex[:8]}"

    )



    stored_name = (

        f"{media_id}_"

        f"{original_name}"

    )



    destination = (

        destination_dir /

        stored_name

    )



    file_size = 0



    try:



        with open(

            destination,

            "wb",

        ) as buffer:



            while True:



                chunk = await file.read(

                    1024 * 1024

                )



                if not chunk:

                    break



                buffer.write(chunk)

                file_size += len(chunk)



    except Exception as error:



        if destination.exists():

            try:

                destination.unlink()

            except OSError:

                pass



        raise HTTPException(

            status_code=500,

            detail=(

                f"Failed to save file: "

                f"{error}"

            ),

        )



    finally:

        await file.close()



    media_item = {

        "id": media_id,

        "name": original_name,

        "filename": stored_name,

        "type": media_type,

        "content_type": file.content_type,

        "size": file_size,

        "path": str(destination),

        "url": create_project_file_url(

            project_id,

            media_type,

            stored_name,

        ),

    }



    normalize_project(project)



    project[

        media_type

    ].append(media_item)



    if media_type == "videos":

        try:

            media_item["analysis"] = analyze_uploaded_video_file(destination)

            media_item["analyzed_at"] = now_iso()

        except Exception as error:

            media_item["analysis_error"] = str(error)



    project[

        "updated_at"

    ] = now_iso()



    save_project_workspace(project)

    save_knowledge()



    return {

        "success": True,

        "project_id": project_id,

        "media_type": media_type,

        "file": media_item,

        "project": project,

    }





# ============================================================

# DELETE PROJECT MEDIA

# ============================================================



@app.delete(

    "/projects/{project_id}/media/{media_id}"

)

def delete_project_media(

    project_id: str,

    media_id: str,

):



    project = get_project_or_404(

        project_id

    )



    target = None

    target_type = None



    for media_type in [

        "images",

        "videos",

        "music",

    ]:



        for item in project.get(

            media_type,

            [],

        ):



            if item.get("id") == media_id:

                target = item

                target_type = media_type

                break



        if target is not None:

            break



    if target is None:

        raise HTTPException(

            status_code=404,

            detail="Media file not found",

        )



    file_path = target.get(

        "path"

    )



    if file_path:



        path = Path(file_path)



        if path.exists():



            try:

                path.unlink()

            except OSError:

                pass



    project[

        target_type

    ] = [

        item

        for item in project[

            target_type

        ]

        if item.get("id") != media_id

    ]



    project[

        "updated_at"

    ] = now_iso()



    save_project_workspace(project)

    save_knowledge()



    return {

        "success": True,

        "message": (

            "Media deleted successfully"

        ),

        "media_id": media_id,

        "project": project,

    }





# ============================================================

# GENERATE PROJECT CONTENT

# ============================================================



@app.post(

    "/projects/{project_id}/generate"

)

def generate_project(

    project_id: str,

    request: ProjectGenerateRequest,

):



    project = get_project_or_404(

        project_id

    )



    normalize_project(project)



    script = project.get(

        "script",

        "",

    )



    if not script.strip():

        raise HTTPException(

            status_code=400,

            detail=(

                "Project script "

                "cannot be empty"

            ),

        )



    generated_dir = (

        create_project_workspace(

            project_id

        )

        / "generated"

    )



    output_name = (

        request.output_name

        or

        f"{project_id}_video.mp4"

    )



    output_name = Path(

        output_name

    ).name



    if not output_name.lower().endswith(

        ".mp4"

    ):

        output_name += ".mp4"



    requested_output_path = (

        generated_dir /

        output_name

    )



    print("=" * 60)

    print("FRAMECRAFT PROJECT GENERATION")

    print("=" * 60)

    print(

        f"Project: {project_id}"

    )

    print(

        f"Output: {requested_output_path}"

    )



    try:



        result = (

            fafm.generate_project_content(

                project=project,

                output_path=str(

                    requested_output_path

                ),

                generate_thumbnail=(

                    request.generate_thumbnail

                ),

                thumbnail_title=(

                    request.thumbnail_title

                    or project.get("name")

                    or "FrameCraft AI"

                ),

            )

        )



    except Exception as error:



        print(

            "Project generation error:",

            error,

        )



        raise HTTPException(

            status_code=500,

            detail=(

                "Project generation "

                f"failed: {error}"

            ),

        )



    if not isinstance(result, dict):

        result = {

            "success": True,

            "video": result,

        }



    # --------------------------------------------------------

    # VIDEO

    # --------------------------------------------------------



    video_source = None



    possible_video = (

        result.get("video_path")

        or result.get("video")

        or result.get("output_video")

        or result.get("output_path")

    )



    if isinstance(

        possible_video,

        dict

    ):

        possible_video = (

            possible_video.get("output")

            or possible_video.get("path")

            or possible_video.get("video")

        )



    if isinstance(

        possible_video,

        (str, Path)

    ):

        candidate = Path(

            possible_video

        )



        if candidate.exists():

            video_source = candidate



    if video_source is None:



        if requested_output_path.exists():

            video_source = requested_output_path



        else:



            candidate = (

                OUTPUT_DIR /

                output_name

            )



            if candidate.exists():

                video_source = candidate



    generated_files = []



    if video_source is not None:



        final_video_path = (

            generated_dir /

            video_source.name

        )



        copied = copy_if_exists(

            video_source,

            final_video_path,

        )



        if copied is not None:



            generated_files.append({

                "type": "video",

                "filename": copied.name,

                "path": str(copied),

                "url": create_generated_file_url(

                    project_id,

                    copied.name,

                ),

            })



    # --------------------------------------------------------

    # THUMBNAIL

    # --------------------------------------------------------



    thumbnail_source = (

        find_existing_thumbnail(

            result,

            generated_dir,

        )

    )



    if thumbnail_source is not None:



        thumbnail_destination = (

            generated_dir /

            thumbnail_source.name

        )



        copied = copy_if_exists(

            thumbnail_source,

            thumbnail_destination,

        )



        if copied is not None:



            generated_files.append({

                "type": "thumbnail",

                "filename": copied.name,

                "path": str(copied),

                "url": create_generated_file_url(

                    project_id,

                    copied.name,

                ),

            })



    # --------------------------------------------------------

    # THUMBNAIL METADATA

    # --------------------------------------------------------



    thumbnail_metadata_source = (

        find_existing_thumbnail_metadata(

            result,

            generated_dir,

        )

    )



    if (

        thumbnail_metadata_source is not None

    ):



        thumbnail_metadata_destination = (

            generated_dir /

            thumbnail_metadata_source.name

        )



        copied = copy_if_exists(

            thumbnail_metadata_source,

            thumbnail_metadata_destination,

        )



        if copied is not None:



            generated_files.append({

                "type": "thumbnail_metadata",

                "filename": copied.name,

                "path": str(copied),

                "url": create_generated_file_url(

                    project_id,

                    copied.name,

                ),

            })



    # --------------------------------------------------------

    # VIDEO METADATA

    #

    # IMPORTANT:

    # result["metadata"] can be a dictionary.

    # Never pass that dictionary to Path().

    # --------------------------------------------------------



    metadata_source = None

    metadata_value = result.get(

        "metadata"

    )



    possible_metadata_path = (

        result.get("metadata_path")

    )



    if isinstance(

        possible_metadata_path,

        (str, Path)

    ):



        candidate = Path(

            possible_metadata_path

        )



        if candidate.exists():

            metadata_source = candidate



    if metadata_source is None:



        if isinstance(

            metadata_value,

            (str, Path)

        ):



            candidate = Path(

                metadata_value

            )



            if candidate.exists():

                metadata_source = candidate



    if metadata_source is not None:



        metadata_destination = (

            generated_dir /

            metadata_source.name

        )



        copied = copy_if_exists(

            metadata_source,

            metadata_destination,

        )



        if copied is not None:



            generated_files.append({

                "type": "metadata",

                "filename": copied.name,

                "path": str(copied),

                "url": create_generated_file_url(

                    project_id,

                    copied.name,

                ),

            })



    elif isinstance(

        metadata_value,

        dict

    ):



        metadata_destination = (

            generated_dir /

            "framecraft_metadata.json"

        )



        saved = save_metadata_dictionary(

            metadata_value,

            metadata_destination,

        )



        if saved is not None:



            generated_files.append({

                "type": "metadata",

                "filename": saved.name,

                "path": str(saved),

                "url": create_generated_file_url(

                    project_id,

                    saved.name,

                ),

            })



    # --------------------------------------------------------

    # Deduplicate generated files

    # --------------------------------------------------------



    unique_files = []

    seen = set()



    for item in generated_files:



        key = (

            item["type"],

            item["filename"],

        )



        if key not in seen:

            seen.add(key)

            unique_files.append(item)



    generated_files = unique_files



    # --------------------------------------------------------

    # Persist project generation information

    # --------------------------------------------------------



    project[

        "generated"

    ] = generated_files



    # Keep compatibility with older frontend/data.

    project[

        "generated_videos"

    ] = [

        item

        for item in generated_files

        if item.get("type") == "video"

    ]



    project[

        "updated_at"

    ] = now_iso()



    save_project_workspace(project)

    save_knowledge()



    video_url = None

    thumbnail_url = None

    metadata_url = None



    for item in generated_files:



        if item["type"] == "video":

            video_url = item["url"]



        elif item["type"] == "thumbnail":

            thumbnail_url = item["url"]



        elif item["type"] == "metadata":

            metadata_url = item["url"]



    return {

        "success": True,

        "project_id": project_id,

        "project": project,

        "result": result,

        "generated_files": generated_files,

        "video_url": video_url,

        "thumbnail_url": thumbnail_url,

        "metadata_url": metadata_url,

    }





# ============================================================

# COMMENT INTELLIGENCE

# ============================================================



@app.post("/comments/process")

def process_comment(

    request: CommentRequest

):



    try:

        project = find_project(request.project_id) if request.project_id else None

        if request.project_id and project is None:

            raise HTTPException(status_code=404, detail="Project not found")



        profile = get_creator_profile_data()

        if request.creator_id and not profile.get("id"):

            profile["id"] = request.creator_id



        result = fafm.process_comment(

            comment=request.comment,

            creator_profile=profile,

        )



        context = contextual_intelligence.build_context(

            comment=request.comment,

            project=project,

            video_id=request.video_id,

            creator_profile=profile,

        )



        contextual = contextual_intelligence.generate_contextual_reply(

            comment=request.comment,

            context=context,

            base_result=result,

        )



        if isinstance(result, dict):

            result.update(contextual.get("result_updates", {}))

            result["live_context"] = contextual.get("context_summary", {})



        event = {

            "id": f"comment_{uuid.uuid4().hex[:10]}",

            "comment": request.comment.strip(),

            "project_id": request.project_id,

            "video_id": request.video_id,

            "occurred_at": request.occurred_at or now_iso(),

            "analyzed_at": now_iso(),

            "reply": contextual.get("reply"),

            "reply_source": contextual.get("reply_source", "template"),

            "grounded": contextual.get("grounded", False),

            "analysis": (result.get("analysis", result) if isinstance(result, dict) else {}),

            "context_summary": contextual.get("context_summary", {}),

        }



        events = get_live_comment_events()

        events.append(event)

        save_live_comment_events(events[-5000:])



        if isinstance(result, dict):

            result["live_comment_id"] = event["id"]

            result["reply"] = contextual.get("reply")

            result["reply_source"] = contextual.get("reply_source", "template")



        return result



    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=f"Live comment analysis failed: {error}",

        )





@app.get("/comments/pending")

def pending_comments():

    try:

        replies = fafm.pending_replies()

        events = get_live_comment_events()

        for reply in replies:

            comment_text = reply.get("comment") if isinstance(reply, dict) else None

            match = next((e for e in reversed(events) if comment_text and e.get("comment") == comment_text), None)

            if match and isinstance(reply, dict):

                reply["contextual_reply"] = match.get("reply")

                reply["reply_source"] = match.get("reply_source")

                reply["live_context"] = match.get("context_summary", {})

        return {"success": True, "replies": replies}

    except Exception as error:

        raise HTTPException(status_code=500, detail=str(error))





@app.get("/comments/all")

def all_comments():

    try:

        replies = fafm.all_replies()

        events = get_live_comment_events()

        for reply in replies:

            comment_text = reply.get("comment") if isinstance(reply, dict) else None

            match = next((e for e in reversed(events) if comment_text and e.get("comment") == comment_text), None)

            if match and isinstance(reply, dict):

                reply["contextual_reply"] = match.get("reply")

                reply["reply_source"] = match.get("reply_source")

                reply["live_context"] = match.get("context_summary", {})

        return {"success": True, "replies": replies}

    except Exception as error:

        raise HTTPException(status_code=500, detail=str(error))





@app.post("/comments/approve")

def approve_comment(

    request: ReplyDecisionRequest

):



    try:



        return {

            "success": True,

            "result": fafm.approve_reply(

                request.reply_id

            ),

        }



    except Exception as error:



        raise HTTPException(

            status_code=500,

            detail=str(error),

        )





@app.post("/comments/reject")

def reject_comment(

    request: ReplyDecisionRequest

):



    try:



        return {

            "success": True,

            "result": fafm.reject_reply(

                request.reply_id

            ),

        }



    except Exception as error:



        raise HTTPException(

            status_code=500,

            detail=str(error),

        )





# ============================================================

# CREATOR INTELLIGENCE

# ============================================================



@app.post("/creator/analyze")

def analyze_creator():



    try:



        return fafm.analyze_creator()



    except Exception as error:



        raise HTTPException(

            status_code=500,

            detail=(

                f"Creator analysis "

                f"failed: {error}"

            ),

        )





# ============================================================

# COMMENT ANALYSIS SUMMARY

# ============================================================



@app.post("/comments/analyze-batch")

def analyze_comments_batch(request: BatchCommentRequest):



    comments = [c.strip() for c in request.comments if c and c.strip()]

    if not comments:

        raise HTTPException(status_code=400, detail="At least one comment is required.")



    results = []

    for comment in comments:

        results.append(process_comment(CommentRequest(

            comment=comment,

            project_id=request.project_id,

            video_id=request.video_id,

        )))



    categories = {}

    sentiments = {}

    for result in results:

        analysis = result.get("analysis", result) if isinstance(result, dict) else {}

        if not isinstance(analysis, dict):

            analysis = {}

        category = analysis.get("category", "unknown")

        sentiment = analysis.get("sentiment", "neutral")

        categories[category] = categories.get(category, 0) + 1

        sentiments[sentiment] = sentiments.get(sentiment, 0) + 1



    return {

        "success": True,

        "count": len(results),

        "results": results,

        "summary": {

            "categories": categories,

            "sentiments": sentiments,

        },

    }





@app.get("/comments/summary")

def comments_summary(

    project_id: str | None = None,

    video_id: str | None = None,

    date: str | None = None,

):



    events = get_live_comment_events()

    filtered = []

    for event in events:

        if project_id and event.get("project_id") != project_id:

            continue

        if video_id and event.get("video_id") != video_id:

            continue

        if date and not str(event.get("occurred_at", "")).startswith(date):

            continue

        filtered.append(event)



    categories = {}

    sentiments = {}

    sources = {}

    for item in filtered:

        analysis = item.get("analysis", {})

        if not isinstance(analysis, dict):

            analysis = {}

        category = analysis.get("category", "unknown")

        sentiment = analysis.get("sentiment", "neutral")

        source = item.get("reply_source", "template")

        categories[category] = categories.get(category, 0) + 1

        sentiments[sentiment] = sentiments.get(sentiment, 0) + 1

        sources[source] = sources.get(source, 0) + 1



    positive = sentiments.get("positive", 0)

    total = len(filtered)

    return {

        "success": True,

        "total": total,

        "pending": len(fafm.pending_replies()),

        "categories": categories,

        "sentiments": sentiments,

        "reply_sources": sources,

        "positive_rate": round((positive / total) * 100, 1) if total else 0,

        "date": date,

        "project_id": project_id,

        "video_id": video_id,

    }





@app.get("/comments/live")

def live_comments(

    project_id: str | None = None,

    video_id: str | None = None,

    date: str | None = None,

    limit: int = 100,

):

    events = get_live_comment_events()

    filtered = []

    for event in reversed(events):

        if project_id and event.get("project_id") != project_id:

            continue

        if video_id and event.get("video_id") != video_id:

            continue

        if date and not str(event.get("occurred_at", "")).startswith(date):

            continue

        filtered.append(event)

        if len(filtered) >= max(1, min(limit, 500)):

            break

    return {"success": True, "count": len(filtered), "comments": filtered}





@app.get("/comments/{reply_id}/approve")

def approve_reply_alias_get(reply_id: str):

    return {"success": True, "result": fafm.approve_reply(reply_id)}





@app.post("/comments/{reply_id}/approve")

def approve_reply_alias(reply_id: str):

    return {"success": True, "result": fafm.approve_reply(reply_id)}





@app.post("/comments/{reply_id}/reject")

def reject_reply_alias(reply_id: str):

    return {"success": True, "result": fafm.reject_reply(reply_id)}





@app.get("/comments/replies")

def replies_alias():

    return all_comments()





# ============================================================

# CREATOR PROFILE PERSISTENCE

# ============================================================



def load_json_file(path: Path, default):

    if not path.exists():

        return default

    try:

        with path.open("r", encoding="utf-8") as file:

            data = json.load(file)

        return data

    except Exception:

        return default





def save_json_file(path: Path, data):

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:

        json.dump(data, file, indent=2, ensure_ascii=False)





@app.get("/creator/profile")

def get_creator_profile():



    profile = load_json_file(CREATOR_PROFILE_FILE, {})



    if not isinstance(profile, dict):

        profile = {}



    return {

        "success": True,

        "creator_profile": profile,

    }





@app.put("/creator/profile")

def update_creator_profile(request: CreatorProfileRequest):



    profile = request.model_dump()

    save_json_file(CREATOR_PROFILE_FILE, profile)



    # Keep the active comment pipeline synchronized.

    try:

        if fafm.comment_pipeline is not None:

            fafm.comment_pipeline.creator_profile = profile

            if hasattr(fafm.comment_pipeline, "analyzer"):

                fafm.comment_pipeline.analyzer.creator_profile = profile

    except Exception:

        pass



    return {

        "success": True,

        "creator_profile": profile,

    }





# ============================================================

# SETTINGS PERSISTENCE

# ============================================================



DEFAULT_SETTINGS = {

    "auto_reply_enabled": True,

    "confidence_threshold": 0.75,

    "notifications_enabled": True,

    "default_music_mode": "ai",

    "default_media_source": "both",

}





@app.get("/settings")

def get_settings():



    settings = load_json_file(

        SETTINGS_FILE,

        DEFAULT_SETTINGS.copy(),

    )



    merged = DEFAULT_SETTINGS.copy()

    if isinstance(settings, dict):

        merged.update(settings)



    return {

        "success": True,

        "settings": merged,

    }





@app.put("/settings")

def update_settings(request: SettingsRequest):



    if not 0 <= request.confidence_threshold <= 1:

        raise HTTPException(

            status_code=400,

            detail="confidence_threshold must be between 0 and 1.",

        )



    if request.default_music_mode not in {"ai", "uploaded", "search"}:

        raise HTTPException(status_code=400, detail="Invalid default_music_mode.")



    if request.default_media_source not in {"uploaded", "ai", "both"}:

        raise HTTPException(status_code=400, detail="Invalid default_media_source.")



    settings = request.model_dump()

    save_json_file(SETTINGS_FILE, settings)



    try:

        if fafm.comment_pipeline is not None:

            if hasattr(fafm.comment_pipeline, "auto_reply_enabled"):

                fafm.comment_pipeline.auto_reply_enabled = settings["auto_reply_enabled"]

            if hasattr(fafm.comment_pipeline, "confidence_threshold"):

                fafm.comment_pipeline.confidence_threshold = settings["confidence_threshold"]

    except Exception:

        pass



    return {

        "success": True,

        "settings": settings,

    }





# ============================================================

# LIVE DASHBOARD DATA

# ============================================================



@app.get("/dashboard/overview")

def dashboard_overview():



    projects = get_all_projects()

    events = get_live_comment_events()

    posts = get_publishing_posts()



    videos_generated = sum(

        1 for project in projects

        for item in project.get("generated", [])

        if isinstance(item, dict) and item.get("type") == "video"

    )

    images_uploaded = sum(len(project.get("images", [])) for project in projects)

    videos_uploaded = sum(len(project.get("videos", [])) for project in projects)

    music_uploaded = sum(len(project.get("music", [])) for project in projects)



    sentiments = {}

    for event in events:

        analysis = event.get("analysis", {})

        if isinstance(analysis, dict):

            sentiment = analysis.get("sentiment", "neutral")

            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1



    total_comments = len(events)

    positive = sentiments.get("positive", 0)

    engagement = round((positive / total_comments) * 100, 1) if total_comments else 0



    activities = []

    for project in projects:

        activities.append({

            "id": f"project-{project.get('id')}",

            "action": "Project updated",

            "project": project.get("name", "Untitled project"),

            "time": project.get("updated_at") or project.get("created_at"),

        })

    for event in events[-20:]:

        activities.append({

            "id": event.get("id"),

            "action": "Comment analyzed",

            "project": event.get("project_id") or "Live audience",

            "time": event.get("analyzed_at") or event.get("occurred_at"),

        })

    activities.sort(key=lambda x: x.get("time") or "", reverse=True)



    return {

        "success": True,

        "stats": {

            "totalProjects": len(projects),

            "videosGenerated": videos_generated,

            "scheduledPosts": sum(1 for p in posts if p.get("status") == "Scheduled"),

            "audienceEngagement": engagement,

            "commentsAnalyzed": total_comments,

            "pendingReplies": len(fafm.pending_replies()),

            "imagesUploaded": images_uploaded,

            "videosUploaded": videos_uploaded,

            "musicUploaded": music_uploaded,

        },

        "activities": activities[:10],

    }





# ============================================================

# PUBLISHING

# ============================================================



@app.get("/publishing")

def get_publishing():

    posts = get_publishing_posts()

    return {"success": True, "posts": posts}





@app.post("/publishing")

def create_publishing_post(request: PublishPostRequest):

    posts = get_publishing_posts()

    post = request.model_dump()

    post["id"] = f"post_{uuid.uuid4().hex[:8]}"

    post["created_at"] = now_iso()

    if post.get("project_id"):

        project = find_project(post["project_id"])

        if project:

            post["project_name"] = project.get("name")

    posts.append(post)

    save_publishing_posts(posts)

    return {"success": True, "post": post}





@app.put("/publishing/{post_id}")

def update_publishing_post(post_id: str, request: PublishStatusRequest):

    posts = get_publishing_posts()

    for post in posts:

        if post.get("id") == post_id:

            post["status"] = request.status

            post["updated_at"] = now_iso()

            save_publishing_posts(posts)

            return {"success": True, "post": post}

    raise HTTPException(status_code=404, detail="Publishing post not found")





@app.delete("/publishing/{post_id}")

def delete_publishing_post(post_id: str):

    posts = get_publishing_posts()

    filtered = [p for p in posts if p.get("id") != post_id]

    if len(filtered) == len(posts):

        raise HTTPException(status_code=404, detail="Publishing post not found")

    save_publishing_posts(filtered)

    return {"success": True, "deleted": post_id}





# ============================================================

# LIVE VIDEO ANALYSIS

# ============================================================



@app.post("/projects/{project_id}/videos/{video_id}/analyze")

def analyze_project_video(project_id: str, video_id: str):

    project = get_project_or_404(project_id)

    video = find_video_in_project(project, video_id)

    if video is None or video.get("id") != video_id:

        raise HTTPException(status_code=404, detail="Video not found")

    path = Path(video.get("path", ""))

    if not path.exists():

        raise HTTPException(status_code=404, detail="Video file not found")

    analysis = analyze_uploaded_video_file(path)

    video["analysis"] = analysis

    video["analyzed_at"] = now_iso()

    project["updated_at"] = now_iso()

    save_project_workspace(project)

    save_knowledge()

    return {"success": True, "project_id": project_id, "video_id": video_id, "analysis": analysis, "video": video}







# ============================================================
# YOUTUBE ACCOUNT CONNECTION
# ============================================================

@app.get("/platforms/youtube/connect")
def youtube_connect(user_id: str):
    user_id = user_id.strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    try:
        authorization_url = create_authorization_url(user_id=user_id)
        return {"success": True, "authorization_url": authorization_url, "user_id": user_id}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"YouTube OAuth initialization failed: {error}")


@app.get("/platforms/youtube/callback")
def youtube_callback(state: str, code: str):
    try:
        result = complete_authorization(state=state, code=code)
        return {"success": True, "message": "YouTube account connected successfully.", "youtube": result}
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"YouTube OAuth callback failed: {error}")


@app.get("/platforms/youtube/status")
def youtube_status(user_id: str):
    user_id = user_id.strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    try:
        return {"success": True, **get_connection_status(user_id)}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Could not get YouTube status: {error}")


@app.post("/platforms/youtube/disconnect")
def youtube_disconnect(user_id: str):
    user_id = user_id.strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    try:
        return {"success": True, **disconnect_youtube(user_id)}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"YouTube disconnect failed: {error}")


# ============================================================


def save_youtube_publishing_record(
    *,
    project,
    user_id,
    title,
    status,
    youtube_result,
    scheduled_at=None,
):
    """Persist a real YouTube publish/schedule operation in FrameCraft."""
    posts = get_publishing_posts()
    now = now_iso()
    post = {
        "id": f"youtube_{uuid.uuid4().hex[:10]}",
        "project_id": project.get("id"),
        "project_name": project.get("name"),
        "title": title,
        "platform": "YouTube",
        "status": status,
        "user_id": user_id,
        "youtube_video_id": youtube_result.get("video_id"),
        "youtube_url": youtube_result.get("video_url"),
        "scheduled_at": scheduled_at or youtube_result.get("publish_at"),
        "published_at": now if status == "Published" else None,
        "created_at": now,
        "updated_at": now,
    }
    posts.append(post)
    save_publishing_posts(posts)
    return post

# YOUTUBE VIDEO PUBLISHING
# ============================================================


@app.post("/platforms/youtube/publish")
def youtube_publish(request: YouTubePublishRequest):
    """Upload a generated FrameCraft MP4 and publish it immediately to YouTube."""
    user_id = request.user_id.strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    project_id = request.project_id.strip()
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id is required")

    title = request.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required")

    project = get_project_or_404(project_id)
    video = find_generated_video(project, request.video_id)
    if video is None:
        raise HTTPException(
            status_code=404,
            detail="Generated MP4 video not found in project",
        )

    video_path = Path(video["path"])
    try:
        result = publish_video_now(
            user_id=user_id,
            video_path=str(video_path),
            title=title,
            description=request.description,
            tags=request.tags,
            category_id=request.category_id,
        )
        post = save_youtube_publishing_record(
            project=project,
            user_id=user_id,
            title=title,
            status="Published",
            youtube_result=result,
        )
        project["updated_at"] = now_iso()
        save_project_workspace(project)
        save_knowledge()

        return {
            "success": True,
            "message": "Video published to YouTube successfully.",
            "project_id": project_id,
            "video": video,
            "youtube": result,
            "post": post,
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"YouTube publish failed: {error}",
        )


@app.post("/platforms/youtube/schedule")
def youtube_schedule(request: YouTubeScheduleRequest):
    """Upload a generated FrameCraft MP4 and schedule it on YouTube."""
    user_id = request.user_id.strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    project_id = request.project_id.strip()
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id is required")

    title = request.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required")

    if not request.scheduled_at.strip():
        raise HTTPException(status_code=400, detail="scheduled_at is required")

    project = get_project_or_404(project_id)
    video = find_generated_video(project, request.video_id)
    if video is None:
        raise HTTPException(
            status_code=404,
            detail="Generated MP4 video not found in project",
        )

    video_path = Path(video["path"])
    try:
        result = schedule_video(
            user_id=user_id,
            video_path=str(video_path),
            title=title,
            description=request.description,
            tags=request.tags,
            category_id=request.category_id,
            scheduled_at=request.scheduled_at,
        )
        post = save_youtube_publishing_record(
            project=project,
            user_id=user_id,
            title=title,
            status="Scheduled",
            youtube_result=result,
            scheduled_at=result.get("publish_at") or request.scheduled_at,
        )
        project["updated_at"] = now_iso()
        save_project_workspace(project)
        save_knowledge()

        return {
            "success": True,
            "message": "Video uploaded and scheduled successfully on YouTube.",
            "project_id": project_id,
            "video": video,
            "youtube": result,
            "post": post,
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"YouTube scheduling failed: {error}",
        )


@app.get("/platforms/youtube/video/{youtube_video_id}/status")
def youtube_video_status(
    youtube_video_id: str,
    user_id: str = "demo_user",
):
    """Return the current YouTube processing/publication status for a video."""
    user_id = user_id.strip()
    youtube_video_id = youtube_video_id.strip()

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    if not youtube_video_id:
        raise HTTPException(status_code=400, detail="youtube_video_id is required")

    try:
        result = get_youtube_video_status(
            user_id=user_id,
            video_id=youtube_video_id,
        )
        return {
            "success": True,
            "youtube_video_id": youtube_video_id,
            "youtube": result,
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not get YouTube video status: {error}",
        )


# ============================================================




@app.post("/publishing/sync-youtube")
def sync_youtube_publishing_status(user_id: str = "demo_user"):
    """
    Reconcile FrameCraft publishing records with the current YouTube status.
    Scheduled records become Published when YouTube reports privacyStatus=public.
    """
    user_id = user_id.strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    posts = get_publishing_posts()
    changed = 0
    synced = []

    for post in posts:
        if post.get("platform") != "YouTube":
            continue

        youtube_video_id = str(post.get("youtube_video_id") or "").strip()
        if not youtube_video_id:
            continue

        try:
            youtube_status = get_youtube_video_status(
                user_id=user_id,
                video_id=youtube_video_id,
            )
        except Exception as error:
            synced.append({
                "post_id": post.get("id"),
                "youtube_video_id": youtube_video_id,
                "error": str(error),
            })
            continue

        privacy_status = youtube_status.get("privacy_status")
        upload_status = youtube_status.get("upload_status")

        previous_status = post.get("status")

        if privacy_status == "public":
            post["status"] = "Published"
            if not post.get("published_at"):
                post["published_at"] = now_iso()
        elif previous_status == "Published" and privacy_status != "public":
            # Keep an already-published FrameCraft record stable unless YouTube
            # explicitly reports a different state that we know how to represent.
            pass
        elif post.get("scheduled_at"):
            post["status"] = "Scheduled"

        post["youtube_status"] = {
            "privacy_status": privacy_status,
            "upload_status": upload_status,
            "publish_at": youtube_status.get("publish_at"),
        }
        post["updated_at"] = now_iso()

        if post.get("status") != previous_status:
            changed += 1

        synced.append({
            "post_id": post.get("id"),
            "youtube_video_id": youtube_video_id,
            "status": post.get("status"),
            "privacy_status": privacy_status,
            "upload_status": upload_status,
        })

    save_publishing_posts(posts)

    return {
        "success": True,
        "changed": changed,
        "posts": posts,
        "synced": synced,
    }


@app.get("/platforms/youtube/video/{video_id}/comments")
def youtube_video_comments(
    video_id: str,
    user_id: str = "demo_user",
    max_results: int = 100,
):
    """Fetch comments from a YouTube video for FrameCraft analysis."""
    user_id = user_id.strip()
    video_id = video_id.strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not video_id:
        raise HTTPException(status_code=400, detail="video_id is required")
    try:
        return get_youtube_video_comments(
            user_id=user_id,
            video_id=video_id,
            max_results=max_results,
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not fetch YouTube comments: {type(error).__name__}: {error}",
        )


# CUSTOM OPENAPI

# ============================================================



def custom_openapi():



    if app.openapi_schema:

        return app.openapi_schema



    schema = get_openapi(

        title=app.title,

        version=app.version,

        description=app.description,

        routes=app.routes,

    )



    components = (

        schema

        .get("components", {})

        .get("schemas", {})

    )



    for component in components.values():



        properties = component.get(

            "properties",

            {},

        )



        for prop in properties.values():



            if (

                prop.get("type") == "string"

                and prop.get(

                    "contentMediaType"

                ) == "application/octet-stream"

            ):



                prop.pop(

                    "contentMediaType",

                    None,

                )



                prop["format"] = "binary"



            items = prop.get("items")



            if isinstance(items, dict):



                if (

                    items.get(

                        "contentMediaType"

                    )

                    == "application/octet-stream"

                ):



                    items.pop(

                        "contentMediaType",

                        None,

                    )



                    items["type"] = "string"

                    items["format"] = "binary"



    app.openapi_schema = schema



    return app.openapi_schema





app.openapi = custom_openapi
