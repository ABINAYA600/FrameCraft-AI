from app.services.creator_profile_analyzer import (
    CreatorProfileAnalyzer
)


print("================================")
print("CREATOR PROFILE ANALYZER TEST")
print("================================")


transcripts = [
    {
        "video": "video1.mp4",
        "text": """
        Hey guys! Welcome back.
        Today I am going to show you how this works.
        Let me explain it step by step.
        """
    },
    {
        "video": "video2.mp4",
        "text": """
        Hi everyone!
        This is another simple tutorial.
        I hope this helps you.
        """
    },
    {
        "video": "video3.mp4",
        "text": """
        Let's learn something new today.
        Keep going and never give up!
        """
    }
]


comments = [
    {
        "text": "Thank you so much! 😊"
    },
    {
        "text": "This is very useful 👍"
    },
    {
        "text": "Can you explain this in more detail?"
    }
]


captions = [
    {
        "text": "Welcome back everyone! 😊"
    },
    {
        "text": "Today we learn something new."
    }
]


creator_settings = {
    "auto_reply": True
}


analyzer = CreatorProfileAnalyzer(
    output_path="output/creator_profile.json"
)


profile = analyzer.analyze(
    transcripts=transcripts,
    comments=comments,
    captions=captions,
    creator_settings=creator_settings
)


print()
print("================================")
print("CREATOR PROFILE")
print("================================")

print("Tone:")
print(profile["tone"])

print()

print("Language:")
print(profile["language"])

print()

print("Style:")
print(profile["style"])

print()

print("Reply Length:")
print(profile["reply_length"])

print()

print("Emoji Preference:")
print(profile["emoji_preference"])

print()

print("Auto Reply:")
print(profile["auto_reply"])

print()

print("Topics To Avoid:")
print(profile["topics_to_avoid"])

print()

print("Confidence:")
print(profile["confidence"])

print()
print("================================")
print("CREATOR PROFILE TEST PASSED")
print("================================")