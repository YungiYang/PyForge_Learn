"""
Обширная база данных экосистемы Python: библиотеки, источники, документация и сниппеты по предметным областям.
"""

ECOSYSTEM_TOPICS = [
    # ------------------ KIVY & MOBILE / DESKTOP GUI ------------------
    {
        "id": "kivy_and_gui",
        "category": "Кроссплатформенный GUI & Mobile",
        "title": "Kivy: Разработка интерфейсов для Windows, Android, iOS и Linux",
        "keywords": ["kivy", "киви", "kivymd", "мобильные приложения", "android", "ios", "тачскрин", "touch", "gui", "интерфейс"],
        "libraries": [
            {
                "name": "Kivy",
                "pypi": "kivy",
                "github": "https://github.com/kivy/kivy",
                "docs": "https://kivy.org/doc/stable/",
                "badge": "⭐ 19,000+ stars (Cross-Platform)",
                "description": "Кроссплатформенный фреймворк для создания сенсорных и десктопных GUI-приложений на Python с единой кодовой базой для Windows, macOS, Linux, Android и iOS.",
                "install": "pip install kivy",
                "code": '''from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class KivyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.lbl = Label(text="Добро пожаловать в Kivy!", font_size=22)
        btn = Button(text="Нажми меня 🚀", size_hint=(1, 0.4), background_color=(0.1, 0.6, 0.9, 1))
        btn.bind(on_press=self.on_btn_click)
        
        layout.add_widget(self.lbl)
        layout.add_widget(btn)
        return layout

    def on_btn_click(self, instance):
        self.lbl.text = "Кнопка успешно нажата! 🎉"

if __name__ == '__main__':
    KivyApp().run()
'''
            },
            {
                "name": "KivyMD",
                "pypi": "kivymd",
                "github": "https://github.com/kivymd/KivyMD",
                "docs": "https://kivymd.readthedocs.io/",
                "badge": "Material Design 3 Widgets",
                "description": "Набор современных Material Design компонентов для Kivy (кнопки, карточки, диалоги, навигационные панели).",
                "install": "pip install kivymd",
                "code": '''from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.screen import MDScreen

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        screen = MDScreen()
        btn = MDRaisedButton(
            text="Material Design Кнопка",
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        screen.add_widget(btn)
        return screen

if __name__ == "__main__":
    MainApp().run()
'''
            }
        ],
        "sources": [
            {"title": "Официальная документация Kivy", "url": "https://kivy.org/doc/stable/"},
            {"title": "Документация KivyMD (Material Design)", "url": "https://kivymd.readthedocs.io/"},
            {"title": "Kivy GitHub Репозиторий", "url": "https://github.com/kivy/kivy"}
        ]
    },

    # ------------------ OCR & ДОКУМЕНТЫ ------------------
    {
        "id": "ocr_text_recognition",
        "category": "OCR & Компьютерное зрение",
        "title": "Распознавание текста с изображений и сканов (OCR)",
        "keywords": ["ocr", "распознавание текста", "скан", "текст с картинки", "tesseract", "easyocr", "paddleocr", "документы", "распознать фото"],
        "libraries": [
            {
                "name": "EasyOCR",
                "pypi": "easyocr",
                "github": "https://github.com/JaidedAI/EasyOCR",
                "docs": "https://www.jaided.ai/easyocr/",
                "badge": "Top Choice (80+ языков)",
                "description": "Готовая библиотека глубокого обучения для OCR с поддержкой русского, английского и 80+ других языков. Не требует установки внешних бинарников Tesseract.",
                "install": "pip install easyocr pillow torch",
                "code": '''import easyocr

# Инициализируем распознавание для русского и английского языков
reader = easyocr.Reader(['ru', 'en'], gpu=False)

# Распознаем текст с изображения
results = reader.readtext('invoice.png', detail=0)

for line in results:
    print(f"Распознанная строка: {line}")
'''
            },
            {
                "name": "pytesseract",
                "pypi": "pytesseract",
                "github": "https://github.com/madmaze/pytesseract",
                "docs": "https://github.com/tesseract-ocr/tesseract",
                "badge": "Classic Google OCR",
                "description": "Python-обертка для движка Google Tesseract OCR. Высокая скорость работы на CPU для сканов документов хорошего качества.",
                "install": "pip install pytesseract pillow",
                "code": '''import pytesseract
from PIL import Image

# Требуется установленный бинарник Tesseract OCR в системе
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

image = Image.open('document.png')
text = pytesseract.image_to_string(image, lang='rus+eng')
print("Результат OCR:\\n", text)
'''
            }
        ],
        "sources": [
            {"title": "Awesome OCR Collection", "url": "https://github.com/tesseract-ocr/tesseract"},
            {"title": "PyPI EasyOCR Official", "url": "https://pypi.org/project/easyocr/"}
        ]
    },

    # ------------------ PDF & ОТЧЕТЫ ------------------
    {
        "id": "pdf_processing",
        "category": "Работа с PDF & Документооборот",
        "title": "Генерация, парсинг и редактирование PDF файлов",
        "keywords": ["pdf", "пдф", "генерация pdf", "парсинг pdf", "чтение pdf", "отчеты", "таблицы в pdf", "pdfplumber", "reportlab", "pypdf", "fitz", "pymupdf"],
        "libraries": [
            {
                "name": "PyMuPDF (fitz)",
                "pypi": "PyMuPDF",
                "github": "https://github.com/pymupdf/PyMuPDF",
                "docs": "https://pymupdf.readthedocs.io/",
                "badge": "Самый быстрый PDF движок",
                "description": "Высокопроизводительная библиотека для молниеносного извлечения текста, картинок, таблиц, рендеринга страниц PDF в изображения и объединения файлов.",
                "install": "pip install PyMuPDF",
                "code": '''import fitz  # PyMuPDF

# Открываем документ
doc = fitz.open("sample.pdf")

# Извлекаем текст со всех страниц
for page_num, page in enumerate(doc):
    text = page.get_text()
    print(f"--- Страница {page_num + 1} ---")
    print(text[:300])

# Конвертируем первую страницу в PNG картинку
pix = doc[0].get_pixmap()
pix.save("page_1.png")
'''
            },
            {
                "name": "ReportLab",
                "pypi": "reportlab",
                "github": "https://github.com/mrsoftware/ReportLab",
                "docs": "https://docs.reportlab.com/",
                "badge": "Генератор красивых PDF",
                "description": "Стандарт индустрии для программного создания профессиональных PDF-отчетов, счетов, сертификатов с графикой и таблицами.",
                "install": "pip install reportlab",
                "code": '''from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=A4)
styles = getSampleStyleSheet()
story = [
    Paragraph("Финансовый отчет за 2026 год", styles['Heading1']),
    Spacer(1, 15),
    Paragraph("Отчет сгенерирован автоматически на Python.", styles['Normal'])
]
doc.build(story)
print("PDF отчет успешно создан!")
'''
            }
        ],
        "sources": [
            {"title": "PyMuPDF Docs", "url": "https://pymupdf.readthedocs.io/"},
            {"title": "ReportLab User Guide", "url": "https://www.reportlab.com/docs/"}
        ]
    },

    # ------------------ EXCEL, WORD & ОФИС ------------------
    {
        "id": "office_excel_word",
        "category": "Офисные документы (Office & Excel)",
        "title": "Работа с Excel (XLSX), Word (DOCX) и таблицами",
        "keywords": ["excel", "эксель", "xlsx", "word", "ворд", "docx", "таблицы", "openpyxl", "python-docx", "pandas excel", "csv", "office"],
        "libraries": [
            {
                "name": "openpyxl",
                "pypi": "openpyxl",
                "github": "https://github.com/theorchard/openpyxl",
                "docs": "https://openpyxl.readthedocs.io/",
                "badge": "Лучший для Excel XLSX",
                "description": "Чтение, запись, форматирование, формулы, стили и диаграммы в файлах Excel `.xlsx` без необходимости установки Microsoft Office.",
                "install": "pip install openpyxl",
                "code": '''from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

wb = Workbook()
ws = wb.active
ws.title = "Продажи"

# Заголовки с оформлением
headers = ["ID", "Товар", "Цена (руб)", "Количество", "Итого"]
ws.append(headers)

# Стилизация заголовка
for col in range(1, 6):
    cell = ws.cell(row=1, column=col)
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")

# Данные с формулой
ws.append([1, "Ноутбук Pro", 85000, 2, "=C2*D2"])
wb.save("sales_report.xlsx")
print("Excel файл создан!")
'''
            },
            {
                "name": "python-docx",
                "pypi": "python-docx",
                "github": "https://github.com/python-openxml/python-docx",
                "docs": "https://python-docx.readthedocs.io/",
                "badge": "Лучший для Word DOCX",
                "description": "Создание и редактирование документов Microsoft Word (`.docx`), абзацев, таблиц и изображений.",
                "install": "pip install python-docx",
                "code": '''from docx import Document

doc = Document()
doc.add_heading('Коммерческое предложение', level=0)
doc.add_paragraph('Уважаемый клиент, представляем наш новый программный комплекс.')
doc.save('proposal.docx')
print("Word документ сохранен!")
'''
            }
        ],
        "sources": [
            {"title": "OpenPyXL Documentation", "url": "https://openpyxl.readthedocs.io/"},
            {"title": "python-docx Official Docs", "url": "https://python-docx.readthedocs.io/"}
        ]
    },

    # ------------------ ПАРСИНГ & ВЕБ-СКРЕЙПИНГ ------------------
    {
        "id": "scraping_and_browser_automation",
        "category": "Парсинг & Автоматизация браузера",
        "title": "Парсинг сайтов, обход Cloudflare и автоматизация браузера",
        "keywords": ["парсинг", "парсер", "scraping", "scraper", "cloudflare", "playwright", "selenium", "curl_cffi", "beautifulsoup", "bs4", "антифрод", "капча", "браузер"],
        "libraries": [
            {
                "name": "Playwright for Python",
                "pypi": "playwright",
                "github": "https://github.com/microsoft/playwright-python",
                "docs": "https://playwright.dev/python/",
                "badge": "Next-Gen Browser Automation",
                "description": "Современный инструмент от Microsoft для управления Chromium, Firefox и WebKit. Поддерживает async/await, перехват сетевых запросов и SPA сайты (React, Vue).",
                "install": "pip install playwright && playwright install chromium",
                "code": '''import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://news.ycombinator.com")
        
        # Получаем заголовки статей
        titles = await page.eval_on_selector_all(".titleline > a", "elements => elements.map(e => e.innerText)")
        print("Топ заголовков:", titles[:5])
        
        await browser.close()

asyncio.run(main())
'''
            },
            {
                "name": "curl_cffi (TLS Fingerprint Bypass)",
                "pypi": "curl_cffi",
                "github": "https://github.com/yifeikong/curl_cffi",
                "docs": "https://curl-cffi.readthedocs.io/",
                "badge": "Обход Cloudflare & TLS защиты",
                "description": "Сверхбыстрый HTTP-клиент, имитирующий TLS/JA3/JA4 отпечатки реальных браузеров (Chrome, Safari). Позволяет скачивать данные с защищенных Cloudflare сайтов.",
                "install": "pip install curl_cffi",
                "code": '''from curl_cffi import requests

# Имитируем браузер Chrome 120 с его реальным TLS отпечатком
response = requests.get(
    "https://httpbin.org/headers",
    impersonate="chrome120"
)

print("Статус ответа:", response.status_code)
print(response.json())
'''
            }
        ],
        "sources": [
            {"title": "Playwright Python Documentation", "url": "https://playwright.dev/python/"},
            {"title": "curl-cffi GitHub Repository", "url": "https://github.com/yifeikong/curl_cffi"}
        ]
    },

    # ------------------ ЛОКАЛЬНЫЙ AI / LLM / НЕЙРОСЕТИ ------------------
    {
        "id": "local_ai_and_llms",
        "category": "Искусственный интеллект & LLM",
        "title": "Интеграция с языковыми моделями (LLM, Ollama, LangChain)",
        "keywords": ["ai", "llm", "нейросеть", "чат gpt", "ollama", "langchain", "openai", "gemini", "локальная модель", "эмбеддинги", "векторная бд", "rag", "chromadb"],
        "libraries": [
            {
                "name": "Ollama Python",
                "pypi": "ollama",
                "github": "https://github.com/ollama/ollama-python",
                "docs": "https://ollama.com/",
                "badge": "100% Локальный AI без интернета",
                "description": "Простой Python SDK для запуска локальных LLM (Llama 3, Mistral, Gemma, Qwen, DeepSeek) прямо на вашем компьютере бесплатно.",
                "install": "pip install ollama",
                "code": '''import ollama

# Запуск инференса локальной модели
response = ollama.chat(model='llama3', messages=[
    {'role': 'user', 'content': 'Напиши функцию на Python для вычисления чисел Фибоначчи'}
])

print("Ответ локальной модели:\\n", response['message']['content'])
'''
            },
            {
                "name": "ChromaDB (Vector Database)",
                "pypi": "chromadb",
                "github": "https://github.com/chroma-core/chroma",
                "docs": "https://docs.trychroma.com/",
                "badge": "Векторная БД для RAG систем",
                "description": "Встраиваемая векторная база данных для создания поисковых систем по документам и контекстных баз знаний для нейросетей.",
                "install": "pip install chromadb",
                "code": '''import chromadb

client = chromadb.Client()
collection = client.create_collection(name="docs")

# Добавляем документы
collection.add(
    documents=["FastAPI - фреймворк для API", "PySide6 - библиотека для GUI"],
    ids=["id1", "id2"]
)

# Семантический поиск
results = collection.query(query_texts=["как создать десктопный интерфейс"], n_results=1)
print("Найден документ:", results['documents'])
'''
            }
        ],
        "sources": [
            {"title": "Ollama Library", "url": "https://github.com/ollama/ollama-python"},
            {"title": "LangChain Python Docs", "url": "https://python.langchain.com/"}
        ]
    },

    # ------------------ АУДИО, ЗВУК И МУЗЫКА ------------------
    {
        "id": "audio_and_speech",
        "category": "Аудио, Речь & Мультимедиа",
        "title": "Синтез речи (TTS), распознавание голоса (STT) и аудио-обработка",
        "keywords": ["аудио", "звук", "голос", "распознавание речи", "синтез речи", "tts", "stt", "whisper", "sounddevice", "pydub", "librosa", "музыка", "плеер"],
        "libraries": [
            {
                "name": "faster-whisper",
                "pypi": "faster-whisper",
                "github": "https://github.com/SYSTRAN/faster-whisper",
                "docs": "https://github.com/SYSTRAN/faster-whisper",
                "badge": "Быстрое распознавание голоса",
                "description": "Оптимизированная версия OpenAI Whisper на CTranslate2. Работает в 4 раза быстрее оригинала с поддержкой русского языка.",
                "install": "pip install faster-whisper",
                "code": '''from faster-whisper import WhisperModel

# Загружаем компактную модель на CPU/GPU
model = WhisperModel("base", device="cpu", compute_type="int8")

segments, info = model.transcribe("audio.mp3", beam_size=5)
print(f"Язык аудио: {info.language} (вероятность {info.language_probability:.2f})")

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
'''
            },
            {
                "name": "sounddevice & soundfile",
                "pypi": "sounddevice",
                "github": "https://github.com/spatialaudio/python-sounddevice",
                "docs": "https://python-sounddevice.readthedocs.io/",
                "badge": "Запись и воспроизведение звука",
                "description": "Кроссплатформенная запись с микрофона и воспроизведение через динамики в реальном времени с поддержкой NumPy массивов.",
                "install": "pip install sounddevice soundfile numpy",
                "code": '''import sounddevice as sd
import soundfile as sf

# Воспроизведение аудиофайла
data, fs = sf.read('music.wav')
sd.play(data, fs)
sd.wait()
print("Воспроизведение завершено!")
'''
            }
        ],
        "sources": [
            {"title": "faster-whisper GitHub", "url": "https://github.com/SYSTRAN/faster-whisper"},
            {"title": "sounddevice Documentation", "url": "https://python-sounddevice.readthedocs.io/"}
        ]
    },

    # ------------------ СЕТИ, WEBSOCKETS & IOT ------------------
    {
        "id": "websockets_and_networking",
        "category": "Сетевые протоколы & WebSockets",
        "title": "Двусторонняя связь в реальном времени, WebSockets и gRPC",
        "keywords": ["websocket", "вебсокет", "сокеты", "сеть", "realtime", "grpc", "scapy", "aiohttp", "websockets", "mqtt", "iot"],
        "libraries": [
            {
                "name": "websockets",
                "pypi": "websockets",
                "github": "https://github.com/python-websockets/websockets",
                "docs": "https://websockets.readthedocs.io/",
                "badge": "Стандарт WebSocket для Python",
                "description": "Библиотека для создания клиентских и серверных WebSocket приложений на базе asyncio.",
                "install": "pip install websockets",
                "code": '''import asyncio
import websockets

async def echo_server(websocket):
    async for message in websocket:
        print(f"Получено: {message}")
        await websocket.send(f"Эхо: {message}")

async def main():
    async with websockets.serve(echo_server, "localhost", 8765):
        print("WebSocket сервер запущен на ws://localhost:8765")
        await asyncio.Future()  # Бесконечный цикл

# asyncio.run(main())
'''
            }
        ],
        "sources": [
            {"title": "websockets Official Docs", "url": "https://websockets.readthedocs.io/"}
        ]
    }
]
