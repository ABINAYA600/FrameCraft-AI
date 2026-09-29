from app.services.music_catalog import MusicCatalog


print("Starting Music Catalog Test...")

catalog = MusicCatalog()


print("\n========== ALL MUSIC ==========")

for track in catalog.get_all_tracks():

    print(
        track["title"],
        "->",
        track["mood"]
    )


print("\n========== SEARCH TEST ==========")

results = catalog.search("peaceful")

for track in results:

    print(
        "Found:",
        track["title"]
    )


print("\n========== MOOD TEST ==========")

results = catalog.search_by_mood("happy")

for track in results:

    print(
        "Mood Match:",
        track["title"]
    )


print("\nMusic Catalog Test Completed!")