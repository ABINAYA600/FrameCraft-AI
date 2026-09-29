import os
import json
import uuid
from datetime import datetime


class CreatorKnowledge:

    def __init__(
        self,
        storage_path="output/creator_knowledge.json"
    ):

        self.storage_path = storage_path

        directory = os.path.dirname(self.storage_path)

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        self.data = {
            "facts": [],
            "projects": [],
            "faqs": [],
            "approved_answers": [],
            "expertise": [],
            "preferred_terms": [],
            "restricted_topics": [],
            "do_not_claim": []
        }

    # ==================================================
    # GENERIC ITEM ID
    # ==================================================

    def _generate_id(self, prefix):

        return (
            f"{prefix}_"
            f"{uuid.uuid4().hex[:8]}"
        )

    # ==================================================
    # ADD FACT
    # ==================================================

    def add_fact(
        self,
        fact,
        category="general"
    ):

        item = {
            "id": self._generate_id("fact"),
            "fact": fact,
            "category": category
        }

        self.data["facts"].append(item)

        return item

    # ==================================================
    # ADD PROJECT
    # ==================================================

    def add_project(
        self,
        name,
        description="",
        script="",
        media_source="both"
    ):

        now = datetime.now().isoformat()

        item = {
            "id": self._generate_id("project"),

            "name": name,

            "description": description,

            "script": script,

            "media_source": media_source,

            "images": [],

            "videos": [],

            "music": [],

            "generated_videos": [],

            "created_at": now,

            "updated_at": now
        }

        self.data["projects"].append(item)

        return item

    # ==================================================
    # GET PROJECT
    # ==================================================

    def get_project(self, project_id):

        for project in self.data["projects"]:

            if project["id"] == project_id:
                return project

        return None

    # ==================================================
    # GET ALL PROJECTS
    # ==================================================

    def get_projects(self):

        return self.data["projects"]

    # ==================================================
    # UPDATE PROJECT
    # ==================================================

    def update_project(
        self,
        project_id,
        name=None,
        description=None,
        script=None,
        media_source=None
    ):

        project = self.get_project(project_id)

        if project is None:
            return None

        if name is not None:
            project["name"] = name

        if description is not None:
            project["description"] = description

        if script is not None:
            project["script"] = script

        if media_source is not None:
            project["media_source"] = media_source

        project["updated_at"] = datetime.now().isoformat()

        return project

    # ==================================================
    # ADD MEDIA TO PROJECT
    # ==================================================

    def add_project_media(
        self,
        project_id,
        media_type,
        media_item
    ):

        project = self.get_project(project_id)

        if project is None:
            return None

        if media_type not in [
            "images",
            "videos",
            "music"
        ]:
            raise ValueError(
                "media_type must be images, videos, or music"
            )

        project[media_type].append(media_item)

        project["updated_at"] = datetime.now().isoformat()

        return project

    # ==================================================
    # REMOVE MEDIA FROM PROJECT
    # ==================================================

    def remove_project_media(
        self,
        project_id,
        media_type,
        media_id
    ):

        project = self.get_project(project_id)

        if project is None:
            return None

        if media_type not in [
            "images",
            "videos",
            "music"
        ]:
            raise ValueError(
                "media_type must be images, videos, or music"
            )

        media_list = project[media_type]

        for index, item in enumerate(media_list):

            if item.get("id") == media_id:

                removed = media_list.pop(index)

                project["updated_at"] = datetime.now().isoformat()

                return removed

        return None

    # ==================================================
    # ADD GENERATED VIDEO
    # ==================================================

    def add_generated_video(
        self,
        project_id,
        video_item
    ):

        project = self.get_project(project_id)

        if project is None:
            return None

        project["generated_videos"].append(
            video_item
        )

        project["updated_at"] = datetime.now().isoformat()

        return project

    # ==================================================
    # ADD FAQ
    # ==================================================

    def add_faq(
        self,
        question,
        answer
    ):

        item = {
            "id": self._generate_id("faq"),
            "question": question,
            "answer": answer
        }

        self.data["faqs"].append(item)

        return item

    # ==================================================
    # ADD APPROVED ANSWER
    # ==================================================

    def add_approved_answer(
        self,
        question,
        answer
    ):

        item = {
            "id": self._generate_id("answer"),
            "question": question,
            "answer": answer
        }

        self.data["approved_answers"].append(item)

        return item

    # ==================================================
    # ADD EXPERTISE
    # ==================================================

    def add_expertise(
        self,
        topic
    ):

        if topic not in self.data["expertise"]:

            self.data["expertise"].append(topic)

        return self.data["expertise"]

    # ==================================================
    # ADD PREFERRED TERM
    # ==================================================

    def add_preferred_term(
        self,
        term,
        preferred_usage=""
    ):

        item = {
            "term": term,
            "preferred_usage": preferred_usage
        }

        self.data["preferred_terms"].append(item)

        return item

    # ==================================================
    # ADD RESTRICTED TOPIC
    # ==================================================

    def add_restricted_topic(
        self,
        topic
    ):

        if topic not in self.data["restricted_topics"]:

            self.data["restricted_topics"].append(topic)

        return self.data["restricted_topics"]

    # ==================================================
    # ADD DO-NOT-CLAIM
    # ==================================================

    def add_do_not_claim(
        self,
        statement
    ):

        if statement not in self.data["do_not_claim"]:

            self.data["do_not_claim"].append(
                statement
            )

        return self.data["do_not_claim"]

    # ==================================================
    # SEARCH KNOWLEDGE
    # ==================================================

    def search(
        self,
        query
    ):

        if not query:
            return []

        query_words = set(
            query.lower().split()
        )

        results = []

        # ----------------------------------------------
        # Facts
        # ----------------------------------------------

        for item in self.data["facts"]:

            text = (
                item["fact"]
                + " "
                + item["category"]
            ).lower()

            score = sum(
                1
                for word in query_words
                if word in text
            )

            if score > 0:

                results.append(
                    {
                        "type": "fact",
                        "score": score,
                        "data": item
                    }
                )

        # ----------------------------------------------
        # Projects
        # ----------------------------------------------

        for item in self.data["projects"]:

            text = (
                item.get("name", "")
                + " "
                + item.get("description", "")
                + " "
                + item.get("script", "")
            ).lower()

            score = sum(
                1
                for word in query_words
                if word in text
            )

            if score > 0:

                results.append(
                    {
                        "type": "project",
                        "score": score,
                        "data": item
                    }
                )

        # ----------------------------------------------
        # FAQs
        # ----------------------------------------------

        for item in self.data["faqs"]:

            text = (
                item["question"]
                + " "
                + item["answer"]
            ).lower()

            score = sum(
                1
                for word in query_words
                if word in text
            )

            if score > 0:

                results.append(
                    {
                        "type": "faq",
                        "score": score,
                        "data": item
                    }
                )

        # ----------------------------------------------
        # Approved Answers
        # ----------------------------------------------

        for item in self.data["approved_answers"]:

            text = (
                item["question"]
                + " "
                + item["answer"]
            ).lower()

            score = sum(
                1
                for word in query_words
                if word in text
            )

            if score > 0:

                results.append(
                    {
                        "type": "approved_answer",
                        "score": score,
                        "data": item
                    }
                )

        # ----------------------------------------------
        # Highest relevance first
        # ----------------------------------------------

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results

    # ==================================================
    # GET ALL KNOWLEDGE
    # ==================================================

    def get_all(self):

        return self.data

    # ==================================================
    # SAVE
    # ==================================================

    def save(self):

        directory = os.path.dirname(
            self.storage_path
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        with open(
            self.storage_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.data,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"Creator knowledge saved: "
            f"{self.storage_path}"
        )

        return self.storage_path

    # ==================================================
    # LOAD
    # ==================================================

    def load(self):

        if not os.path.exists(
            self.storage_path
        ):

            print(
                "No creator knowledge found."
            )

            return self.data

        with open(
            self.storage_path,
            "r",
            encoding="utf-8"
        ) as file:

            loaded_data = json.load(file)

        # Preserve existing structure while allowing
        # older creator_knowledge.json files to load.

        for key in self.data:

            if key in loaded_data:

                self.data[key] = loaded_data[key]

        # Upgrade old projects automatically.

        for project in self.data["projects"]:

            project.setdefault(
                "script",
                ""
            )

            project.setdefault(
                "media_source",
                "both"
            )

            project.setdefault(
                "images",
                []
            )

            project.setdefault(
                "videos",
                []
            )

            project.setdefault(
                "music",
                []
            )

            project.setdefault(
                "generated_videos",
                []
            )

            project.setdefault(
                "created_at",
                datetime.now().isoformat()
            )

            project.setdefault(
                "updated_at",
                project["created_at"]
            )

        print(
            f"Creator knowledge loaded: "
            f"{self.storage_path}"
        )

        return self.data