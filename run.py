import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

def open_browser(port: int):
    # Не открываем браузер в облачных контейнерах (Render, Hugging Face, Docker)
    if os.environ.get("SPACE_ID") or os.environ.get("RENDER") or os.environ.get("KOYEB"):
        return
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{port}")

def main():
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    try:
        import uvicorn
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        panel = Panel(
            f"[bold cyan]⚡ PyForge: Ultimate Python App Studio & Handbook[/bold cyan]\n"
            f"[green]Сервер запускается по адресу:[/green] [bold yellow]http://{host}:{port}[/bold yellow]\n\n"
            "[dim]• Конструктор проектов под ключ (PySide6, CustomTkinter, FastAPI, Aiogram 3)\n"
            "• Интерактивная песочница и 100+ готовых сниппетов\n"
            "• Тренажер практики с ИИ-наставником и генератором задач по библиотекам\n"
            "• Нажмите Ctrl+C для остановки сервера.[/dim]",
            title="🚀 PyForge Ready",
            border_style="cyan"
        )
        console.print(panel)
    except Exception:
        print(f"Запуск PyForge на http://{host}:{port} ...")

    # Автоматическое открытие в браузере (для локального запуска)
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Запуск FastAPI приложения через uvicorn
    import uvicorn
    uvicorn.run("app.main:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
