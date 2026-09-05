"""
Инструменты современного Python-разработчика: Ruff, Mypy, UV, Poetry, Pytest.
"""

TOOLS_TOPICS = [
    {
        "id": "uv-fastest-package-manager",
        "title": "UV: Революционный сверхбыстрый менеджер пакетов (на Rust)",
        "icon": "zap",
        "category": "tools",
        "summary": "Менеджер пакетов от создателей Ruff, заменяющий pip, poetry, pyenv и virtualenv в 10-100 раз быстрее.",
        "content": """
### Почему все переходят на `uv` в 2024-2026 годах?
`uv` написан на Rust и устанавливает зависимости за миллисекунды благодаря глобальному кэшированию и параллельной загрузке колес (wheels).

#### Основные команды `uv`:
```bash
# Установка uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Или на Windows через powershell / winget:
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 1. Мгновенное создание виртуального окружения
uv venv

# 2. Мгновенная установка пакетов
uv pip install fastapi uvicorn pydantic

# 3. Управление проектами и lock-файлами
uv init my-project
uv add requests
uv run main.py
```
"""
    },
    {
        "id": "ruff-linter-formatter",
        "title": "Ruff: Молниеносный Линтер и Форматтер кода",
        "icon": "check-circle",
        "category": "tools",
        "summary": "Заменяет Flake8, Black, isort, pydocstyle и pyupgrade в одной утилите, работающей в 100 раз быстрее.",
        "content": """
### Как настроить Ruff в проекте:
Добавьте в ваш `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # Pyflakes
    "I",    # isort (сортировка импортов)
    "B",    # flake8-bugbear (поиск скрытых багов)
    "UP",   # pyupgrade (обновление синтаксиса до нового Python)
    "RUF",  # Ruff-специфичные правила
]
ignore = ["E501"]  # Игнорировать слишком длинные строки при необходимости

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

#### Запуск проверки и автоисправления:
```bash
# Проверить код на ошибки
ruff check .

# Автоматически исправить большинство ошибок и отсортировать импорты
ruff check --fix .

# Отформатировать весь проект (аналог Black)
ruff format .
```
"""
    },
    {
        "id": "pytest-mastery",
        "title": "Тестирование с Pytest: Фикстуры, Моки и Параметризация",
        "icon": "test-tube",
        "category": "tools",
        "summary": "Как писать надежные юнит- и интеграционные тесты с `pytest`, `pytest-asyncio` и фикстурами `conftest.py`.",
        "content": """
### 1. Фикстуры в `tests/conftest.py`:
```python
# tests/conftest.py
import pytest
import sqlite3
from typing import Generator

@pytest.fixture
def memory_db() -> Generator[sqlite3.Connection, None, None]:
    # Создаем базу данных в памяти для каждого теста
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);")
    conn.commit()
    yield conn
    conn.close()
```

### 2. Тесты с параметризацией и асинхронностью:
```python
# tests/test_app.py
import pytest

def calculate_discount(price: float, discount_percent: int) -> float:
    if not (0 <= discount_percent <= 100):
        raise ValueError("Скидка должна быть от 0 до 100")
    return price * (1 - discount_percent / 100)

# Параметризованный тест (запускается для каждого набора параметров)
@pytest.mark.parametrize("price, discount, expected", [
    (100.0, 10, 90.0),
    (200.0, 50, 100.0),
    (50.0, 0, 50.0),
    (100.0, 100, 0.0),
])
def test_calculate_discount(price, discount, expected):
    assert calculate_discount(price, discount) == expected

def test_calculate_discount_invalid():
    with pytest.raises(ValueError):
        calculate_discount(100.0, 150)

# Асинхронный тест
@pytest.mark.asyncio
async def test_async_fetch():
    import asyncio
    await asyncio.sleep(0.01)
    assert True
```

#### Запуск тестов:
```bash
pytest -v --durations=5
```
"""
    }
]
