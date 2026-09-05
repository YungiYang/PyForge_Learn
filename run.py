import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

# Добавляем пути в sys.path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from app.main import app

def open_browser(port: int):
    # Не открываем браузер в облачных контейнерах (Render, Hugging Face, Docker)
    if os.environ.get("SPACE_ID") or os.environ.get("RENDER") or os.environ.get("KOYEB") or os.environ.get("PORT"):
        return
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{port}")

def main():
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    print(f"🚀 PyForge запускается на http://{host}:{port} ...")

    # Автоматическое открытие в браузере (только для локального запуска)
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Запуск сервера
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
