from ml_models.script_model import ScriptModel


script = """
Welcome to our organic farm.
Fresh vegetables are harvested every morning.
Our farmers use sustainable farming methods.
"""


model = ScriptModel()

result = model.process(script)

print("\n========== Script Analysis ==========\n")

print(f"Total Scenes : {result['total_scenes']}\n")

for index, scene in enumerate(result["scenes"], start=1):
    print(f"Scene {index}")
    print(scene)
    print()

print("Embedding Shape:", result["embeddings"].shape)