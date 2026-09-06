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

        if title_data.get("grant_to_all", False):
            users = AuthService._load_users()
            for u in users.values():
                unlocked = u.get("unlocked_titles", [])
                if title_id not in unlocked:
                    unlocked.append(title_id)
                    u["unlocked_titles"] = unlocked
            AuthService._save_users(users)
        elif title_data.get("target_username"):
            target_u = title_data["target_username"].strip().lower()
            users = AuthService._load_users()
            if target_u in users:
                unlocked = users[target_u].get("unlocked_titles", [])
                if title_id not in unlocked:
                    unlocked.append(title_id)
                    users[target_u]["unlocked_titles"] = unlocked
                if title_data.get("set_active", False):
                    users[target_u]["active_title_id"] = title_id
                AuthService._save_users(users)
        elif title_data.get("unlock_now", True):
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
    def grant_title_to_user(cls, token: str, username: Optional[str], title_id: str, set_active: bool = False, grant_to_all: bool = False) -> Dict[str, Any]:
        cls.verify_creator(token)
        all_titles = get_all_titles()
        matched_title = next((t for t in all_titles if t["id"] == title_id), None)
        if not matched_title:
            raise ValueError(f"Титул «{title_id}» не найден в каталоге")

        title_name = matched_title.get("name", title_id)
        users = AuthService._load_users()

        if grant_to_all:
            for u in users.values():
                unlocked = u.get("unlocked_titles", [])
                if title_id not in unlocked:
                    unlocked.append(title_id)
                    u["unlocked_titles"] = unlocked
                if set_active:
                    u["active_title_id"] = title_id
            AuthService._save_users(users)
            return {
                "success": True,
                "message": f"Титул «{title_name}» успешно выдан ВСЕМ ({len(users)}) пользователям платформы! 🎉"
            }

        if not username:
            raise ValueError("Укажите логин пользователя для выдачи титула")

        target_uname = username.strip().lower()
        if target_uname not in users:
            raise ValueError(f"Пользователь «{target_uname}» не найден")

        unlocked = users[target_uname].get("unlocked_titles", [])
        if title_id not in unlocked:
            unlocked.append(title_id)
            users[target_uname]["unlocked_titles"] = unlocked
        if set_active:
            users[target_uname]["active_title_id"] = title_id

        AuthService._save_users(users)
        return {
            "success": True,
            "user": AuthService.sanitize_user(users[target_uname]),
            "message": f"Титул «{title_name}» успешно выдан пользователю @{target_uname}! 👑"
        }

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
    def _get_custom_roles_file(cls) -> Path:
        return Path(__file__).resolve().parent.parent / "data" / "custom_roles.json"

    @classmethod
    def get_all_roles(cls) -> List[Dict[str, Any]]:
        builtin_roles = [
            {"id": "creator", "name": "Создатель", "icon": "crown", "color_class": "from-amber-500/25 via-orange-500/25 to-rose-500/25 border-amber-500/60 text-amber-300", "is_builtin": True},
            {"id": "admin", "name": "Администратор", "icon": "shield-alert", "color_class": "bg-red-500/20 border-red-500/50 text-red-300", "is_builtin": True},
            {"id": "moderator", "name": "Модератор", "icon": "shield-check", "color_class": "bg-emerald-500/20 border-emerald-500/50 text-emerald-300", "is_builtin": True},
            {"id": "vip", "name": "VIP / Pro", "icon": "sparkles", "color_class": "bg-purple-500/20 border-purple-500/50 text-purple-300", "is_builtin": True},
            {"id": "mentor", "name": "Эксперт & Ментор", "icon": "brain", "color_class": "bg-cyan-500/20 border-cyan-500/50 text-cyan-300", "is_builtin": True},
            {"id": "user", "name": "Пользователь", "icon": "user", "color_class": "text-slate-400 border-slate-700 bg-slate-800/40", "is_builtin": True}
        ]
        from .db_storage import DBStorage
        try:
            custom_list = DBStorage.load_json("custom_roles.json", default=[])
            if isinstance(custom_list, list):
                builtin_ids = {r["id"] for r in builtin_roles}
                for cr in custom_list:
                    if cr.get("id") and cr["id"] not in builtin_ids:
                        cr["is_builtin"] = False
                        builtin_roles.append(cr)
        except Exception:
            pass
        return builtin_roles

    @classmethod
    def create_custom_role(cls, token: str, role_data: Dict[str, Any]) -> Dict[str, Any]:
        cls.verify_creator(token)
        raw_id = (role_data.get("id") or "").strip().lower()
        if not raw_id:
            raw_id = f"role_{secrets.token_hex(3)}"
        # Sanitize id
        clean_id = "".join(c for c in raw_id if c.isalnum() or c in "_-")
        name = (role_data.get("name") or clean_id).strip()
        if not name:
            raise ValueError("Укажите название роли")

        new_role = {
            "id": clean_id,
            "name": name,
            "icon": (role_data.get("icon") or "award").strip(),
            "color_class": (role_data.get("color_class") or "bg-sky-500/20 border-sky-500/50 text-sky-300").strip(),
            "description": (role_data.get("description") or "").strip(),
            "is_builtin": False
        }

        from .db_storage import DBStorage
        custom_list = DBStorage.load_json("custom_roles.json", default=[])
        if not isinstance(custom_list, list):
            custom_list = []

        # Replace or append
        custom_list = [r for r in custom_list if r.get("id") != clean_id]
        custom_list.append(new_role)

        DBStorage.save_json("custom_roles.json", custom_list)

        return {
            "success": True,
            "role": new_role,
            "roles": cls.get_all_roles(),
            "message": f"Роль «{name}» успешно создана и доступна для выдачи! 🛡️"
        }

    @classmethod
    def delete_custom_role(cls, token: str, role_id: str) -> Dict[str, Any]:
        cls.verify_creator(token)
        builtins = {"creator", "admin", "moderator", "vip", "mentor", "user"}
        if role_id.lower() in builtins:
            raise ValueError("Нельзя удалить стандартную системную роль")

        from .db_storage import DBStorage
        try:
            custom_list = DBStorage.load_json("custom_roles.json", default=[])
            if isinstance(custom_list, list):
                custom_list = [r for r in custom_list if r.get("id") != role_id]
                DBStorage.save_json("custom_roles.json", custom_list)
        except Exception:
            pass

        # Reset users having this deleted role to 'user'
        users = AuthService._load_users()
        modified = False
        for u in users.values():
            if u.get("role") == role_id:
                u["role"] = "user"
                modified = True
        if modified:
            AuthService._save_users(users)

        return {
            "success": True,
            "roles": cls.get_all_roles(),
            "message": f"Роль «{role_id}» успешно удалена"
        }

    @classmethod
    def set_user_role(cls, token: str, username: str, role: str) -> Dict[str, Any]:
        cls.verify_creator(token)
        target_role = role.lower().strip()
        all_role_ids = {r["id"] for r in cls.get_all_roles()}
        if target_role not in all_role_ids:
            raise ValueError(f"Недопустимая роль «{role}». Доступные роли: {', '.join(all_role_ids)}")

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

    @classmethod
    def export_backup(cls, token: str) -> Dict[str, Any]:
        cls.verify_creator(token)
        data_dir = Path(__file__).resolve().parent.parent / "data"
        backup: Dict[str, Any] = {
            "version": "1.0",
            "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "files": {}
        }
        json_filenames = [
            "users.json", "sessions.json", "custom_roles.json",
            "custom_titles.json", "forum_data.json", "ideas_data.json",
            "custom_tasks.json"
        ]
        for name in json_filenames:
            file_path = data_dir / name
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        backup["files"][name] = json.load(f)
                except Exception:
                    pass
        return backup

    @classmethod
    def import_backup(cls, token: str, backup_data: Dict[str, Any]) -> Dict[str, Any]:
        cls.verify_creator(token)
        data_dir = Path(__file__).resolve().parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        files = backup_data.get("files", {})
        if not files:
            raise ValueError("Резервная копия не содержит данных файлов")

        restored_files = []
        for name, content in files.items():
            if name.endswith(".json") and "/" not in name and "\\" not in name:
                file_path = data_dir / name
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(content, f, ensure_ascii=False, indent=2)
                restored_files.append(name)

        return {
            "success": True,
            "restored_files": restored_files,
            "message": f"Резервная копия успешно восстановлена ({len(restored_files)} файлов: {', '.join(restored_files)})! 🎉"
        }

