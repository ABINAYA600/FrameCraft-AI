from app.services.comment_reply_pipeline import (
    CommentReplyPipeline,
)


print("================================")
print("FRAMECRAFT COMMENT REPLY PIPELINE")
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


pipeline = CommentReplyPipeline(
    creator_profile=creator_profile,
    auto_reply_enabled=True,
)


comments = [
    "Amazing video!",
    "Thank you for sharing this!",
    "Hey!",
    "How did you make this?",
    "I love your content!",
    "Where do you live?",
    "You are fake!",
    "Follow me and check my profile",
]


print()
print("================================")
print("PROCESSING COMMENTS")
print("================================")


results = []


for number, comment in enumerate(
    comments,
    start=1,
):

    print()
    print(
        f"Comment {number}: "
        f"{comment}"
    )

    result = (
        pipeline.process_comment(
            comment
        )
    )

    results.append(result)

    print(
        f"Category: "
        f"{result['category']}"
    )

    print(
        f"Complexity: "
        f"{result['complexity']}"
    )

    print(
        f"Confidence: "
        f"{result['confidence']}"
    )

    print(
        f"Status: "
        f"{result['status']}"
    )

    print(
        f"Permission required: "
        f"{result['requires_permission']}"
    )

    print(
        f"Reply: "
        f"{result['reply']}"
    )

    print(
        f"Reason: "
        f"{result['reason']}"
    )


# =========================================
# SUMMARY
# =========================================

automatic = [
    result
    for result in results
    if result["status"]
    == "auto_approved"
]


pending = [
    result
    for result in results
    if result["status"]
    == "waiting_for_creator"
]


print()
print("================================")
print("PIPELINE SUMMARY")
print("================================")

print(
    f"Total comments: "
    f"{len(results)}"
)

print(
    f"Automatic replies: "
    f"{len(automatic)}"
)

print(
    f"Creator approval required: "
    f"{len(pending)}"
)


print()
print("================================")
print("PENDING CREATOR APPROVAL")
print("================================")


for item in pipeline.pending_replies():

    print()
    print(
        f"Reply ID: "
        f"{item['reply_id']}"
    )

    print(
        f"Comment: "
        f"{item['comment']}"
    )

    print(
        f"Suggested reply: "
        f"{item['reply']}"
    )


print()
print("================================")
print("COMMENT REPLY PIPELINE TEST PASSED")
print("================================")