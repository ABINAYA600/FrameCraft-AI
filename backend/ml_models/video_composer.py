import os

from moviepy import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    concatenate_audioclips
)


class VideoComposer:

    def __init__(self):

        print("Video Composer Initialized!")

        self.output_folder = "output"

        os.makedirs(
            self.output_folder,
            exist_ok=True
        )

    # ==================================================
    # LOAD VIDEO
    # ==================================================

    def load_video(self, path, duration=5):

        print(
            f"Loading video: {path}"
        )

        clip = VideoFileClip(path)

        if clip.duration > duration:

            clip = clip.subclipped(
                0,
                duration
            )

        return clip

    # ==================================================
    # LOAD IMAGE
    # ==================================================

    def load_image(self, path, duration=5):

        print(
            f"Loading image: {path}"
        )

        return (
            ImageClip(path)
            .with_duration(duration)
        )

    # ==================================================
    # CREATE MEDIA CLIP
    # ==================================================

    def create_clip(
        self,
        media_type,
        media_path,
        duration=5
    ):

        if not os.path.exists(media_path):

            print(
                f"❌ Media not found: {media_path}"
            )

            return None

        if media_type == "video":

            return self.load_video(
                media_path,
                duration
            )

        if media_type == "image":

            return self.load_image(
                media_path,
                duration
            )

        print(
            f"❌ Unsupported media type: "
            f"{media_type}"
        )

        return None

    # ==================================================
    # CREATE MUSIC SEGMENT
    # ==================================================

    def create_music_segment(
        self,
        music,
        start_time,
        duration,
        state,
        volume
    ):

        if start_time >= music.duration:

            return None

        end_time = min(
            start_time + duration,
            music.duration
        )

        actual_duration = (
            end_time - start_time
        )

        if actual_duration <= 0:

            return None

        # ----------------------------------------------
        # Extract music segment
        # ----------------------------------------------

        segment = music.subclipped(
            start_time,
            end_time
        )

        # ==================================================
        # MUSIC STATE
        # ==================================================

        if state == "ON":

            segment = segment.with_volume_scaled(
                0.30
            )

        elif state == "DUCK":

            # Speech/background dialogue
            # Keep music quieter but audible.

            segment = segment.with_volume_scaled(
                0.15
            )

        elif state == "OFF":

            segment = segment.with_volume_scaled(
                0.0
            )

        elif state == "FADE_IN":

            # ------------------------------------------------
            # Temporary stable implementation.
            #
            # We will add smooth fade after confirming
            # ON / DUCK / OFF works correctly.
            # ------------------------------------------------

            segment = segment.with_volume_scaled(
                0.30
            )

        elif state == "FADE_OUT":

            # ------------------------------------------------
            # Temporary stable implementation.
            #
            # We will add smooth fade after confirming
            # ON / DUCK / OFF works correctly.
            # ------------------------------------------------

            segment = segment.with_volume_scaled(
                0.30
            )

        else:

            segment = segment.with_volume_scaled(
                volume
            )

        return segment

    # ==================================================
    # CREATE SCENE-LEVEL MUSIC
    # ==================================================

    def create_music_timeline(
        self,
        music_path,
        storyboard,
        music_timeline
    ):

        if not music_path:

            return None

        if not os.path.exists(music_path):

            print(
                f"❌ Music not found: {music_path}"
            )

            return None

        print(
            "\nCreating scene-level music..."
        )

        # ------------------------------------------------
        # Load source music
        # ------------------------------------------------

        music = AudioFileClip(
            music_path
        )

        audio_segments = []

        current_time = 0

        # ==================================================
        # PROCESS EACH SCENE
        # ==================================================

        for scene in storyboard:

            scene_number = scene.get(
                "scene_number"
            )

            duration = scene.get(
                "duration",
                5
            )

            # ----------------------------------------------
            # Find decision for this scene
            # ----------------------------------------------

            decision = next(
                (
                    item
                    for item in music_timeline
                    if item.get("scene_number")
                    == scene_number
                ),
                None
            )

            # ----------------------------------------------
            # Default
            # ----------------------------------------------

            if decision is None:

                state = "ON"

                volume = 0.70

            else:

                state = decision.get(
                    "music_state",
                    "ON"
                )

                volume = decision.get(
                    "volume",
                    0.30
                )

            print(
                f"Scene {scene_number} "
                f"→ {state} "
                f"→ Volume: {volume}"
            )

            # ----------------------------------------------
            # Create segment
            # ----------------------------------------------

            segment = self.create_music_segment(
                music=music,
                start_time=current_time,
                duration=duration,
                state=state,
                volume=volume
            )

            if segment is not None:

                audio_segments.append(
                    segment
                )

            current_time += duration

        # ==================================================
        # NO AUDIO SEGMENTS
        # ==================================================

        if not audio_segments:

            music.close()

            return None

        # ==================================================
        # COMBINE AUDIO SEGMENTS
        # ==================================================

        print(
            "\nCombining music segments..."
        )

        final_music = concatenate_audioclips(
            audio_segments
        )

        print(
            "Music timeline created."
        )

        # IMPORTANT:
        #
        # Do NOT close `music` here.
        # The audio segments still depend on it.
        #
        # It will be closed after the processed audio
        # has been rendered.
        # ==================================================

        return final_music, music

    # ==================================================
    # COMPOSE FINAL VIDEO
    # ==================================================

    def compose(
        self,
        storyboard,
        music_path=None,
        music_timeline=None,
        output_name="framecraft_output.mp4",
        generate_thumbnail=False,
        thumbnail_title=None,
        thumbnail_output_name=None,
        return_metadata=False,
    ):

        print(
            "\nStarting Video Composition..."
        )

        clips = []

        music = None

        final_music = None

        # ==================================================
        # PROCESS STORYBOARD
        # ==================================================

        for scene in storyboard:

            scene_number = scene.get(
                "scene_number"
            )

            media_type = scene.get(
                "media_type"
            )

            media_path = scene.get(
                "media_path"
            )

            duration = scene.get(
                "duration",
                5
            )

            print(
                f"\nScene {scene_number}"
            )

            print(
                f"Type: {media_type}"
            )

            print(
                f"File: {media_path}"
            )

            clip = self.create_clip(
                media_type,
                media_path,
                duration
            )

            if clip is not None:

                clips.append(
                    clip
                )

                print(
                    "✅ Clip added"
                )

        # ==================================================
        # NO VIDEO
        # ==================================================

        if not clips:

            print(
                "❌ No valid media clips found."
            )

            return None

        print(
            f"\nTotal clips: {len(clips)}"
        )

        # ==================================================
        # COMBINE VIDEO
        # ==================================================

        print(
            "\nCombining clips..."
        )

        final_video = concatenate_videoclips(
            clips,
            method="compose"
        )

        # ==================================================
        # MUSIC
        # ==================================================

        if (
            music_path
            and os.path.exists(music_path)
        ):

            print(
                f"🎵 Adding music: {music_path}"
            )

            # ==================================================
            # SCENE LEVEL MUSIC
            # ==================================================

            if music_timeline:

                result = self.create_music_timeline(
                    music_path=music_path,
                    storyboard=storyboard,
                    music_timeline=music_timeline
                )

                if result is not None:

                    final_music, music = result

            # ==================================================
            # CONTINUOUS MUSIC
            # ==================================================

            else:

                print(
                    "Using continuous background music."
                )

                music = AudioFileClip(
                    music_path
                )

                if music.duration > final_video.duration:

                    final_music = music.subclipped(
                        0,
                        final_video.duration
                    )

                else:

                    final_music = music

                final_music = (
                    final_music
                    .with_volume_scaled(0.30)
                )

            # ==================================================
            # WRITE PROCESSED AUDIO FIRST
            # ==================================================

            if final_music is not None:

                temp_audio_path = os.path.join(
                    self.output_folder,
                    "framecraft_processed_music.wav"
                )

                print(
                    "\nWriting processed music..."
                )

                final_music.write_audiofile(
                    temp_audio_path,
                    fps=44100,
                    nbytes=2,
                    codec="pcm_s16le"
                )

                print(
                    "✅ Processed music saved:"
                )

                print(
                    temp_audio_path
                )

                # ----------------------------------------------
                # Close generated timeline
                # ----------------------------------------------

                try:

                    final_music.close()

                except Exception:

                    pass

                # ----------------------------------------------
                # Close source music
                # ----------------------------------------------

                if music is not None:

                    try:

                        music.close()

                    except Exception:

                        pass

                    music = None

                # ==================================================
                # RELOAD PROCESSED AUDIO
                # ==================================================

                print(
                    "\nReloading processed music..."
                )

                final_music = AudioFileClip(
                    temp_audio_path
                )

                # ----------------------------------------------
                # Match video duration
                # ----------------------------------------------

                if (
                    final_music.duration
                    > final_video.duration
                ):

                    final_music = final_music.subclipped(
                        0,
                        final_video.duration
                    )

                # ----------------------------------------------
                # Attach audio
                # ----------------------------------------------

                final_video = final_video.with_audio(
                    final_music
                )

                print(
                    "✅ Music attached to video."
                )

        else:

            print(
                "No background music selected."
            )

        # ==================================================
        # OUTPUT
        # ==================================================

        output_path = os.path.join(
            self.output_folder,
            output_name
        )

        print(
            "\nRendering final video..."
        )

        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac"
        )

        # ==================================================
        # CLEANUP
        # ==================================================

        print(
            "\nCleaning resources..."
        )

        for clip in clips:

            try:

                clip.close()

            except Exception:

                pass

        if final_music is not None:

            try:

                final_music.close()

            except Exception:

                pass

        try:

            final_video.close()

        except Exception:

            pass

        # ==================================================
        # THUMBNAIL GENERATION (OPTIONAL)
        # ==================================================
        thumbnail_path = None
        thumbnail_metadata_path = None

        if generate_thumbnail and os.path.exists(output_path):
            print("\nGenerating Video Thumbnail...")
            try:
                from app.services.thumbnail_generator import ThumbnailGenerator

                # Determine thumbnail filenames from video output name
                video_stem = os.path.splitext(output_name)[0]
                if not thumbnail_output_name:
                    thumb_name = f"{video_stem}_thumbnail.jpg"
                else:
                    thumb_name = thumbnail_output_name

                thumb_meta_name = f"{os.path.splitext(thumb_name)[0]}_metadata.json"

                # Title fallback
                title = thumbnail_title or "FrameCraft AI"

                thumb_generator = ThumbnailGenerator(output_folder=self.output_folder)
                thumbnail_path = thumb_generator.create_thumbnail(
                    video_path=output_path,
                    output_name=thumb_name,
                    title=title,
                    metadata_name=thumb_meta_name,
                )
                thumbnail_metadata_path = os.path.join(
                    self.output_folder,
                    thumb_meta_name
                ).replace("\\", "/")
                thumbnail_path = thumbnail_path.replace("\\", "/")

                print("✅ Thumbnail generated successfully.")

            except Exception as e:
                print(f"\n⚠️ Thumbnail generation failed:\n{e}")
                print("Video generation completed successfully.\n")

        print(
            "\n================================"
        )

        print(
            "Video Composition Completed!"
        )

        print(
            "Output:",
            output_path
        )

        if thumbnail_path:
            print(
                "Thumbnail:",
                thumbnail_path
            )

        if thumbnail_metadata_path:
            print(
                "Metadata:",
                thumbnail_metadata_path
            )

        print(
            "================================"
        )

        if return_metadata:
            return {
                "video": output_path.replace("\\", "/"),
                "thumbnail": thumbnail_path,
                "thumbnail_metadata": thumbnail_metadata_path,
            }

        return output_path

    # ==================================================
    # BACKWARD COMPATIBILITY
    # ==================================================

    def create_video(
        self,
        storyboard,
        music_path=None,
        music_timeline=None,
        output_name="framecraft_output.mp4",
        generate_thumbnail=False,
        thumbnail_title=None,
        thumbnail_output_name=None,
        return_metadata=False,
    ):

        return self.compose(
            storyboard=storyboard,
            music_path=music_path,
            music_timeline=music_timeline,
            output_name=output_name,
            generate_thumbnail=generate_thumbnail,
            thumbnail_title=thumbnail_title,
            thumbnail_output_name=thumbnail_output_name,
            return_metadata=return_metadata,
        )
