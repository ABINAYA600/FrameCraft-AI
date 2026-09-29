from ml_models.decision_engine import DecisionEngine


print("Starting Decision Engine Test...")


engine = DecisionEngine()


scenes = [
    "Welcome to our organic farm",
    "Fresh vegetables are harvested every morning",
    "Modern tractors help improve productivity"
]


storyboard = engine.process(
    scenes
)


print("\n")
print("=" * 75)
print("FRAMECRAFT AI FINAL STORYBOARD")
print("=" * 75)


for item in storyboard:

    print("\nScene", item["scene_number"])
    print("-" * 60)

    print(
        "Scene Text :",
        item["scene"]
    )

    print(
        "Media Type :",
        item["media_type"]
    )

    print(
        "Media      :",
        item["media"]
    )

    print(
        "Score      :",
        item["score"]
    )

    print(
        "Duration   :",
        item["duration"],
        "seconds"
    )

    print(
        "Transition :",
        item["transition"]
    )

    print(
        "Effect     :",
        item["camera_effect"]
    )


print("\n")
print("=" * 75)
print("Decision Engine Test Completed!")
print("=" * 75)