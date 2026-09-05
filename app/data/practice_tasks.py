"""
Банк практических заданий по Python с автоматическими тест-кейсами.
"""

PRACTICE_TASKS = [
    # ---------------- JUNIOR TASKS ----------------
    {
        "id": "task_palindrome",
        "title": "Проверка палиндрома",
        "difficulty": "Junior",
        "category": "Строки и Базовые алгоритмы",
        "reward_stars": 15,
        "description": """Напишите функцию `is_palindrome(text: str) -> bool`, которая проверяет, является ли переданная строка палиндромом.

**Правила:**
- Регистр символов и пробелы не должны влиять на результат (например, `"А роза упала на лапу Азора"` -> `True`).
- Функция должна возвращать `True` или `False`.
""",
        "starter_code": '''def is_palindrome(text: str) -> bool:
    # Очистите строку от пробелов и приведите к нижнему регистру
    # Ваш код здесь
    pass
''',
        "entry_point": "is_palindrome",
        "test_cases": [
            {"input": ["radar"], "expected": True},
            {"input": ["hello"], "expected": False},
            {"input": ["A man a plan a canal Panama"], "expected": True},
            {"input": ["А роза упала на лапу Азора"], "expected": True},
            {"input": ["Python"], "expected": False}
        ]
    },
    {
        "id": "task_word_frequency",
        "title": "Подсчет частоты слов",
        "difficulty": "Junior",
        "category": "Словари и Списки",
        "reward_stars": 20,
        "description": """Напишите функцию `word_count(text: str) -> dict[str, int]`, которая принимает строку текста и возвращает словарь с количеством повторений каждого слова (в нижнем регистре).

**Пример:**
`"Python is fast and Python is cool"` -> `{"python": 2, "is": 2, "fast": 1, "and": 1, "cool": 1}`
""",
        "starter_code": '''def word_count(text: str) -> dict[str, int]:
    # Ваш код здесь
    pass
''',
        "entry_point": "word_count",
        "test_cases": [
            {"input": ["apple banana apple orange banana apple"], "expected": {"apple": 3, "banana": 2, "orange": 1}},
            {"input": ["hello world hello"], "expected": {"hello": 2, "world": 1}},
            {"input": ["one"], "expected": {"one": 1}}
        ]
    },
    {
        "id": "task_chunk_list",
        "title": "Разбиение списка на чанки (N частей)",
        "difficulty": "Junior",
        "category": "Списки и Срезы",
        "reward_stars": 20,
        "description": """Напишите функцию `chunk_list(items: list, size: int) -> list[list]`, которая разбивает список на подсписки указанной длины `size`.

**Пример:**
`chunk_list([1, 2, 3, 4, 5, 6, 7], 3)` -> `[[1, 2, 3], [4, 5, 6], [7]]`
""",
        "starter_code": '''def chunk_list(items: list, size: int) -> list[list]:
    # Ваш код здесь
    pass
''',
        "entry_point": "chunk_list",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5, 6, 7], 3], "expected": [[1, 2, 3], [4, 5, 6], [7]]},
            {"input": [[10, 20, 30, 40], 2], "expected": [[10, 20], [30, 40]]},
            {"input": [[], 5], "expected": []}
        ]
    },

    # ---------------- MIDDLE TASKS ----------------
    {
        "id": "task_timing_decorator",
        "title": "Декоратор кеширования (Memoization)",
        "difficulty": "Middle",
        "category": "Декораторы и Замыкания",
        "reward_stars": 35,
        "description": """Напишите декоратор `memoize(func)`, который сохраняет результаты вызова функции для переданных аргументов в кеш и при повторном вызове с теми же аргументами возвращает значение из кеша без повторного вычисления.

**Пример:**
```python
@memoize
def fib(n):
    if n < 2: return n
    return fib(n - 1) + fib(n - 2)
```
""",
        "starter_code": '''def memoize(func):
    cache = {}
    def wrapper(*args):
        # Реализуйте проверку в cache и сохранение
        pass
    return wrapper
''',
        "entry_point": "memoize",
        "test_custom": True,
        "test_cases": [
            {"type": "memoize_test"}
        ]
    },
    {
        "id": "task_validate_email",
        "title": "Валидатор Email адресов",
        "difficulty": "Middle",
        "category": "Регулярные выражения (Regex)",
        "reward_stars": 35,
        "description": """Напишите функцию `is_valid_email(email: str) -> bool`, проверяющую корректность email адреса с помощью регулярных выражений.

**Требования:**
- Содержит имя пользователя (буквы, цифры, точки, дефисы, подчеркивания).
- Символ `@`.
- Доменное имя и зону (например `gmail.com`, `yandex.ru`, `dev-site.org`).
""",
        "starter_code": '''import re

def is_valid_email(email: str) -> bool:
    # Ваш код здесь
    pass
''',
        "entry_point": "is_valid_email",
        "test_cases": [
            {"input": ["developer@example.com"], "expected": True},
            {"input": ["user.name+tag@sub.domain.org"], "expected": True},
            {"input": ["invalid-email@"], "expected": False},
            {"input": ["@missing-user.com"], "expected": False},
            {"input": ["no-at-sign.com"], "expected": False}
        ]
    },

    # ---------------- SENIOR TASKS ----------------
    {
        "id": "task_async_rate_limiter",
        "title": "Асинхронный батчинг с ограничением скорости",
        "difficulty": "Senior",
        "category": "AsyncIO & Concurrency",
        "reward_stars": 75,
        "description": """Напишите асинхронную функцию `async_gather_limited(tasks_func_list, max_concurrent: int) -> list`, которая параллельно запускает список асинхронных корутин, ограничивая число одновременно выполняемых задач до `max_concurrent` с помощью `asyncio.Semaphore`.

**Сигнатура:**
```python
async def async_gather_limited(tasks_list, max_concurrent: int = 3) -> list:
    pass
```
""",
        "starter_code": '''import asyncio

async def async_gather_limited(coroutines_list, max_concurrent: int = 3) -> list:
    # Используйте asyncio.Semaphore
    pass
''',
        "entry_point": "async_gather_limited",
        "is_async": True,
        "test_cases": [
            {"type": "async_semaphore_test"}
        ]
    },
    {
        "id": "task_lru_cache_impl",
        "title": "Собственная реализация LRU Cache",
        "difficulty": "Senior",
        "category": "ООП & Структуры данных",
        "reward_stars": 80,
        "description": """Реализуйте класс `LRUCache(capacity: int)` (Least Recently Used Cache) с методами:
- `get(key: str) -> any`: возвращает значение или `None`, обновляя порядок использования.
- `put(key: str, value: any)`: добавляет ключ-значение. Если лимит `capacity` превышен, удаляет самый давно использованный элемент.
""",
        "starter_code": '''from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        # Ваш код инициализации

    def get(self, key):
        pass

    def put(self, key, value):
        pass
''',
        "entry_point": "LRUCache",
        "is_class": True,
        "test_cases": [
            {"type": "lru_cache_test"}
        ]
    }
]
