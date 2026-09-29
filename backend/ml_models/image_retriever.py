import os
from PIL import Image

import torch
import open_clip


class ImageModel:
    """
    Image Module for FrameCraft AI Foundation Model (FAFM)

    Responsibilities
    ----------------
    1. Load the CLIP model.
    2. Load all images from a folder.
    3. Match a scene with the most relevant image.
    4. Return the best image and complete rankings.
    """

    def __init__(self):

        print("Loading CLIP Model...")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32",
            pretrained="laion2b_s34b_b79k"
        )

        self.tokenizer = open_clip.get_tokenizer("ViT-B-32")

        self.model.to(self.device)
        self.model.eval()

        print("✅ CLIP Model Loaded Successfully!")

    # ---------------------------------------------------
    # Load Images
    # ---------------------------------------------------

    def load_images(self, image_folder):

        supported_extensions = (".jpg", ".jpeg", ".png")

        images = []

        for file in os.listdir(image_folder):

            if file.lower().endswith(supported_extensions):
                images.append(file)

        return sorted(images)

    # ---------------------------------------------------
    # Match Single Scene
    # ---------------------------------------------------

    def match_images(self, scene, image_folder):

        image_files = self.load_images(image_folder)

        text = self.tokenizer([scene]).to(self.device)

        rankings = []

        with torch.no_grad():

            text_features = self.model.encode_text(text)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            for image_name in image_files:

                image_path = os.path.join(image_folder, image_name)

                image = Image.open(image_path).convert("RGB")

                image = self.preprocess(image).unsqueeze(0).to(self.device)

                image_features = self.model.encode_image(image)
                image_features /= image_features.norm(dim=-1, keepdim=True)

                similarity = (
                    image_features @ text_features.T
                ).item()

                rankings.append(
                    {
                        "image": image_name,
                        "score": round(similarity, 4)
                    }
                )

        rankings.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return {
            "scene": scene,
            "best_image": rankings[0]["image"],
            "best_score": rankings[0]["score"],
            "rankings": rankings
        }

    # ---------------------------------------------------
    # Match Multiple Scenes
    # ---------------------------------------------------

    def process(self, scenes, image_folder):

        storyboard = []

        for scene in scenes:

            result = self.match_images(
                scene,
                image_folder
            )

            storyboard.append(result)

        return storyboard