"""
Сервис Таблицы Лидеров (Leaderboard) для рейтинга пользователей PyForge по набранным звёздам и очкам.
"""

from typing import Dict, Any, List, Optional
from .auth_service import AuthService
from ..data.titles_catalog import TITLES_CATALOG

TITLE_MAP = {t["id"]: t for t in TITLES_CATALOG}

class LeaderboardService:
    @classmethod
    def get_leaderboard(cls, current_username: Optional[str] = None) -> Dict[str, Any]:
        """Возвращает глобальный рейтинг пользователей с рангами и метаданными"""
        users_map = AuthService._load_users()
        users_list = list(users_map.values())

        # Сортировка: сначала по звездам (убывание), затем по решенным задачам
        users_list.sort(key=lambda u: (u.get("stars", 0), len(u.get("solved_tasks", []))), reverse=True)

        rankings = []
        user_rank_info = None

        for idx, u in enumerate(users_list, 1):
            title_id = u.get("active_title_id", "title_novice")
            title_info = TITLE_MAP.get(title_id, {"name": "🐍 Начинающий Змеелов", "rarity": "COMMON", "color": "text-slate-300"})

            is_current = False
            if current_username and u.get("username", "").lower() == current_username.lower():
                is_current = True

            is_dev = AuthService.is_developer(u.get("username", "")) or u.get("is_developer", False) or u.get("role") == "creator"
            entry = {
                "rank": idx,
                "id": u.get("id"),
                "username": u.get("username"),
                "display_name": u.get("display_name") or u.get("username"),
                "avatar": u.get("avatar"),
                "is_developer": is_dev,
                "role": "creator" if is_dev else "user",
                "stars": u.get("stars", 0),
                "total_earned_stars": u.get("total_earned_stars", 0),
                "solved_tasks_count": len(u.get("solved_tasks", [])),
                "title_name": title_info["name"],
                "title_rarity": title_info.get("rarity", "COMMON"),
                "is_current_user": is_current
            }
            rankings.append(entry)

            if is_current:
                user_rank_info = entry

        return {
            "success": True,
            "total_players": len(rankings),
            "top_3": rankings[:3],
            "rankings": rankings,
            "current_user_rank": user_rank_info
        }
