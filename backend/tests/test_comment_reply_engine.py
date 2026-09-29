from app.services.comment_reply_engine import CommentReplyEngine


print("================================")
print("COMMENT REPLY ENGINE TEST")
print("================================")


creator_profile = {
    "tone": "friendly",
    "language": "English",
    "style": "casual",
    "reply_length": "short",
    "emoji_preference": "occasional",
    "auto_reply_enabled": True,
    "topics_to_avoid": [
        "politics",
        "personal information",
    ],
}


engine = CommentReplyEngine(
    creator_profile=creator_profile,
    auto_reply_enabled=True,
)


comments = [
    "Amazing video! I loved it!",
    "Thank you for sharing this.",
    "Hey!",
    "How did you make this video?",
    "This is really helpful.",
    "Where do you live?",
    "You are fake!",
    "Follow me and check my profile",
    "Can you explain this?",
    "I love your content!",
]


print()
print("================================")
print("COMMENT ANALYSIS")
print("================================")


for index, comment in enumerate(comments, start=1):

    print()
    print(f"Comment {index}: {comment}")

    result = engine.analyze_comment(comment)

    print(f"Category: {result.category}")
    print(f"Sentiment: {result.sentiment}")
    print(f"Complexity: {result.complexity}")
    print(f"Confidence: {result.confidence}")
    print(
        f"Requires Permission: "
        f"{result.requires_permission}"
    )
    print(f"Reason: {result.reason}")

    if result.suggested_reply:
        print(
            f"Suggested Reply: "
            f"{result.suggested_reply}"
        )


print()
print("================================")
print("BATCH TEST")
print("================================")


batch_result = engine.analyze_comments(
    comments
)

print(f"Comments processed: {len(batch_result)}")


automatic = [
    item
    for item in batch_result
    if not item["requires_permission"]
]

permission_required = [
    item
    for item in batch_result
    if item["requires_permission"]
]


print(
    f"Automatic replies: "
    f"{len(automatic)}"
)

print(
    f"Permission required: "
    f"{len(permission_required)}"
)


print()
print("================================")
print("COMMENT REPLY ENGINE TEST PASSED")
print("================================")