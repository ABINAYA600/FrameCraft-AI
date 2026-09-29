from ml_models.fafm import FAFM


def print_separator():
    print()
    print("=" * 60)


def main():

    print()
    print("=" * 60)
    print("FAFM TEST")
    print("=" * 60)

    # =========================================================
    # 1. INITIALIZATION
    # =========================================================

    print()
    print("[1] Initializing FAFM...")

    try:

        fafm = FAFM()

        print("✓ FAFM initialization completed")

    except Exception as e:

        print("✗ FAFM initialization failed")
        print(
            f"ERROR: {type(e).__name__}: {str(e)}"
        )

        return

    # =========================================================
    # 2. SYSTEM STATUS
    # =========================================================

    print()
    print("[2] Checking system status...")

    status = fafm.get_system_status()

    print(status)

    # =========================================================
    # 3. SCRIPT PROCESSING
    # =========================================================

    print()
    print("[3] Testing script processing...")

    script = """
    Smart farming uses artificial intelligence.
    Farmers can monitor crops using sensors.
    AI helps farmers improve productivity.
    """

    result = fafm.process_script(script)

    print("Success:", result["success"])

    if not result["success"]:

        print(
            "ERROR:",
            result.get("error")
        )

    else:

        print()
        print("Scenes:")

        for index, scene in enumerate(
            result["scenes"],
            start=1
        ):

            print(
                f"  Scene {index}: {scene}"
            )

        print()
        print(
            "Scene count:",
            result.get("scene_count")
        )

        print(
            "Embedding shape:",
            result.get("embedding_shape")
        )

    # =========================================================
    # 4. COMMENT PROCESSING
    # =========================================================

    print()
    print("[4] Testing comment processing...")

    comments = [

        "Nice video!",

        "Thank you for this!",

        "Can you explain how this works?",

        "Send me your phone number",
    ]

    for comment in comments:

        print()
        print(
            f"Comment: {comment}"
        )

        result = fafm.process_comment(
            comment
        )

        print(result)

    # =========================================================
    # 5. CREATOR PROFILE ANALYSIS
    # =========================================================

    print()
    print("[5] Testing creator analysis...")

    transcripts = [

        {
            "text": (
                "Hello everyone! Welcome to my tutorial. "
                "Today I will explain how smart farming works."
            )
        },

        {
            "text": (
                "This technology helps farmers monitor "
                "their crops and improve productivity."
            )
        },
    ]

    captions = [

        {
            "text": (
                "Learn these simple steps to improve "
                "your farming process."
            )
        }
    ]

    creator_comments = [

        {
            "text": "Great explanation!"
        },

        {
            "text": "Thank you!"
        },
    ]

    creator_settings = {

        "auto_reply": True

    }

    creator_result = fafm.analyze_creator(

        transcripts=transcripts,

        comments=creator_comments,

        captions=captions,

        creator_settings=creator_settings,
    )

    print(creator_result)

    if creator_result["success"]:

        profile = creator_result[
            "creator_profile"
        ]

        print()
        print("Creator Profile Summary:")

        print(
            "Tone:",
            profile.get("tone")
        )

        print(
            "Language:",
            profile.get("language")
        )

        print(
            "Style:",
            profile.get("style")
        )

        print(
            "Reply Length:",
            profile.get("reply_length")
        )

        print(
            "Emoji Preference:",
            profile.get(
                "emoji_preference"
            )
        )

        print(
            "Auto Reply:",
            profile.get(
                "auto_reply"
            )
        )

        print(
            "Topics to Avoid:",
            profile.get(
                "topics_to_avoid"
            )
        )

        print(
            "Confidence:",
            profile.get(
                "confidence"
            )
        )

    else:

        print(
            "ERROR:",
            creator_result.get(
                "error"
            )
        )

    # =========================================================
    # 6. TEST PERMISSION / PENDING REPLIES
    # =========================================================

    print()
    print("[6] Checking pending replies...")

    pending = fafm.pending_replies()

    print(
        "Pending replies:"
    )

    print(pending)

    # =========================================================
    # 7. SYSTEM STATUS AFTER PROCESSING
    # =========================================================

    print()
    print("[7] Final FAFM system status...")

    final_status = fafm.get_system_status()

    for module, state in final_status.items():

        print(
            f"{module}: {state}"
        )

    # =========================================================
    # COMPLETED
    # =========================================================

    print()
    print("=" * 60)
    print("FAFM TEST COMPLETED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()