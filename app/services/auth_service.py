"""
Сервис аутентификации и управления аккаунтами пользователей PyForge.
"""

import json
import time
import hashlib
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional

USERS_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "users.json"
SESSIONS_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sessions.json"

# Начальные пользователи (пустой список для чистой базы)
INITIAL_DEMO_USERS = []

class AuthService:
    @classmethod
    def _load_users(cls) -> Dict[str, Dict[str, Any]]:
        """Загрузка пользователей из файла"""
        if not USERS_DATA_FILE.exists():
            users_map = {u["username"].lower(): u for u in INITIAL_DEMO_USERS}
            cls._save_users(users_map)
            return users_map
        try:
            with open(USERS_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            users_map = {u["username"].lower(): u for u in INITIAL_DEMO_USERS}
            cls._save_users(users_map)
            return users_map

    @classmethod
    def _save_users(cls, users: Dict[str, Dict[str, Any]]):
        USERS_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(USERS_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

    @classmethod
    def _load_sessions(cls) -> Dict[str, str]:
        """Загрузка активных токенов сессий: token -> username"""
        if not SESSIONS_DATA_FILE.exists():
            return {}
        try:
            with open(SESSIONS_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def _save_sessions(cls, sessions: Dict[str, str]):
        SESSIONS_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSIONS_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)

    @classmethod
    def register(cls, username: str, password: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        username_clean = username.strip()
        if len(username_clean) < 3:
            raise ValueError("Имя пользователя должно содержать минимум 3 символа")
        if len(password) < 4:
            raise ValueError("Пароль должен содержать минимум 4 символа")

        users = cls._load_users()
        key = username_clean.lower()
        if key in users:
            raise ValueError(f"Пользователь с именем «{username_clean}» уже зарегистрирован")

        pass_hash = hashlib.sha256(password.encode()).hexdigest()
        avatar = f"https://api.dicebear.com/7.x/bottts/svg?seed={username_clean}"
        user_id = f"user_{int(time.time())}_{secrets.token_hex(4)}"

        new_user = {
            "id": user_id,
            "username": username_clean,
            "display_name": (display_name or username_clean).strip(),
            "password_hash": pass_hash,
            "avatar": avatar,
            "stars": 0,
            "total_earned_stars": 0,
            "active_title_id": "title_novice",
            "unlocked_titles": ["title_novice"],
            "solved_tasks": [],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        users[key] = new_user
        cls._save_users(users)

        # Создаем токен сессии
        token = secrets.token_hex(24)
        sessions = cls._load_sessions()
        sessions[token] = key
        cls._save_sessions(sessions)

        return {
            "success": True,
            "token": token,
            "user": cls.sanitize_user(new_user)
        }

    @classmethod
    def login(cls, username: str, password: str) -> Dict[str, Any]:
        username_clean = username.strip()
        users = cls._load_users()
        key = username_clean.lower()

        if key not in users:
            raise ValueError("Неверное имя пользователя или пароль")

        user = users[key]
        pass_hash = hashlib.sha256(password.encode()).hexdigest()
        if user["password_hash"] != pass_hash:
            raise ValueError("Неверное имя пользователя или пароль")

        token = secrets.token_hex(24)
        sessions = cls._load_sessions()
        sessions[token] = key
        cls._save_sessions(sessions)

        return {
            "success": True,
            "token": token,
            "user": cls.sanitize_user(user)
        }

    @classmethod
    def get_user_by_token(cls, token: Optional[str]) -> Optional[Dict[str, Any]]:
        if not token:
            return None
        sessions = cls._load_sessions()
        username_key = sessions.get(token)
        if not username_key:
            return None
        users = cls._load_users()
        user = users.get(username_key)
        return user

    @classmethod
    def logout(cls, token: str) -> bool:
        sessions = cls._load_sessions()
        if token in sessions:
            del sessions[token]
            cls._save_sessions(sessions)
            return True
        return False

    @classmethod
    def sanitize_user(cls, user: Dict[str, Any]) -> Dict[str, Any]:
        """Возвращает безопасный профиль пользователя без хэша пароля"""
        return {
            "id": user.get("id"),
            "username": user.get("username"),
            "display_name": user.get("display_name"),
            "avatar": user.get("avatar"),
            "stars": user.get("stars", 0),
            "total_earned_stars": user.get("total_earned_stars", 0),
            "active_title_id": user.get("active_title_id", "title_novice"),
            "unlocked_titles": user.get("unlocked_titles", ["title_novice"]),
            "solved_tasks": user.get("solved_tasks", []),
            "created_at": user.get("created_at")
        }

    @classmethod
    def update_user_profile(cls, username_key: str, updater_func) -> Dict[str, Any]:
        """Атомарное обновление данных пользователя"""
        users = cls._load_users()
        key = username_key.lower()
        if key in users:
            users[key] = updater_func(users[key])
            cls._save_users(users)
            return users[key]
        return {}
