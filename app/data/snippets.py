"""
Библиотека готовых практических сниппетов для Python 3.10-3.13.
"""

SNIPPETS_DATA = [
    # ------------------ ASYNCIO ------------------
    {
        "id": "async-semaphore-rate-limit",
        "title": "Ограничение параллельных запросов (Semaphore / Rate Limiting)",
        "category": "AsyncIO",
        "tags": ["asyncio", "semaphore", "network", "aiohttp"],
        "description": "Как отправить 10 000 сетевых запросов, ограничив параллельность, например, не более 10 одновременных соединений.",
        "code": '''import asyncio
import aiohttp

async def fetch_worker(sem: asyncio.Semaphore, url: str, session: aiohttp.ClientSession) -> dict:
    async with sem:  # Не более 10 одновременных задач
        try:
            async with session.get(url, timeout=5) as response:
                data = await response.text()
                return {"url": url, "status": response.status, "length": len(data)}
        except Exception as e:
            return {"url": url, "error": str(e)}

async def main():
    semaphore = asyncio.Semaphore(10)  # Лимит параллельных запросов
    urls = [f"https://httpbin.org/get?item={i}" for i in range(50)]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_worker(semaphore, url, session) for url in urls]
        results = await asyncio.gather(*tasks)

    print(f"Успешно обработано {len(results)} запросов!")

if __name__ == "__main__":
    asyncio.run(main())
'''
    },
    {
        "id": "async-retry-decorator",
        "title": "Асинхронный декоратор повтора с экспоненциальной задержкой (Retry)",
        "category": "AsyncIO",
        "tags": ["asyncio", "decorator", "retry", "network"],
        "description": "Автоматический повтор упавшей функции при сетевых сбоях с увеличением времени ожидания (Exponential Backoff).",
        "code": '''import asyncio
import functools
import logging

def async_retry(max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logging.error(f"Функция {func.__name__} упала после {max_retries} попыток: {e}")
                        raise
                    logging.warning(f"Попытка {attempt} завершилась ошибкой: {e}. Повтор через {delay:.1f}с...")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator

# Пример использования:
@async_retry(max_retries=3, initial_delay=0.5)
async def unstable_network_call():
    import random
    if random.random() < 0.7:
        raise ConnectionError("Сбой сети")
    return "Успех!"
'''
    },

    # ------------------ ФАЙЛЫ И СИСТЕМА ------------------
    {
        "id": "pathlib-recipes",
        "title": "Профессиональная работа с путями и файлами через Pathlib",
        "category": "Файлы и ОС",
        "tags": ["pathlib", "files", "os", "json"],
        "description": "Современная работа с файловой системой без устаревшего os.path.",
        "code": '''from pathlib import Path
import json

# Получение пути к директории текущего скрипта
PROJECT_ROOT = Path(__file__).resolve().parent

# Безопасное создание вложенных директорий
logs_dir = PROJECT_ROOT / "logs" / "daily"
logs_dir.mkdir(parents=True, exist_ok=True)

# Поиск всех .json файлов во всех подпапках
config_files = list(PROJECT_ROOT.glob("**/*.json"))

# Атомарная запись в файл (защита от повреждения при сбое питания)
data_file = PROJECT_ROOT / "data.json"
temp_file = data_file.with_suffix(".tmp")

sample_data = {"app": "PyForge", "version": "1.0.0", "settings": {"theme": "dark"}}
temp_file.write_text(json.dumps(sample_data, indent=2, ensure_ascii=False), encoding="utf-8")
temp_file.replace(data_file)  # Атомарная замена

# Чтение файла одной строкой
content = data_file.read_text(encoding="utf-8")
print(f"Размер файла: {data_file.stat().st_size} байт")
'''
    },
    {
        "id": "file-downloader-progress",
        "title": "Скачивание больших файлов с прогресс-баром",
        "category": "Сеть",
        "tags": ["requests", "streaming", "download", "progress"],
        "description": "Потоковое скачивание файлов (streaming) без переполнения оперативной памяти.",
        "code": '''import requests
from pathlib import Path
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

def download_file_with_progress(url: str, destination: Path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))

    with Progress(
        TextColumn("[bold blue]{task.fields[filename]}"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("download", total=total_size, filename=destination.name)
        
        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 64):  # 64 KB куски
                if chunk:
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))

    print(f"Скачивание завершено: {destination}")
'''
    },

    # ------------------ БЕЗОПАСНОСТЬ И ХЭШИ ------------------
    {
        "id": "security-password-hashing",
        "title": "Безопасное хэширование паролей и генерация токенов",
        "category": "Безопасность",
        "tags": ["security", "passwords", "tokens", "hashlib", "secrets"],
        "description": "Хэширование с солью (PBKDF2/SHA256) и криптографически стойкая генерация API-ключей.",
        "code": '''import hashlib
import os
import secrets

def hash_password(password: str) -> str:
    \"\"\"Хэширование пароля алгоритмом PBKDF2-HMAC-SHA256 с индивидуальной солью\"\"\"
    salt = os.urandom(32)  # Случайная криптографическая соль
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}:{key.hex()}"

def verify_password(stored_hash: str, provided_password: str) -> bool:
    \"\"\"Проверка соответствия введенного пароля\"\"\"
    salt_hex, key_hex = stored_hash.split(":")
    salt = bytes.fromhex(salt_hex)
    key = bytes.fromhex(key_hex)
    new_key = hashlib.pbkdf2_hmac("sha256", provided_password.encode("utf-8"), salt, 100_000)
    # secrets.compare_digest защищает от timing attacks (атак по времени)
    return secrets.compare_digest(key, new_key)

def generate_api_key(prefix: str = "sk_live_") -> str:
    \"\"\"Генерация надежного случайного API ключа\"\"\"
    return f"{prefix}{secrets.token_urlsafe(32)}"

# Пример использования:
hashed = hash_password("SuperSecret123!")
assert verify_password(hashed, "SuperSecret123!") is True
assert verify_password(hashed, "WrongPassword") is False
print(f"Хэш: {hashed}")
print(f"Сгенерированный API-ключ: {generate_api_key()}")
'''
    },

    # ------------------ ДЕКОРАТОРЫ И МАГИЯ ------------------
    {
        "id": "timing-profiler-decorator",
        "title": "Декоратор замера времени выполнения функции",
        "category": "Паттерны & Утилиты",
        "tags": ["decorator", "profiling", "timing", "performance"],
        "description": "Измерение точного времени работы функции (синхронной и асинхронной).",
        "code": '''import time
import functools
import inspect

def timeit(func):
    \"\"\"Универсальный декоратор замера времени для синхронных и асинхронных функций\"\"\"
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            print(f"⏱️ Async '{func.__name__}' выполнена за {elapsed * 1000:.2f} мс")
            return result
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            print(f"⏱️ Sync '{func.__name__}' выполнена за {elapsed * 1000:.2f} мс")
            return result
        return sync_wrapper

# Пример:
@timeit
def heavy_calculation():
    return sum(i * i for i in range(1_000_000))

heavy_calculation()
'''
    },
    {
        "id": "singleton-threadsafe",
        "title": "Потокобезопасный Синглтон (Thread-safe Singleton)",
        "category": "Паттерны & Утилиты",
        "tags": ["singleton", "threading", "oop", "patterns"],
        "description": "Идеальная реализация паттерна Одиночка с двойной проверкой блокировки (Double-Checked Locking).",
        "code": '''import threading

class SingletonMeta(type):
    \"\"\"Потокобезопасный метакласс Singleton\"\"\"
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

class DatabaseManager(metaclass=SingletonMeta):
    def __init__(self):
        self.connection_string = "sqlite:///app.db"
        print("Инициализация подключения к БД (должно произойти только 1 раз!)")

# Проверка
db1 = DatabaseManager()
db2 = DatabaseManager()
assert db1 is db2
print(f"Один и тот же объект: {db1 is db2}")
'''
    },
    {
        "id": "modern-pattern-matching",
        "title": "Pattern Matching (match / case) в Python 3.10+",
        "category": "Python Core",
        "tags": ["match-case", "python310", "patterns", "clean-code"],
        "description": "Элегантная обработка сложных вложенных структур, команд и ответов API без каскадов if/elif.",
        "code": '''from dataclasses import dataclass

@dataclass
class Command:
    action: str
    target: str
    params: dict

def handle_event(event: dict | Command):
    match event:
        # Сопоставление со словарем
        case {"type": "message", "text": str(text), "user_id": int(uid)}:
            print(f"Сообщение от пользователя {uid}: {text}")

        case {"type": "status_change", "status": "online" | "away" as st}:
            print(f"Статус изменен на {st}")

        # Сопоставление с экземпляром класса
        case Command(action="delete", target=target, params={"force": True}):
            print(f"Принудительное удаление объекта {target}!")

        case Command(action=action, target=target):
            print(f"Команда '{action}' над '{target}'")

        # Обработка любых других случаев
        case _:
            print("Неизвестный формат события")

handle_event({"type": "message", "text": "Привет всем!", "user_id": 42})
handle_event(Command(action="delete", target="user_123", params={"force": True}))
'''
    }
]
