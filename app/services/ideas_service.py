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

INITIAL_IDEAS = [
    {
        "id": "idea_1",
        "title": "Добавить рандомизатор задач по библиотекам (Kivy, FastAPI, Re, Pandas)",
        "description": "Было бы круто выбирать библиотеку и получать уникальные практические задачи с авто-тестами и наградами в звездах!",
        "category": "practice",
        "author_username": "AlexPy",
        "author_display_name": "Алексей Pythonist",
        "author_avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=AlexPy",
        "status": "completed",
        "status_label": "✅ Реализовано",
        "votes": 54,
        "voted_by": ["AlexPy", "ElenaCode", "DmitryPro", "OlgaAI"],
        "dev_response": "Уже добавлено в PyForge v1.1! Поддерживается более 12+ библиотек с тестами и генерацией.",
        "created_at": "2026-08-28T10:00:00Z"
    },
    {
        "id": "idea_2",
        "title": "Интеграция ИИ-наставника прямо в VS Code как расширение",
        "description": "Хочется, чтобы ошибки подсвечивались волнистыми линиями прямо в моем редакторе VS Code с подсказками от наставника.",
        "category": "ai_mentor",
        "author_username": "ElenaCode",
        "author_display_name": "Елена (Async Dev)",
        "author_avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=ElenaCode",
        "status": "completed",
        "status_label": "✅ Реализовано",
        "votes": 42,
        "voted_by": ["AlexPy", "ElenaCode"],
        "dev_response": "Расширение `vscode-extension` создано и доступно прямо в репозитории проекта с Live Bridge!",
        "created_at": "2026-08-29T15:30:00Z"
    },
    {
        "id": "idea_3",
        "title": "Добавить мультиплеер / Дуэли разработчиков (Code Battle 1v1)",
        "description": "Возможность соревноваться в реальном времени с другим игроком: кто быстрее и чище решит задачу на Python на время.",
        "category": "practice",
        "author_username": "DmitryPro",
        "author_display_name": "Дмитрий В.",
        "author_avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=DmitryPro",
        "status": "in_progress",
        "status_label": "🚀 В разработке",
        "votes": 89,
        "voted_by": ["AlexPy", "ElenaCode", "DmitryPro"],
        "dev_response": "Отличная идея! Проектируем WebSocket протокол для синхронизации тестов и таймеров дуэли.",
        "created_at": "2026-09-02T11:00:00Z"
    },
    {
        "id": "idea_4",
        "title": "Шаблон Telegram-бота на Aiogram 3 с WebApp и платными подписками (Stars)",
        "description": "Добавить в конструктор готовый проект Telegram Mini App с интеграцией платежей Telegram Stars и базой PostgreSQL.",
        "category": "templates",
        "author_username": "OlgaAI",
        "author_display_name": "Ольга Нейросети",
        "author_avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=OlgaAI",
        "status": "under_review",
        "status_label": "💡 На рассмотрении",
        "votes": 37,
        "voted_by": ["OlgaAI"],
        "dev_response": "Взяли на анализ, готовим архитектурный шаблон.",
        "created_at": "2026-09-04T16:20:00Z"
    }
]

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
