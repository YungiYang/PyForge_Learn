"""
Шаблоны готовых проектов под ключ для генератора проектов (Scaffolder).
Каждый шаблон содержит полноценную рабочую структуру файлов и готовый код.
"""

PROJECT_TEMPLATES = {
    "pyside6_app": {
        "id": "pyside6_app",
        "name": "PySide6 Desktop Application",
        "category": "desktop",
        "description": "Полнофункциональное десктопное приложение на PySide6 (Qt) с фоновыми потоками, красивым интерфейсом, базой данных SQLite и скриптом сборки в .EXE.",
        "icon": "monitor",
        "files": {
            "pyproject.toml": '''[project]
name = "pyside6-pro-app"
version = "1.0.0"
description = "Modern PySide6 Desktop Application"
dependencies = [
    "PySide6>=6.6.0",
    "pydantic>=2.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pyinstaller>=6.5.0",
    "ruff>=0.4.0",
]
''',
            "requirements.txt": '''PySide6>=6.6.0
pydantic>=2.7.0
pyinstaller>=6.5.0
pytest>=8.0.0
''',
            "README.md": '''# PySide6 Modern Desktop Application

### Запуск в режиме разработки:
```bash
python src/main.py
```

### Сборка в автономный .EXE:
```bash
python build_exe.py
```
Исполняемый файл появится в папке `dist/`.
''',
            "src/main.py": '''import sys
import time
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QListWidget, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, QObject

class WorkerSignals(QObject):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

class BackgroundWorker(QThread):
    def __init__(self, task_name: str):
        super().__init__()
        self.task_name = task_name
        self.signals = WorkerSignals()

    def run(self):
        try:
            for i in range(1, 101):
                time.sleep(0.02)  # Имитация длительной операции
                self.signals.progress.emit(i)
            self.signals.finished.emit(f"Задача '{self.task_name}' успешно выполнена!")
        except Exception as e:
            self.signals.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Modern Desktop Studio")
        self.resize(650, 500)
        self.worker = None

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title_label = QLabel("🚀 Панель управления PySide6")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)

        # Поле ввода и кнопка добавления
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Введите название задачи...")
        self.add_btn = QPushButton("Добавить задачу")
        self.add_btn.clicked.connect(self._add_task)
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.add_btn)
        layout.addLayout(input_layout)

        # Список задач
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)

        # Прогресс-бар фоновой задачи
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Кнопка запуска тяжелой операции в потоке
        self.run_heavy_btn = QPushButton("Запустить тяжелую фоновую обработку")
        self.run_heavy_btn.setObjectName("primaryBtn")
        self.run_heavy_btn.clicked.connect(self._start_heavy_task)
        layout.addWidget(self.run_heavy_btn)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QWidget { color: #f8fafc; font-family: 'Segoe UI', sans-serif; }
            QLabel#titleLabel { font-size: 20px; font-weight: bold; color: #38bdf8; }
            QLineEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                color: #ffffff;
            }
            QLineEdit:focus { border-color: #38bdf8; }
            QListWidget {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item { padding: 8px; border-radius: 6px; }
            QListWidget::item:selected { background-color: #38bdf8; color: #0f172a; font-weight: bold; }
            QPushButton {
                background-color: #334155;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 600;
                color: #ffffff;
            }
            QPushButton:hover { background-color: #475569; }
            QPushButton#primaryBtn {
                background-color: #0284c7;
                color: white;
            }
            QPushButton#primaryBtn:hover { background-color: #0369a1; }
            QProgressBar {
                border: 1px solid #334155;
                border-radius: 6px;
                text-align: center;
                background-color: #1e293b;
                height: 20px;
            }
            QProgressBar::chunk { background-color: #38bdf8; border-radius: 5px; }
        """)

    def _add_task(self):
        text = self.task_input.text().strip()
        if text:
            self.task_list.addItem(f"📌 {text}")
            self.task_input.clear()

    def _start_heavy_task(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Внимание", "Фоновая задача уже выполняется!")
            return

        self.run_heavy_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        self.worker = BackgroundWorker("Обработка данных")
        self.worker.signals.progress.connect(self.progress_bar.setValue)
        self.worker.signals.finished.connect(self._on_task_finished)
        self.worker.signals.error.connect(self._on_task_error)
        self.worker.start()

    def _on_task_finished(self, msg: str):
        self.run_heavy_btn.setEnabled(True)
        self.task_list.addItem(f"✅ {msg}")
        QMessageBox.information(self, "Готово", msg)

    def _on_task_error(self, err: str):
        self.run_heavy_btn.setEnabled(True)
        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {err}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
''',
            "build_exe.py": '''import PyInstaller.__main__
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PyInstaller.__main__.run([
    str(ROOT / "src" / "main.py"),
    "--name=PySide6ProApp",
    "--windowed",
    "--noconfirm",
    "--clean",
])
print("Сборка успешно завершена! Исполняемый файл находится в папке dist/")
'''
        }
    },

    "fastapi_backend": {
        "id": "fastapi_backend",
        "name": "FastAPI Clean Architecture Backend",
        "category": "web",
        "description": "Масштабируемый REST API бэкенд на FastAPI с валидацией Pydantic v2, базой данных SQLite (SQLAlchemy 2.0), CORS, Swagger UI и тестами pytest.",
        "icon": "zap",
        "files": {
            "pyproject.toml": '''[project]
name = "fastapi-clean-api"
version = "1.0.0"
description = "FastAPI Scalable REST API"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.29.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.2.0",
    "sqlalchemy>=2.0.0",
    "aiosqlite>=0.20.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
    "ruff>=0.4.0",
]
''',
            "requirements.txt": '''fastapi>=0.110.0
uvicorn[standard]>=0.29.0
pydantic>=2.7.0
pydantic-settings>=2.2.0
sqlalchemy>=2.0.0
aiosqlite>=0.20.0
httpx>=0.27.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
''',
            ".env.example": '''APP_NAME="FastAPI Enterprise API"
DEBUG=True
DATABASE_URL="sqlite+aiosqlite:///./data.db"
SECRET_KEY="super-secret-key-change-in-production"
''',
            "README.md": '''# FastAPI Clean Architecture REST API

### Запуск сервера:
```bash
uvicorn src.main:app --reload --port 8000
```
- Документация Swagger UI: http://127.0.0.1:8000/docs
- Документация ReDoc: http://127.0.0.1:8000/redoc

### Запуск тестов:
```bash
pytest
```
''',
            "src/config.py": '''from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "FastAPI Clean API"
    debug: bool = True
    database_url: str = "sqlite+aiosqlite:///./data.db"
    secret_key: str = "default-secret-key-must-be-changed"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
''',
            "src/models.py": '''from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, func

class Base(DeclarativeBase):
    pass

class ItemDB(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(String(500), default="")
    price: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

# Pydantic Schemas
class ItemCreate(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    description: Optional[str] = ""
    price: float = Field(gt=0)

class ItemResponse(ItemCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
''',
            "src/db.py": '''from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.config import settings
from src.models import Base

engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session
''',
            "src/routes.py": '''from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db import get_db
from src.models import ItemDB, ItemCreate, ItemResponse

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("", response_model=List[ItemResponse])
async def list_items(db: AsyncSession = Depends(get_db)):
    stmt = select(ItemDB).order_by(ItemDB.id.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item_in: ItemCreate, db: AsyncSession = Depends(get_db)):
    item = ItemDB(**item_in.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(ItemDB, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    return item
''',
            "src/main.py": '''from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.db import init_db
from src.routes import router as items_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Действия при старте приложения
    await init_db()
    yield
    # Действия при завершении приложения

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items_router)

@app.get("/")
async def root():
    return {"message": "API работает в штатном режиме", "docs": "/docs"}
''',
            "tests/test_api.py": '''import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
'''
        }
    },

    "customtkinter_app": {
        "id": "customtkinter_app",
        "name": "CustomTkinter Lightweight GUI",
        "category": "desktop",
        "description": "Легковесное, красивое десктопное приложение с автоматической поддержкой темной и светлой темы, вкладками и низким потреблением ресурсов.",
        "icon": "layout",
        "files": {
            "requirements.txt": '''customtkinter>=5.2.0
pillow>=10.0.0
pyinstaller>=6.5.0
''',
            "src/main.py": '''import customtkinter as ctk
import tkinter.messagebox as messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CustomTkinter Modern Studio")
        self.geometry("700x480")
        self.minsize(600, 400)

        # Конфигурация сетки
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Боковая панель
        self.sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="PyForge CTk", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_1 = ctk.CTkButton(self.sidebar, text="Главная", command=lambda: self.show_page("home"))
        self.btn_1.grid(row=1, column=0, padx=20, pady=10)

        self.btn_2 = ctk.CTkButton(self.sidebar, text="Настройки", command=lambda: self.show_page("settings"))
        self.btn_2.grid(row=2, column=0, padx=20, pady=10)

        # Переключатель темы
        self.theme_switch = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"], command=self.change_theme)
        self.theme_switch.grid(row=5, column=0, padx=20, pady=20)

        # Основная область контента
        self.main_frame = ctk.CTkFrame(self, corner_radius=12)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.page_title = ctk.CTkLabel(self.main_frame, text="Добро пожаловать!", font=ctk.CTkFont(size=22, weight="bold"))
        self.page_title.pack(padx=20, pady=(30, 10))

        self.entry = ctk.CTkEntry(self.main_frame, placeholder_text="Введите текст для обработки...", width=350)
        self.entry.pack(padx=20, pady=15)

        self.action_btn = ctk.CTkButton(self.main_frame, text="Выполнить действие", command=self.on_action)
        self.action_btn.pack(padx=20, pady=10)

        self.output_textbox = ctk.CTkTextbox(self.main_frame, height=180)
        self.output_textbox.pack(padx=20, pady=20, fill="both", expand=True)

    def change_theme(self, new_theme: str):
        ctk.set_appearance_mode(new_theme)

    def show_page(self, page_name: str):
        self.output_textbox.insert("end", f"Переход на страницу: {page_name}\\n")

    def on_action(self):
        text = self.entry.get()
        if not text:
            messagebox.showwarning("Внимание", "Поле ввода не должно быть пустым!")
            return
        self.output_textbox.insert("end", f"Обработано: {text.upper()}\\n")
        self.entry.delete(0, "end")

if __name__ == "__main__":
    app = App()
    app.mainloop()
'''
        }
    },

    "aiogram_bot": {
        "id": "aiogram_bot",
        "name": "Aiogram 3 Modern Telegram Bot",
        "category": "bots",
        "description": "Современный асинхронный бот на базе Aiogram 3 с разделением по роутерам, FSM-машиной состояний и Inline-клавиатурами.",
        "icon": "message-square",
        "files": {
            "requirements.txt": '''aiogram>=3.4.0
pydantic-settings>=2.2.0
aiohttp>=3.9.0
''',
            ".env.example": '''BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
ADMIN_ID="12345678"
''',
            "src/config.py": '''from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str
    admin_id: int = 0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

config = Settings()
''',
            "src/handlers.py": '''from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

class FeedbackForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_message = State()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Оставить отзыв", callback_data="start_feedback")
    builder.button(text="ℹ️ Помощь", callback_data="show_help")
    builder.adjust(1)

    await message.answer(
        f"Здравствуйте, {message.from_user.first_name}!\\n"
        "Я демонстрационный бот на Aiogram 3. Выберите действие:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data == "start_feedback")
async def start_feedback_flow(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(FeedbackForm.waiting_for_name)
    await callback.message.answer("Как вас зовут?")
    await callback.answer()

@router.message(FeedbackForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(FeedbackForm.waiting_for_message)
    await message.answer("Отлично! Теперь напишите ваше сообщение:")

@router.message(FeedbackForm.waiting_for_message)
async def process_feedback_message(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get("name")
    feedback = message.text
    await state.clear()

    await message.answer(f"Спасибо, {name}! Ваш отзыв принят:\\n\\n«{feedback}»")
''',
            "src/main.py": '''import asyncio
import logging
from aiogram import Bot, Dispatcher
from src.config import config
from src.handlers import router as main_router

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    dp.include_router(main_router)

    logging.info("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
'''
        }
    },

    "typer_cli": {
        "id": "typer_cli",
        "name": "Typer + Rich CLI Application",
        "category": "cli",
        "description": "Красивая и быстрая консольная утилита с автодополнением, цветным форматированием, спиннерами и таблицами Rich.",
        "icon": "terminal",
        "files": {
            "requirements.txt": '''typer[all]>=0.12.0
rich>=13.7.0
''',
            "src/main.py": '''import typer
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="🚀 Профессиональная CLI-утилита")
console = Console()

@app.command()
def hello(name: str = typer.Option("Пользователь", "--name", "-n", help="Имя для приветствия")):
    """Выводит красивое приветствие"""
    panel = Panel(
        f"[bold green]Добро пожаловать, {name}![/bold green]\\nВы используете современный CLI стек на [cyan]Typer + Rich[/cyan].",
        title="PyForge CLI",
        border_style="cyan"
    )
    console.print(panel)

@app.command()
def scan(target: str = typer.Argument("localhost", help="Цель сканирования")):
    """Имитация сканирования с красивым спиннером и таблицей"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=f"Сканирование {target}...", total=None)
        time.sleep(1.5)

    table = Table(title=f"Результаты сканирования: {target}")
    table.add_column("Порт / Сервис", style="cyan", no_wrap=True)
    table.add_column("Протокол", style="magenta")
    table.add_column("Статус", style="green")

    table.add_row("80 (HTTP)", "TCP", "[green]OPEN[/green]")
    table.add_row("443 (HTTPS)", "TCP", "[green]OPEN[/green]")
    table.add_row("8000 (FastAPI)", "TCP", "[green]OPEN[/green]")
    table.add_row("22 (SSH)", "TCP", "[red]CLOSED[/red]")

    console.print(table)

if __name__ == "__main__":
    app()
'''
        }
    }
}
