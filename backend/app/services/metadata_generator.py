import os
import re
import json
from collections import Counter
from typing import List, Dict, Any, Optional


# ==================================================
# COMMON STOPWORDS FOR NLP HEURISTICS
# ==================================================
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "using", "uses", "used", "shows", "showing", "scene"
}


# ==================================================
# METADATA STRATEGY (PLUGGABLE FOR FUTURE LLM)
# ==================================================
class BaseMetadataStrategy:
    """Base interface for metadata generation strategies."""

    def generate_title(self, scenes: List[str], requested_title: Optional[str] = None, platform: str = "youtube") -> str:
        raise NotImplementedError

    def generate_description(self, scenes: List[str], title: str, platform: str = "youtube") -> str:
        raise NotImplementedError

    def generate_hashtags(self, scenes: List[str], title: str, platform: str = "youtube") -> List[str]:
        raise NotImplementedError


class LocalMetadataStrategy(BaseMetadataStrategy):
    """
    Deterministic, content-grounded metadata generation using
    local NLP heuristics and keyword extraction from the storyboard.
    """

    def _extract_keywords(self, text_list: List[str]) -> List[str]:
        """Extracts frequency-ranked content keywords excluding stopwords."""
        words = []
        for text in text_list:
            clean = re.sub(r"[^\w\s-]", " ", str(text).lower())
            tokens = [w.strip() for w in clean.split() if len(w.strip()) > 2]
            words.extend([w for w in tokens if w not in STOPWORDS])

        counts = Counter(words)
        return [word for word, _ in counts.most_common()]

    def generate_title(self, scenes: List[str], requested_title: Optional[str] = None, platform: str = "youtube") -> str:
        if requested_title and str(requested_title).strip():
            return str(requested_title).strip()

        if not scenes:
            return "FrameCraft AI Video"

        # Look for salient noun phrases or key topics
        keywords = self._extract_keywords(scenes)

        if not keywords:
            # Fallback to first scene snippet
            first_scene = scenes[0].strip().rstrip(".")
            return first_scene[:50].title() if first_scene else "FrameCraft AI Video"

        # Check for multi-word domain concepts in scenes
        combined_text = " ".join(scenes).lower()

        key_phrases = [
            ("modern farming technology", "Modern Farming Technology"),
            ("smart farming technology", "Smart Farming Technology"),
            ("smart farming", "Smart Farming"),
            ("sustainable agriculture", "Sustainable Agriculture"),
            ("organic farming", "Organic Farming"),
            ("crop production", "Modern Crop Production"),
            ("fresh produce", "Fresh Farm Produce"),
            ("agricultural technology", "Agricultural Technology"),
        ]

        for phrase, formatted in key_phrases:
            if phrase in combined_text:
                return formatted

        # Construct title from top 2-3 salient keywords
        top_words = [w.title() for w in keywords[:3]]
        if len(top_words) >= 2:
            return f"{top_words[0]} {top_words[1]} {top_words[2]}" if len(top_words) == 3 else f"{top_words[0]} & {top_words[1]}"

        return top_words[0] if top_words else "FrameCraft AI Video"

    def generate_description(self, scenes: List[str], title: str, platform: str = "youtube") -> str:
        if not scenes:
            return f"Video created with FrameCraft AI: {title}."

        cleaned_scenes = [s.strip().rstrip(".") for s in scenes if s and s.strip()]

        if not cleaned_scenes:
            return f"Explore {title} created with FrameCraft AI."

        # Ground description naturally from scenes
        if len(cleaned_scenes) == 1:
            body = f"Explore {cleaned_scenes[0].lower()}."
        elif len(cleaned_scenes) == 2:
            body = f"Explore {cleaned_scenes[0].lower()} and {cleaned_scenes[1].lower()}."
        else:
            first_part = ", ".join(s.lower() for s in cleaned_scenes[:-1])
            last_part = cleaned_scenes[-1].lower()
            body = f"Discover {first_part}, and {last_part}."

        # Adapt based on platform
        if platform in ("youtube_shorts", "instagram", "instagram_reels"):
            description = f"{title}\n\n{body}\n\nCreated with FrameCraft AI."
        else:
            description = (
                f"Welcome to this comprehensive overview of {title}.\n\n"
                f"{body}\n\n"
                f"Generated automatically with FrameCraft AI."
            )

        # Enforce maximum character bound (~5000 chars)
        if len(description) > 5000:
            description = description[:4990] + "..."

        return description

    def generate_hashtags(self, scenes: List[str], title: str, platform: str = "youtube") -> List[str]:
        hashtags = []
        seen = set()

        def add_tag(tag_str: str, max_limit: int = 9):
            clean_tag = re.sub(r"[^\w]", "", tag_str)
            if not clean_tag:
                return
            formatted_tag = f"#{clean_tag}"
            tag_lower = formatted_tag.lower()
            if tag_lower not in seen and len(hashtags) < max_limit:
                seen.add(tag_lower)
                hashtags.append(formatted_tag)

        # 1. Topic-specific concept extraction (e.g. #Farming, #AgriTech, #SmartFarming)
        combined_text = f"{title} {' '.join(scenes)}".lower()

        phrase_map = [
            ("organic farming", "OrganicFarming"),
            ("sustainable agriculture", "SustainableAgriculture"),
            ("sustainable farming", "SustainableFarming"),
            ("smart farming", "SmartFarming"),
            ("farming technology", "AgriTech"),
            ("crop production", "CropProduction"),
            ("fresh vegetables", "FreshProduce"),
            ("modern farm", "ModernFarming"),
            ("modern tractors", "Tractors"),
            ("agriculture", "Agriculture"),
            ("farming", "Farming"),
            ("technology", "Technology"),
            ("innovation", "Innovation"),
        ]

        for phrase, tag in phrase_map:
            if phrase in combined_text:
                add_tag(tag, max_limit=9)

        # 2. Extract single salient keywords from title & scenes
        keywords = self._extract_keywords([title] + scenes)
        for kw in keywords:
            if len(kw) >= 4:
                add_tag(kw.title(), max_limit=9)

        # 3. Always include FrameCraftAI brand hashtag
        if "#FrameCraftAI".lower() not in seen:
            if len(hashtags) >= 10:
                hashtags = hashtags[:9]
            hashtags.append("#FrameCraftAI")

        # Ensure max 8-10 hashtags
        return hashtags[:10]


