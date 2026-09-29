import os

from app.services.media_retrieval import MediaRetrieval


class DecisionEngine:

    """
    FrameCraft AI Decision Engine

    Decides:
        - image or video
        - selected media
        - duration
        - transition
        - camera effect
        - clip timing
    """

    def __init__(self):

        print("Initializing Decision Engine...")

        self.media_retrieval = MediaRetrieval()

        print("✅ Decision Engine Initialized!")

    # --------------------------------------------------
    # Decide media for one scene
    # --------------------------------------------------

    def decide_scene(
        self,
        scene,
        scene_number,
        used_videos=None
    ):

        if used_videos is None:
            used_videos = set()

        result = self.media_retrieval.retrieve(
            scene,
            top_k=5
        )

        rankings = result["rankings"]

        if not rankings:

            return {
                "scene_number": scene_number,
                "scene": scene,
                "media_type": None,
                "media": None,
                "score": 0,
                "duration": 5,
                "transition": "fade",
                "camera_effect": None
            }

        # ------------------------------------------------
        # Prefer an unused video when possible
        # ------------------------------------------------

        selected = None

        for item in rankings:

            if item["type"] == "video":

                video_name = item["file"]

                if video_name not in used_videos:

                    selected = item

                    used_videos.add(
                        video_name
                    )

                    break

        # ------------------------------------------------
        # If no unused video, use best result
        # ------------------------------------------------

        if selected is None:

            selected = rankings[0]

            if selected["type"] == "video":

                used_videos.add(
                    selected["file"]
                )

        # ------------------------------------------------
        # Decide duration
        # ------------------------------------------------

        if selected["type"] == "video":

            duration = 5

            transition = "cut"

            camera_effect = None

        else:

            duration = 5

            transition = "fade"

            camera_effect = "zoom_in"

        # ------------------------------------------------
        # Create decision
        # ------------------------------------------------

        decision = {

            "scene_number": scene_number,

            "scene": scene,

            "media_type": selected["type"],

            "media": selected["file"],

            "media_path": selected["path"],

            "score": selected["score"],

            "duration": duration,

            "transition": transition,

            "camera_effect": camera_effect
        }

        return decision

    # --------------------------------------------------
    # Process complete storyboard
    # --------------------------------------------------

    def process(
        self,
        scenes
    ):

        storyboard = []

        used_videos = set()

        for index, scene in enumerate(
            scenes,
            start=1
        ):

            decision = self.decide_scene(
                scene=scene,
                scene_number=index,
                used_videos=used_videos
            )

            storyboard.append(
                decision
            )

        return storyboard