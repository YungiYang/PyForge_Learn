"""
Руководство и генераторы конфигураций для сборки, компиляции и дистрибуции Python-приложений.
"""

PACKAGING_TOPICS = [
    {
        "id": "pyinstaller-guide",
        "title": "Сборка в .EXE через PyInstaller (Полное руководство)",
        "icon": "package",
        "category": "packaging",
        "summary": "Как превратить Python-скрипт в независимый исполняемый файл Windows без необходимости установки Python у пользователя.",
        "content": """
### Главный секрет: Корректная работа с путями (`sys._MEIPASS`)
Когда PyInstaller собирает приложение с флагом `--onefile`, при запуске все картинки, иконки и шрифты распаковываются во временную системную папку `_MEIxxxx`. Если вы используете обычный относительный путь `assets/icon.png`, приложение упадет!

#### Обязательная вспомогательная функция для путей:
```python
import sys
import os
from pathlib import Path

def get_resource_path(relative_path: str) -> Path:
    \"\"\"Получает абсолютный путь к ресурсам для разработки и для PyInstaller .exe\"\"\"
    try:
        # PyInstaller создает временную папку _MEIPASS при запуске .exe
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Обычный запуск из исходного кода
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path

# Пример использования:
# icon_file = get_resource_path("assets/icon.ico")
```

---

### Основные флаги командной строки PyInstaller:

| Флаг | Описание |
|---|---|
| `-F`, `--onefile` | Упаковать всё в один единственный `.exe` файл |
| `-D`, `--onedir` | Создать папку с `.exe` и `.dll` (быстрее запускается) |
| `-w`, `--windowed` | Скрыть черное окно консоли (для GUI-приложений) |
| `-i app.ico`, `--icon=app.ico` | Задать иконку исполняемого файла |
| `--add-data "src;dest"` | Добавить внешние файлы (на Windows разделитель `;`, на Linux/macOS `:`) |
| `--hidden-import <модуль>` | Принудительно включить модуль, который PyInstaller не смог обнаружить сам |
| `--clean` | Очистить кэш сборки перед созданием |

#### Пример готовой команды для GUI-приложения:
```bash
pyinstaller --noconfirm --onedir --windowed --icon "assets/app.ico" --add-data "assets;assets" --name "MySuperApp" src/main.py
```
"""
    },
    {
        "id": "nuitka-compilation",
        "title": "Компиляция в машинный код с Nuitka (Защита от декомпиляции)",
        "icon": "binary",
        "category": "packaging",
        "summary": "Nuitka транслирует Python в C++, компилирует нативным компилятором (MSVC/GCC) и ускоряет работу в 2-4 раза, полностью защищая код.",
        "content": """
### Почему Nuitka превосходит PyInstaller для коммерческих проектов?
- **100% защита от декомпиляции**: в отличие от PyInstaller (где упакован байткод `.pyc`, легко восстанавливаемый декомпилятором), Nuitka создает настоящий бинарный машинный код `.exe`.
- **Прирост производительности**: функции и циклы работают быстрее.
- **Поддержка всех библиотек**: PySide6, PyQt, NumPy, Torch, FastAPI.

#### Требования:
Установленный компилятор C (на Windows Nuitka сама предложит автоматически скачать компилятор `w64devkit` / `MinGW64` или использует Visual Studio C++).

```bash
pip install nuitka
```

#### Команда для компиляции GUI-приложения в независимый дистрибутив:
```bash
python -m nuitka --standalone \
  --windows-disable-console \
  --windows-icon-from-ico=assets/app.ico \
  --enable-plugin=pyside6 \
  --include-data-dir=assets=assets \
  --output-dir=dist \
  src/main.py
```
"""
    },
    {
        "id": "inno-setup-installer",
        "title": "Создание Windows-установщика (Inno Setup)",
        "icon": "shield",
        "category": "packaging",
        "summary": "Как упаковать папку с .exe в красивый профессиональный инсталлятор (Setup.exe) с выбором папки, ярлыками на рабочем столе и деинсталлятором.",
        "content": r"""
### Пошаговое руководство:

1. Скачайте бесплатную утилиту [Inno Setup](https://jrsoftware.org/isdl.php).
2. Соберите проект через PyInstaller в режиме папки (`--onedir`).
3. Создайте файл конфигурации `setup_script.iss`:

```pascal
; Inno Setup Script Template
#define MyAppName "PyForge App"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Developer"
#define MyAppExeName "MySuperApp.exe"

[Setup]
AppId={{A6D7C2B1-4E8F-4123-9999-PYFORGEAPP}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=output_installer
OutputBaseFilename=PyForge_Setup_v1.0.0
SetupIconFile=assets\app.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\MySuperApp\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\MySuperApp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
```

4. Скомпилируйте скрипт в Inno Setup Compiler — вы получите готовый `PyForge_Setup_v1.0.0.exe`!
"""
    },
    {
        "id": "docker-packaging",
        "title": "Упаковка веб-сервисов в Docker (Multi-stage)",
        "icon": "container",
        "category": "packaging",
        "summary": "Профессиональный Dockerfile для FastAPI/Flask с минимальным размером образа и запуском от непривилегированного пользователя.",
        "content": """
### Оптимизированный двухэтапный (Multi-Stage) Dockerfile:

```dockerfile
# ----------------- Stage 1: Build Stage -----------------
FROM python:3.12-slim AS builder

WORKDIR /build

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ----------------- Stage 2: Runtime Stage -----------------
FROM python:3.12-slim AS runner

WORKDIR /app

# Создаем пользователя без прав root для безопасности
RUN useradd -m -u 1000 appuser

# Копируем установленные пакеты из первого этапа
COPY --from=builder /root/.local /home/appuser/.local
COPY . /app

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Запуск и сборка контейнера:
```bash
docker build -t my-python-service:1.0 .
docker run -d -p 8000:8000 --name api-service my-python-service:1.0
```
"""
    }
]
