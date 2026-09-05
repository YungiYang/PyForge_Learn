"""
Полный справочник по всем популярным фреймворкам для создания приложений на Python.
"""

FRAMEWORKS_DATA = [
    # ------------------- DESKTOP GUI -------------------
    {
        "id": "pyside6",
        "name": "PySide6 (Qt for Python)",
        "category": "desktop",
        "icon": "monitor",
        "badge": "Industry Standard",
        "description": "Официальная библиотека от The Qt Company для создания мощных, нативных и красивых десктопных приложений корпоративного уровня.",
        "pros": [
            "Огромный набор виджетов, графиков, мультимедиа и веб-рендеринга",
            "Поддержка Qt Designer (визуальный редактор интерфейсов)",
            "Мощная система стилизации через QSS (аналог CSS) и QML/Qt Quick",
            "Высокая производительность (C++ ядро)"
        ],
        "cons": [
            "Большой размер итогового .exe сборщика (~50-80 МБ)",
            "Крутая кривая обучения (сигналы/слоты, потоки QThread, жизненный цикл)"
        ],
        "install": "pip install PySide6 PySide6-Fluent-Widgets",
        "quickstart": '''import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Modern App")
        self.resize(400, 300)

        layout = QVBoxLayout()
        self.label = QLabel("Привет из PySide6!", alignment=Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: #3b82f6;")
        
        btn = QPushButton("Нажми меня")
        btn.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; border-radius: 8px; padding: 10px; font-size: 14px; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        btn.clicked.connect(self.on_button_clicked)

        layout.addWidget(self.label)
        layout.addWidget(btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_button_clicked(self):
        self.label.setText("Кнопка успешно нажата! 🎉")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
'''
    },
    {
        "id": "customtkinter",
        "name": "CustomTkinter",
        "category": "desktop",
        "icon": "layout",
        "badge": "Beginner Friendly & Modern",
        "description": "Современная надстройка над стандартным Tkinter с автоматической поддержкой темной/светлой темы, скругленными углами и легким весом.",
        "pros": [
            "Невероятно легкий старт и интуитивный синтаксис",
            "Маленький размер итогового .exe файла (~10-15 МБ)",
            "Автоматическое масштабирование под HighDPI экраны",
            "Встроенные темы (Dark, Light, System, Blue, Green, Dark-Blue)"
        ],
        "cons": [
            "Меньше готовых сложных компонентов (нет встроенного рендеринга Web или 3D)",
            "Основан на Tkinter, поэтому сложные кастомные анимации требуют ручной реализации"
        ],
        "install": "pip install customtkinter pillow",
        "quickstart": '''import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CustomTkinter App")
        self.geometry("400x320")

        self.label = ctk.CTkLabel(self, text="Добро пожаловать в CustomTkinter", font=ctk.CTkFont(size=18, weight="bold"))
        self.label.pack(padx=20, pady=(40, 20))

        self.entry = ctk.CTkEntry(self, placeholder_text="Введите ваше имя...")
        self.entry.pack(padx=20, pady=10, fill="x")

        self.btn = ctk.CTkButton(self, text="Поприветствовать", command=self.greet)
        self.btn.pack(padx=20, pady=10)

    def greet(self):
        name = self.entry.get()
        if name:
            self.label.configure(text=f"Привет, {name}! 🚀")

if __name__ == "__main__":
    app = App()
    app.mainloop()
'''
    },
    {
        "id": "flet",
        "name": "Flet (Flutter for Python)",
        "category": "desktop",
        "icon": "smartphone",
        "badge": "Cross-Platform UI",
        "description": "Позволяет создавать кроссплатформенные приложения (Windows, macOS, Linux, Android, iOS и Web) на базе движка Flutter без написания кода на Dart.",
        "pros": [
            "Один код работает на ПК, смартфонах и в браузере",
            "Богатая библиотека красивых готовых Material 3 компонентов",
            "Поддержка реактивного состояния и асинхронности из коробки"
        ],
        "cons": [
            "Требует запущенного рантайма Flutter",
            "Специфика жизненного цикла страниц"
        ],
        "install": "pip install flet",
        "quickstart": '''import flet as ft

def main(page: ft.Page):
    page.title = "Flet Cross-Platform App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        txt_number.value = str(int(txt_number.value) - 1)
        page.update()

    def plus_click(e):
        txt_number.value = str(int(txt_number.value) + 1)
        page.update()

    page.add(
        ft.Row(
            [
                ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                txt_number,
                ft.IconButton(ft.Icons.ADD, on_click=plus_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
'''
    },

    # ------------------- WEB & BACKEND -------------------
    {
        "id": "fastapi",
        "name": "FastAPI",
        "category": "web",
        "icon": "zap",
        "badge": "Top Web API Framework",
        "description": "Высокопроизводительный современный веб-фреймворк для создания REST API на Python 3.8+ с автоматической генерацией интерактивной документации Swagger/OpenAPI.",
        "pros": [
            "Автоматическая валидация данных через Pydantic v2",
            "Автодокументация API на Swagger UI (/docs) и ReDoc (/redoc)",
            "Полная поддержка async/await и высокая скорость на уровне Node.js и Go",
            "Встроенная система внедрения зависимостей (Dependency Injection)"
        ],
        "cons": [
            "Не включает встроенный ORM или админку (в отличие от Django)"
        ],
        "install": "pip install fastapi uvicorn pydantic",
        "quickstart": '''from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(title="Modern REST API", version="1.0.0")

class Item(BaseModel):
    id: int
    title: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0)
    in_stock: bool = True

items_db: List[Item] = []

@app.get("/items", response_model=List[Item])
async def get_items():
    return items_db

@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    for existing in items_db:
        if existing.id == item.id:
            raise HTTPException(status_code=400, detail="Товар с таким ID уже существует")
    items_db.append(item)
    return item

# Запуск: uvicorn main:app --reload
'''
    },
    {
        "id": "flask",
        "name": "Flask",
        "category": "web",
        "icon": "globe",
        "badge": "Lightweight Classic",
        "description": "Микрофреймворк для создания веб-сайтов и простых сервисов. Дает полную свободу выбора библиотек и структуры проекта.",
        "pros": [
            "Простота и гибкость",
            "Огромная экосистема расширений (Flask-SQLAlchemy, Flask-Login, Flask-Migrate)",
            "Идеален для небольших сайтов с Jinja2 шаблонами"
        ],
        "cons": [
            "Синхронный по умолчанию (async поддерживается ограниченно)",
            "Нет встроенной автогенерации OpenAPI/Swagger"
        ],
        "install": "pip install flask jinja2",
        "quickstart": '''from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Добро пожаловать в Flask!</h1>"

@app.route("/api/echo", methods=["POST"])
def echo():
    data = request.get_json() or {}
    return jsonify({"received": data, "status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
'''
    },

    # ------------------- TELEGRAM BOTS -------------------
    {
        "id": "aiogram",
        "name": "Aiogram 3.x",
        "category": "bots",
        "icon": "message-square",
        "badge": "Modern Async Telegram",
        "description": "Самый мощный и популярный асинхронный фреймворк для создания Telegram-ботов любой сложности.",
        "pros": [
            "Полная асинхронность и поддержка Bot API 7.x+",
            "Модульная система роутеров (Routers)",
            "Встроенная машина состояний (FSM - Finite State Machine) для пошаговых диалогов",
            "Поддержка Middleware для авторизации, троттлинга и логирования"
        ],
        "cons": [
            "Архитектура 3.x кардинально отличается от устаревшего 2.x (нужно следить за актуальностью туториалов)"
        ],
        "install": "pip install aiogram aiohttp",
        "quickstart": '''import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔥 Документация", url="https://docs.aiogram.dev")
    builder.button(text="⭐ Нажми меня", callback_data="btn_clicked")
    
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я современный бот на Aiogram 3.",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "btn_clicked")
async def handle_callback(callback: types.CallbackQuery):
    await callback.answer("Кнопка нажата!", show_alert=True)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
'''
    },

    # ------------------- CLI & UTILITIES -------------------
    {
        "id": "typer-rich",
        "name": "Typer + Rich",
        "category": "cli",
        "icon": "terminal",
        "badge": "Modern CLI Stack",
        "description": "Создание потрясающих консольных утилит с автодополнением команд, таблицами, прогресс-барами и подсветкой синтаксиса.",
        "pros": [
            "Автоматический генератор CLI на основе Type Hints",
            "Красивый цветной вывод в терминал с Rich (Markdown, таблицы, панели, спиннеры)",
            "Автоматическая справка `--help` с примерами"
        ],
        "cons": [
            "Ориентирован только на работу в терминале"
        ],
        "install": "pip install typer rich",
        "quickstart": '''import typer
from rich.console import Console
from rich.table import Table
from rich.progress import track
import time

app = typer.Typer(help="Супер-утилита на Typer + Rich")
console = Console()

@app.command()
def process(count: int = typer.Option(5, help="Количество элементов для обработки")):
    """Обработка данных с красивым прогресс-баром"""
    console.print(f"[bold green]Запуск обработки {count} элементов...[/bold green]")
    
    for i in track(range(count), description="Обработка..."):
        time.sleep(0.3)
    
    table = Table(title="Результаты выполнения")
    table.add_column("ID", style="cyan")
    table.add_column("Статус", style="green")
    table.add_row("1", "Успешно")
    table.add_row("2", "Успешно")
    console.print(table)

if __name__ == "__main__":
    app()
'''
    },

    # ------------------- DATA & AI -------------------
    {
        "id": "streamlit",
        "name": "Streamlit",
        "category": "data",
        "icon": "bar-chart-2",
        "badge": "Fastest Data/AI UI",
        "description": "Позволяет превратить Python-скрипты в интерактивные веб-дашборды и интерфейсы для работы с нейросетями за считанные минуты без фронтенда.",
        "pros": [
            "Ноль знаний HTML/CSS/JS — всё пишется чистым Python",
            "Мгновенное отображение графиков (Plotly, Matplotlib, Altair)",
            "Встроенные виджеты для чатов с LLM (`st.chat_message`, `st.chat_input`)"
        ],
        "cons": [
            "Перезапускает весь скрипт сверху вниз при каждом взаимодействии (требует использования `st.session_state` и `st.cache_data`)"
        ],
        "install": "pip install streamlit",
        "quickstart": '''import streamlit as st

st.set_page_config(page_title="AI Data Dashboard", layout="wide")

st.title("📊 Интерактивный Data & AI Дашборд")

user_input = st.text_input("Введите ваш промпт для AI:", "Как создать приложение на Python?")

col1, col2 = st.columns(2)
with col1:
    temperature = st.slider("Креативность (Temperature)", 0.0, 1.0, 0.7)
with col2:
    model = st.selectbox("Модель", ["Gemini 1.5 Pro", "Claude 3.5 Sonnet", "GPT-4o"])

if st.button("🚀 Сгенерировать ответ"):
    with st.spinner("Думаю..."):
        st.success(f"Ответ от {model} с температурой {temperature}: Отличный запрос!")
'''
    },

    # ------------------- GAMES -------------------
    {
        "id": "pygame",
        "name": "Pygame / Pygame-CE",
        "category": "games",
        "icon": "gamepad-2",
        "badge": "Game Dev & Multimedia",
        "description": "Классическая кроссплатформенная библиотека для создания 2D-игр, симуляций, физических песочниц и мультимедиа-приложений.",
        "pros": [
            "Полный контроль над игровым циклом, событиями мыши и клавиатуры",
            "Поддержка спрайтов, коллизий, воспроизведения звуков и музыки",
            "Огромное сообщество и сотни обучающих материалов"
        ],
        "cons": [
            "Ориентирован в первую очередь на 2D графику",
            "Сложнее упаковать под веб и мобильные устройства"
        ],
        "install": "pip install pygame-ce",
        "quickstart": '''import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Pygame 2D Template")
clock = pygame.time.Clock()

x, y = 300, 220
speed = 5

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: x -= speed
    if keys[pygame.K_RIGHT]: x += speed
    if keys[pygame.K_UP]: y -= speed
    if keys[pygame.K_DOWN]: y += speed

    screen.fill((30, 30, 40))
    pygame.draw.circle(screen, (59, 130, 246), (x, y), 25)
    
    pygame.display.flip()
    clock.tick(60)
'''
    }
]
