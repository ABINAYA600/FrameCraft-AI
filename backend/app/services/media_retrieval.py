import os

from app.services.image_retriever import ImageRetriever
from app.services.video_retriever import VideoRetriever


class MediaRetrieval:

    """
    FrameCraft AI Media Retrieval Engine

    Retrieves both:
        1. Images
        2. Video clips

    and selects the best media for each scene.
    """

    def __init__(
        self,
        image_folder="datasets/images",
        video_embeddings="datasets/embeddings/video_embeddings.pkl",
        clips_folder="datasets/clips"
    ):

        print("Initializing Media Retrieval Engine...")

        self.image_folder = image_folder

        self.image_retriever = ImageRetriever(
            image_folder=image_folder
        )

        self.video_retriever = VideoRetriever(
            embeddings_file=video_embeddings,
            clips_folder=clips_folder
        )

        print("✅ Media Retrieval Engine Initialized!")

    # ---------------------------------------------------
    # Retrieve media for one scene
    # ---------------------------------------------------

    def retrieve(self, scene, top_k=5):

        print("\n" + "=" * 60)
        print("MEDIA RETRIEVAL")
        print("=" * 60)

        print(f"Scene: {scene}")

        # -----------------------------
        # Image retrieval
        # -----------------------------

        image_result = self.image_retriever.retrieve(
            scene,
            top_k=top_k
        )

        # -----------------------------
        # Video retrieval
        # -----------------------------

        video_result = self.video_retriever.retrieve(
            scene,
            top_k=top_k
        )

        # -----------------------------
        # Combine results
        # -----------------------------

        candidates = []

        # Images

        for item in image_result["rankings"]:

            candidates.append(
                {
                    "type": "image",
                    "file": item["image"],
                    "path": os.path.join(
                        self.image_folder,
                        item["image"]
                    ),
                    "score": item["score"]
                }
            )

        # Videos

        for item in video_result["rankings"]:

            candidates.append(
                {
                    "type": "video",
                    "file": item["video"],
                    "path": item["path"],
                    "score": item["score"]
                }
            )

        # -----------------------------
        # Sort all media together
        # -----------------------------

        candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        top_media = candidates[:top_k]

        if not top_media:

            return {
                "scene": scene,
                "best_media": None,
                "rankings": []
            }

        best = top_media[0]

        return {
            "scene": scene,

            "best_media": {
                "type": best["type"],
                "file": best["file"],
                "path": best["path"],
                "score": best["score"]
            },

            "rankings": top_media
        }

    # ---------------------------------------------------
    # Process multiple scenes
    # ---------------------------------------------------

    def process(self, scenes, top_k=5):

        storyboard = []

        for scene in scenes:

            result = self.retrieve(
                scene,
                top_k=top_k
            )

            storyboard.append(result)

        return storyboard