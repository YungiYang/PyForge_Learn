"""
Генератор практических задач по выбранным Python-библиотекам с готовыми тестами и наградами.
"""

import time
import random
from typing import Dict, Any, List, Optional

# Каталог поддерживаемых библиотек и готовых задач
LIBRARY_TASK_CATALOG: Dict[str, Dict[str, Any]] = {
    "re": {
        "name": "re (Регулярные выражения)",
        "icon": "🔍",
        "category": "Standard Library / Text Processing",
        "description": "Модуль для поиска, сопоставления и трансформации строк по регулярным шаблонам.",
        "tasks": [
            {
                "title": "Извлечение всех хэштегов из текста",
                "difficulty": "Junior",
                "reward_stars": 20,
                "description": """Напишите функцию `extract_hashtags(text: str) -> list[str]`, которая находит все хэштеги в строке (начинаются с `#` и содержат буквы, цифры или подчеркивания).
Хэштег должен возвращаться БЕЗ знака `#` и в нижнем регистре.

**Пример:**
`"Hello #Python_3 and #fastapi! Check #100daysOfCode"` -> `["python_3", "fastapi", "100daysofcode"]`
""",
                "starter_code": '''import re

def extract_hashtags(text: str) -> list[str]:
    # Используйте re.findall для поиска тегов
    pattern = r"#(\\w+)"
    return [tag.lower() for tag in re.findall(pattern, text)]
''',
                "entry_point": "extract_hashtags",
                "test_cases": [
                    {"input": ["Hello #Python_3 and #fastapi! Check #100daysOfCode"], "expected": ["python_3", "fastapi", "100daysofcode"]},
                    {"input": ["No tags here!"], "expected": []},
                    {"input": ["#Code #CODE #code"], "expected": ["code", "code", "code"]}
                ]
            },
            {
                "title": "Маскирование номеров кредитных карт",
                "difficulty": "Middle",
                "reward_stars": 35,
                "description": """Напишите функцию `mask_card_numbers(text: str) -> str`, которая находит все 16-значные номера банковских карт (в форматах `XXXX-XXXX-XXXX-XXXX` или `XXXXXXXXXXXXXXXX`) и маскирует средние 8 цифр символами `*` (`XXXX-****-****-XXXX` или `XXXX********XXXX`).

**Пример:**
`"Payment card 1234-5678-9876-5432 processed"` -> `"Payment card 1234-****-****-5432 processed"`
""",
                "starter_code": '''import re

def mask_card_numbers(text: str) -> str:
    # Замените средние цифры карты на звездочки с помощью re.sub
    def repl_hyphen(m):
        return f"{m.group(1)}-****-****-{m.group(4)}"
    text = re.sub(r"(\\d{4})-(\\d{4})-(\\d{4})-(\\d{4})", repl_hyphen, text)
    
    def repl_plain(m):
        return f"{m.group(1)}********{m.group(2)}"
    return re.sub(r"(\\b\\d{4})\\d{8}(\\d{4}\\b)", repl_plain, text)
''',
                "entry_point": "mask_card_numbers",
                "test_cases": [
                    {"input": ["Payment card 1234-5678-9876-5432 processed"], "expected": "Payment card 1234-****-****-5432 processed"},
                    {"input": ["Direct number 1234567812345678 in text"], "expected": "Direct number 1234********5678 in text"},
                    {"input": ["Amount is 1234 dollars"], "expected": "Amount is 1234 dollars"}
                ]
            }
        ]
    },

    "fastapi": {
        "name": "fastapi (REST API & Web)",
        "icon": "⚡",
        "category": "Web Frameworks",
        "description": "Высокопроизводительный асинхронный веб-фреймворк для создания REST API на Python.",
        "tasks": [
            {
                "title": "FastAPI: Формирование структуры пагинированного ответа",
                "difficulty": "Junior",
                "reward_stars": 25,
                "description": """Напишите функцию `build_paginated_response(items: list, page: int, limit: int) -> dict`, которая моделирует стандартный пагинированный ответ FastAPI эндпоинта.

**Структура ответа:**
```python
{
    "total": len(items),
    "page": page,
    "limit": limit,
    "pages_count": (total + limit - 1) // limit, # или 0 если items пуст
    "data": items_on_this_page
}
```
""",
                "starter_code": '''def build_paginated_response(items: list, page: int, limit: int) -> dict:
    total = len(items)
    pages_count = (total + limit - 1) // limit if total > 0 else 0
    start = (page - 1) * limit
    end = start + limit
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages_count": pages_count,
        "data": items[start:end]
    }
''',
                "entry_point": "build_paginated_response",
                "test_cases": [
                    {"input": [[1, 2, 3, 4, 5], 1, 2], "expected": {"total": 5, "page": 1, "limit": 2, "pages_count": 3, "data": [1, 2]}},
                    {"input": [[1, 2, 3, 4, 5], 3, 2], "expected": {"total": 5, "page": 3, "limit": 2, "pages_count": 3, "data": [5]}},
                    {"input": [[], 1, 10], "expected": {"total": 0, "page": 1, "limit": 10, "pages_count": 0, "data": []}}
                ]
            },
            {
                "title": "FastAPI: Валидация Query-фильтра поиска",
                "difficulty": "Middle",
                "reward_stars": 40,
                "description": """Напишите функцию `filter_products(products: list[dict], min_price: float = None, max_price: float = None, category: str = None) -> list[dict]`, фильтрующую список словарей товаров по переданным query-параметрам.
""",
                "starter_code": '''def filter_products(products: list[dict], min_price: float = None, max_price: float = None, category: str = None) -> list[dict]:
    result = []
    for item in products:
        if min_price is not None and item.get("price", 0) < min_price:
            continue
        if max_price is not None and item.get("price", 0) > max_price:
            continue
        if category is not None and item.get("category") != category:
            continue
        result.append(item)
    return result
''',
                "entry_point": "filter_products",
                "test_cases": [
                    {
                        "input": [
                            [{"name": "A", "price": 100, "category": "tech"}, {"name": "B", "price": 250, "category": "tech"}, {"name": "C", "price": 50, "category": "food"}],
                            100, 200, "tech"
                        ],
                        "expected": [{"name": "A", "price": 100, "category": "tech"}]
                    },
                    {
                        "input": [
                            [{"name": "A", "price": 10}, {"name": "B", "price": 20}],
                            None, 15, None
                        ],
                        "expected": [{"name": "A", "price": 10}]
                    }
                ]
            }
        ]
    },

    "kivy": {
        "name": "kivy (Cross-platform GUI & Mobile)",
        "icon": "📱",
        "category": "GUI & Mobile",
        "description": "Фреймворк для кроссплатформенных приложений с сенсорным экраном (Windows, Linux, Android, iOS).",
        "tasks": [
            {
                "title": "Kivy: Калькулятор адаптивного размера виджетов (size_hint & dp)",
                "difficulty": "Junior",
                "reward_stars": 25,
                "description": """В Kivy размеры элементов задаются пропорционально экрану (`size_hint_x`, `size_hint_y`) либо в плотностно-независимых пикселях `dp`.
Напишите функцию `calculate_widget_bounds(parent_width: int, parent_height: int, size_hint: tuple[float, float], pos_hint: dict) -> dict`, вычисляющую абсолютные координаты `[x, y, width, height]` виджета.

`pos_hint` может содержать:
- `center_x`, `center_y` (от 0.0 до 1.0)
- `x`, `y` (от 0.0 до 1.0)
""",
                "starter_code": '''def calculate_widget_bounds(parent_width: int, parent_height: int, size_hint: tuple[float, float], pos_hint: dict) -> dict:
    w = int(parent_width * size_hint[0])
    h = int(parent_height * size_hint[1])
    
    if "center_x" in pos_hint:
        x = int(parent_width * pos_hint["center_x"] - w / 2)
    else:
        x = int(parent_width * pos_hint.get("x", 0.0))
        
    if "center_y" in pos_hint:
        y = int(parent_height * pos_hint["center_y"] - h / 2)
    else:
        y = int(parent_height * pos_hint.get("y", 0.0))
        
    return {"x": x, "y": y, "width": w, "height": h}
''',
                "entry_point": "calculate_widget_bounds",
                "test_cases": [
                    {
                        "input": [800, 600, [0.5, 0.2], {"center_x": 0.5, "center_y": 0.5}],
                        "expected": {"x": 200, "y": 240, "width": 400, "height": 120}
                    },
                    {
                        "input": [1000, 1000, [0.2, 0.1], {"x": 0.1, "y": 0.1}],
                        "expected": {"x": 100, "y": 100, "width": 200, "height": 100}
                    }
                ]
            }
        ]
    },

    "openpyxl": {
        "name": "openpyxl (Excel & Spreadsheets)",
        "icon": "📊",
        "category": "Office & Data",
        "description": "Библиотека для чтения, генерации и модификации файлов Excel (.xlsx).",
        "tasks": [
            {
                "title": "openpyxl: Конвертер координат ячеек Excel (A1 -> row, col)",
                "difficulty": "Junior",
                "reward_stars": 20,
                "description": """Напишите функцию `excel_coordinate_to_indices(cell_ref: str) -> tuple[int, int]`, преобразующую адрес ячейки Excel (например, `"A1"`, `"B5"`, `"AA10"`) в кортеж номеров `[row, col]` (индексация с 1, как в openpyxl).

**Примеры:**
`"A1"` -> `[1, 1]`
`"C3"` -> `[3, 3]`
`"Z1"` -> `[1, 26]`
`"AA2"` -> `[2, 27]`
""",
                "starter_code": '''def excel_coordinate_to_indices(cell_ref: str) -> list[int]:
    col_str = ""
    row_str = ""
    for char in cell_ref:
        if char.isalpha():
            col_str += char.upper()
        else:
            row_str += char
            
    col = 0
    for char in col_str:
        col = col * 26 + (ord(char) - ord('A') + 1)
        
    return [int(row_str), col]
''',
                "entry_point": "excel_coordinate_to_indices",
                "test_cases": [
                    {"input": ["A1"], "expected": [1, 1]},
                    {"input": ["C3"], "expected": [3, 3]},
                    {"input": ["Z1"], "expected": [1, 26]},
                    {"input": ["AA2"], "expected": [2, 27]}
                ]
            }
        ]
    },

    "pathlib": {
        "name": "pathlib (File System & Paths)",
        "icon": "📁",
        "category": "Standard Library / System",
        "description": "Объектно-ориентированная работа с путями файловой системы.",
        "tasks": [
            {
                "title": "pathlib: Группировка файлов по расширениям",
                "difficulty": "Junior",
                "reward_stars": 20,
                "description": """Напишите функцию `group_files_by_extension(filenames: list[str]) -> dict[str, list[str]]`, которая принимает список имен файлов и группирует их по расширениям (расширение в нижнем регистре с точкой, например `'.py'`, или `''` для файлов без расширения). Имена внутри списков отсортированы по алфавиту.
""",
                "starter_code": '''from pathlib import Path

def group_files_by_extension(filenames: list[str]) -> dict[str, list[str]]:
    result = {}
    for name in filenames:
        ext = Path(name).suffix.lower()
        if ext not in result:
            result[ext] = []
        result[ext].append(name)
    for ext in result:
        result[ext].sort()
    return result
''',
                "entry_point": "group_files_by_extension",
                "test_cases": [
                    {
                        "input": [["main.py", "app.py", "style.css", "data.json", "index.html", "README"]],
                        "expected": {
                            ".py": ["app.py", "main.py"],
                            ".css": ["style.css"],
                            ".json": ["data.json"],
                            ".html": ["index.html"],
                            "": ["README"]
                        }
                    },
                    {
                        "input": [["photo.JPG", "photo2.jpg"]],
                        "expected": {".jpg": ["photo.JPG", "photo2.jpg"]}
                    }
                ]
            },
            {
                "title": "pathlib: Поиск относительного безопасного пути (Path Traversal Guard)",
                "difficulty": "Middle",
                "reward_stars": 35,
                "description": """Напишите функцию `is_safe_subpath(base_dir: str, requested_path: str) -> bool`, проверяющую, лежит ли запрашиваемый путь `requested_path` строго внутри базовой директории `base_dir` (защита от атак `../..`).
""",
                "starter_code": '''from pathlib import Path

def is_safe_subpath(base_dir: str, requested_path: str) -> bool:
    try:
        base = Path(base_dir).resolve()
        target = (base / requested_path).resolve()
        return target == base or base in target.parents
    except Exception:
        return False
''',
                "entry_point": "is_safe_subpath",
                "test_cases": [
                    {"input": ["/var/www/uploads", "images/avatar.png"], "expected": True},
                    {"input": ["/var/www/uploads", "../../etc/passwd"], "expected": False},
                    {"input": ["/app", "."], "expected": True}
                ]
            }
        ]
    },

    "requests": {
        "name": "requests / httpx (HTTP Clients)",
        "icon": "🌐",
        "category": "Networking & API",
        "description": "Популярнейшие библиотеки для отправки HTTP запросов, работы с REST API и сессиями.",
        "tasks": [
            {
                "title": "requests: Сборка URL с query-параметрами и сортировкой",
                "difficulty": "Junior",
                "reward_stars": 20,
                "description": """Напишите функцию `build_query_url(base_url: str, params: dict) -> str`, которая формирует полный URL из `base_url` и словаря параметров `params`. Параметры должны быть отсортированы по ключу по алфавиту и соединены через `&`. Если `params` пуст — вернуть `base_url`.
""",
                "starter_code": '''from urllib.parse import quote_plus

def build_query_url(base_url: str, params: dict) -> str:
    if not params:
        return base_url
    query_parts = []
    for k in sorted(params.keys()):
        v = params[k]
        query_parts.append(f"{quote_plus(str(k))}={quote_plus(str(v))}")
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{'&'.join(query_parts)}"
''',
                "entry_point": "build_query_url",
                "test_cases": [
                    {
                        "input": ["https://api.example.com/search", {"q": "python", "limit": 10}],
                        "expected": "https://api.example.com/search?limit=10&q=python"
                    },
                    {
                        "input": ["https://api.example.com/data", {}],
                        "expected": "https://api.example.com/data"
                    }
                ]
            }
        ]
    },

    "sqlite3": {
        "name": "sqlite3 (Embedded Database)",
        "icon": "🗄️",
        "category": "Databases & Storage",
        "description": "Встроенная легковесная реляционная база данных SQL в стандартной библиотеке Python.",
        "tasks": [
            {
                "title": "sqlite3: Генерация параметризованного SQL INSERT запроса",
                "difficulty": "Junior",
                "reward_stars": 25,
                "description": """Напишите функцию `generate_insert_sql(table_name: str, data: dict) -> tuple[str, list]`, которая формирует безопасный параметризованный SQL запрос (с плейсхолдерами `?`) и список значений. Ключи должны быть отсортированы по алфавиту.

**Пример:**
`generate_insert_sql("users", {"name": "Alice", "age": 25})`
-> `["INSERT INTO users (age, name) VALUES (?, ?)", [25, "Alice"]]`
""",
                "starter_code": '''def generate_insert_sql(table_name: str, data: dict) -> list:
    keys = sorted(data.keys())
    columns = ", ".join(keys)
    placeholders = ", ".join(["?"] * len(keys))
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    values = [data[k] for k in keys]
    return [sql, values]
''',
                "entry_point": "generate_insert_sql",
                "test_cases": [
                    {
                        "input": ["users", {"name": "Alice", "age": 25}],
                        "expected": ["INSERT INTO users (age, name) VALUES (?, ?)", [25, "Alice"]]
                    },
                    {
                        "input": ["logs", {"level": "INFO"}],
                        "expected": ["INSERT INTO logs (level) VALUES (?)", ["INFO"]]
                    }
                ]
            }
        ]
    },

    "json": {
        "name": "json (Serialization & Parsing)",
        "icon": "📦",
        "category": "Standard Library / Serialization",
        "description": "Стандартный модуль для сериализации и десериализации данных в формате JSON.",
        "tasks": [
            {
                "title": "json: Безопасный парсинг с глубоким извлечением ключа (JSON Path)",
                "difficulty": "Junior",
                "reward_stars": 20,
                "description": """Напишите функцию `json_get_deep(json_str: str, path: str, default=None) -> any`, которая парсит JSON строку и извлекает значение по точечному пути `path` (например `"user.profile.age"`). Если путь не существует или JSON невалиден, возвращает `default`.
""",
                "starter_code": '''import json

def json_get_deep(json_str: str, path: str, default=None):
    try:
        data = json.loads(json_str)
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    except Exception:
        return default
''',
                "entry_point": "json_get_deep",
                "test_cases": [
                    {
                        "input": ['{"user": {"profile": {"age": 30, "city": "Moscow"}}}', "user.profile.age"],
                        "expected": 30
                    },
                    {
                        "input": ['{"user": {"name": "Ivan"}}', "user.missing.key", "N/A"],
                        "expected": "N/A"
                    },
                    {
                        "input": ['invalid json string', "any.path"],
                        "expected": None
                    }
                ]
            }
        ]
    },

    "pandas": {
        "name": "pandas (Data Analysis & Manipulation)",
        "icon": "🐼",
        "category": "Data Science & Analytics",
        "description": "Мощная библиотека для структурирования, очистки и анализа табличных данных (DataFrames).",
        "tasks": [
            {
                "title": "pandas: Расчет агрегированной статистики по категориям",
                "difficulty": "Middle",
                "reward_stars": 35,
                "description": """Напишите функцию `aggregate_sales_data(records: list[dict]) -> dict[str, dict]`, которая группирует список записей `[{"category": "A", "sales": 100}, ...]` по категории и рассчитывает:
- `count`: количество записей
- `total`: сумму `sales`
- `avg`: среднее значение `sales` (округленное до 2 знаков)
""",
                "starter_code": '''def aggregate_sales_data(records: list[dict]) -> dict[str, dict]:
    groups = {}
    for r in records:
        cat = r["category"]
        sales = r["sales"]
        if cat not in groups:
            groups[cat] = []
        groups[cat].append(sales)
        
    result = {}
    for cat, values in groups.items():
        total = sum(values)
        count = len(values)
        avg = round(total / count, 2) if count else 0
        result[cat] = {"count": count, "total": total, "avg": avg}
    return result
''',
                "entry_point": "aggregate_sales_data",
                "test_cases": [
                    {
                        "input": [[
                            {"category": "Food", "sales": 100},
                            {"category": "Tech", "sales": 500},
                            {"category": "Food", "sales": 200},
                            {"category": "Tech", "sales": 100}
                        ]],
                        "expected": {
                            "Food": {"count": 2, "total": 300, "avg": 150.0},
                            "Tech": {"count": 2, "total": 600, "avg": 300.0}
                        }
                    }
                ]
            }
        ]
    },

    "pydantic": {
        "name": "pydantic (Data Validation & Settings)",
        "icon": "🛡️",
        "category": "Modern Tooling & Typing",
        "description": "Библиотека для валидации данных и управления настройками с использованием подсказок типов Python.",
        "tasks": [
            {
                "title": "Pydantic: Очистка и приведение типов сырого словаря",
                "difficulty": "Junior",
                "reward_stars": 25,
                "description": """Напишите функцию `sanitize_user_input(raw: dict) -> dict`, которая принимает сырой словарь пользователя и валидирует/приводит поля:
- `username`: строка в нижнем регистре без лишних пробелов.
- `age`: целое число (если передана строка `"25"` -> `25`). Если число < 0 или не число -> `None`.
- `is_active`: булево значение (`True`/`False`).
""",
                "starter_code": '''def sanitize_user_input(raw: dict) -> dict:
    username = str(raw.get("username", "")).strip().lower()
    
    raw_age = raw.get("age")
    try:
        age = int(raw_age)
        if age < 0:
            age = None
    except (ValueError, TypeError):
        age = None
        
    is_active = bool(raw.get("is_active", False))
    
    return {
        "username": username,
        "age": age,
        "is_active": is_active
    }
''',
                "entry_point": "sanitize_user_input",
                "test_cases": [
                    {
                        "input": [{"username": "  AliceDev  ", "age": "28", "is_active": 1}],
                        "expected": {"username": "alicedev", "age": 28, "is_active": True}
                    },
                    {
                        "input": [{"username": "Bob", "age": "-5", "is_active": False}],
                        "expected": {"username": "bob", "age": None, "is_active": False}
                    }
                ]
            }
        ]
    },

    "collections": {
        "name": "collections (Advanced Containers)",
        "icon": "📚",
        "category": "Standard Library / Data Structures",
        "description": "Специализированные контейнеры: Counter, defaultdict, deque, OrderedDict, namedtuple.",
        "tasks": [
            {
                "title": "collections: Поиск N наиболее часто встречающихся элементов",
                "difficulty": "Junior",
                "reward_stars": 20,
                "description": """Напишите функцию `top_n_frequent(items: list, n: int) -> list[tuple]`, которая возвращает список из `n` наиболее часто встречающихся элементов и их количества, отсортированных по убыванию частоты.
При равной частоте элементы сортируются по возрастанию значения.
""",
                "starter_code": '''from collections import Counter

def top_n_frequent(items: list, n: int) -> list:
    counts = Counter(items)
    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], str(x[0])))
    return [list(pair) for pair in sorted_items[:n]]
''',
                "entry_point": "top_n_frequent",
                "test_cases": [
                    {
                        "input": [["a", "b", "c", "a", "b", "a"], 2],
                        "expected": [["a", 3], ["b", 2]]
                    },
                    {
                        "input": [[10, 20, 30, 10, 20, 10], 1],
                        "expected": [[10, 3]]
                    }
                ]
            }
        ]
    },

    "datetime": {
        "name": "datetime (Dates & Timezones)",
        "icon": "⏰",
        "category": "Standard Library / Time",
        "description": "Работа с датами, временем, интервалами timedelta и часовыми поясами.",
        "tasks": [
            {
                "title": "datetime: Расчет разницы в днях между датами в ISO формате",
                "difficulty": "Junior",
                "reward_stars": 20,
                "description": """Напишите функцию `days_between(date_str_1: str, date_str_2: str) -> int`, вычисляющую абсолютное количество календарных дней между двумя датами формата `"YYYY-MM-DD"`.
""",
                "starter_code": '''from datetime import datetime

def days_between(date_str_1: str, date_str_2: str) -> int:
    d1 = datetime.strptime(date_str_1, "%Y-%m-%d")
    d2 = datetime.strptime(date_str_2, "%Y-%m-%d")
    return abs((d2 - d1).days)
''',
                "entry_point": "days_between",
                "test_cases": [
                    {"input": ["2026-01-01", "2026-01-10"], "expected": 9},
                    {"input": ["2025-12-31", "2026-01-01"], "expected": 1},
                    {"input": ["2026-05-20", "2026-05-20"], "expected": 0}
                ]
            }
        ]
    },

    "customtkinter": {
        "name": "customtkinter / tkinter (Modern GUI)",
        "icon": "🎨",
        "category": "GUI & Desktop",
        "description": "Современная надстройка над Tkinter с поддержкой темной/светлой темы и красивых скругленных виджетов.",
        "tasks": [
            {
                "title": "CustomTkinter: Расчет цветовой палитры и контраста для темы",
                "difficulty": "Junior",
                "reward_stars": 20,
                "description": """Напишите функцию `get_theme_contrast_color(hex_color: str) -> str`, которая по заданному hex-цвету фона (`#RRGGBB`) определяет цвет текста: если фон светлый (яркость >= 128) — возвращает `"#000000"`, иначе `"#FFFFFF"`.
Формула яркости: `(0.299*R + 0.587*G + 0.114*B)`.
""",
                "starter_code": '''def get_theme_contrast_color(hex_color: str) -> str:
    hex_clean = hex_color.lstrip("#")
    r = int(hex_clean[0:2], 16)
    g = int(hex_clean[2:4], 16)
    b = int(hex_clean[4:6], 16)
    
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#000000" if luminance >= 128 else "#FFFFFF"
''',
                "entry_point": "get_theme_contrast_color",
                "test_cases": [
                    {"input": ["#FFFFFF"], "expected": "#000000"},
                    {"input": ["#000000"], "expected": "#FFFFFF"},
                    {"input": ["#1A1A1A"], "expected": "#FFFFFF"},
                    {"input": ["#E0E0E0"], "expected": "#000000"}
                ]
            }
        ]
    }
}

