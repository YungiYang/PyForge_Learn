"""
Сервис сбора и голосования за идеи и предложения для создателей PyForge (Creator Ideas & Feature Requests Hub).
"""

import json
import time
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional
from .auth_service import AuthService

IDEAS_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "ideas_data.json"

# Начальные идеи сообщества (пустой список для чистой базы)
INITIAL_IDEAS = []

class IdeasService:
    @classmethod
    def _load_ideas(cls) -> List[Dict[str, Any]]:
        if not IDEAS_DATA_FILE.exists():
            cls._save_ideas(INITIAL_IDEAS)
            return list(INITIAL_IDEAS)
        try:
            with open(IDEAS_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            cls._save_ideas(INITIAL_IDEAS)
            return list(INITIAL_IDEAS)

    @classmethod
    def _save_ideas(cls, ideas: List[Dict[str, Any]]):
        IDEAS_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(IDEAS_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(ideas, f, ensure_ascii=False, indent=2)

    @classmethod
    def list_ideas(cls, category: Optional[str] = None, status: Optional[str] = None, sort_by: str = "popular") -> List[Dict[str, Any]]:
        ideas = cls._load_ideas()
        filtered = ideas

        if category and category != "all":
            filtered = [i for i in filtered if i.get("category") == category]

        if status and status != "all":
            filtered = [i for i in filtered if i.get("status") == status]

        if sort_by == "popular":
            filtered.sort(key=lambda x: x.get("votes", 0), reverse=True)
        else: # "new"
            filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return filtered

    @classmethod
    def submit_idea(cls, title: str, description: str, category: str, author_username: str) -> Dict[str, Any]:
        ideas = cls._load_ideas()
        user_info = AuthService.get_user_by_token(author_username) or {}
        display_name = user_info.get("display_name") or author_username
        avatar = user_info.get("avatar") or f"https://api.dicebear.com/7.x/bottts/svg?seed={author_username}"

        idea_id = f"idea_{int(time.time())}_{secrets.token_hex(3)}"
        new_idea = {
            "id": idea_id,
            "title": title.strip(),
            "description": description.strip(),
            "category": category,
            "author_username": author_username,
            "author_display_name": display_name,
            "author_avatar": avatar,
            "status": "under_review",
            "status_label": "💡 На рассмотрении",
            "votes": 1,
            "voted_by": [author_username],
            "dev_response": "Спасибо за идею! Создатели PyForge уже изучают ваше предложение.",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        ideas.insert(0, new_idea)
        cls._save_ideas(ideas)
        return new_idea

    @classmethod
    def vote_idea(cls, idea_id: str, username: str) -> Dict[str, Any]:
        ideas = cls._load_ideas()
        for i in ideas:
            if i["id"] == idea_id:
                voted_by = i.get("voted_by", [])
                if username in voted_by:
                    voted_by.remove(username)
                    i["votes"] = max(0, i.get("votes", 1) - 1)
                    has_voted = False
                else:
                    voted_by.append(username)
                    i["votes"] = i.get("votes", 0) + 1
                    has_voted = True
                i["voted_by"] = voted_by
                cls._save_ideas(ideas)
                return {"success": True, "votes": i["votes"], "has_voted": has_voted}
        raise ValueError("Идея не найдена")

    @classmethod
    def update_idea_status(cls, idea_id: str, status: str, dev_response: Optional[str] = None) -> Dict[str, Any]:
        ideas = cls._load_ideas()
        status_labels = {
            "under_review": "💡 На рассмотрении",
            "in_progress": "🚀 В разработке",
            "completed": "✅ Реализовано",
            "rejected": "❌ Отклонено"
        }
        for i in ideas:
            if i["id"] == idea_id:
                if status in status_labels:
                    i["status"] = status
                    i["status_label"] = status_labels[status]
                if dev_response is not None:
                    i["dev_response"] = dev_response.strip()
                cls._save_ideas(ideas)
                return i
        raise ValueError("Идея не найдена")

    @classmethod
    def delete_idea(cls, idea_id: str) -> bool:
        ideas = cls._load_ideas()
        filtered = [i for i in ideas if i["id"] != idea_id]
        if len(filtered) != len(ideas):
            cls._save_ideas(filtered)
            return True
        return False

