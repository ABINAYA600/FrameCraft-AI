from app.services.media_retrieval import MediaRetrieval


print("Starting Media Retrieval Test...")

engine = MediaRetrieval()


scenes = [
    "Welcome to our organic farm",
    "Fresh vegetables are harvested every morning",
    "Modern tractors help improve productivity"
]


results = engine.process(
    scenes,
    top_k=5
)


print("\n")
print("=" * 70)
print("FRAMECRAFT AI MEDIA RETRIEVAL")
print("=" * 70)


for result in results:

    print("\n")
    print("Scene")
    print("-" * 50)

    print(result["scene"])

    print("\nBest Media")
    print("-" * 50)

    best = result["best_media"]

    if best:

        print(
            f"Type  : {best['type']}"
        )

        print(
            f"File  : {best['file']}"
        )

        print(
            f"Score : {best['score']}"
        )

    print("\nRanking")
    print("-" * 50)

    for index, item in enumerate(
        result["rankings"],
        start=1
    ):

        print(
            f"{index}. "
            f"[{item['type']}] "
            f"{item['file']} "
            f"({item['score']})"
        )


print("\n")
print("=" * 70)
print("Media Retrieval Test Completed!")
print("=" * 70)