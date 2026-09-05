"""
Интеллектуальный сервис поиска библиотек, инструментов и источников (AI & Live Web Scout).
Выполняет живой поиск по Интернету (GitHub API, PyPI Registry, Web) и базе знаний.
"""

import json
import urllib.request
import urllib.parse
import re
from typing import List, Dict, Any, Optional
from ..data.curated_ecosystem import ECOSYSTEM_TOPICS

# Словарь смыслового перевода русскоязычных запросов для поиска по мировым репозиториям
RU_EN_MAPPINGS = {
    "распознавание лиц": "face recognition",
    "распознавание речи": "speech recognition whisper",
    "распознавание текста": "ocr text recognition tesseract",
    "парсинг": "web scraping crawler",
    "парсер": "web scraper playwright",
    "скачать видео": "video downloader yt-dlp",
    "скачать музыку": "music audio downloader",
    "графический интерфейс": "gui framework desktop",
    "десктоп": "desktop application gui",
    "компьютерное зрение": "computer vision opencv",
    "нейросеть": "machine learning neural network",
    "нейросети": "deep learning pytorch transformers",
    "чат бот": "telegram bot aiogram",
    "боты": "bot automation",
    "база данных": "database orm sqlalchemy",
    "вебсокеты": "websocket realtime asyncio",
    "игры": "game development pygame",
    "таблицы": "excel openpyxl pandas",
    "ворд": "word docx python-docx",
    "отчеты": "pdf generation reportlab fitz"
}

# Известные готовые сниппеты для популярных библиотек
KNOWN_CODE_SNIPPETS = {
    "kivy": '''# Пример простого приложения на Kivy
from kivy.app import App
from kivy.uix.button import Button

class MyApp(App):
    def build(self):
        return Button(text='Привет из Kivy! 🚀', font_size=24)

if __name__ == '__main__':
    MyApp().run()
''',
    "kivymd": '''# Пример Material Design интерфейса на KivyMD
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return MDRaisedButton(text="Нажми меня (KivyMD)", pos_hint={"center_x": 0.5, "center_y": 0.5})

if __name__ == "__main__":
    MainApp().run()
''',
    "opencv-python": '''import cv2

# Чтение и отображение изображения
img = cv2.imread('image.jpg')
if img is not None:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('gray_image.jpg', gray)
    print("Изображение успешно обработано!")
''',
    "mediapipe": '''import mediapipe as mp
import cv2

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=2)
print("MediaPipe Hands инициализирован успешно!")
''',
    "yolov8": '''from ultralytics import YOLO

# Загрузка предобученной модели детекции объектов
model = YOLO('yolov8n.pt')
results = model('https://ultralytics.com/images/bus.jpg')
print(f"Обнаружено объектов: {len(results[0].boxes)}")
''',
    "telethon": '''from telethon import TelegramClient

api_id = 12345
api_hash = 'your_api_hash'
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start()
    print("Клиент Telegram успешно запущен!")

# with client:
#     client.loop.run_until_complete(main())
''',
    "pyrogram": '''from pyrogram import Client

app = Client("my_account", api_id=12345, api_hash="your_api_hash")

async def main():
    async with app:
        await app.send_message("me", "Привет от Pyrogram!")

# app.run(main())
'''
}

