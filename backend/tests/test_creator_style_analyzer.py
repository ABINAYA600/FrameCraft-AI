from app.services.creator_style_analyzer import (
    CreatorStyleAnalyzer
)


print("================================")
print("CREATOR STYLE ANALYZER TEST")
print("================================")


previous_videos = [

    {
        "title": "Welcome to My AI Journey",

        "script": """
        Hey everyone! 😊
        Welcome back to my channel.
        Today we are going to learn about
        artificial intelligence in a simple way.
        I hope this helps you understand AI better!
        """
    },

    {
        "title": "Machine Learning Explained",

        "script": """
        Hi everyone! 👋
        In today's video, we will learn
        how machine learning works.
        I will explain it step by step
        so it is easy to understand.
        Thanks for watching! ❤️
        """
    },

    {
        "title": "AI Project Development",

        "script": """
        Hey guys! 🚀
        Today I am showing you my AI project.
        We will build it step by step
        and understand how the technology works.
        I hope you enjoy the journey!
        """
    },

    {
        "title": "Smart Technology",

        "script": """
        Welcome back everyone!
        In this video we explore
        smart technology and artificial intelligence.
        Let's learn something new together.
        """
    }
]


# ==================================================
# INITIALIZE
# ==================================================

analyzer = CreatorStyleAnalyzer(
    "output/test_creator_profile.json"
)


# ==================================================
# ANALYZE
# ==================================================

profile, path = (
    analyzer.analyze_and_save(
        previous_videos
    )
)


# ==================================================
# PRINT RESULTS
# ==================================================

print(
    "\nDetected Language:"
)

print(
    profile["language"]
)


print(
    "\nDetected Tone:"
)

print(
    profile["tone"]
)


print(
    "\nDetected Style:"
)

print(
    profile["style"]
)


print(
    "\nDetected Reply Length:"
)

print(
    profile["reply_length"]
)


print(
    "\nEmoji Usage:"
)

print(
    profile["emoji_usage"]
)


print(
    "\nDetected Niche:"
)

print(
    profile["niche"]
)


print(
    "\nCommon Phrases:"
)

for phrase in profile[
    "common_phrases"
]:

    print(
        phrase
    )


print(
    "\nVideos Analyzed:"
)

print(
    profile["analysis"][
        "videos_analyzed"
    ]
)


print(
    "\nProfile File:"
)

print(
    path
)


print(
    "\n================================"
)

print(
    "CREATOR STYLE ANALYZER TEST PASSED"
)

print(
    "================================"
)