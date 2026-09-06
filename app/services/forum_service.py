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
        from .db_storage import DBStorage
        data = DBStorage.load_json("forum_data.json", default=None)
        if data is None:
            data = list(INITIAL_TOPICS)
            cls._save_topics(data)
        return data if isinstance(data, list) else []

    @classmethod
    def _save_topics(cls, topics: List[Dict[str, Any]]):
        from .db_storage import DBStorage
        DBStorage.save_json("forum_data.json", topics)

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

        users_map = AuthService._load_users()
        from ..data.titles_catalog import get_all_titles
        all_titles = get_all_titles()
        title_map = {t["id"]: t for t in all_titles}

        results = []
        for t in filtered:
            uname = t["author_username"]
            u_data = users_map.get(uname.lower(), {})
            d_name = u_data.get("display_name") or t.get("author_display_name") or uname
            avatar = u_data.get("avatar") or t.get("author_avatar") or f"https://api.dicebear.com/7.x/bottts/svg?seed={uname}"
            is_creator = AuthService.is_developer(uname) or u_data.get("role") == "creator" or uname.lower() == "chevels"
            user_role = "creator" if is_creator else u_data.get("role", "user")
            is_dev = is_creator or user_role in ["creator", "admin"] or u_data.get("is_developer", False)

            t_id = u_data.get("active_title_id")
            title_name = title_map.get(t_id, {}).get("name") if t_id else t.get("author_title", "🐍 Pythonist")

            results.append({
                "id": t["id"],
                "title": t["title"],
                "category": t["category"],
                "author_username": uname,
                "author_display_name": d_name,
                "author_avatar": avatar,
                "author_role": user_role,
                "author_is_dev": is_dev,
                "author_title": title_name,
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
        users_map = AuthService._load_users()
        from ..data.titles_catalog import get_all_titles
        all_titles = get_all_titles()
        title_map = {t["id"]: t for t in all_titles}

        for t in topics:
            if t["id"] == topic_id:
                t["views"] = t.get("views", 0) + 1

                uname = t["author_username"]
                u_data = users_map.get(uname.lower(), {})
                t["author_display_name"] = u_data.get("display_name") or t.get("author_display_name") or uname
                t["author_avatar"] = u_data.get("avatar") or t.get("author_avatar") or f"https://api.dicebear.com/7.x/bottts/svg?seed={uname}"
                is_creator = AuthService.is_developer(uname) or u_data.get("role") == "creator" or uname.lower() == "chevels"
                t["author_role"] = "creator" if is_creator else u_data.get("role", "user")
                t["author_is_dev"] = is_creator or t["author_role"] in ["creator", "admin"] or u_data.get("is_developer", False)
                t_id = u_data.get("active_title_id")
                if t_id and t_id in title_map:
                    t["author_title"] = title_map[t_id]["name"]

                for c in t.get("comments", []):
                    c_uname = c["author_username"]
                    c_data = users_map.get(c_uname.lower(), {})
                    c["author_display_name"] = c_data.get("display_name") or c.get("author_display_name") or c_uname
                    c["author_avatar"] = c_data.get("avatar") or c.get("author_avatar") or f"https://api.dicebear.com/7.x/bottts/svg?seed={c_uname}"
                    c_creator = AuthService.is_developer(c_uname) or c_data.get("role") == "creator" or c_uname.lower() == "chevels"
                    c["author_role"] = "creator" if c_creator else c_data.get("role", "user")
                    c["author_is_dev"] = c_creator or c["author_role"] in ["creator", "admin"] or c_data.get("is_developer", False)
                    c_t_id = c_data.get("active_title_id")
                    if c_t_id and c_t_id in title_map:
                        c["author_title"] = title_map[c_t_id]["name"]

                cls._save_topics(topics)
                return t
        return None

    @classmethod
    def create_topic(cls, title: str, category: str, content: str, author_username: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        topics = cls._load_topics()
        users_map = AuthService._load_users()
        user_info = users_map.get(author_username.lower()) or AuthService.get_user_by_token(author_username) or {}
        display_name = user_info.get("display_name") or author_username
        avatar = user_info.get("avatar") or f"https://api.dicebear.com/7.x/bottts/svg?seed={author_username}"
        is_creator = AuthService.is_developer(author_username) or user_info.get("role") == "creator" or author_username.lower() == "chevels"
        author_role = "creator" if is_creator else user_info.get("role", "user")
        is_dev = is_creator or author_role in ["creator", "admin"] or user_info.get("is_developer", False)

        topic_id = f"topic_{int(time.time())}_{secrets.token_hex(3)}"
        new_topic = {
            "id": topic_id,
            "title": title.strip(),
            "category": category,
            "author_username": author_username,
            "author_display_name": display_name,
            "author_avatar": avatar,
            "author_role": author_role,
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
        users_map = AuthService._load_users()
        for t in topics:
            if t["id"] == topic_id:
                user_info = users_map.get(author_username.lower()) or AuthService.get_user_by_token(author_username) or {}
                display_name = user_info.get("display_name") or author_username
                avatar = user_info.get("avatar") or f"https://api.dicebear.com/7.x/bottts/svg?seed={author_username}"
                is_creator = AuthService.is_developer(author_username) or user_info.get("role") == "creator" or author_username.lower() == "chevels"
                author_role = "creator" if is_creator else user_info.get("role", "user")
                is_dev = is_creator or author_role in ["creator", "admin"] or user_info.get("is_developer", False)

                comment_id = f"comm_{int(time.time())}_{secrets.token_hex(3)}"
                comment = {
                    "id": comment_id,
                    "author_username": author_username,
                    "author_display_name": display_name,
                    "author_avatar": avatar,
                    "author_role": author_role,
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
