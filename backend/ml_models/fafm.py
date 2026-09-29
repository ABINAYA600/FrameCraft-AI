from typing import Dict, Any, Optional
import os


class FAFM:
    """
    FrameCraft AI Foundation Model (FAFM)

    Central orchestration and intelligence layer for FrameCraft AI.

    FAFM coordinates:
        - Script Model
        - Comment Reply Pipeline
        - Creator Profile Analyzer
        - Media Retrieval
        - Music Manager
        - Decision Engine
        - Thumbnail Generator
        - Metadata Generator
        - Video Composer

    FAFM is an orchestration layer over specialized models/services.
    """

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):

        print("=" * 60)
        print("Initializing FrameCraft AI Foundation Model...")
        print("=" * 60)

        # -----------------------------------------------------
        # Module references
        # -----------------------------------------------------

        self.script_model = None
        self.comment_pipeline = None
        self.creator_profile_analyzer = None

        self.media_retrieval = None
        self.music_manager = None
        self.decision_engine = None
        self.thumbnail_generator = None
        self.metadata_generator = None
        self.video_composer = None

        # -----------------------------------------------------
        # Initialize modules
        # -----------------------------------------------------

        self._initialize_modules()

        print("=" * 60)
        print("FAFM Initialized Successfully!")
        print("=" * 60)

    # =========================================================
    # MODULE INITIALIZATION
    # =========================================================

    def _initialize_modules(self):

        # -----------------------------------------------------
        # SCRIPT MODEL
        # -----------------------------------------------------

        try:

            print("Loading Script Model...")

            from ml_models.script_model import ScriptModel

            self.script_model = ScriptModel()

            print("✓ Script Model ready")

        except Exception as e:

            print(
                f"⚠ Script Model unavailable: "
                f"{type(e).__name__}: {str(e)}"
            )

        # -----------------------------------------------------
        # COMMENT REPLY PIPELINE
        # -----------------------------------------------------

        try:

            from app.services.comment_reply_pipeline import (
                CommentReplyPipeline
            )

            self.comment_pipeline = CommentReplyPipeline()

            print("✓ Comment Reply Pipeline ready")

        except Exception as e:

            print(
                f"⚠ Comment Reply Pipeline unavailable: "
                f"{type(e).__name__}: {str(e)}"
            )

        # -----------------------------------------------------
        # CREATOR PROFILE ANALYZER
        # -----------------------------------------------------

        try:

            from app.services.creator_profile_analyzer import (
                CreatorProfileAnalyzer
            )

            self.creator_profile_analyzer = (
                CreatorProfileAnalyzer()
            )

            print("✓ Creator Profile Analyzer ready")

        except Exception as e:

            print(
                f"⚠ Creator Profile Analyzer unavailable: "
                f"{type(e).__name__}: {str(e)}"
            )

        # -----------------------------------------------------
        # MEDIA RETRIEVAL
        # -----------------------------------------------------

        try:

            from app.services.media_retrieval import MediaRetrieval

            self.media_retrieval = MediaRetrieval()

            print("✓ Media Retrieval ready")

        except Exception as e:

            print(
                f"⚠ Media Retrieval unavailable: "
                f"{type(e).__name__}: {str(e)}"
            )

        # -----------------------------------------------------
        # MUSIC MANAGER
        # -----------------------------------------------------

        try:

            from app.services.music_manager import MusicManager

            self.music_manager = MusicManager()

            print("✓ Music Manager ready")

        except Exception as e:

            print(
                f"⚠ Music Manager unavailable: "
                f"{type(e).__name__}: {str(e)}"
            )

        # -----------------------------------------------------
        # DECISION ENGINE
        # -----------------------------------------------------

        try:

            from ml_models.decision_engine import DecisionEngine

            self.decision_engine = DecisionEngine()

            print("✓ Decision Engine ready")

        except Exception as e:

            print(
                f"⚠ Decision Engine unavailable: "
                f"{type(e).__name__}: {str(e)}"
            )

        # -----------------------------------------------------
        # THUMBNAIL GENERATOR
        # -----------------------------------------------------

        try:

            from app.services.thumbnail_generator import (
                ThumbnailGenerator
            )

            self.thumbnail_generator = ThumbnailGenerator()

            print("✓ Thumbnail Generator ready")

        except Exception as e:

            print(
                f"⚠ Thumbnail Generator unavailable: "
                f"{type(e).__name__}: {str(e)}"
            )

        # -----------------------------------------------------
        # METADATA GENERATOR
        # -----------------------------------------------------

        try:

            from app.services.metadata_generator import (
                MetadataGenerator
            )

            self.metadata_generator = MetadataGenerator()

            print("✓ Metadata Generator ready")

        except Exception as e:

            print(
                f"⚠ Metadata Generator unavailable: "
                f"{type(e).__name__}: {str(e)}"
            )

        # -----------------------------------------------------
        # VIDEO COMPOSER
        # -----------------------------------------------------

        try:

            from ml_models.video_composer import VideoComposer

            self.video_composer = VideoComposer()

            print("✓ Video Composer ready")

        except Exception as e:

            print(
                f"⚠ Video Composer unavailable: "
                f"{type(e).__name__}: {str(e)}"
            )

    # =========================================================
    # JSON SAFE CONVERSION
    # =========================================================

    def _make_json_safe(self, value):

        """
        Convert NumPy and other non-JSON-native values into
        standard Python objects.

        This is required because FastAPI cannot directly serialize
        NumPy arrays returned by the Script Model.
        """

        # -----------------------------------------------------
        # None
        # -----------------------------------------------------

        if value is None:
            return None

        # -----------------------------------------------------
        # Dictionary
        # -----------------------------------------------------

        if isinstance(value, dict):

            return {
                str(key): self._make_json_safe(item)
                for key, item in value.items()
            }

        # -----------------------------------------------------
        # List
        # -----------------------------------------------------

        if isinstance(value, list):

            return [
                self._make_json_safe(item)
                for item in value
            ]

        # -----------------------------------------------------
        # Tuple
        # -----------------------------------------------------

        if isinstance(value, tuple):

            return [
                self._make_json_safe(item)
                for item in value
            ]

        # -----------------------------------------------------
        # NumPy arrays / scalars
        # -----------------------------------------------------

        if hasattr(value, "tolist"):

            try:

                converted = value.tolist()

                return self._make_json_safe(converted)

            except Exception:
                pass

        # -----------------------------------------------------
        # Path-like objects
        # -----------------------------------------------------

        if hasattr(value, "__fspath__"):

            try:
                return os.fspath(value)
            except Exception:
                pass

        # -----------------------------------------------------
        # Primitive values
        # -----------------------------------------------------

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool
            )
        ):

            return value

        # -----------------------------------------------------
        # Final fallback
        # -----------------------------------------------------

        return str(value)

    # =========================================================
    # SCRIPT PROCESSING
    # =========================================================

    def process_script(
        self,
        script: str
    ) -> Dict[str, Any]:

        if not script or not script.strip():

            return {
                "success": False,
                "error": "Script cannot be empty."
            }

        if self.script_model is None:

            return {
                "success": False,
                "error": "Script model is unavailable."
            }

        try:

            print("\nProcessing script...")

            result = self.script_model.process(script)

            # -------------------------------------------------
            # ScriptModel normally returns:
            #
            # scenes, embeddings
            #
            # But support dictionary output too.
            # -------------------------------------------------

            if isinstance(result, dict):

                scenes = result.get(
                    "scenes",
                    []
                )

                embeddings = result.get(
                    "embeddings"
                )

            else:

                scenes, embeddings = result

            # -------------------------------------------------
            # Embedding shape
            # -------------------------------------------------

            try:

                embedding_shape = embeddings.shape

            except AttributeError:

                embedding_shape = None

            print(
                f"✓ Generated {len(scenes)} scenes"
            )

            return {
                "success": True,
                "scenes": scenes,
                "scene_count": len(scenes),
                "embeddings": embeddings,
                "embedding_shape": embedding_shape
            }

        except Exception as e:

            return {
                "success": False,
                "error": (
                    f"Script processing failed: "
                    f"{type(e).__name__}: {str(e)}"
                )
            }

    # =========================================================
    # MEDIA RETRIEVAL
    # =========================================================

    def retrieve_media(
        self,
        scenes,
        top_k: int = 5
    ):

        if self.media_retrieval is None:

            return []

        try:

            return self.media_retrieval.process(
                scenes,
                top_k=top_k
            )

        except Exception as e:

            print(
                f"Media retrieval failed: "
                f"{type(e).__name__}: {str(e)}"
            )

            return []

    # =========================================================
    # STORYBOARD CREATION
    # =========================================================

    def create_storyboard(
        self,
        scenes
    ):

        if self.decision_engine is None:

            return []

        try:

            storyboard = self.decision_engine.process(
                scenes
            )

            return storyboard

        except Exception as e:

            print(
                f"Storyboard creation failed: "
                f"{type(e).__name__}: {str(e)}"
            )

            return []

    # =========================================================
    # MUSIC RECOMMENDATION
    # =========================================================

    def recommend_music(
        self,
        mood: str,
        energy: Optional[str] = None
    ):

        if self.music_manager is None:

            return []

        try:

            return self.music_manager.recommend_music(
                mood,
                energy
            )

        except Exception as e:

            print(
                f"Music recommendation failed: "
                f"{type(e).__name__}: {str(e)}"
            )

            return []

    # =========================================================
    # VIDEO COMPOSITION
    # =========================================================

    def compose_video(
        self,
        storyboard,
        music_path=None,
        output_name="framecraft_output.mp4",
        generate_thumbnail=False,
        thumbnail_title=None,
        return_metadata=False
    ):

        if self.video_composer is None:

            return None

        try:

            video_result = self.video_composer.compose(
                storyboard=storyboard,
                music_path=music_path,
                output_name=output_name,
                generate_thumbnail=False,
                thumbnail_title=thumbnail_title,
                return_metadata=return_metadata
            )

            return video_result

        except Exception as e:

            print(
                f"Video composition failed: "
                f"{type(e).__name__}: {str(e)}"
            )

            return None

    # =========================================================
    # COMPLETE CONTENT GENERATION
    # =========================================================

    def generate_content(
        self,
        script: str,
        music_path=None,
        output_name="framecraft_output.mp4",
        top_k=5,
        generate_thumbnail=True,
        thumbnail_title=None
    ):

        print("\n")
        print("=" * 60)
        print("FRAMECRAFT AI CONTENT GENERATION")
        print("=" * 60)

        # =====================================================
        # 1. SCRIPT PROCESSING
        # =====================================================

        print("\n[1/6] Processing script...")

        script_result = self.process_script(
            script
        )

        if not script_result.get("success"):

            return script_result

        scenes = script_result["scenes"]
        embeddings = script_result["embeddings"]
        embedding_shape = script_result["embedding_shape"]

        # =====================================================
        # 2. STORYBOARD
        # =====================================================

        print("\n[2/6] Creating storyboard...")

        storyboard = self.create_storyboard(
            scenes
        )

        print(
            f"✓ Storyboard created with "
            f"{len(storyboard)} scenes"
        )

        # =====================================================
        # 3. MUSIC
        # =====================================================

        print(
            "\n[3/6] Selecting background music..."
        )

        music_result = {
            "mood": None,
            "music": None,
            "path": None
        }

        selected_music_path = music_path

        try:

            from ml_models.music_model import MusicModel

            print("Loading Music Model...")

            music_model = MusicModel()

            print("Music Model Loaded Successfully!")

            music_result = music_model.select_music(
                script
            )

            print(
                f"✓ Detected mood: "
                f"{music_result.get('mood')}"
            )

            print(
                f"✓ Using music: "
                f"{music_result.get('path')}"
            )

            # -------------------------------------------------
            # Use supplied music if provided.
            # Otherwise use MusicModel selection.
            # -------------------------------------------------

            if selected_music_path is None:

                selected_music_path = (
                    music_result.get("path")
                )

            # -------------------------------------------------
            # Prefer WAV when an equivalent WAV exists.
            #
            # MoviePy/FFmpeg was more reliable with WAV in
            # the current FrameCraft environment.
            # -------------------------------------------------

            if selected_music_path:

                base_path, extension = os.path.splitext(
                    selected_music_path
                )

                wav_path = base_path + ".wav"

                if os.path.exists(wav_path):

                    selected_music_path = wav_path

        except Exception as e:

            print(
                f"⚠ Music selection failed: "
                f"{type(e).__name__}: {str(e)}"
            )

        # =====================================================
        # 4. VIDEO COMPOSITION
        # =====================================================

        print(
            "\n[4/6] Composing final video..."
        )

        video_result = self.compose_video(
            storyboard=storyboard,
            music_path=selected_music_path,
            output_name=output_name,
            generate_thumbnail=False,
            thumbnail_title=thumbnail_title,
            return_metadata=True
        )

        if video_result is None:

            return {
                "success": False,
                "error": "Video composition failed."
            }

        print(
            f"✓ Video created: "
            f"{video_result}"
        )

        # -----------------------------------------------------
        # Normalize video output path
        # -----------------------------------------------------

        video_output = video_result

        if isinstance(video_result, dict):

            video_output = (
                video_result.get("output")
                or video_result.get("path")
                or video_result.get("video")
            )

        # =====================================================
        # 5. THUMBNAIL
        # =====================================================

        print(
            "\n[5/6] Generating AI thumbnail..."
        )

        thumbnail_path = None
        thumbnail_metadata_path = None

        if (
            generate_thumbnail
            and self.thumbnail_generator is not None
            and video_output
            and os.path.exists(video_output)
        ):

            try:

                thumbnail_path = (
                    self.thumbnail_generator.create_thumbnail(
                        video_path=video_output,
                        output_name="framecraft_thumbnail.jpg",
                        title=thumbnail_title,
                        candidate_count=12
                    )
                )

                print(
                    f"✓ Thumbnail created: "
                    f"{thumbnail_path}"
                )

                thumbnail_metadata_path = os.path.join(
                    "output",
                    "thumbnail_metadata.json"
                )

            except Exception as e:

                print(
                    f"⚠ Thumbnail generation failed: "
                    f"{type(e).__name__}: {str(e)}"
                )

        # =====================================================
        # 6. METADATA
        # =====================================================

        print(
            "\n[6/6] Generating video metadata..."
        )

        metadata = None
        metadata_path = None

        if self.metadata_generator is not None:

            try:

                metadata = (
                    self.metadata_generator.generate_metadata(
                        storyboard=storyboard,
                        requested_title=thumbnail_title,
                        platform="youtube"
                    )
                )

                metadata_path = (
                    self.metadata_generator.save_metadata(
                        metadata,
                        output_name="framecraft_metadata.json"
                    )
                )

                print(
                    f"✓ Metadata created: "
                    f"{metadata_path}"
                )

            except Exception as e:

                print(
                    f"⚠ Metadata generation failed: "
                    f"{type(e).__name__}: {str(e)}"
                )

        # =====================================================
        # FINAL RESULT
        # =====================================================

        print("\n")
        print("=" * 60)
        print("FRAMECRAFT AI GENERATION COMPLETE")
        print("=" * 60)

        result = {
            "success": True,

            "script": script,

            "scenes": scenes,

            "scene_count": len(scenes),

            "embeddings": embeddings,

            "embedding_shape": embedding_shape,

            "storyboard": storyboard,

            "music": music_result,

            "music_path": selected_music_path,

            "video": video_result,

            "thumbnail": thumbnail_path,

            "thumbnail_metadata": thumbnail_metadata_path,

            "metadata": metadata,

            "metadata_path": metadata_path
        }

        # =====================================================
        # IMPORTANT:
        #
        # Convert NumPy arrays / tuples / NumPy scalar values
        # into JSON-safe Python objects before returning.
        #
        # This fixes the FastAPI 500 error.
        # =====================================================

        return self._make_json_safe(
            result
        )


    # =========================================================
    # PROJECT CONTENT GENERATION
    # =========================================================

    def generate_project_content(
        self,
        project,
        output_path,
        generate_thumbnail=True,
        thumbnail_title=None,
    ):
        """
        Generate content for a saved FrameCraft project.

        media_source:
            uploaded -> use creator-uploaded images/videos
            ai       -> use existing AI media retrieval
            both     -> use uploaded media first and AI media for
                        remaining scenes
        """

        import shutil
        from pathlib import Path

        if not project:
            raise ValueError("Project data is required.")

        script = (project.get("script") or "").strip()

        if not script:
            raise ValueError(
                "Project script is empty. Add a script before generating."
            )

        media_source = project.get("media_source", "both")
        if media_source not in {"uploaded", "ai", "both"}:
            media_source = "both"

        # -----------------------------------------------------
        # 1. Process script
        # -----------------------------------------------------

        script_result = self.process_script(script)

        if not script_result.get("success"):
            raise ValueError(
                script_result.get(
                    "error",
                    "Script processing failed."
                )
            )

        scenes = script_result.get("scenes", [])
        if not scenes:
            raise ValueError("No scenes could be generated from the script.")

        # -----------------------------------------------------
        # 2. Create normal AI storyboard
        # -----------------------------------------------------

        storyboard = self.create_storyboard(scenes)

        if not storyboard:
            raise ValueError("Unable to create storyboard.")

        # -----------------------------------------------------
        # 3. Collect valid uploaded visual media
        # -----------------------------------------------------

        uploaded_media = []

        for media_type in ("videos", "images"):
            for item in project.get(media_type, []) or []:
                path = item.get("path")
                if not path:
                    continue

                media_path = Path(path)
                if not media_path.exists():
                    continue

                composer_type = "video" if media_type == "videos" else "image"

                uploaded_media.append({
                    "id": item.get("id"),
                    "path": str(media_path),
                    "media_type": composer_type,
                    "name": item.get("name", media_path.name),
                })

        # -----------------------------------------------------
        # 4. Apply project media preference
        # -----------------------------------------------------

        if media_source == "uploaded":
            if not uploaded_media:
                raise ValueError(
                    "This project is set to use uploaded media, "
                    "but no valid uploaded images or videos were found."
                )
            storyboard = self._apply_uploaded_media(
                storyboard,
                uploaded_media,
                replace_all=True,
            )

        elif media_source == "both" and uploaded_media:
            storyboard = self._apply_uploaded_media(
                storyboard,
                uploaded_media,
                replace_all=False,
            )

        # -----------------------------------------------------
        # 5. Select music
        # -----------------------------------------------------

        selected_music_path = None
        music_mode = str(project.get("music_mode", "ai")).lower().strip()
        selected_music_id = project.get("selected_music_id")

        music_result = {
            "mood": None,
            "music": None,
            "path": None,
            "source": music_mode,
        }

        # -----------------------------------------------------
        # AI SELECT
        # -----------------------------------------------------
        if music_mode == "ai":
            try:
                from ml_models.music_model import MusicModel

                music_model = MusicModel()
                music_result = music_model.select_music(script)
                selected_music_path = music_result.get("path")
                music_result["source"] = "ai"

            except Exception as error:
                print(
                    f"⚠ AI music selection failed: "
                    f"{type(error).__name__}: {str(error)}"
                )

        # -----------------------------------------------------
        # MY MUSIC / UPLOADED
        # -----------------------------------------------------
        elif music_mode == "uploaded":
            for item in project.get("music", []) or []:
                path = item.get("path")
                if path and Path(path).exists():
                    selected_music_path = str(Path(path))
                    music_result = {
                        "mood": item.get("mood"),
                        "music": item.get("name") or item.get("filename"),
                        "path": selected_music_path,
                        "source": "uploaded",
                    }
                    break

        # -----------------------------------------------------
        # SEARCH MUSIC
        # -----------------------------------------------------
        elif music_mode == "search":
            # Search results are selected by ID and persisted in the
            # project. The actual audio must exist in the local/approved
            # FrameCraft catalog or project music collection.
            for item in project.get("music", []) or []:
                item_id = item.get("id") or item.get("music_id") or item.get("filename")
                if selected_music_id and item_id == selected_music_id:
                    path = item.get("path")
                    if path and Path(path).exists():
                        selected_music_path = str(Path(path))
                        music_result = {
                            "mood": item.get("mood"),
                            "music": item.get("name") or item.get("filename"),
                            "path": selected_music_path,
                            "source": "search",
                        }
                        break

            # If the selected catalog ID was not part of project media,
            # resolve it from the FrameCraft catalog.
            if selected_music_path is None and selected_music_id:
                music_dir = Path("datasets/music")
                for candidate in music_dir.iterdir() if music_dir.exists() else []:
                    if candidate.stem == str(selected_music_id) and candidate.is_file():
                        selected_music_path = str(candidate)
                        music_result = {
                            "mood": None,
                            "music": candidate.stem,
                            "path": selected_music_path,
                            "source": "search",
                        }
                        break

        # -----------------------------------------------------
        # Normalize to WAV when an equivalent WAV exists.
        # -----------------------------------------------------
        if selected_music_path:
            base_path, _ = os.path.splitext(selected_music_path)
            wav_path = base_path + ".wav"
            if os.path.exists(wav_path):
                selected_music_path = wav_path
                music_result["path"] = wav_path

        print(
            f"🎵 Music mode: {music_mode} | "
            f"Selected: {selected_music_path}"
        )

        # -----------------------------------------------------
        # 6. Compose video
        # -----------------------------------------------------

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        video_result = self.compose_video(
            storyboard=storyboard,
            music_path=selected_music_path,
            output_name=output_path.name,
            generate_thumbnail=False,
            thumbnail_title=thumbnail_title,
            return_metadata=True,
        )

        if video_result is None:
            raise RuntimeError("Video composition failed.")

        video_output = video_result
        if isinstance(video_result, dict):
            video_output = (
                video_result.get("output")
                or video_result.get("path")
                or video_result.get("video")
            )

        if not video_output:
            raise RuntimeError("Video Composer returned no output path.")

        video_output = Path(video_output)

        if not video_output.exists():
            raise RuntimeError(
                f"Generated video was not found: {video_output}"
            )

        # VideoComposer writes to its own output folder. Copy the
        # finished artifact into this project's generated folder.
        if video_output.resolve() != output_path.resolve():
            shutil.copy2(video_output, output_path)

        # -----------------------------------------------------
        # 7. Thumbnail
        # -----------------------------------------------------

        thumbnail_path = None
        thumbnail_metadata_path = None

        if (
            generate_thumbnail
            and self.thumbnail_generator is not None
            and output_path.exists()
        ):
            try:
                title = thumbnail_title or project.get("name") or "FrameCraft AI"
                thumbnail_name = f"{output_path.stem}_thumbnail.jpg"
                thumbnail_path = self.thumbnail_generator.create_thumbnail(
                    video_path=str(output_path),
                    output_name=thumbnail_name,
                    title=title,
                    candidate_count=12,
                )

                if thumbnail_path:
                    thumbnail_path = Path(thumbnail_path)
                    target_thumbnail = output_path.parent / thumbnail_name
                    if thumbnail_path.exists() and thumbnail_path.resolve() != target_thumbnail.resolve():
                        shutil.copy2(thumbnail_path, target_thumbnail)
                    thumbnail_path = target_thumbnail

                    source_meta = thumbnail_path.parent / "thumbnail_metadata.json"
                    if source_meta.exists():
                        target_meta = output_path.parent / f"{output_path.stem}_thumbnail_metadata.json"
                        if source_meta.resolve() != target_meta.resolve():
                            shutil.copy2(source_meta, target_meta)
                        thumbnail_metadata_path = target_meta

            except Exception as error:
                print(
                    f"⚠ Project thumbnail generation failed: "
                    f"{type(error).__name__}: {str(error)}"
                )

        # -----------------------------------------------------
        # 8. Metadata
        # -----------------------------------------------------

        metadata = None
        metadata_path = None

        if self.metadata_generator is not None:
            try:
                metadata = self.metadata_generator.generate_metadata(
                    storyboard=storyboard,
                    requested_title=(
                        thumbnail_title
                        or project.get("name")
                    ),
                    platform="youtube",
                )

                metadata_path = (
                    output_path.parent
                    / f"{output_path.stem}_metadata.json"
                )

                self.metadata_generator.save_metadata(
                    metadata,
                    output_path=str(metadata_path),
                )

            except Exception as error:
                print(
                    f"⚠ Project metadata generation failed: "
                    f"{type(error).__name__}: {str(error)}"
                )

        # -----------------------------------------------------
        # 9. Return JSON-safe result
        # -----------------------------------------------------

        result = {
            "success": True,
            "project_id": project.get("id"),
            "project_name": project.get("name"),
            "media_source": media_source,
            "script": script,
            "scenes": scenes,
            "scene_count": len(scenes),
            "storyboard": storyboard,
            "music": music_result,
            "music_path": selected_music_path,
            "video": str(output_path),
            "video_path": str(output_path),
            "thumbnail": str(thumbnail_path) if thumbnail_path else None,
            "thumbnail_metadata": (
                str(thumbnail_metadata_path)
                if thumbnail_metadata_path
                else None
            ),
            "metadata": metadata,
            "metadata_path": str(metadata_path) if metadata_path else None,
        }

        return self._make_json_safe(result)

    def _apply_uploaded_media(
        self,
        storyboard,
        uploaded_media,
        replace_all=False,
    ):
        """Apply uploaded project media to storyboard scenes."""

        if not uploaded_media:
            return storyboard

        result = []

        for index, scene in enumerate(storyboard):
            scene_copy = dict(scene)

            if replace_all:
                media = uploaded_media[index % len(uploaded_media)]
            elif index < len(uploaded_media):
                media = uploaded_media[index]
            else:
                result.append(scene_copy)
                continue

            scene_copy["media_type"] = media["media_type"]
            scene_copy["media_path"] = media["path"]
            scene_copy["source"] = "uploaded"
            scene_copy["uploaded_media_id"] = media.get("id")
            scene_copy["uploaded_media_name"] = media.get("name")

            # Keep the original scene duration/transition/camera settings.
            result.append(scene_copy)

        return result

    # =========================================================
    # COMMENT PROCESSING
    # =========================================================

    def process_comment(
        self,
        comment: str,
        creator_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        if not comment or not comment.strip():

            return {
                "success": False,
                "error": "Comment cannot be empty."
            }

        if self.comment_pipeline is None:

            return {
                "success": False,
                "error": "Comment pipeline is unavailable."
            }

        try:

            # -------------------------------------------------
            # Update creator profile if provided
            # -------------------------------------------------

            if creator_profile:

                self.comment_pipeline.creator_profile = (
                    creator_profile
                )

                if hasattr(
                    self.comment_pipeline,
                    "analyzer"
                ):

                    self.comment_pipeline.analyzer.creator_profile = (
                        creator_profile
                    )

            # -------------------------------------------------
            # Process comment
            # -------------------------------------------------

            result = (
                self.comment_pipeline.process_comment(
                    comment
                )
            )

            return result

        except Exception as e:

            return {
                "success": False,
                "error": (
                    f"Comment processing failed: "
                    f"{type(e).__name__}: {str(e)}"
                )
            }

    # =========================================================
    # CREATOR ANALYSIS
    # =========================================================

    def analyze_creator(
        self,
        transcripts=None,
        comments=None,
        captions=None,
        creator_settings=None
    ) -> Dict[str, Any]:

        if self.creator_profile_analyzer is None:

            return {
                "success": False,
                "error": (
                    "Creator Profile Analyzer "
                    "is unavailable."
                )
            }

        try:

            print(
                "\nAnalyzing creator profile..."
            )

            profile = (
                self.creator_profile_analyzer.analyze(
                    transcripts=transcripts or [],
                    comments=comments or [],
                    captions=captions or [],
                    creator_settings=(
                        creator_settings or {}
                    )
                )
            )

            # -------------------------------------------------
            # Synchronize comment pipeline
            # -------------------------------------------------

            if self.comment_pipeline is not None:

                self.comment_pipeline.creator_profile = (
                    profile
                )

                if hasattr(
                    self.comment_pipeline,
                    "analyzer"
                ):

                    self.comment_pipeline.analyzer.creator_profile = (
                        profile
                    )

            return {
                "success": True,
                "creator_profile": profile
            }

        except Exception as e:

            return {
                "success": False,
                "error": (
                    f"Creator analysis failed: "
                    f"{type(e).__name__}: {str(e)}"
                )
            }

    # =========================================================
    # APPROVE REPLY
    # =========================================================

    def approve_reply(
        self,
        reply_id: str
    ) -> Dict[str, Any]:

        if self.comment_pipeline is None:

            return {
                "success": False,
                "error": "Comment pipeline unavailable."
            }

        try:

            return self.comment_pipeline.approve(
                reply_id
            )

        except Exception as e:

            return {
                "success": False,
                "error": (
                    f"Reply approval failed: "
                    f"{type(e).__name__}: {str(e)}"
                )
            }

    # =========================================================
    # REJECT REPLY
    # =========================================================

    def reject_reply(
        self,
        reply_id: str
    ) -> Dict[str, Any]:

        if self.comment_pipeline is None:

            return {
                "success": False,
                "error": "Comment pipeline unavailable."
            }

        try:

            return self.comment_pipeline.reject(
                reply_id
            )

        except Exception as e:

            return {
                "success": False,
                "error": (
                    f"Reply rejection failed: "
                    f"{type(e).__name__}: {str(e)}"
                )
            }

    # =========================================================
    # PENDING REPLIES
    # =========================================================

    def pending_replies(self):

        if self.comment_pipeline is None:

            return []

        try:

            return (
                self.comment_pipeline.pending_replies()
            )

        except Exception as e:

            print(
                f"Could not retrieve pending replies: {e}"
            )

            return []

    # =========================================================
    # ALL REPLIES
    # =========================================================

    def all_replies(self):

        if self.comment_pipeline is None:

            return []

        try:

            return (
                self.comment_pipeline.all_replies()
            )

        except Exception as e:

            print(
                f"Could not retrieve replies: {e}"
            )

            return []

    # =========================================================
    # SYSTEM STATUS
    # =========================================================

    def get_system_status(self):

        return {

            "fafm": "ready",

            "script_model": (
                "ready"
                if self.script_model
                else "unavailable"
            ),

            "comment_reply_pipeline": (
                "ready"
                if self.comment_pipeline
                else "unavailable"
            ),

            "creator_profile_analyzer": (
                "ready"
                if self.creator_profile_analyzer
                else "unavailable"
            ),

            "media_retrieval": (
                "ready"
                if self.media_retrieval
                else "unavailable"
            ),

            "music_manager": (
                "ready"
                if self.music_manager
                else "unavailable"
            ),

            "decision_engine": (
                "ready"
                if self.decision_engine
                else "unavailable"
            ),

            "thumbnail_generator": (
                "ready"
                if self.thumbnail_generator
                else "unavailable"
            ),

            "metadata_generator": (
                "ready"
                if self.metadata_generator
                else "unavailable"
            ),

            "video_composer": (
                "ready"
                if self.video_composer
                else "unavailable"
            )
        }


# =============================================================
# SINGLETON FAFM INSTANCE
# =============================================================

_fafm_instance = None


def get_fafm() -> FAFM:

    global _fafm_instance

    if _fafm_instance is None:

        _fafm_instance = FAFM()

    return _fafm_instance