from app.services.creator_knowledge import CreatorKnowledge


print("================================")
print("CREATOR KNOWLEDGE TEST")
print("================================")


knowledge = CreatorKnowledge(
    "output/test_creator_knowledge.json"
)


# ==================================================
# ADD FACTS
# ==================================================

knowledge.add_fact(
    "FrameCraft AI is an AI-based video creation system.",
    category="project"
)

knowledge.add_fact(
    "FrameCraft AI can automatically recommend background music.",
    category="feature"
)


# ==================================================
# ADD PROJECT
# ==================================================

knowledge.add_project(
    "FrameCraft AI",
    "An AI system for automated video creation."
)


# ==================================================
# ADD FAQ
# ==================================================

knowledge.add_faq(
    "What is FrameCraft AI?",
    "FrameCraft AI helps automate video creation using AI."
)


# ==================================================
# APPROVED ANSWER
# ==================================================

knowledge.add_approved_answer(
    "Does FrameCraft AI generate thumbnails?",
    "Yes. FrameCraft AI can automatically generate thumbnails."
)


# ==================================================
# EXPERTISE
# ==================================================

knowledge.add_expertise(
    "Artificial Intelligence"
)

knowledge.add_expertise(
    "Machine Learning"
)

knowledge.add_expertise(
    "Video Generation"
)


# ==================================================
# PREFERRED TERMS
# ==================================================

knowledge.add_preferred_term(
    "FrameCraft",
    "Always write it as FrameCraft AI."
)


# ==================================================
# RESTRICTED TOPICS
# ==================================================

knowledge.add_restricted_topic(
    "Private personal information"
)


# ==================================================
# DO NOT CLAIM
# ==================================================

knowledge.add_do_not_claim(
    "Do not claim that a feature exists unless it has been confirmed."
)


# ==================================================
# SEARCH
# ==================================================

print(
    "\nSearching knowledge..."
)

results = knowledge.search(
    "FrameCraft AI thumbnail"
)


for result in results:

    print(
        "\nType:",
        result["type"]
    )

    print(
        "Score:",
        result["score"]
    )

    print(
        "Data:",
        result["data"]
    )


# ==================================================
# SAVE
# ==================================================

knowledge.save()


print("\n================================")
print("CREATOR KNOWLEDGE TEST PASSED")
print("================================")