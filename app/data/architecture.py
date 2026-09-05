"""
Архитектурные паттерны, структура проектов и лучшие практики разработки на Python.
"""

ARCHITECTURE_TOPICS = [
    {
        "id": "project-layout",
        "title": "Современная структура Python-проекта (src-layout)",
        "icon": "folder-tree",
        "category": "architecture",
        "summary": "Золотой стандарт структуры проектов на Python 3.12-3.13 с использованием src/ layout, pyproject.toml и uv/poetry.",
        "content": """
### Почему `src-layout` стал стандартом?
Использование папки `src/` гарантирует, что тесты и скрипты импортируют установленный пакет, а не локальную директорию в корне проекта. Это предотвращает случайные ошибки импорта в production.

#### Рекомендуемая файловая структура:
```text
my_awesome_project/
├── .github/
│   └── workflows/
│       └── tests.yml            # CI/CD автоматизация
├── src/
│   └── my_project/
│       ├── __init__.py          # Версия и экспорт публичного API
│       ├── main.py              # Точка входа в приложение
│       ├── config.py            # Настройки (Pydantic Settings / .env)
│       ├── core/                # Ядро, бизнес-логика, доменные модели
│       │   ├── __init__.py
│       │   ├── models.py        # Dataclasses / Pydantic модели
│       │   └── exceptions.py    # Пользовательские исключения
│       ├── services/            # Сервисный слой (бизнес-операции)
│       │   ├── __init__.py
│       │   └── user_service.py
│       ├── db/                  # База данных (SQLAlchemy, SQLite)
│       │   ├── __init__.py
│       │   ├── session.py       # Подключение и сессии
│       │   └── repository.py    # Доступ к данным
│       └── ui/ или api/         # Слой представления (GUI или REST API)
│           ├── __init__.py
│           └── routes.py
├── tests/                       # Тесты (pytest)
│   ├── conftest.py              # Фикстуры
│   ├── test_services.py
│   └── test_api.py
├── assets/                      # Иконки, картинки, стили
├── .env.example                 # Пример переменных окружения
├── .gitignore                   # Игнорирование __pycache__, .venv
├── pyproject.toml               # Конфигурация проекта, зависимостей и линтеров
└── README.md                    # Описание и запуск
```

#### Пример современного `pyproject.toml` (стандарт PEP 621):
```toml
[project]
name = "my-awesome-project"
version = "0.1.0"
description = "Профессиональное приложение на Python"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.7.0",
    "pydantic-settings>=2.2.0",
    "rich>=13.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.4.0",
    "mypy>=1.9.0",
]

[project.scripts]
my-app = "my_project.main:main"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```
"""
    },
    {
        "id": "clean-architecture",
        "title": "Чистая Архитектура (Clean Architecture) и Service-Repository",
        "icon": "layers",
        "category": "architecture",
        "summary": "Разделение ответственности: Domain, Repository, Service и Presentation слои для масштабируемых приложений.",
        "content": """
### Принципы чистой архитектуры на Python
Главное правило: **зависимости направлены внутрь**. Внутренние слои (бизнес-логика) ничего не знают о внешних (база данных, GUI, веб-фреймворк).

```
   ┌────────────────────────────────────────────────────────┐
   │             Presentation Layer (UI, API, CLI)          │
   ├────────────────────────────────────────────────────────┤
   │             Service Layer (Бизнес-сценарии)             │
   ├────────────────────────────────────────────────────────┤
   │             Repository Layer (Хранилище / БД)          │
   ├────────────────────────────────────────────────────────┤
   │             Domain Entities (Модели, Dataclasses)       │
   └────────────────────────────────────────────────────────┘
```

#### 1. Доменный слой (Сущности):
```python
# src/core/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class Task:
    id: Optional[int]
    title: str
    is_completed: bool = False
    created_at: Optional[datetime] = None
```

#### 2. Слой интерфейса репозитория (Абстракция):
```python
# src/db/repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from ..core.models import Task

class TaskRepository(ABC):
    @abstractmethod
    def add(self, task: Task) -> Task:
        pass

    @abstractmethod
    def get_all(self) -> List[Task]:
        pass

    @abstractmethod
    def mark_completed(self, task_id: int) -> bool:
        pass
```

#### 3. Сервисный слой (Бизнес-логика):
```python
# src/services/task_service.py
from ..core.models import Task
from ..db.repository import TaskRepository

class TaskService:
    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    def create_new_task(self, title: str) -> Task:
        clean_title = title.strip()
        if len(clean_title) < 3:
            raise ValueError("Название задачи должно содержать минимум 3 символа")
        task = Task(id=None, title=clean_title)
        return self._repo.add(task)

    def complete_task(self, task_id: int) -> bool:
        return self._repo.mark_completed(task_id)
```

**Преимущества**: Вы можете легко заменить SQLite на PostgreSQL, или PySide6 на FastAPI, не трогая ни единой строчки в `TaskService`!
"""
    },
    {
        "id": "async-concurrency",
        "title": "Асинхронность (AsyncIO) vs Потоки (Threading) vs Процессы",
        "icon": "cpu",
        "category": "architecture",
        "summary": "Когда использовать async/await, ThreadPoolExecutor или ProcessPoolExecutor, и как подружить их с GUI.",
        "content": """
### Сравнительная таблица многозадачности в Python

| Метод | Идеально для | Блокируется GIL? | Накладные расходы | Безопасность |
|---|---|---|---|---|
| **AsyncIO** (`async/await`) | Сетевые запросы, Web/API, чат-боты, тысячи соединений | Да (один поток) | Минимальные (микросекунды) | Высокая (кооперативная) |
| **Threading** (`threading`, `ThreadPoolExecutor`) | Файловый I/O, долгие сетевые операции, фоновые задачи в GUI | Да | Средние (~1-2 МБ на поток) | Требует мьютексов (`Lock`) |
| **Multiprocessing** (`ProcessPoolExecutor`) | CPU-heavy вычисления (ML, обработка видео, парсинг больших данных) | **Нет (каждый процесс имеет свой GIL)** | Высокие (память процесса) | Изолированная память |

---

### Практические паттерны:

#### 1. Современный AsyncIO с `TaskGroup` (Python 3.11+):
```python
import asyncio
import aiohttp

async def fetch_status(url: str, session: aiohttp.ClientSession) -> dict:
    async with session.get(url, timeout=5) as response:
        return {"url": url, "status": response.status}

async def check_all_sites(urls: list[str]):
    async with aiohttp.ClientSession() as session:
        # TaskGroup автоматически отменяет остальные задачи при ошибке в одной!
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(fetch_status(url, session)) for url in urls]
    
    return [task.result() for task in tasks]
```

#### 2. Фоновые задачи в GUI без зависания интерфейса:
В GUI-приложениях (PySide6 / PyQt / Tkinter) **любая долгая операция в основном потоке замораживает окно**.

```python
# Безопасный запуск в пуле потоков с возвратом в UI
import concurrent.futures
from PySide6.QtCore import QObject, Signal, Slot

class WorkerSignals(QObject):
    finished = Signal(object)
    error = Signal(str)

def run_heavy_task_in_background(signals: WorkerSignals, data: str):
    try:
        # Тяжелые вычисления или скачивание
        import time
        time.sleep(2)
        result = f"Обработано: {data}"
        signals.finished.emit(result)
    except Exception as e:
        signals.error.emit(str(e))
```
"""
    },
    {
        "id": "design-patterns",
        "title": "Паттерны проектирования на Python (GoF & Pythonic)",
        "icon": "puzzle",
        "category": "architecture",
        "summary": "Singleton, Dependency Injection, Factory, Observer, Strategy и Decorator на реальных примерах.",
        "content": """
### 1. Паттерн «Фабрика» (Factory Pattern)
```python
from abc import ABC, abstractmethod
from typing import Literal

class Exporter(ABC):
    @abstractmethod
    def export(self, data: dict) -> bytes: ...

class JsonExporter(Exporter):
    def export(self, data: dict) -> bytes:
        import json
        return json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')

class CsvExporter(Exporter):
    def export(self, data: dict) -> bytes:
        import csv, io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)
        return output.getvalue().encode('utf-8')

class ExporterFactory:
    @staticmethod
    def get_exporter(format_type: Literal['json', 'csv']) -> Exporter:
        if format_type == 'json':
            return JsonExporter()
        elif format_type == 'csv':
            return CsvExporter()
        raise ValueError(f"Неизвестный формат: {format_type}")
```

### 2. Паттерн «Наблюдатель» / Event Bus (Observer Pattern)
```python
from typing import Callable, Dict, List

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, handler: Callable):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(handler)

    def emit(self, event_name: str, **payload):
        for handler in self._subscribers.get(event_name, []):
            handler(**payload)

# Использование
events = EventBus()
events.subscribe("user_registered", lambda email, **kw: print(f"Отправка письма на {email}"))
events.subscribe("user_registered", lambda **kw: print("Запись метрики в аналитику"))

events.emit("user_registered", email="dev@example.com", username="alex")
```
"""
    },
    {
        "id": "type-hints-pydantic",
        "title": "Строгая типизация (Type Hints) и Pydantic v2",
        "icon": "shield-check",
        "category": "architecture",
        "summary": "Как использовать мощь Python 3.12+ типизации, Generic, Pydantic v2 и Dataclasses для защиты от багов.",
        "content": """
### Зачем нужна строгая типизация?
Python остается динамическим языком, но современные IDE (VS Code, PyCharm, Antigravity) и статические анализаторы (`mypy`, `pyright`, `ruff`) находят 90% ошибок до запуска приложения!

#### Современные аннотации типов (Python 3.10+):
```python
from typing import TypeVar, Generic, Optional, Literal, Self

# Union через вертикальную черту вместо Union[int, None]
def find_user(user_id: int) -> str | None:
    return "Alex" if user_id == 1 else None

# Literal для строгих перечислений
Status = Literal["pending", "active", "cancelled"]

def set_status(status: Status) -> None:
    print(f"Новый статус: {status}")

# Self для методов, возвращающих текущий экземпляр (Method Chaining)
class QueryBuilder:
    def __init__(self):
        self._query = []

    def select(self, field: str) -> Self:
        self._query.append(f"SELECT {field}")
        return self

    def from_table(self, table: str) -> Self:
        self._query.append(f"FROM {table}")
        return self
```

#### Pydantic v2: Валидация данных и Настройки приложения:
```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    app_name: str = "PyForge App"
    debug: bool = False
    database_url: str = "sqlite:///./app.db"
    secret_key: str = Field(min_length=16)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Валидация входных данных пользователя
class CreateUserDto(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    age: int = Field(ge=18, le=120)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Имя пользователя должно содержать только буквы и цифры")
        return v.lower()
```
"""
    }
]
