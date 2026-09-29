from app.services.creator_profile import CreatorProfile


print("================================")
print("CREATOR PROFILE TEST")
print("================================")


profile = CreatorProfile(
    "output/test_creator_profile.json"
)


# ==================================================
# UPDATE
# ==================================================

profile.update_profile(

    creator_name="Abinaya",

    niche=[
        "AI",
        "Technology",
        "Education"
    ],

    language="English",

    tone="friendly",

    style="simple",

    reply_length="short",

    use_emojis=True,

    avoid_arguments=True,

    auto_reply_enabled=False,

    require_permission_for_complex=True,

    preferred_greeting="Thanks for your comment!",

    preferred_signoff="",

    topics_to_avoid=[
        "political arguments"
    ]
)


print("\nCreator Profile:")

print(
    profile.get_profile()
)


# ==================================================
# SAVE
# ==================================================

profile.save()


# ==================================================
# LOAD
# ==================================================

loaded_profile = CreatorProfile(
    "output/test_creator_profile.json"
)

loaded_profile.load()


print("\nLoaded Creator Name:")

print(
    loaded_profile.get(
        "creator_name"
    )
)


print("\n================================")
print("CREATOR PROFILE TEST PASSED")
print("================================")