class AIScoutService:
    @staticmethod
    def get_suggestions() -> List[Dict[str, str]]:
        """Популярные подсказки для быстрого поиска"""
        return [
            {"label": "📱 Kivy (Кроссплатформенный GUI)", "query": "kivy"},
            {"label": "🔍 OCR и сканирование текста", "query": "распознавание текста с картинок ocr"},
            {"label": "📄 PDF отчеты и таблицы", "query": "генерация и парсинг pdf файлов"},
            {"label": "📊 Excel (XLSX) и Word (DOCX)", "query": "работа с excel и word файлами"},
            {"label": "🌐 Парсинг & Обход Cloudflare", "query": "парсинг сайтов с защитой cloudflare и playwright"},
            {"label": "👁️ Компьютерное зрение & OpenCV", "query": "computer vision opencv mediapipe"},
            {"label": "🤖 Локальные нейросети (LLM)", "query": "локальные языковые модели ollama и chromadb"},
            {"label": "🎙️ Распознавание речи & Аудио", "query": "распознавание речи whisper"},
            {"label": "⚡ WebSockets в реальном времени", "query": "двусторонняя связь websockets"},
        ]

    @classmethod
    def search(cls, query: str, mode: str = "web", llm_config: Optional[dict] = None) -> Dict[str, Any]:
        """
        Основной метод поиска библиотек и источников:
        Поддерживает: 'web' (поиск по интернету и PyPI), 'smart' (локальный поиск), 'llm' (нейросеть).
        """
        q = query.strip()
        if not q:
            return {"query": "", "mode": mode, "results": [], "summary": "Пожалуйста, введите тему для поиска."}

        if mode == "llm" and llm_config and llm_config.get("api_key"):
            return cls._query_external_llm(q, llm_config)
        elif mode == "smart":
            # Smart локальный поиск + при необходимости интернет
            local_res = cls._smart_semantic_search(q)
            if local_res and len(local_res.get("libraries", [])) > 0 and local_res.get("category") != "Индивидуальный подбор":
                return local_res
            return cls._live_web_search(q)
        else:
            # Режим по умолчанию: Живой поиск по Интернету и PyPI (Live Web Search)
            return cls._live_web_search(q)

    @classmethod
    def _live_web_search(cls, query: str) -> Dict[str, Any]:
        """
        Реальный поиск по Сети: GitHub API + PyPI Registry API + перевод запроса.
        """
        # 1. Проверяем точное имя пакета в PyPI
        direct_pkg_info = cls._fetch_pypi_package_info(query.strip())
        
        # 2. Ищем репозитории на GitHub
        web_query = cls._translate_query(query)
        encoded_q = urllib.parse.quote(f"{web_query} language:python")
        url = f"https://api.github.com/search/repositories?q={encoded_q}&sort=stars&order=desc&per_page=6"

        headers = {
            "User-Agent": "PyForge-WebScout/2.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/vnd.github.v3+json"
        }

        matched_libraries = []
        matched_sources = []

        # Если точный пакет существует в PyPI, добавляем его на первое место
        if direct_pkg_info:
            pkg_name = direct_pkg_info["name"]
            code_snippet = KNOWN_CODE_SNIPPETS.get(pkg_name.lower()) or f'''# Использование библиотеки {pkg_name}
import {pkg_name.lower().replace('-', '_')}

print("Пакет {pkg_name} успешно загружен!")
'''
            matched_libraries.append({
                "name": pkg_name,
                "pypi": pkg_name,
                "github": direct_pkg_info.get("github") or f"https://github.com/search?q={urllib.parse.quote(pkg_name)}",
                "docs": direct_pkg_info.get("docs") or direct_pkg_info.get("home_page") or f"https://pypi.org/project/{pkg_name}/",
                "badge": f"PyPI v{direct_pkg_info.get('version', 'latest')}",
                "description": direct_pkg_info.get("summary") or "Официальный пакет из реестра PyPI.",
                "install": f"pip install {pkg_name}",
                "code": code_snippet
            })
            matched_sources.append({
                "title": f"Официальная страница PyPI: {pkg_name}",
                "url": f"https://pypi.org/project/{pkg_name}/"
            })
            if direct_pkg_info.get("docs"):
                matched_sources.append({
                    "title": f"Официальная документация: {pkg_name}",
                    "url": direct_pkg_info["docs"]
                })

        # Запрос к GitHub API
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            items = data.get("items", [])
            for item in items:
                repo_name = item.get("name")
                
                # Пропускаем дубликаты
                if any(lib["name"].lower() == repo_name.lower() for lib in matched_libraries):
                    continue

                pypi_meta = cls._fetch_pypi_package_info(repo_name)
                stars_count = item.get("stargazers_count", 0)
                stars_formatted = f"⭐ {stars_count:,}"

                desc = item.get("description") or (pypi_meta.get("summary") if pypi_meta else "Популярный репозиторий Python на GitHub.")
                docs_url = (pypi_meta.get("docs") if pypi_meta else None) or item.get("homepage") or item.get("html_url")
                
                code_snippet = KNOWN_CODE_SNIPPETS.get(repo_name.lower()) or f'''# Пример работы с {repo_name}
# Установка: pip install {repo_name.lower()}
import {repo_name.lower().replace('-', '_')}

print("Модуль {repo_name} успешно импортирован!")
'''

                matched_libraries.append({
                    "name": repo_name,
                    "pypi": pypi_meta.get("pypi") if pypi_meta else repo_name.lower(),
                    "github": item.get("html_url"),
                    "docs": docs_url,
                    "badge": stars_formatted,
                    "description": desc,
                    "install": f"pip install {repo_name.lower()}",
                    "code": code_snippet
                })

                matched_sources.append({
                    "title": f"GitHub: {item.get('full_name')} ({stars_formatted})",
                    "url": item.get("html_url")
                })
        except Exception as e:
            # Если нет интернета или превышен лимит GitHub, дополняем из локальной базы
            pass

        # Если интернет ничего не вернул или вернул мало, дополняем из локальной базы
        if len(matched_libraries) < 2:
            local_res = cls._smart_semantic_search(query)
            for lib in local_res.get("libraries", []):
                if not any(l["name"].lower() == lib["name"].lower() for l in matched_libraries):
                    matched_libraries.append(lib)
            for src in local_res.get("sources", []):
                if not any(s["url"] == src["url"] for s in matched_sources):
                    matched_sources.append(src)

        summary_text = (
            f"ИИ нашел в Интернете и каталогах {len(matched_libraries)} актуальных решений по запросу «{query}». "
            f"Рейтинги, документация и команды установки получены в реальном времени."
        )

        return {
            "query": query,
            "mode": "web",
            "summary": summary_text,
            "topic_title": f"Интернет-поиск: {query}",
            "category": "Live Web & PyPI Results",
            "libraries": matched_libraries[:6],
            "sources": matched_sources[:8]
        }

    @classmethod
    def _fetch_pypi_package_info(cls, pkg_name: str) -> Optional[Dict[str, Any]]:
        """Получает метаданные о пакете из PyPI"""
        clean_name = pkg_name.strip().replace("_", "-")
        url = f"https://pypi.org/pypi/{urllib.parse.quote(clean_name)}/json"
        req = urllib.request.Request(url, headers={"User-Agent": "PyForge-WebScout/2.0"})
        try:
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            info = data.get("info", {})
            urls = info.get("project_urls") or {}
            doc_url = urls.get("Documentation") or urls.get("Homepage") or info.get("home_page")
            gh_url = urls.get("Source") or urls.get("Code") or urls.get("GitHub") or (info.get("home_page") if "github.com" in str(info.get("home_page")) else None)
            return {
                "name": info.get("name"),
                "version": info.get("version"),
                "summary": info.get("summary"),
                "home_page": info.get("home_page"),
                "docs": doc_url,
                "github": gh_url,
                "pypi": info.get("name")
            }
        except Exception:
            return None

    @classmethod
    def _translate_query(cls, query: str) -> str:
        q_clean = query.lower().strip()
        for ru_phrase, en_trans in RU_EN_MAPPINGS.items():
            if ru_phrase in q_clean:
                q_clean = q_clean.replace(ru_phrase, en_trans)
        return q_clean

    @classmethod
    def _smart_semantic_search(cls, query: str) -> Dict[str, Any]:
        """Локальный семантический поиск по curated базе знаний"""
        tokens = [t.lower() for t in query.split() if len(t) > 1]
        scored_topics = []

        for topic in ECOSYSTEM_TOPICS:
            score = 0
            title_lower = topic["title"].lower()
            category_lower = topic["category"].lower()
            keywords_lower = [k.lower() for k in topic.get("keywords", [])]

            if query.lower() in title_lower or query.lower() in category_lower:
                score += 10

            for kw in keywords_lower:
                if kw in query.lower() or query.lower() in kw:
                    score += 8
                for token in tokens:
                    if token in kw:
                        score += 3

            for token in tokens:
                if token in title_lower:
                    score += 4
                for lib in topic.get("libraries", []):
                    if token in lib["name"].lower() or token in lib.get("description", "").lower():
                        score += 5

            if score > 0:
                scored_topics.append((score, topic))

        scored_topics.sort(key=lambda x: x[0], reverse=True)

        if not scored_topics:
            return cls._live_web_search(query)

        best_topics = [item[1] for item in scored_topics[:3]]
        matched_libraries = []
        matched_sources = []
        for t in best_topics:
            matched_libraries.extend(t.get("libraries", []))
            matched_sources.extend(t.get("sources", []))

        return {
            "query": query,
            "mode": "smart",
            "summary": f"По запросу «{query}» подобраны проверенные библиотеки из базы знаний PyForge.",
            "topic_title": best_topics[0]["title"],
            "category": best_topics[0]["category"],
            "libraries": matched_libraries[:6],
            "sources": matched_sources[:6]
        }

    @classmethod
    def _query_external_llm(cls, query: str, config: dict) -> Dict[str, Any]:
        """Обращение к LLM API (Ollama / OpenAI)"""
        endpoint = config.get("endpoint", "http://localhost:11434/v1/chat/completions")
        api_key = config.get("api_key", "ollama")
        model = config.get("model", "llama3")

        prompt = f"""Ты эксперт по разработке на Python. Пользователь ищет библиотеки и источники для задачи: '{query}'.
Ответь в формате JSON со следующей структурой:
{{
  "summary": "Краткий вывод и архитектурный совет",
  "topic_title": "Название темы",
  "category": "Категория",
  "libraries": [
    {{
      "name": "Имя библиотеки",
      "pypi": "pypi_name",
      "github": "https://github.com/...",
      "docs": "https://...",
      "badge": "Краткое преимущество",
      "description": "Описание на русском",
      "install": "pip install ...",
      "code": "Минимальный рабочий пример на Python"
    }}
  ],
  "sources": [
    {{"title": "Название источника", "url": "https://..."}}
  ]
}}
Верни ТОЛЬКО валидный JSON."""

        try:
            payload = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }).encode("utf-8")

            req = urllib.request.Request(
                endpoint,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
            )

            with urllib.request.urlopen(req, timeout=12.0) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))

            content = resp_data["choices"][0]["message"]["content"].strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            parsed = json.loads(content)
            parsed["query"] = query
            parsed["mode"] = "llm"
            return parsed
        except Exception:
            return cls._live_web_search(query)
