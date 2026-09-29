from sentence_transformers import SentenceTransformer


class ScriptModel:
    """
    Script Module for FrameCraft AI Foundation Model (FAFM)

    Responsibilities:
    1. Load the pre-trained Sentence Transformer model.
    2. Split the user's script into scenes.
    3. Generate semantic embeddings for each scene.
    """

    def __init__(self):
        print("Loading Script Model...")

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        print("✅ Script Model Loaded Successfully!")

    # -----------------------------------------
    # Scene Segmentation
    # -----------------------------------------
    def split_into_scenes(self, script: str):
        """
        Split the script into scenes using periods.
        Later this can be replaced with NLP-based segmentation.
        """

        scenes = [
            sentence.strip()
            for sentence in script.split(".")
            if sentence.strip()
        ]

        return scenes

    # -----------------------------------------
    # Embedding Generation
    # -----------------------------------------
    def generate_embeddings(self, scenes):
        """
        Generate sentence embeddings for each scene.
        """

        embeddings = self.model.encode(scenes)

        return embeddings

    # -----------------------------------------
    # Complete Script Processing Pipeline
    # -----------------------------------------
    def process(self, script: str):
        """
        Complete Script Processing Pipeline

        Input:
            Raw Script

        Output:
            {
                scenes,
                embeddings,
                total_scenes
            }
        """

        scenes = self.split_into_scenes(script)

        embeddings = self.generate_embeddings(scenes)

        result = {
            "scenes": scenes,
            "embeddings": embeddings,
            "total_scenes": len(scenes)
        }

        return result