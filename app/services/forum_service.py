"""
Сервис Форума сообщества PyForge (Community Forum).
"""

import json
import time
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional
from .auth_service import AuthService

FORUM_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "forum_data.json"

FORUM_CATEGORIES = [
    {"id": "all", "name": "Все темы", "icon": "layers"},
    {"id": "general", "name": "Вопросы новичков", "icon": "help-circle"},
    {"id": "practice", "name": "Разбор задач тренажера", "icon": "award"},
    {"id": "architecture", "name": "Архитектура & ООП", "icon": "boxes"},
    {"id": "web", "name": "FastAPI & Web", "icon": "globe"},
    {"id": "gui", "name": "GUI & Десктоп", "icon": "layout"},
    {"id": "community", "name": "Общение & Проекты", "icon": "message-square"}
]

# Начальные темы форума (пустой список для чистой базы)
INITIAL_TOPICS = []

class ForumService:
    @classmethod
    def _load_topics(cls) -> List[Dict[str, Any]]:
        if not FORUM_DATA_FILE.exists():
            cls._save_topics(INITIAL_TOPICS)
            return list(INITIAL_TOPICS)
        try:
            with open(FORUM_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            cls._save_topics(INITIAL_TOPICS)
            return list(INITIAL_TOPICS)

    @classmethod
    def _save_topics(cls, topics: List[Dict[str, Any]]):
        FORUM_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(FORUM_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)

    @classmethod
    def get_categories(cls) -> List[Dict[str, Any]]:
        return FORUM_CATEGORIES

    @classmethod
    def list_topics(cls, category: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        topics = cls._load_topics()
        filtered = topics

        if category and category != "all":
            filtered = [t for t in filtered if t.get("category") == category]

        if search:
            q = search.lower().strip()
            filtered = [
                t for t in filtered
                if q in t.get("title", "").lower() or q in t.get("content", "").lower() or any(q in tag.lower() for tag in t.get("tags", []))
            ]

        # Сортируем: сначала самые свежие и популярные
        filtered.sort(key=lambda t: t.get("created_at", ""), reverse=True)

        results = []
        for t in filtered:
            results.append({
                "id": t["id"],
                "title": t["title"],
                "category": t["category"],
                "author_username": t["author_username"],
                "author_display_name": t.get("author_display_name") or t["author_username"],
                "author_avatar": t.get("author_avatar"),
                "author_title": t.get("author_title", "🐍 Pythonist"),
                "preview": t["content"][:160] + "..." if len(t["content"]) > 160 else t["content"],
                "tags": t.get("tags", []),
                "views": t.get("views", 0),
                "upvotes": t.get("upvotes", 0),
                "comments_count": len(t.get("comments", [])),
                "created_at": t.get("created_at")
            })
        return results

    @classmethod
    def get_topic(cls, topic_id: str) -> Optional[Dict[str, Any]]:
        topics = cls._load_topics()
        for t in topics:
            if t["id"] == topic_id:
                t["views"] = t.get("views", 0) + 1
                cls._save_topics(topics)
                return t
        return None

    @classmethod
    def create_topic(cls, title: str, category: str, content: str, author_username: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        topics = cls._load_topics()
        user_info = AuthService.get_user_by_token(author_username) or {}
        display_name = user_info.get("display_name") or author_username
        avatar = user_info.get("avatar") or f"https://api.dicebear.com/7.x/bottts/svg?seed={author_username}"
        is_dev = AuthService.is_developer(author_username)

        topic_id = f"topic_{int(time.time())}_{secrets.token_hex(3)}"
        new_topic = {
            "id": topic_id,
            "title": title.strip(),
            "category": category,
            "author_username": author_username,
            "author_display_name": display_name,
            "author_avatar": avatar,
            "author_title": "👑 Создатель & Lead Dev" if is_dev else "🐍 Pythonist",
            "author_is_dev": is_dev,
            "content": content.strip(),
            "tags": tags or [category],
            "views": 1,
            "upvotes": 1,
            "upvoted_by": [author_username],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "comments": []
        }

        topics.insert(0, new_topic)
        cls._save_topics(topics)
        return new_topic

    @classmethod
    def add_comment(cls, topic_id: str, content: str, author_username: str) -> Dict[str, Any]:
        topics = cls._load_topics()
        for t in topics:
            if t["id"] == topic_id:
                user_info = AuthService.get_user_by_token(author_username) or {}
                display_name = user_info.get("display_name") or author_username
                avatar = user_info.get("avatar") or f"https://api.dicebear.com/7.x/bottts/svg?seed={author_username}"
                is_dev = AuthService.is_developer(author_username)

                comment_id = f"comm_{int(time.time())}_{secrets.token_hex(3)}"
                comment = {
                    "id": comment_id,
                    "author_username": author_username,
                    "author_display_name": display_name,
                    "author_avatar": avatar,
                    "author_title": "👑 Создатель & Lead Dev" if is_dev else "🐍 Pythonist",
                    "author_is_dev": is_dev,
                    "content": content.strip(),
                    "upvotes": 0,
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                if "comments" not in t:
                    t["comments"] = []
                t["comments"].append(comment)
                cls._save_topics(topics)
                return comment
        raise ValueError("Тема форума не найдена")

    @classmethod
    def upvote_topic(cls, topic_id: str, username: str) -> Dict[str, Any]:
        topics = cls._load_topics()
        for t in topics:
            if t["id"] == topic_id:
                upvoted_by = t.get("upvoted_by", [])
                if username in upvoted_by:
                    upvoted_by.remove(username)
                    t["upvotes"] = max(0, t.get("upvotes", 1) - 1)
                    voted = False
                else:
                    upvoted_by.append(username)
                    t["upvotes"] = t.get("upvotes", 0) + 1
                    voted = True
                t["upvoted_by"] = upvoted_by
                cls._save_topics(topics)
                return {"success": True, "upvotes": t["upvotes"], "voted": voted}
        raise ValueError("Тема не найдена")
