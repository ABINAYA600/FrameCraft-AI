import os
import json
import math
import numpy as np
import torch
import open_clip

from moviepy import VideoFileClip
from PIL import Image, ImageDraw, ImageFont


class ThumbnailGenerator:
    """
    FrameCraft AI Thumbnail Generator

    Automatically generates high-impact video thumbnails using:
    1. Visual quality scoring (brightness, contrast, sharpness)
    2. OpenCLIP ViT-B-32 semantic relevance scoring based on title/topic
    3. Visual diversity calculation (pairwise pixel difference)
    4. Intelligent layout decision (single, split, collage_3, collage_4)
    5. Adaptive title rendering with shadows and semi-transparent backdrop
    """

    def __init__(
        self,
        output_folder="output",
        quality_weight=0.30,
        semantic_weight=0.50,
        diversity_weight=0.20,
        enable_clip=True,
    ):
        self.output_folder = output_folder
        self.quality_weight = quality_weight
        self.semantic_weight = semantic_weight
        self.diversity_weight = diversity_weight
        self.enable_clip = enable_clip

        os.makedirs(self.output_folder, exist_ok=True)

        print("Thumbnail Generator Initialized!")

        # ==================================================
        # CLIP INITIALIZATION
        # ==================================================
        self.clip_available = False
        self.clip_model = None
        self.clip_preprocess = None
        self.clip_tokenizer = None

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"CLIP device: {self.device}")

        if not self.enable_clip:
            print("CLIP disabled by configuration. Using visual scoring fallback.")
            return

        try:
            print("Loading CLIP model...")
            (
                self.clip_model,
                _,
                self.clip_preprocess,
            ) = open_clip.create_model_and_transforms(
                "ViT-B-32",
                pretrained="openai"
            )

            self.clip_model = self.clip_model.to(self.device)
            self.clip_model.eval()

            self.clip_tokenizer = open_clip.get_tokenizer("ViT-B-32")
            self.clip_available = True
            print("✅ CLIP model loaded!")

        except Exception as e:
            print("⚠️ CLIP could not be loaded.")
            print(f"Reason: {e}")
            print("Using visual scoring fallback.")

    # ==================================================
    # EXTRACT FRAME
    # ==================================================
    def extract_frame(self, video, timestamp):
        """Safely extract a single frame as PIL Image at timestamp."""
        duration = getattr(video, "duration", 0.0) or 0.0
        safe_max = max(duration - 0.05, 0.0)
        timestamp = max(0.0, min(float(timestamp), safe_max))

        frame = video.get_frame(timestamp)
        return Image.fromarray(frame)

    # ==================================================
    # FRAME QUALITY SCORE
    # ==================================================
    def calculate_frame_score(self, image):
        """
        Calculates a visual quality score based on brightness and contrast.
        Returns a float in [0.0, 1.0].
        """
        grayscale = image.convert("L")
        histogram = grayscale.histogram()

        total_pixels = image.width * image.height
        if total_pixels == 0:
            return 0.0

        # Brightness (average pixel intensity)
        brightness = (
            sum(value * count for value, count in enumerate(histogram))
            / total_pixels
        )

        # Contrast (standard deviation)
        variance = (
            sum((value - brightness) ** 2 * count for value, count in enumerate(histogram))
            / total_pixels
        )
        contrast = math.sqrt(variance)

        # Brightness score (bell curve centered around 128)
        brightness_score = max(0.0, 1.0 - abs(brightness - 128.0) / 128.0)

        # Contrast score (normalized up to 64)
        contrast_score = min(contrast / 64.0, 1.0)

        # Combined quality score
        score = brightness_score * 0.40 + contrast_score * 0.60
        return float(np.clip(score, 0.0, 1.0))

    # ==================================================
    # CLIP SEMANTIC SCORE (SINGLE IMAGE)
    # ==================================================
    def calculate_clip_score(self, image, title):
        """Calculates semantic similarity between a single image and title."""
        if not self.clip_available or not title or not str(title).strip():
            return 0.0

        try:
            image_input = self.clip_preprocess(image).unsqueeze(0).to(self.device)
            text_input = self.clip_tokenizer([title]).to(self.device)

            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_input)
                text_features = self.clip_model.encode_text(text_input)

                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)

                similarity = (image_features @ text_features.T).item()

            # Normalized cosine similarity mapped from [-1, 1] to [0, 1]
            score = (similarity + 1.0) / 2.0
            return float(np.clip(score, 0.0, 1.0))

        except Exception as e:
            print(f"⚠️ CLIP scoring failed: {e}")
            return 0.0

    # ==================================================
    # BATCH CLIP SEMANTIC SCORE
    # ==================================================
    def calculate_clip_scores_batch(self, images, title):
        """
        Batch encodes candidate frames for optimal performance.
        Returns a list of semantic scores corresponding to each image.
        """
        if not images:
            return []

        if not self.clip_available or not title or not str(title).strip():
            return [0.0] * len(images)

        try:
            batch_tensors = torch.stack([self.clip_preprocess(img) for img in images]).to(self.device)
            text_input = self.clip_tokenizer([title]).to(self.device)

            with torch.no_grad():
                image_features = self.clip_model.encode_image(batch_tensors)
                text_features = self.clip_model.encode_text(text_input)

                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)

                similarities = (image_features @ text_features.T).squeeze(-1).cpu().numpy()

            scores = [float(np.clip((sim + 1.0) / 2.0, 0.0, 1.0)) for sim in similarities]
            return scores

        except Exception as e:
            print(f"⚠️ Batch CLIP scoring failed: {e}. Falling back to sequential scoring.")
            return [self.calculate_clip_score(img, title) for img in images]

    # ==================================================
    # VISUAL DIFFERENCE
    # ==================================================
    def calculate_visual_difference(self, image1, image2):
        """
        Calculates normalized L1 pixel difference between two images.
        Returns a float in [0.0, 1.0].
        """
        img1_arr = np.array(image1.resize((64, 64)).convert("RGB"), dtype=np.float32)
        img2_arr = np.array(image2.resize((64, 64)).convert("RGB"), dtype=np.float32)

        difference = np.mean(np.abs(img1_arr - img2_arr)) / 255.0
        return float(difference)

    # ==================================================
    # EXTRACT CANDIDATE FRAMES
    # ==================================================
    def extract_candidate_frames(self, video_path, candidate_count=12):
        """
        Extracts candidate frames from video, scores their quality,
        and computes batch CLIP semantic relevance.
        """
        print("\nAnalyzing video frames...")

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            video = VideoFileClip(video_path)
        except Exception as e:
            raise ValueError(f"Failed to open video file '{video_path}': {e}")

        try:
            duration = video.duration
            if duration is None or duration <= 0:
                raise ValueError(f"Video has invalid duration: {duration}")

            # Adapt candidate count for very short videos
            actual_count = max(1, min(candidate_count, int(duration * 10) if duration < 1.0 else candidate_count))

            timestamps = [
                duration * (i + 1) / (actual_count + 1)
                for i in range(actual_count)
            ]

            images = []
            quality_scores = []

            for ts in timestamps:
                img = self.extract_frame(video, ts)
                images.append(img)
                q_score = self.calculate_frame_score(img)
                quality_scores.append(q_score)

        finally:
            video.close()

        # Batch CLIP scoring
        clip_scores = self.calculate_clip_scores_batch(images, getattr(self, "thumbnail_title", None))

        candidates = []
        has_semantic = self.clip_available and bool(getattr(self, "thumbnail_title", None))

        for ts, img, q_score, c_score in zip(timestamps, images, quality_scores, clip_scores):
            if has_semantic:
                total_w = self.quality_weight + self.semantic_weight
                w_q = self.quality_weight / total_w if total_w > 0 else 0.5
                w_s = self.semantic_weight / total_w if total_w > 0 else 0.5
                combined_score = q_score * w_q + c_score * w_s
            else:
                combined_score = q_score

            print(f"\nChecking frame at {ts:.2f}s")
            print(f"Quality: {q_score:.3f}")
            print(f"CLIP: {c_score:.3f}")
            print(f"Combined: {combined_score:.3f}")

            candidates.append({
                "timestamp": ts,
                "image": img,
                "quality_score": q_score,
                "clip_score": c_score,
                "combined_score": combined_score,
            })

        return candidates

    # ==================================================
    # SELECT DIVERSE FRAMES
    # ==================================================
    def select_diverse_frames(self, candidates, number_of_frames):
        """
        Selects top diverse frames combining semantic score, quality, and visual difference.
        """
        if not candidates:
            return []

        number_of_frames = min(number_of_frames, len(candidates))
        if number_of_frames <= 0:
            return []

        # Start with the highest-scoring candidate frame
        sorted_candidates = sorted(
            candidates,
            key=lambda x: x["combined_score"],
            reverse=True
        )

        selected = [sorted_candidates[0]]
        remaining = [c for c in candidates if c is not selected[0]]

        has_semantic = self.clip_available and bool(getattr(self, "thumbnail_title", None))

        while len(selected) < number_of_frames and remaining:
            best_candidate = None
            best_selection_score = -1.0

            for candidate in remaining:
                differences = [
                    self.calculate_visual_difference(candidate["image"], sel["image"])
                    for sel in selected
                ]
                diversity_score = min(differences) if differences else 0.0

                if has_semantic:
                    total_w = self.quality_weight + self.semantic_weight + self.diversity_weight
                    w_q = self.quality_weight / total_w
                    w_s = self.semantic_weight / total_w
                    w_d = self.diversity_weight / total_w
                    selection_score = (
                        candidate["quality_score"] * w_q
                        + candidate["clip_score"] * w_s
                        + diversity_score * w_d
                    )
                else:
                    total_w = self.quality_weight + self.diversity_weight
                    w_q = self.quality_weight / total_w if total_w > 0 else 0.6
                    w_d = self.diversity_weight / total_w if total_w > 0 else 0.4
                    selection_score = (
                        candidate["quality_score"] * w_q
                        + diversity_score * w_d
                    )

                if selection_score > best_selection_score:
                    best_selection_score = selection_score
                    best_candidate = candidate

            if best_candidate is None:
                break

            selected.append(best_candidate)
            remaining.remove(best_candidate)

        # Sort selected frames chronologically
        selected.sort(key=lambda x: x["timestamp"])
        return selected

    # ==================================================
    # DECIDE THUMBNAIL LAYOUT
    # ==================================================
    def decide_layout(self, candidates):
        """
        Decides layout based on candidate count, pairwise diversity,
        and frame dominance.
        """
        if not candidates or len(candidates) <= 1:
            return "single"

        # Use top candidates by combined score for diversity analysis
        strongest = sorted(
            candidates,
            key=lambda x: x["combined_score"],
            reverse=True
        )[:min(6, len(candidates))]

        differences = []
        for i in range(len(strongest)):
            for j in range(i + 1, len(strongest)):
                diff = self.calculate_visual_difference(
                    strongest[i]["image"],
                    strongest[j]["image"]
                )
                differences.append(diff)

        if not differences:
            return "single"

        average_difference = sum(differences) / len(differences)
        print(f"\nAverage visual diversity: {average_difference:.3f}")

        # Check if single top frame is overwhelmingly dominant
        if len(strongest) >= 2:
            top1_score = strongest[0]["combined_score"]
            top2_score = strongest[1]["combined_score"]
            if (top1_score - top2_score) > 0.25 and average_difference < 0.15:
                print("Automatic thumbnail layout: single (dominant frame detected)")
                return "single"

        available_count = len(candidates)

        if average_difference < 0.12 or available_count < 2:
            layout = "single"
        elif average_difference < 0.25 or available_count < 3:
            layout = "split"
        elif average_difference < 0.40 or available_count < 4:
            layout = "collage_3"
        else:
            layout = "collage_4"

        print(f"Automatic thumbnail layout: {layout}")
        return layout

    # ==================================================
    # LOAD FONT
    # ==================================================
    def load_font(self, size):
        """Loads a bold truetype font cross-platform or falls back to default."""
        font_paths = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]

        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue

        try:
            return ImageFont.load_default()
        except Exception:
            return None

    # ==================================================
    # ADD TITLE OVERLAY
    # ==================================================
    def add_title(self, image, title):
        """
        Adds a clean, highly legible title overlay with text wrapping,
        semi-transparent backdrop, and drop shadow.
        """
        if not title or not str(title).strip():
            return image

        title = str(title).strip()
        img_w, img_h = image.size

        # Choose initial font size based on image dimensions
        font_size = max(24, int(img_h * 0.075))
        font = self.load_font(font_size)

        max_text_width = int(img_w * 0.88)
        padding_x = int(img_w * 0.04)
        padding_y = 16

        draw_temp = ImageDraw.Draw(image)

        def get_text_size(text, fnt):
            if hasattr(draw_temp, "textbbox"):
                bbox = draw_temp.textbbox((0, 0), text, font=fnt)
                return bbox[2] - bbox[0], bbox[3] - bbox[1]
            else:
                return fnt.getsize(text)

        # Word wrap text to fit within max_text_width
        words = title.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            line_w, _ = get_text_size(test_line, font)
            if line_w <= max_text_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []

        if current_line:
            lines.append(" ".join(current_line))

        if not lines:
            lines = [title]

        # Calculate total height
        line_heights = [get_text_size(line, font)[1] for line in lines]
        line_spacing = int(font_size * 0.25)
        total_text_height = sum(line_heights) + (len(lines) - 1) * line_spacing

        overlay_height = total_text_height + padding_y * 2 + 10
        overlay_y = img_h - overlay_height

        # Semi-transparent dark overlay banner
        overlay = Image.new("RGBA", (img_w, overlay_height), (0, 0, 0, 140))
        image_rgba = image.convert("RGBA")
        image_rgba.alpha_composite(overlay, (0, overlay_y))
        image = image_rgba.convert("RGB")
        draw = ImageDraw.Draw(image)

        # Draw lines of text with shadow
        cur_y = overlay_y + padding_y
        for line in lines:
            # Shadow
            draw.text((padding_x + 3, cur_y + 3), line, font=font, fill=(0, 0, 0))
            # Text
            draw.text((padding_x, cur_y), line, font=font, fill=(255, 255, 255))
            _, h = get_text_size(line, font)
            cur_y += h + line_spacing

        return image

    # ==================================================
    # SINGLE THUMBNAIL
    # ==================================================
    def create_single_thumbnail(self, frame_image, title):
        """Generates a 1280x720 single frame thumbnail."""
        image = frame_image.copy().resize((1280, 720), Image.Resampling.LANCZOS)
        return self.add_title(image, title)

    # ==================================================
    # SPLIT THUMBNAIL
    # ==================================================
    def create_split_thumbnail(self, frames, title):
        """Generates a 1280x720 2-frame split thumbnail."""
        if len(frames) < 2:
            return self.create_single_thumbnail(frames[0]["image"], title)

        canvas = Image.new("RGB", (1280, 720), "black")
        width = 640
        height = 720

        for index, frame_data in enumerate(frames[:2]):
            image = frame_data["image"].copy().resize((width, height), Image.Resampling.LANCZOS)
            canvas.paste(image, (index * width, 0))

        return self.add_title(canvas, title)

    # ==================================================
    # COLLAGE THUMBNAIL (3 or 4 frames)
    # ==================================================
    def create_collage_thumbnail(self, frames, title):
        """Generates a 1280x720 collage thumbnail (3 or 4 frames)."""
        if len(frames) <= 1:
            return self.create_single_thumbnail(frames[0]["image"], title)
        elif len(frames) == 2:
            return self.create_split_thumbnail(frames, title)

        canvas = Image.new("RGB", (1280, 720), "black")

        if len(frames) == 3:
            positions = [
                (0, 0, 640, 360),
                (640, 0, 640, 360),
                (320, 360, 640, 360),
            ]
        else:
            positions = [
                (0, 0, 640, 360),
                (640, 0, 640, 360),
                (0, 360, 640, 360),
                (640, 360, 640, 360),
            ]

        for frame_data, (x, y, w, h) in zip(frames[:len(positions)], positions):
            image = frame_data["image"].copy().resize((w, h), Image.Resampling.LANCZOS)
            canvas.paste(image, (x, y))

        return self.add_title(canvas, title)

    # ==================================================
    # CREATE THUMBNAIL (MAIN ENTRYPOINT)
    # ==================================================
    def create_thumbnail(
        self,
        video_path,
        output_name="framecraft_thumbnail.jpg",
        title=None,
        candidate_count=12,
        metadata_name=None,
    ):
        """
        End-to-end thumbnail generation pipeline.
        Extracts candidates, scores them, selects diverse frames,
        renders the composite thumbnail, and writes metadata.
        """
        self.thumbnail_title = title

        print("\n================================")
        print("AI THUMBNAIL GENERATION")
        print("================================")

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")

        # Extract & score candidates
        candidates = self.extract_candidate_frames(video_path, candidate_count)
        if not candidates:
            raise RuntimeError("No candidate frames could be extracted from the video.")

        # Decide layout
        layout = self.decide_layout(candidates)

        # Number of frames required for decided layout
        layout_frames_map = {
            "single": 1,
            "split": 2,
            "collage_3": 3,
            "collage_4": 4,
        }
        requested_frames = layout_frames_map.get(layout, 1)

        # Select diverse frames
        selected_frames = self.select_diverse_frames(candidates, requested_frames)
        if not selected_frames:
            raise RuntimeError("Unable to select thumbnail frames.")

        # Automatically adjust layout if fewer frames were selected
        actual_frame_count = len(selected_frames)
        if actual_frame_count == 1:
            layout = "single"
        elif actual_frame_count == 2 and layout in ("collage_3", "collage_4"):
            layout = "split"
        elif actual_frame_count == 3 and layout == "collage_4":
            layout = "collage_3"

        print("\nSelected frames:")
        for frame in selected_frames:
            print(
                f"  {frame['timestamp']:.2f}s"
                f" | Quality: {frame['quality_score']:.3f}"
                f" | CLIP: {frame.get('clip_score', 0.0):.3f}"
                f" | Combined: {frame['combined_score']:.3f}"
            )

        # Generate thumbnail image
        if layout == "single":
            thumbnail = self.create_single_thumbnail(selected_frames[0]["image"], title)
        elif layout == "split":
            thumbnail = self.create_split_thumbnail(selected_frames, title)
        else:
            thumbnail = self.create_collage_thumbnail(selected_frames, title)

        # Save thumbnail
        output_path = os.path.join(self.output_folder, output_name)
        thumbnail.save(output_path, "JPEG", quality=95)

        # Determine metadata path
        if not metadata_name:
            if output_name == "framecraft_thumbnail.jpg":
                metadata_name = "thumbnail_metadata.json"
            else:
                thumb_stem = os.path.splitext(output_name)[0]
                metadata_name = f"{thumb_stem}_metadata.json"

        metadata_path = os.path.join(self.output_folder, metadata_name)

        # Metadata dictionary
        metadata = {
            "layout": layout,
            "frame_count": len(selected_frames),
            "selection_method": (
                "CLIP + visual quality + diversity"
                if (self.clip_available and title)
                else "visual quality + diversity"
            ),
            "title": title,
            "thumbnail": output_path.replace("\\", "/"),
            "frames": [
                {
                    "timestamp": round(float(frame["timestamp"]), 2),
                    "quality_score": round(float(frame["quality_score"]), 3),
                    "clip_score": round(float(frame.get("clip_score", 0.0)), 3),
                    "combined_score": round(float(frame.get("combined_score", 0.0)), 3),
                }
                for frame in selected_frames
            ],
        }

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        print("\n================================")
        print("THUMBNAIL GENERATION COMPLETED")
        print("================================")
        print(f"Layout: {layout}")
        print(f"Frames: {len(selected_frames)}")
        print(f"Selection: {metadata['selection_method']}")
        print(f"Thumbnail: {output_path.replace(chr(92), '/')}")
        print(f"Metadata: {metadata_path.replace(chr(92), '/')}")
        print("================================")

        return output_path