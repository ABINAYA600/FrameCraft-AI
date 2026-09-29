from ml_models.script_model import ScriptModel
from ml_models.image_model import ImageModel


script = """
Welcome to our organic farm.
Fresh vegetables are harvested every morning.
Modern tractors help improve productivity.
"""


# ------------------------------------
# Script Module
# ------------------------------------

script_model = ScriptModel()

script_result = script_model.process(script)

scenes = script_result["scenes"]


# ------------------------------------
# Image Module
# ------------------------------------

image_model = ImageModel()

storyboard = image_model.process(
    scenes,
    "datasets/samples"
)


# ------------------------------------
# Display Output
# ------------------------------------

print("\n")
print("=" * 70)
print("FRAMECRAFT AI STORYBOARD")
print("=" * 70)

for index, item in enumerate(storyboard, start=1):

    print(f"\nScene {index}")
    print("-" * 50)

    print("Scene Text :")
    print(item["scene"])

    print("\nBest Image :")
    print(item["best_image"])

    print("\nSimilarity :")
    print(item["best_score"])

    print("\nRanking")

    for rank, image in enumerate(item["rankings"], start=1):

        print(
            f"{rank}. {image['image']}  ({image['score']})"
        )

print("\n")
print("=" * 70)
print("Storyboarding Completed Successfully!")
print("=" * 70)