import os
import pickle

import torch
import open_clip


class VideoRetriever:
    """
    FrameCraft AI
    ----------------
    Retrieves the most relevant video clip for a given scene.

    Stored data:
        datasets/embeddings/video_embeddings.pkl

    Actual videos:
        datasets/clips/
    """

    def __init__(
        self,
        embeddings_file="datasets/embeddings/video_embeddings.pkl",
        clips_folder="datasets/clips"
    ):

        print("Loading Video Retriever...")

        self.embeddings_file = embeddings_file
        self.clips_folder = clips_folder

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        # Load CLIP
        self.model, _, _ = open_clip.create_model_and_transforms(
            "ViT-B-32",
            pretrained="laion2b_s34b_b79k"
        )

        self.tokenizer = open_clip.get_tokenizer(
            "ViT-B-32"
        )

        self.model.to(self.device)
        self.model.eval()

        # Load stored embeddings
        with open(
            self.embeddings_file,
            "rb"
        ) as file:

            self.embeddings = pickle.load(file)

        print("✅ Video Retriever Loaded!")

        print(
            f"Loaded embeddings: "
            f"{len(self.embeddings)}"
        )

    # ---------------------------------------------------
    # Convert frame name to video clip name
    # ---------------------------------------------------

    def frame_to_video(self, frame_name):

        video_name = os.path.splitext(
            frame_name
        )[0] + ".mp4"

        video_path = os.path.join(
            self.clips_folder,
            video_name
        )

        return video_path

    # ---------------------------------------------------
    # Retrieve videos for one scene
    # ---------------------------------------------------

    def retrieve(
        self,
        scene,
        top_k=5
    ):

        print(
            f"\nSearching videos for:"
        )

        print(
            f'"{scene}"'
        )

        # Create text embedding
        text = self.tokenizer(
            [scene]
        ).to(self.device)

        with torch.no_grad():

            text_features = self.model.encode_text(
                text
            )

            text_features /= text_features.norm(
                dim=-1,
                keepdim=True
            )

        rankings = []

        # Compare with stored embeddings
        for frame_name, embedding in self.embeddings.items():

            video_path = self.frame_to_video(
                frame_name
            )

            # Make sure corresponding video exists
            if not os.path.exists(video_path):
                continue

            video_embedding = torch.tensor(
                embedding,
                dtype=torch.float32
            ).to(self.device)

            video_embedding /= video_embedding.norm()

            similarity = (
                video_embedding @
                text_features[0]
            ).item()

            rankings.append(
                {
                    "video": os.path.basename(
                        video_path
                    ),
                    "path": video_path,
                    "score": round(
                        similarity,
                        4
                    )
                }
            )

        # Highest similarity first
        rankings.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        if not rankings:

            return {
                "scene": scene,
                "best_video": None,
                "best_score": None,
                "rankings": []
            }

        # Top K
        top_results = rankings[:top_k]

        return {
            "scene": scene,
            "best_video": top_results[0]["video"],
            "best_path": top_results[0]["path"],
            "best_score": top_results[0]["score"],
            "rankings": top_results
        }