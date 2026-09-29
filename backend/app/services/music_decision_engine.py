class MusicDecisionEngine:

    def decide(self, scenes):

        timeline = []

        if not scenes:
            return timeline

        first_scene_number = scenes[0].get(
            "scene_number"
        )

        last_scene_number = scenes[-1].get(
            "scene_number"
        )

        for scene in scenes:

            scene_number = scene.get(
                "scene_number"
            )

            has_speech = scene.get(
                "has_speech",
                False
            )

            importance = scene.get(
                "importance",
                "normal"
            )

            # ==================================================
            # IMPORTANT SPEECH
            # ==================================================

            if has_speech and importance == "high":

                state = "OFF"
                volume = 0.0

            # ==================================================
            # NORMAL SPEECH
            # ==================================================

            elif has_speech:

                state = "DUCK"
                volume = 0.08

            # ==================================================
            # LAST SCENE
            # ==================================================

            elif scene_number == last_scene_number:

                state = "FADE_OUT"
                volume = 0.30

            # ==================================================
            # FIRST SCENE
            # ==================================================

            elif scene_number == first_scene_number:

                state = "FADE_IN"
                volume = 0.30

            # ==================================================
            # NORMAL B-ROLL
            # ==================================================

            else:

                state = "ON"
                volume = 0.30

            timeline.append(
                {
                    "scene_number": scene_number,
                    "music_state": state,
                    "volume": volume
                }
            )

        return timeline