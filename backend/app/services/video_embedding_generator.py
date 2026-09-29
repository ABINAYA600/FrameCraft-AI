import os
import pickle

import torch
import open_clip
from PIL import Image


class VideoEmbeddingGenerator:

    def __init__(self):

        print("Loading CLIP Model for Video Embeddings...")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32",
            pretrained="laion2b_s34b_b79k"
        )

        self.tokenizer = open_clip.get_tokenizer("ViT-B-32")

        self.model.to(self.device)
        self.model.eval()

        print("✅ CLIP Model Loaded!")

    def generate_embeddings(
        self,
        frames_folder,
        output_file
    ):

        supported_extensions = (
            ".jpg",
            ".jpeg",
            ".png"
        )

        frame_files = [
            file
            for file in os.listdir(frames_folder)
            if file.lower().endswith(supported_extensions)
        ]

        frame_files.sort()

        print(f"\nFound {len(frame_files)} frames.")

        embeddings = {}

        with torch.no_grad():

            for frame_name in frame_files:

                frame_path = os.path.join(
                    frames_folder,
                    frame_name
                )

                image = Image.open(
                    frame_path
                ).convert("RGB")

                image_tensor = self.preprocess(
                    image
                ).unsqueeze(0).to(self.device)

                image_features = self.model.encode_image(
                    image_tensor
                )

                image_features /= image_features.norm(
                    dim=-1,
                    keepdim=True
                )

                embeddings[frame_name] = (
                    image_features
                    .cpu()
                    .numpy()[0]
                )

                print(
                    f"✅ Embedded: {frame_name}"
                )

        os.makedirs(
            os.path.dirname(output_file),
            exist_ok=True
        )

        with open(
            output_file,
            "wb"
        ) as file:

            pickle.dump(
                embeddings,
                file
            )

        print("\n================================")
        print("Video Embeddings Generated!")
        print("================================")

        print(
            f"Frames processed : {len(embeddings)}"
        )

        print(
            f"Saved to         : {output_file}"
        )

        return embeddings