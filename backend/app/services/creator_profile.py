import os
import json


class CreatorProfile:

    def __init__(
        self,
        storage_path="output/creator_profile.json"
    ):

        self.storage_path = storage_path

        # Make sure the directory exists
        directory = os.path.dirname(
            self.storage_path
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        # Default creator profile
        self.profile = {

            "creator_name": "",

            "niche": [],

            "language": "English",

            "tone": "friendly",

            "style": "simple",

            "reply_length": "short",

            "use_emojis": True,

            "avoid_arguments": True,

            "auto_reply_enabled": False,

            "require_permission_for_complex": True,

            "preferred_greeting": "",

            "preferred_signoff": "",

            "topics_to_avoid": []
        }

    # ==================================================
    # UPDATE PROFILE
    # ==================================================

    def update_profile(
        self,
        **kwargs
    ):

        for key, value in kwargs.items():

            if key in self.profile:

                self.profile[key] = value

            else:

                print(
                    f"⚠️ Unknown profile field: {key}"
                )

        return self.profile

    # ==================================================
    # GET PROFILE
    # ==================================================

    def get_profile(self):

        return self.profile.copy()

    # ==================================================
    # GET VALUE
    # ==================================================

    def get(
        self,
        key,
        default=None
    ):

        return self.profile.get(
            key,
            default
        )

    # ==================================================
    # SAVE PROFILE
    # ==================================================

    def save(self):

        with open(
            self.storage_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.profile,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"✅ Creator profile saved: "
            f"{self.storage_path}"
        )

        return self.storage_path

    # ==================================================
    # LOAD PROFILE
    # ==================================================

    def load(self):

        if not os.path.exists(
            self.storage_path
        ):

            print(
                "No saved creator profile found."
            )

            return self.profile

        with open(
            self.storage_path,
            "r",
            encoding="utf-8"
        ) as file:

            loaded_profile = json.load(
                file
            )

        # Only accept known fields
        for key in self.profile:

            if key in loaded_profile:

                self.profile[key] = (
                    loaded_profile[key]
                )

        print(
            f"✅ Creator profile loaded: "
            f"{self.storage_path}"
        )

        return self.profile

    # ==================================================
    # RESET PROFILE
    # ==================================================

    def reset(self):

        self.profile = {

            "creator_name": "",

            "niche": [],

            "language": "English",

            "tone": "friendly",

            "style": "simple",

            "reply_length": "short",

            "use_emojis": True,

            "avoid_arguments": True,

            "auto_reply_enabled": False,

            "require_permission_for_complex": True,

            "preferred_greeting": "",

            "preferred_signoff": "",

            "topics_to_avoid": []
        }

        return self.profile