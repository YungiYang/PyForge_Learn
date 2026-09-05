"""
Базы данных, ORM и системы хранения данных в Python.
"""

DATABASES_TOPICS = [
    {
        "id": "sqlalchemy2",
        "title": "SQLAlchemy 2.0 (Современный Declarative ORM)",
        "icon": "database",
        "category": "databases",
        "summary": "Новейший стандарт работы с реляционными БД: Mapped, mapped_column, асинхронные сессии и типизация.",
        "content": """
### Что изменилось в SQLAlchemy 2.0?
SQLAlchemy 2.0 перешла на современный синтаксис с полной поддержкой Type Hints (`Mapped[...]`, `mapped_column`), unified query syntax `select(...)`, и первоклассной поддержкой `asyncio`.

#### 1. Определение моделей с строгой типизацией:
```python
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey, DateTime, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Связь один-ко-многим
    posts: Mapped[List["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")
```

#### 2. Асинхронная сессия (AsyncSession) и запросы:
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# SQLite async driver: aiosqlite, PostgreSQL: asyncpg
DATABASE_URL = "sqlite+aiosqlite:///./app.db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def create_user_and_post(username: str, email: str, post_title: str):
    async with AsyncSessionFactory() as session:
        async with session.begin():
            new_user = User(username=username, email=email)
            new_post = Post(title=post_title, content="Контент первого поста", author=new_user)
            session.add_all([new_user, new_post])
            # commit происходит автоматически при выходе из блока session.begin()

async def get_user_with_posts(user_id: int):
    async with AsyncSessionFactory() as session:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
```
"""
    },
    {
        "id": "sqlite-best-practices",
        "title": "SQLite3: Тонкая настройка и WAL режим",
        "icon": "hard-drive",
        "category": "databases",
        "summary": "Как выжать максимум производительности и надежности из встроенного SQLite в многопоточных приложениях.",
        "content": """
### Почему SQLite — лучший выбор для 95% десктопных приложений?
- Не требует установки сервера БД
- Вся база данных хранится в одном компактном файле `.db`
- Поддерживает транзакции (ACID), JSON-поля, полнотекстовый поиск (FTS5)

#### Рецепт надежного подключения (WAL mode + timeout):
По умолчанию SQLite блокирует всю базу при записи. Включение режима **WAL (Write-Ahead Logging)** позволяет **одновременно читать и писать** без взаимных блокировок!

```python
import sqlite3
from contextlib import contextmanager

DB_PATH = "application.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(
        DB_PATH, 
        timeout=10.0,            # Ждать до 10 сек при блокировке, а не падать сразу
        check_same_thread=False  # Разрешить использование между потоками (при контроле блокировок)
    )
    # Включаем WAL режим для параллельного чтения и быстрой записи
    conn.execute("PRAGMA journal_mode = WAL;")
    # Включаем внешние ключи (foreign keys по умолчанию выключены в sqlite!)
    conn.execute("PRAGMA foreign_keys = ON;")
    # Возвращать строки как словари (dict-like)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db_transaction():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Использование
with db_transaction() as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT);")
    cursor.execute("INSERT INTO notes (title) VALUES (?);", ("Моя первая заметка",))
```
"""
    },
    {
        "id": "alembic-migrations",
        "title": "Миграции базы данных с Alembic",
        "icon": "git-branch",
        "category": "databases",
        "summary": "Как безопасно изменять схему базы данных без потери данных в продакшене.",
        "content": """
### Пошаговая настройка Alembic:

1. **Инициализация проекта миграций**:
```bash
pip install alembic
alembic init alembic
```

2. **Настройка `alembic/env.py` для автогенерации**:
Импортируйте ваш `Base` с моделями в `env.py`:
```python
# alembic/env.py
from src.db.session import Base  # Ваш DeclarativeBase
from src.core.models import *    # Все модели должны быть импортированы

target_metadata = Base.metadata
```

3. **Команды управления миграциями**:
```bash
# Создать автоматическую миграцию на основе изменений в моделях
alembic revision --autogenerate -m "Add user profile table"

# Применить все миграции к текущей БД
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1
```
"""
    },
    {
        "id": "redis-caching",
        "title": "Redis: Кэширование, Сессии и Очереди",
        "icon": "server",
        "category": "databases",
        "summary": "Использование Redis в оперативной памяти для кэширования ответов, хранения токенов и ограничения частоты запросов.",
        "content": """
### Пример кэширования с помощью `redis-py`:
```python
import redis
import json
from typing import Optional

# Подключение к Redis (локальный или облачный)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_user_cached(user_id: int) -> dict:
    cache_key = f"user:{user_id}"
    
    # 1. Проверяем кэш
    cached_data = r.get(cache_key)
    if cached_data:
        print("Данные получены из Redis кэша ⚡")
        return json.loads(cached_data)
    
    # 2. Если нет в кэше — читаем из тяжелой БД
    print("Чтение из базы данных...")
    user_data = {"id": user_id, "name": "Alex", "role": "admin"}
    
    # 3. Сохраняем в кэш с TTL (временем жизни) 60 секунд
    r.setex(cache_key, 60, json.dumps(user_data))
    return user_data
```
"""
    }
]
