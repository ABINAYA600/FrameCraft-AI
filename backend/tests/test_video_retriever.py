from app.services.video_retriever import VideoRetriever


print("Starting Video Retriever Test...")

retriever = VideoRetriever()


scenes = [
    "Welcome to our organic farm",
    "Fresh vegetables are harvested every morning",
    "Modern tractors help improve productivity"
]


print("\n")
print("=" * 70)
print("FRAMECRAFT AI VIDEO RETRIEVAL")
print("=" * 70)


for scene in scenes:

    result = retriever.retrieve(
        scene,
        top_k=5
    )

    print("\n")
    print("Scene")
    print("-" * 50)

    print(scene)

    print("\nBest Video:")
    print(result["best_video"])

    print("\nBest Score:")
    print(result["best_score"])

    print("\nRanking:")
    
    for index, item in enumerate(
        result["rankings"],
        start=1
    ):

        print(
            f"{index}. "
            f"{item['video']} "
            f"({item['score']})"
        )


print("\n")
print("=" * 70)
print("Video Retrieval Test Completed!")
print("=" * 70)