from app.services.video_embedding_generator import (
    VideoEmbeddingGenerator
)


print("Starting Video Embedding Test...")


generator = VideoEmbeddingGenerator()


embeddings = generator.generate_embeddings(
    frames_folder="datasets/frames",
    output_file="datasets/embeddings/video_embeddings.pkl"
)


print("\n========== EMBEDDING TEST ==========")

for frame_name, embedding in embeddings.items():

    print(
        f"{frame_name} -> Shape: {embedding.shape}"
    )


print("\nEmbedding test completed successfully!")