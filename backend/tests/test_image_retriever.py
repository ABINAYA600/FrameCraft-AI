from app.services.image_retriever import ImageRetriever


print("Starting Image Retriever Test...")


retriever = ImageRetriever(
    image_folder="datasets/images"
)


scene = "Modern tractors help improve productivity"


result = retriever.retrieve(
    scene,
    top_k=3
)


print("\n==============================")
print("IMAGE RETRIEVAL RESULT")
print("==============================")


print("\nScene:")
print(result["scene"])


print("\nBest Image:")
print(result["best_image"])


print("\nBest Score:")
print(result["best_score"])


print("\nRanking:")

for index, item in enumerate(
    result["rankings"],
    start=1
):

    print(
        f"{index}. "
        f"{item['image']} "
        f"({item['score']})"
    )


print("\nImage Retriever Test Completed!")