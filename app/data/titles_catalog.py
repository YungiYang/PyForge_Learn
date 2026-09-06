"""
Каталог званий, титулов и достижений для системы геймификации.
"""

TITLES_CATALOG = [
    {
        "id": "title_novice",
        "name": "🐍 Начинающий Змеелов",
        "cost_stars": 0,
        "rarity": "Common",
        "color": "text-slate-300 border-slate-700 bg-slate-800/60",
        "description": "Стартовое звание каждого, кто ступил на путь изучения Python.",
        "icon": "smile"
    },
    {
        "id": "title_list_master",
        "name": "📜 Мастер Списков и Кортежей",
        "cost_stars": 40,
        "rarity": "Common",
        "color": "text-emerald-400 border-emerald-500/30 bg-emerald-950/20",
        "description": "Знает все секреты срезов, генераторов списков и распаковки кортежей.",
        "icon": "list"
    },
    {
        "id": "title_dict_wizard",
        "name": "🔮 Волшебник Хэш-таблиц & Dict",
        "cost_stars": 80,
        "rarity": "Rare",
        "color": "text-sky-400 border-sky-500/30 bg-sky-950/20",
        "description": "Мгновенный доступ по ключу со сложностью O(1) в любых условиях.",
        "icon": "sparkles"
    },
    {
        "id": "title_oop_knight",
        "name": "🛡️ Рыцарь ООП и Паттернов",
        "cost_stars": 150,
        "rarity": "Rare",
        "color": "text-indigo-400 border-indigo-500/30 bg-indigo-950/20",
        "description": "Повелитель инкапсуляции, полиморфизма и чистой архитектуры.",
        "icon": "shield"
    },
    {
        "id": "title_async_adept",
        "name": "⚡ Адепт Асинхронности (Async Master)",
        "cost_stars": 250,
        "rarity": "Epic",
        "color": "text-amber-400 border-amber-500/30 bg-amber-950/20",
        "description": "Укротитель Event Loop, TaskGroup, корутин и параллельных потоков.",
        "icon": "zap"
    },
    {
        "id": "title_bug_hunter",
        "name": "🐛 Истребитель Багов (Bug Hunter)",
        "cost_stars": 400,
        "rarity": "Epic",
        "color": "text-purple-400 border-purple-500/30 bg-purple-950/20",
        "description": "Ни один баг или SyntaxError не скроется от его зоркого глаза.",
        "icon": "crosshair"
    },
    {
        "id": "title_architect",
        "name": "🏛️ Архитектор Чистого Кода",
        "cost_stars": 600,
        "rarity": "Legendary",
        "color": "text-pink-400 border-pink-500/30 bg-pink-950/20",
        "description": "Создает идеальные масштабируемые системы без спагетти-кода.",
        "icon": "boxes"
    },
    {
        "id": "title_grandmaster",
        "name": "👑 Python Grandmaster",
        "cost_stars": 1000,
        "rarity": "Mythic",
        "color": "text-amber-300 border-amber-400/50 bg-gradient-to-r from-amber-500/20 to-indigo-500/20",
        "description": "Высшее признание мастерства в экосистеме Python!",
        "icon": "crown"
    }
]

from pathlib import Path

def get_all_titles():
    """Возвращает список всех титулов (базовые + созданные создателем)"""
    titles = list(TITLES_CATALOG)
    try:
        from ..services.db_storage import DBStorage
        custom_list = DBStorage.load_json("custom_titles.json", default=[])
        if isinstance(custom_list, list):
            titles.extend(custom_list)
    except Exception:
        pass
    return titles

def save_custom_title(title_dict: dict) -> dict:
    """Сохраняет новый кастомный титул через DBStorage"""
    try:
        from ..services.db_storage import DBStorage
        custom_list = DBStorage.load_json("custom_titles.json", default=[])
        if not isinstance(custom_list, list):
            custom_list = []

        existing_idx = next((i for i, t in enumerate(custom_list) if t["id"] == title_dict["id"]), None)
        if existing_idx is not None:
            custom_list[existing_idx] = title_dict
        else:
            custom_list.append(title_dict)

        DBStorage.save_json("custom_titles.json", custom_list)
    except Exception as e:
        print(f"Ошибка сохранения титула: {e}")

    return title_dict

def delete_custom_title(title_id: str) -> bool:
    """Удаляет кастомный титул через DBStorage"""
    try:
        from ..services.db_storage import DBStorage
        custom_list = DBStorage.load_json("custom_titles.json", default=[])
        if not isinstance(custom_list, list):
            return False
        filtered = [t for t in custom_list if t["id"] != title_id]
        DBStorage.save_json("custom_titles.json", filtered)
        return True
    except Exception:
        return False
