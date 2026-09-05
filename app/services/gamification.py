"""
Сервис геймификации: профиль пользователя, баланс звезд, достижения и звания.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..data.titles_catalog import TITLES_CATALOG, get_all_titles

PROFILE_FILE = Path(__file__).resolve().parent.parent / "data" / "user_profile.json"

DEFAULT_PROFILE = {
    "username": "Python Developer",
    "stars": 0,
    "total_earned_stars": 0,
    "active_title_id": "title_novice",
    "unlocked_titles": ["title_novice"],
    "solved_tasks": [],
    "streak_days": 1
}

class GamificationService:
    @classmethod
    def _resolve_user(cls, user_key_or_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not user_key_or_token:
            return None
        from .auth_service import AuthService
        # First try as token
        user = AuthService.get_user_by_token(user_key_or_token)
        if user:
            return user
        # Then try as direct username
        users = AuthService._load_users()
        return users.get(user_key_or_token.lower())

    @classmethod
    def _load_profile(cls, user_key_or_token: Optional[str] = None) -> Dict[str, Any]:
        user = cls._resolve_user(user_key_or_token)
        if user:
            return user

        if not PROFILE_FILE.exists():
            cls._save_profile(DEFAULT_PROFILE)
            return dict(DEFAULT_PROFILE)
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in DEFAULT_PROFILE.items():
                if k not in data:
                    data[k] = v
            return data
        except Exception:
            return dict(DEFAULT_PROFILE)

    @classmethod
    def _save_profile(cls, profile: Dict[str, Any], user_key_or_token: Optional[str] = None):
        user = cls._resolve_user(user_key_or_token)
        if user:
            from .auth_service import AuthService
            AuthService.update_user_profile(user["username"], lambda u: {**u, **profile})
            return

        PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

    @classmethod
    def get_full_profile(cls, user_key_or_token: Optional[str] = None) -> Dict[str, Any]:
        profile = cls._load_profile(user_key_or_token)
        all_titles = get_all_titles()
        active_title_id = profile.get("active_title_id", "title_novice")
        active_title = next((t for t in all_titles if t["id"] == active_title_id), all_titles[0])
        unlocked = profile.get("unlocked_titles", ["title_novice"])
        stars = profile.get("stars", 0)

        # Build titles shop with ownership status
        shop_titles = []
        for t in all_titles:
            is_unlocked = t["id"] in unlocked
            is_active = t["id"] == active_title_id
            can_afford = stars >= t["cost_stars"]
            shop_titles.append({
                **t,
                "is_unlocked": is_unlocked,
                "is_active": is_active,
                "can_afford": can_afford
            })

        return {
            "id": profile.get("id"),
            "username": profile.get("username", "Python Developer"),
            "display_name": profile.get("display_name") or profile.get("username", "Python Developer"),
            "avatar": profile.get("avatar"),
            "stars": stars,
            "total_earned_stars": profile.get("total_earned_stars", 0),
            "active_title": active_title,
            "solved_tasks_count": len(profile.get("solved_tasks", [])),
            "solved_task_ids": profile.get("solved_tasks", []),
            "shop_titles": shop_titles
        }

    @classmethod
    def award_task_completion(cls, task_id: str, stars: int, user_key_or_token: Optional[str] = None) -> Dict[str, Any]:
        profile = cls._load_profile(user_key_or_token)
        solved_tasks = profile.get("solved_tasks", [])
        is_first_solve = task_id not in solved_tasks

        awarded_stars = 0
        if is_first_solve:
            if not isinstance(solved_tasks, list):
                solved_tasks = []
            solved_tasks.append(task_id)
            profile["solved_tasks"] = solved_tasks
            profile["stars"] = profile.get("stars", 0) + stars
            profile["total_earned_stars"] = profile.get("total_earned_stars", 0) + stars
            awarded_stars = stars
            cls._save_profile(profile, user_key_or_token)

        return {
            "is_first_solve": is_first_solve,
            "awarded_stars": awarded_stars,
            "current_stars": profile.get("stars", 0),
            "total_solved": len(profile.get("solved_tasks", []))
        }

    @classmethod
    def buy_title(cls, title_id: str, user_key_or_token: Optional[str] = None) -> Dict[str, Any]:
        profile = cls._load_profile(user_key_or_token)
        all_titles = get_all_titles()
        title = next((t for t in all_titles if t["id"] == title_id), None)
        if not title:
            raise ValueError("Титул не найден")

        unlocked = profile.get("unlocked_titles", ["title_novice"])
        if title_id in unlocked:
            # Уже куплен, просто экипируем
            profile["active_title_id"] = title_id
            cls._save_profile(profile, user_key_or_token)
            return {"status": "success", "message": f"Титул '{title['name']}' экипирован!", "profile": cls.get_full_profile(user_key_or_token)}

        current_stars = profile.get("stars", 0)
        if current_stars < title["cost_stars"]:
            raise ValueError(f"Недостаточно звезд! Требуется {title['cost_stars']} ⭐, у вас {current_stars} ⭐")

        # Покупка
        profile["stars"] = current_stars - title["cost_stars"]
        unlocked.append(title_id)
        profile["unlocked_titles"] = unlocked
        profile["active_title_id"] = title_id
        cls._save_profile(profile, user_key_or_token)

        return {
            "status": "success",
            "message": f"Поздравляем! Вы открыли звание '{title['name']}'! 🎉",
            "profile": cls.get_full_profile(user_key_or_token)
        }

    @classmethod
    def set_active_title(cls, title_id: str, user_key_or_token: Optional[str] = None) -> Dict[str, Any]:
        profile = cls._load_profile(user_key_or_token)
        unlocked = profile.get("unlocked_titles", ["title_novice"])
        if title_id not in unlocked:
            raise ValueError("Вы еще не разблокировали этот титул!")

        profile["active_title_id"] = title_id
        cls._save_profile(profile, user_key_or_token)
        return {"status": "success", "profile": cls.get_full_profile(user_key_or_token)}