# ==================================================
# MAIN METADATA GENERATOR SERVICE
# ==================================================
class MetadataGenerator:
    """
    FrameCraft AI Metadata Generator

    Generates grounded video titles, descriptions, and hashtags
    directly from storyboard / script scenes.
    """

    def __init__(
        self,
        output_folder: str = "output",
        strategy: Optional[BaseMetadataStrategy] = None
    ):
        self.output_folder = output_folder
        self.strategy = strategy or LocalMetadataStrategy()

        os.makedirs(self.output_folder, exist_ok=True)
        print("Metadata Generator Initialized!")

    # ==================================================
    # STORYBOARD TEXT EXTRACTION
    # ==================================================
    def extract_storyboard_text(self, storyboard: Any) -> List[str]:
        """
        Extracts text descriptions from storyboard scenes.
        Supports list of dicts, dicts with various keys, or strings.
        """
        if not storyboard:
            return []

        if isinstance(storyboard, str):
            return [s.strip() for s in storyboard.split(".") if s.strip()]

        scenes_text = []

        if isinstance(storyboard, list):
            for item in storyboard:
                if isinstance(item, dict):
                    # Check common scene description keys
                    text = (
                        item.get("scene")
                        or item.get("description")
                        or item.get("text")
                        or item.get("content")
                        or item.get("script")
                        or ""
                    )
                    if str(text).strip():
                        scenes_text.append(str(text).strip())
                elif isinstance(item, str) and item.strip():
                    scenes_text.append(item.strip())
        elif isinstance(storyboard, dict):
            # Check if dict contains a scenes list
            if "scenes" in storyboard and isinstance(storyboard["scenes"], list):
                return self.extract_storyboard_text(storyboard["scenes"])
            text = (
                storyboard.get("scene")
                or storyboard.get("description")
                or storyboard.get("text")
                or storyboard.get("content")
                or ""
            )
            if str(text).strip():
                scenes_text.append(str(text).strip())

        return scenes_text

    # ==================================================
    # GENERATE METADATA
    # ==================================================
    def generate_metadata(
        self,
        storyboard: Any,
        requested_title: Optional[str] = None,
        platform: str = "youtube"
    ) -> Dict[str, Any]:
        """
        Generates structured metadata (title, description, hashtags)
        grounded in the given storyboard.
        """
        platform = (platform or "youtube").lower()
        scenes = self.extract_storyboard_text(storyboard)

        # 1. Title Generation
        title = self.strategy.generate_title(
            scenes=scenes,
            requested_title=requested_title,
            platform=platform
        )

        # 2. Description Generation
        description = self.strategy.generate_description(
            scenes=scenes,
            title=title,
            platform=platform
        )

        # 3. Hashtag Generation
        hashtags = self.strategy.generate_hashtags(
            scenes=scenes,
            title=title,
            platform=platform
        )

        metadata = {
            "title": title,
            "description": description,
            "hashtags": hashtags,
            "platform": platform,
            "generator": "FrameCraft AI Metadata Generator"
        }

        return metadata

    # ==================================================
    # SAVE METADATA
    # ==================================================
    def save_metadata(
        self,
        metadata: Dict[str, Any],
        output_name: str = "framecraft_metadata.json",
        output_path: Optional[str] = None
    ) -> str:
        """
        Saves metadata dictionary as formatted JSON.
        Returns the saved file path.
        """
        if output_path:
            target_path = output_path
        else:
            target_path = os.path.join(self.output_folder, output_name)

        os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)

        normalized_path = target_path.replace("\\", "/")
        return normalized_path
