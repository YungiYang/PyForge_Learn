"""
Сервис Dev Панели (Админка создателя Chevels).
"""

import json
import time
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional
from .auth_service import AuthService, DEVELOPER_USERNAMES
from ..data.titles_catalog import save_custom_title, delete_custom_title, get_all_titles
from ..data.practice_tasks import save_custom_practice_task, delete_custom_practice_task, get_all_practice_tasks
from .ideas_service import IdeasService

class DevService:
    @classmethod
    def verify_creator(cls, token: Optional[str]) -> Dict[str, Any]:
        if not token:
            raise PermissionError("Доступ запрещен. Необходима авторизация")
        user = AuthService.get_user_by_token(token)
        if not user:
            raise PermissionError("Пользователь не найден")
        uname = user.get("username", "").strip().lower()
        if uname != "chevels":
            raise PermissionError("Доступ запрещен. Панель разработчика доступна только создателю Chevels")
        return user

    @classmethod
    def set_user_stars(cls, token: str, username: Optional[str], amount: int, mode: str = "set") -> Dict[str, Any]:
        cls.verify_creator(token)
        target_uname = (username or "chevels").strip().lower()
        users = AuthService._load_users()
        if target_uname not in users:
            raise ValueError(f"Пользователь «{target_uname}» не найден")
        
        if mode == "add":
            users[target_uname]["stars"] = max(0, users[target_uname].get("stars", 0) + amount)
            if amount > 0:
                users[target_uname]["total_earned_stars"] = users[target_uname].get("total_earned_stars", 0) + amount
        else:
            users[target_uname]["stars"] = max(0, amount)
            if amount > users[target_uname].get("total_earned_stars", 0):
                users[target_uname]["total_earned_stars"] = amount
        
        AuthService._save_users(users)
        sanitized = AuthService.sanitize_user(users[target_uname])
        return {
            "success": True,
            "user": sanitized,
            "user_stars": users[target_uname]["stars"],
            "stars": users[target_uname]["stars"],
            "message": f"Баланс звёзд пользователя {target_uname} успешно обновлен: {users[target_uname]['stars']} ⭐"
        }

    @classmethod
    def create_custom_title(cls, token: str, title_data: Dict[str, Any]) -> Dict[str, Any]:
        creator = cls.verify_creator(token)
        title_id = title_data.get("id") or f"title_{secrets.token_hex(4)}"
        name = title_data.get("name", "").strip()
        if not name:
            raise ValueError("Укажите название титула")

        new_title = {
            "id": title_id,
            "name": name,
            "cost_stars": int(title_data.get("cost_stars", 0)),
            "rarity": title_data.get("rarity", "Legendary"),
            "color": title_data.get("color", "text-amber-300 border-amber-400/50 bg-gradient-to-r from-amber-500/20 to-rose-500/20"),
            "description": title_data.get("description", "Эксклюзивный титул от создателя"),
            "icon": title_data.get("icon", "shield")
        }
        save_custom_title(new_title)

        if title_data.get("unlock_now", True):
            creator_uname = creator["username"].lower()
            users = AuthService._load_users()
            if creator_uname in users:
                unlocked = users[creator_uname].get("unlocked_titles", [])
                if title_id not in unlocked:
                    unlocked.append(title_id)
                    users[creator_uname]["unlocked_titles"] = unlocked
                if title_data.get("set_active", False):
                    users[creator_uname]["active_title_id"] = title_id
                AuthService._save_users(users)

        return {"success": True, "title": new_title, "message": f"Титул «{name}» успешно создан!"}

    @classmethod
    def delete_title(cls, token: str, title_id: str) -> Dict[str, Any]:
        cls.verify_creator(token)
        delete_custom_title(title_id)
        return {"success": True, "message": "Титул удален"}

    @classmethod
    def create_custom_task(cls, token: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        cls.verify_creator(token)
        task_id = task_data.get("id") or f"task_{secrets.token_hex(4)}"
        title = task_data.get("title", "").strip()
        if not title:
            raise ValueError("Укажите заголовок задачи")

        new_task = {
            "id": task_id,
            "title": title,
            "difficulty": task_data.get("difficulty", "Middle"),
            "category": task_data.get("category", "Алгоритмы & Практика"),
            "reward_stars": int(task_data.get("reward_stars", 30)),
            "description": task_data.get("description", ""),
            "starter_code": task_data.get("starter_code", "def solution():\n    pass\n"),
            "entry_point": task_data.get("entry_point", "solution"),
            "test_cases": task_data.get("test_cases", [])
        }
        save_custom_practice_task(new_task)
        return {
            "success": True,
            "task": new_task,
            "message": f"Задача «{title}» успешно добавлена в тренажер! 🎯"
        }

    @classmethod
    def respond_to_idea(cls, token: str, idea_id: str, status: str, dev_response: str) -> Dict[str, Any]:
        cls.verify_creator(token)
        result = IdeasService.update_idea_status(idea_id, status, dev_response)
        return {
            "success": True,
            "idea": result,
            "message": "Официальный ответ создателя опубликован! 🛡️"
        }

    @classmethod
    def list_users_admin(cls, token: str) -> Dict[str, Any]:
        cls.verify_creator(token)
        users_map = AuthService._load_users()
        users_list = [AuthService.sanitize_user(u) for u in users_map.values()]
        return {
            "success": True,
            "total_users": len(users_list),
            "users": users_list
        }

    @classmethod
    def set_user_role(cls, token: str, username: str, role: str) -> Dict[str, Any]:
        cls.verify_creator(token)
        valid_roles = ["creator", "admin", "moderator", "vip", "mentor", "user"]
        target_role = role.lower().strip()
        if target_role not in valid_roles:
            raise ValueError(f"Недопустимая роль «{role}». Доступные роли: {', '.join(valid_roles)}")

        target_uname = username.strip().lower()
        users = AuthService._load_users()
        if target_uname not in users:
            raise ValueError(f"Пользователь «{target_uname}» не найден")

        users[target_uname]["role"] = target_role
        if target_role in ["creator", "admin"]:
            users[target_uname]["is_developer"] = True
        else:
            if target_uname != "chevels":
                users[target_uname]["is_developer"] = False

        AuthService._save_users(users)
        sanitized = AuthService.sanitize_user(users[target_uname])
        return {
            "success": True,
            "user": sanitized,
            "message": f"Роль пользователя @{target_uname} успешно изменена на «{target_role.upper()}»! 🛡️"
        }
