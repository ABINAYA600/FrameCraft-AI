from ml_models.music_model import MusicModel


print("Starting Music Model Test...")


model = MusicModel(
    music_folder="datasets/music"
)


scripts = [
    "Welcome to our peaceful organic farm",
    "Modern tractors improve productivity using technology",
    "We are celebrating the success of our farmers"
]


print("\n")
print("=" * 70)
print("FRAMECRAFT AI MUSIC SELECTION")
print("=" * 70)


for script in scripts:

    result = model.select_music(
        script
    )

    print("\nScript:")
    print(script)

    print("\nMood:")
    print(result["mood"])

    print("Selected Music:")
    print(result["music"])

    print("Music Path:")
    print(result["path"])


print("\n")
print("=" * 70)
print("Music Model Test Completed!")
print("=" * 70)