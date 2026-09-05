"""
Сервис геймификации: профиль пользователя, баланс звезд, достижения и звания.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from ..data.titles_catalog import TITLES_CATALOG

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
    def _load_profile(cls) -> Dict[str, Any]:
        if not PROFILE_FILE.exists():
            cls._save_profile(DEFAULT_PROFILE)
            return dict(DEFAULT_PROFILE)
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Ensure all keys exist
            for k, v in DEFAULT_PROFILE.items():
                if k not in data:
                    data[k] = v
            return data
        except Exception:
            return dict(DEFAULT_PROFILE)

    @classmethod
    def _save_profile(cls, profile: Dict[str, Any]):
        PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

    @classmethod
    def get_full_profile(cls) -> Dict[str, Any]:
        profile = cls._load_profile()
        active_title = next((t for t in TITLES_CATALOG if t["id"] == profile["active_title_id"]), TITLES_CATALOG[0])
        
        # Build titles shop with ownership status
        shop_titles = []
        for t in TITLES_CATALOG:
            is_unlocked = t["id"] in profile["unlocked_titles"]
            is_active = t["id"] == profile["active_title_id"]
            can_afford = profile["stars"] >= t["cost_stars"]
            shop_titles.append({
                **t,
                "is_unlocked": is_unlocked,
                "is_active": is_active,
                "can_afford": can_afford
            })

        return {
            "username": profile.get("username", "Python Developer"),
            "stars": profile.get("stars", 0),
            "total_earned_stars": profile.get("total_earned_stars", 0),
            "active_title": active_title,
            "solved_tasks_count": len(profile.get("solved_tasks", [])),
            "solved_task_ids": profile.get("solved_tasks", []),
            "shop_titles": shop_titles
        }

    @classmethod
    def award_task_completion(cls, task_id: str, stars: int) -> Dict[str, Any]:
        profile = cls._load_profile()
        is_first_solve = task_id not in profile.get("solved_tasks", [])
        
        awarded_stars = 0
        if is_first_solve:
            profile["solved_tasks"].append(task_id)
            profile["stars"] += stars
            profile["total_earned_stars"] += stars
            awarded_stars = stars
            cls._save_profile(profile)

        return {
            "is_first_solve": is_first_solve,
            "awarded_stars": awarded_stars,
            "current_stars": profile["stars"],
            "total_solved": len(profile["solved_tasks"])
        }

    @classmethod
    def buy_title(cls, title_id: str) -> Dict[str, Any]:
        profile = cls._load_profile()
        title = next((t for t in TITLES_CATALOG if t["id"] == title_id), None)
        if not title:
            raise ValueError("Титул не найден")

        if title_id in profile["unlocked_titles"]:
            # Уже куплен, просто экипируем
            profile["active_title_id"] = title_id
            cls._save_profile(profile)
            return {"status": "success", "message": f"Титул '{title['name']}' экипирован!", "profile": cls.get_full_profile()}

        if profile["stars"] < title["cost_stars"]:
            raise ValueError(f"Недостаточно звезд! Требуется {title['cost_stars']} ⭐, у вас {profile['stars']} ⭐")

        # Покупка
        profile["stars"] -= title["cost_stars"]
        profile["unlocked_titles"].append(title_id)
        profile["active_title_id"] = title_id
        cls._save_profile(profile)

        return {
            "status": "success",
            "message": f"Поздравляем! Вы открыли звание '{title['name']}'! 🎉",
            "profile": cls.get_full_profile()
        }

    @classmethod
    def set_active_title(cls, title_id: str) -> Dict[str, Any]:
        profile = cls._load_profile()
        if title_id not in profile["unlocked_titles"]:
            raise ValueError("Вы еще не разблокировали этот титул!")

        profile["active_title_id"] = title_id
        cls._save_profile(profile)
        return {"status": "success", "profile": cls.get_full_profile()}
