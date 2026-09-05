"""
Сервис Таблицы Лидеров (Leaderboard) для рейтинга пользователей PyForge по набранным звёздам и очкам.
"""

from typing import Dict, Any, List, Optional
from .auth_service import AuthService
from ..data.titles_catalog import get_all_titles

class LeaderboardService:
    @classmethod
    def get_leaderboard(cls, current_username: Optional[str] = None) -> Dict[str, Any]:
        """Возвращает глобальный рейтинг пользователей с рангами и метаданными"""
        users_map = AuthService._load_users()
        users_list = list(users_map.values())
        all_titles = get_all_titles()
        title_map = {t["id"]: t for t in all_titles}

        # Сортировка: сначала по звездам (убывание), затем по решенным задачам
        users_list.sort(key=lambda u: (u.get("stars", 0), len(u.get("solved_tasks", []))), reverse=True)

        rankings = []
        user_rank_info = None

        for idx, u in enumerate(users_list, 1):
            uname = u.get("username", "")
            title_id = u.get("active_title_id", "title_novice")
            title_info = title_map.get(title_id, {"name": "🐍 Начинающий Змеелов", "rarity": "COMMON", "color": "text-slate-300"})

            is_current = False
            if current_username and uname.lower() == current_username.lower():
                is_current = True

            is_creator = AuthService.is_developer(uname) or u.get("role") == "creator" or uname.lower() == "chevels"
            user_role = "creator" if is_creator else u.get("role", "user")
            is_dev = is_creator or user_role in ["creator", "admin"] or u.get("is_developer", False)

            entry = {
                "rank": idx,
                "id": u.get("id"),
                "username": uname,
                "display_name": u.get("display_name") or uname,
                "avatar": u.get("avatar"),
                "is_developer": is_dev,
                "role": user_role,
                "stars": u.get("stars", 0),
                "total_earned_stars": u.get("total_earned_stars", 0),
                "solved_tasks_count": len(u.get("solved_tasks", [])),
                "title_name": title_info.get("name", title_id),
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
