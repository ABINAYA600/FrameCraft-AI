import os

import torch
import open_clip
from PIL import Image


class ImageRetriever:

    def __init__(
        self,
        image_folder="datasets/images"
    ):

        print("Loading Image Retriever...")

        self.image_folder = image_folder

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        # Load CLIP
        self.model, _, self.preprocess = (
            open_clip.create_model_and_transforms(
                "ViT-B-32",
                pretrained="laion2b_s34b_b79k"
            )
        )

        self.tokenizer = open_clip.get_tokenizer(
            "ViT-B-32"
        )

        self.model.to(self.device)
        self.model.eval()

        print("✅ Image Retriever Loaded!")

    # --------------------------------------------------
    # Get available images
    # --------------------------------------------------

    def load_images(self):

        supported_extensions = (
            ".jpg",
            ".jpeg",
            ".png"
        )

        images = []

        if not os.path.exists(self.image_folder):

            print(
                f"❌ Image folder not found: "
                f"{self.image_folder}"
            )

            return images

        for file in os.listdir(
            self.image_folder
        ):

            if file.lower().endswith(
                supported_extensions
            ):

                images.append(file)

        return sorted(images)

    # --------------------------------------------------
    # Retrieve images for a scene
    # --------------------------------------------------

    def retrieve(
        self,
        scene,
        top_k=5
    ):

        image_files = self.load_images()

        if not image_files:

            return {
                "scene": scene,
                "best_image": None,
                "best_score": None,
                "rankings": []
            }

        text = self.tokenizer(
            [scene]
        ).to(self.device)

        rankings = []

        with torch.no_grad():

            # Text embedding
            text_features = self.model.encode_text(
                text
            )

            text_features /= text_features.norm(
                dim=-1,
                keepdim=True
            )

            # Compare each image
            for image_name in image_files:

                image_path = os.path.join(
                    self.image_folder,
                    image_name
                )

                try:

                    image = Image.open(
                        image_path
                    ).convert("RGB")

                    image_tensor = self.preprocess(
                        image
                    ).unsqueeze(0).to(
                        self.device
                    )

                    image_features = (
                        self.model.encode_image(
                            image_tensor
                        )
                    )

                    image_features /= (
                        image_features.norm(
                            dim=-1,
                            keepdim=True
                        )
                    )

                    similarity = (
                        image_features
                        @ text_features.T
                    ).item()

                    rankings.append(
                        {
                            "image": image_name,
                            "score": round(
                                similarity,
                                4
                            )
                        }
                    )

                except Exception as error:

                    print(
                        f"⚠️ Could not process "
                        f"{image_name}: {error}"
                    )

        rankings.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        rankings = rankings[:top_k]

        if not rankings:

            return {
                "scene": scene,
                "best_image": None,
                "best_score": None,
                "rankings": []
            }

        return {
            "scene": scene,
            "best_image": rankings[0]["image"],
            "best_score": rankings[0]["score"],
            "rankings": rankings
        }