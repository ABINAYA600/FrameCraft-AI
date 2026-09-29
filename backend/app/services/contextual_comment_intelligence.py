import os
import re
import json
import urllib.request
import urllib.error
from datetime import datetime


class ContextualCommentIntelligence:
    """Grounded comment understanding and reply generation.

    Priority:
      1. creator knowledge base (FAQs, approved answers, facts, projects)
      2. creator profile
      3. current project script/metadata/video context
      4. optional OpenRouter LLM for general questions when configured
      5. existing deterministic reply from FAFM
    """

    STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "what", "why", "how",
        "can", "could", "would", "should", "do", "does", "did", "this", "that",
        "for", "to", "of", "in", "on", "and", "or", "it", "you", "your", "i",
        "we", "me", "my", "about", "please", "tell", "explain", "doesn", "t",
    }

    def __init__(self, knowledge):
        self.knowledge = knowledge

    def _tokens(self, text):
        words = re.findall(r"[a-zA-Z0-9_]+", str(text or "").lower())
        return {w for w in words if len(w) > 2 and w not in self.STOP_WORDS}

    def _score(self, query, text):
        q = self._tokens(query)
        t = self._tokens(text)
        if not q or not t:
            return 0
        overlap = q & t
        return len(overlap) + (1 if overlap and len(overlap) >= 2 else 0)

    def _knowledge_candidates(self, query):
        data = getattr(self.knowledge, "data", {}) or {}
        candidates = []
        for item in data.get("faqs", []):
            text = f"{item.get('question','')} {item.get('answer','')}"
            candidates.append((self._score(query, text), "faq", item))
        for item in data.get("approved_answers", []):
            text = f"{item.get('question','')} {item.get('answer','')}"
            candidates.append((self._score(query, text), "approved_answer", item))
        for item in data.get("facts", []):
            candidates.append((self._score(query, item.get("fact", "")), "fact", item))
        for item in data.get("projects", []):
            text = f"{item.get('name','')} {item.get('description','')}"
            candidates.append((self._score(query, text), "project", item))
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [c for c in candidates if c[0] > 0]

    def build_context(self, comment, project=None, video_id=None, creator_profile=None):
        context = {
            "creator_profile": creator_profile or {},
            "knowledge": [],
            "project": {},
            "video": {},
        }
        candidates = self._knowledge_candidates(comment)
        for score, kind, item in candidates[:5]:
            context["knowledge"].append({"score": score, "type": kind, "data": item})

        if project:
            context["project"] = {
                "id": project.get("id"),
                "name": project.get("name", ""),
                "description": project.get("description", ""),
                "script": project.get("script", ""),
                "media_source": project.get("media_source", "both"),
                "generated_metadata": self._generated_metadata(project),
            }
            videos = project.get("videos", [])
            video = next((v for v in videos if v.get("id") == video_id), None) if video_id else (videos[0] if videos else None)
            if video:
                context["video"] = {
                    "id": video.get("id"),
                    "name": video.get("name"),
                    "filename": video.get("filename"),
                    "content_type": video.get("content_type"),
                    "size": video.get("size"),
                    "analysis": video.get("analysis", {}),
                }
        return context

    def _generated_metadata(self, project):
        for item in project.get("generated", []):
            if isinstance(item, dict) and item.get("type") == "metadata":
                path = item.get("path")
                if path and os.path.exists(path):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            return json.load(f)
                    except Exception:
                        pass
        return {}

    def _project_answer(self, comment, context):
        project = context.get("project") or {}
        script = project.get("script", "")
        if not script:
            return None, 0
        sentences = re.split(r"(?<=[.!?])\s+", script.strip())
        scored = sorted(((self._score(comment, s), s) for s in sentences), reverse=True)
        if scored and scored[0][0] >= 2:
            return scored[0][1].strip(), scored[0][0]
        return None, 0

    def _knowledge_answer(self, context):
        if not context.get("knowledge"):
            return None, 0, None
        top = context["knowledge"][0]
        score, kind, item = top["score"], top["type"], top["data"]
        if kind in {"faq", "approved_answer"}:
            return item.get("answer", "").strip(), score, kind
        if kind == "fact":
            return item.get("fact", "").strip(), score, kind
        if kind == "project":
            return item.get("description", "").strip(), score, kind
        return None, score, kind

    def _profile_answer(self, comment, profile):
        if not profile:
            return None
        text = str(comment).lower()
        if any(x in text for x in ["who are you", "your name", "creator name"]):
            name = profile.get("name") or profile.get("username")
            if name:
                return f"I'm {name}."
        if any(x in text for x in ["what do you create", "your niche", "what is your content about"]):
            niche = profile.get("niche") or profile.get("bio")
            if niche:
                return str(niche).strip()
        if "language" in text and profile.get("language"):
            return f"The creator's preferred communication language is {profile['language']}."
        return None

    def _llm_reply(self, comment, context):
        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            return None
        model = os.getenv("FRAMECRAFT_LLM_MODEL", "openrouter/free").strip()
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are FrameCraft AI's creator comment assistant. "
                        "Answer audience comments using ONLY the supplied context when the question is about the creator, project, or video. "
                        "Do not invent creator facts, private information, project details, or video facts. "
                        "If the context is insufficient for a creator-specific claim, say that the information is not available. "
                        "For ordinary general-knowledge questions, answer briefly and accurately. "
                        "Keep the tone aligned with the creator profile. Never reveal private information."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps({"comment": comment, "context": context}, ensure_ascii=False),
                },
            ],
            "temperature": 0.2,
            "max_tokens": 250,
        }
        request = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-Title": "FrameCraft AI",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content")
                if content:
                    return str(content).strip()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, Exception):
            return None
        return None

    def generate_contextual_reply(self, comment, context, base_result):
        analysis = base_result.get("analysis", base_result) if isinstance(base_result, dict) else {}
        category = analysis.get("category", "unknown") if isinstance(analysis, dict) else "unknown"
        requires_permission = bool(analysis.get("requires_permission")) if isinstance(analysis, dict) else True
        reply = None
        source = "template"
        grounded = False

        # Safety/routing remains controlled by the existing FAFM permission layer.
        if not requires_permission and category in {"question", "neutral", "positive", "thanks", "greeting"}:
            reply, score, kind = self._knowledge_answer(context)
            if reply:
                source = f"knowledge:{kind}"
                grounded = True
            if not reply:
                reply = self._profile_answer(comment, context.get("creator_profile", {}))
                if reply:
                    source = "creator_profile"
                    grounded = True
            if not reply:
                reply, score = self._project_answer(comment, context)
                if reply:
                    source = "project_script"
                    grounded = True

            # Use an LLM only when explicitly configured, and only after local grounding.
            if not reply and category == "question":
                llm = self._llm_reply(comment, context)
                if llm:
                    reply = llm
                    source = "openrouter"
                    grounded = bool(context.get("knowledge") or context.get("project") or context.get("creator_profile"))

        if not reply and isinstance(base_result, dict):
            reply = base_result.get("reply") or base_result.get("generated_reply") or ""

        updates = {}
        if isinstance(base_result, dict):
            updates["contextual_reply"] = reply
            updates["reply_source"] = source
            updates["grounded"] = grounded
            if isinstance(base_result.get("analysis"), dict):
                updates["analysis"] = dict(base_result["analysis"])
                updates["analysis"]["contextual_context"] = {
                    "knowledge_hits": len(context.get("knowledge", [])),
                    "project_id": (context.get("project") or {}).get("id"),
                    "video_id": (context.get("video") or {}).get("id"),
                }
        return {
            "reply": reply,
            "reply_source": source,
            "grounded": grounded,
            "result_updates": updates,
            "context_summary": {
                "knowledge_hits": len(context.get("knowledge", [])),
                "project_name": (context.get("project") or {}).get("name"),
                "video_name": (context.get("video") or {}).get("name"),
                "video_transcript_available": bool(((context.get("video") or {}).get("analysis") or {}).get("transcript_available")),
            },
        }
