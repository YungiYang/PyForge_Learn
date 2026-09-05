"""
Service daily quests
"""
import json, time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

QUESTS_DATA_FILE = Path(__file__).resolve().parent.parent / 'data' / 'daily_quests.json'

QUEST_DEFINITIONS = [
    {'id': 'solve_task', 'title': '🎯 Мастер кода дня', 'description': 'Решите любую задачу в тренажере', 'icon': 'award', 'category': 'practice', 'reward_stars': 40, 'target': 1},
    {'id': 'run_sandbox', 'title': '⚡ Запуск в песочнице', 'description': 'Запустите любой Python-код в Sandbox', 'icon': 'terminal', 'category': 'sandbox', 'reward_stars': 20, 'target': 1},
    {'id': 'community_action', 'title': '💬 Активность сообщества', 'description': 'Оставьте тему/ответ на форуме или проголосуйте', 'icon': 'messages-square', 'category': 'community', 'reward_stars': 25, 'target': 1},
    {'id': 'scaffold_project', 'title': '🚀 Сборка проекта', 'description': 'Сгенерируйте шаблон в Конструкторе', 'icon': 'sparkles', 'category': 'scaffolder', 'reward_stars': 35, 'target': 1}
]

class DailyQuestsService:
    @classmethod
    def _get_today_str(cls) -> str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%d')

    @classmethod
    def _seconds_until_midnight(cls) -> int:
        now = datetime.now(timezone.utc)
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return int((tomorrow - now).total_seconds())

    @classmethod
    def _load_data(cls) -> Dict[str, Any]:
        today = cls._get_today_str()
        if not QUESTS_DATA_FILE.exists():
            data = {'date': today, 'user_progress': {}}
            cls._save_data(data)
            return data
        try:
            with open(QUESTS_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('date') != today:
                data = {'date': today, 'user_progress': {}}
                cls._save_data(data)
            return data
        except Exception:
            data = {'date': today, 'user_progress': {}}
            cls._save_data(data)
            return data

    @classmethod
    def _save_data(cls, data: Dict[str, Any]):
        QUESTS_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(QUESTS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def _resolve_username(cls, token_or_uname: Optional[str]) -> str:
        if not token_or_uname:
            return 'guest'
        from .auth_service import AuthService
        user = AuthService.get_user_by_token(token_or_uname)
        if user:
            return user['username'].lower()
        return str(token_or_uname).strip().lower()

    @classmethod
    def get_daily_quests(cls, token_or_uname: Optional[str] = None) -> Dict[str, Any]:
        uname = cls._resolve_username(token_or_uname)
        data = cls._load_data()
        user_p = data.get('user_progress', {}).get(uname, {})

        quests = []
        completed_count = 0
        total_rewards_available = 0

        for q in QUEST_DEFINITIONS:
            qid = q['id']
            qp = user_p.get(qid, {'progress': 0, 'completed': False, 'claimed': False})
            progress = qp.get('progress', 0)
            target = q['target']
            completed = progress >= target or qp.get('completed', False)
            claimed = qp.get('claimed', False)

            if completed:
                completed_count += 1
            if completed and not claimed:
                total_rewards_available += q['reward_stars']

            quests.append({
                'id': qid,
                'title': q['title'],
                'description': q['description'],
                'icon': q['icon'],
                'category': q['category'],
                'reward_stars': q['reward_stars'],
                'reward_xp': q.get('reward_xp', 50),
                'progress': min(progress, target),
                'target': target,
                'target_count': target,
                'completed': completed,
                'claimed': claimed
            })

        return {
            'success': True,
            'date': data.get('date'),
            'seconds_until_reset': cls._seconds_until_midnight(),
            'seconds_to_reset': cls._seconds_until_midnight(),
            'completed_count': completed_count,
            'total_quests': len(QUEST_DEFINITIONS),
            'total_count': len(QUEST_DEFINITIONS),
            'unclaimed_stars': total_rewards_available,
            'quests': quests
        }

    @classmethod
    def record_activity(cls, token_or_uname: Optional[str], quest_type: str, amount: int = 1) -> bool:
        if not token_or_uname:
            return False
        uname = cls._resolve_username(token_or_uname)
        if not uname or uname == 'guest':
            return False

        data = cls._load_data()
        if 'user_progress' not in data:
            data['user_progress'] = {}
        if uname not in data['user_progress']:
            data['user_progress'][uname] = {}

        quest_def = next((q for q in QUEST_DEFINITIONS if q['id'] == quest_type), None)
        if not quest_def:
            return False

        qp = data['user_progress'][uname].get(quest_type, {'progress': 0, 'completed': False, 'claimed': False})
        qp['progress'] = qp.get('progress', 0) + amount
        if qp['progress'] >= quest_def['target']:
            qp['completed'] = True
        data['user_progress'][uname][quest_type] = qp
        cls._save_data(data)
        return True

    @classmethod
    def claim_reward(cls, token_or_uname: str, quest_id: str) -> Dict[str, Any]:
        uname = cls._resolve_username(token_or_uname)
        if not uname or uname == 'guest':
            raise ValueError('Необходимо войти в аккаунт для получения награды')

        data = cls._load_data()
        user_p = data.get('user_progress', {}).get(uname, {})
        qp = user_p.get(quest_id)

        if not qp or not qp.get('completed'):
            raise ValueError('Задание еще не выполнено')
        if qp.get('claimed'):
            raise ValueError('Награда за это задание уже получена сегодня')

        quest_def = next((q for q in QUEST_DEFINITIONS if q['id'] == quest_id), None)
        if not quest_def:
            raise ValueError('Задание не найдено')

        from .auth_service import AuthService
        reward = quest_def['reward_stars']
        AuthService.update_user_profile(
            uname,
            lambda u: {
                **u,
                'stars': u.get('stars', 0) + reward,
                'total_earned_stars': u.get('total_earned_stars', 0) + reward
            }
        )

        qp['claimed'] = True
        data['user_progress'][uname][quest_id] = qp
        cls._save_data(data)

        return {
            'success': True,
            'awarded_stars': reward,
            'quest_title': quest_def['title'],
            'quests_state': cls.get_daily_quests(token_or_uname)
        }