# Динамический реестр сгенерированных задач
DYNAMIC_GENERATED_TASKS: Dict[str, Dict[str, Any]] = {}

class LibraryTaskGeneratorService:
    @classmethod
    def get_supported_libraries(cls) -> List[Dict[str, Any]]:
        """Возвращает список доступных библиотек с метаинформацией"""
        libs = []
        for key, data in LIBRARY_TASK_CATALOG.items():
            libs.append({
                "id": key,
                "name": data["name"],
                "icon": data["icon"],
                "category": data["category"],
                "description": data["description"],
                "task_count": len(data["tasks"])
            })
        return libs

    @classmethod
    def generate_random_task(cls, library_name: str, difficulty: Optional[str] = None) -> Dict[str, Any]:
        """Генерирует или подбирает случайную задачу по выбранной библиотеке"""
        lib_key = library_name.strip().lower()

        # Если библиотека есть в каталоге
        if lib_key in LIBRARY_TASK_CATALOG:
            lib_info = LIBRARY_TASK_CATALOG[lib_key]
            tasks = lib_info["tasks"]
            if difficulty:
                filtered = [t for t in tasks if t["difficulty"].lower() == difficulty.lower()]
                if filtered:
                    tasks = filtered
            
            chosen_template = random.choice(tasks)
            task_id = f"task_{lib_key}_{int(time.time() * 1000)}_{random.randint(100, 999)}"
            
            generated = {
                "id": task_id,
                "library": lib_key,
                "library_name": lib_info["name"],
                "library_icon": lib_info["icon"],
                "title": f"[{lib_info['name'].split()[0]}] {chosen_template['title']}",
                "difficulty": chosen_template["difficulty"],
                "category": lib_info["category"],
                "reward_stars": chosen_template["reward_stars"],
                "description": chosen_template["description"],
                "starter_code": chosen_template["starter_code"],
                "entry_point": chosen_template["entry_point"],
                "test_cases": chosen_template["test_cases"],
                "is_solved": False
            }
            DYNAMIC_GENERATED_TASKS[task_id] = generated
            return generated

        # Если запрошена произвольная библиотека не из списка, генерируем синтетическую задачу
        diff = difficulty or random.choice(["Junior", "Middle", "Senior"])
        reward_map = {"Junior": 25, "Middle": 45, "Senior": 80}
        stars = reward_map.get(diff, 30)
        task_id = f"task_dyn_{lib_key}_{int(time.time() * 1000)}"

        title = f"[{lib_key.capitalize()}] Реализация сервисного модуля для {lib_key}"
        description = f"""### 🎯 Практическое задание по библиотеке `{lib_key}` ({diff})

Разработайте функцию `process_{lib_key}_data(payload: dict) -> dict`, которая принимает входные данные конфигурации и возвращает обогащенный словарь с метаданными.

**Требования:**
- Проверить наличие ключа `"data"` в `payload`.
- Добавить поле `"processed_by": "{lib_key}"`.
- Добавить поле `"status": "ok"`.
- Вернуть результирующий словарь.
"""
        starter_code = f'''def process_{lib_key}_data(payload: dict) -> dict:
    """Обработчик данных для модуля {lib_key}"""
    result = dict(payload)
    result["processed_by"] = "{lib_key}"
    result["status"] = "ok"
    return result
'''
        generated = {
            "id": task_id,
            "library": lib_key,
            "library_name": lib_key,
            "library_icon": "🧩",
            "title": title,
            "difficulty": diff,
            "category": f"Библиотека: {lib_key}",
            "reward_stars": stars,
            "description": description,
            "starter_code": starter_code,
            "entry_point": f"process_{lib_key}_data",
            "test_cases": [
                {
                    "input": [{"data": [1, 2, 3]}],
                    "expected": {"data": [1, 2, 3], "processed_by": lib_key, "status": "ok"}
                },
                {
                    "input": [{"user": "dev", "active": True}],
                    "expected": {"user": "dev", "active": True, "processed_by": lib_key, "status": "ok"}
                }
            ],
            "is_solved": False
        }
        DYNAMIC_GENERATED_TASKS[task_id] = generated
        return generated

    @classmethod
    def get_dynamic_task(cls, task_id: str) -> Optional[Dict[str, Any]]:
        return DYNAMIC_GENERATED_TASKS.get(task_id)
