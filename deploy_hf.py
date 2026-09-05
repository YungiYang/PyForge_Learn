"""
Автоматический деплой PyForge на бесплатный облачный хостинг Hugging Face Spaces (24/7).
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("🚀 PyForge: Авто-деплой на бесплатный хостинг Hugging Face (24/7)")
    print("=" * 60)
    print("\nПреимущества Hugging Face Spaces:")
    print("  • 100% Бесплатно 24/7 (Не засыпает)")
    print("  • 16 ГБ RAM и 2 vCPU")
    print("  • Защищенный HTTPS домен навсегда\n")

    # Проверка наличия huggingface_hub
    try:
        from huggingface_hub import HfApi, create_repo, upload_folder
    except ImportError:
        print("📦 Установка библиотеки huggingface_hub...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub"])
        from huggingface_hub import HfApi, create_repo, upload_folder

    print("🔑 Шаг 1: Получите бесплатный токен Hugging Face (Write):")
    print("   👉 https://huggingface.co/settings/tokens (нажмите 'Create new token' -> тип 'Write')\n")

    token = input("Вставьте ваш Hugging Face Token (hf_...): ").strip()
    if not token:
        print("❌ Токен не введен. Деплой отменен.")
        return

    space_name = input("Имя спейса (по умолчанию 'pyforge-studio'): ").strip() or "pyforge-studio"

    api = HfApi(token=token)

    try:
        user_info = api.whoami()
        username = user_info["name"]
        repo_id = f"{username}/{space_name}"

        print(f"\n📡 Создание Space: {repo_id} (Docker SDK)...")
        create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            private=False,
            exist_ok=True,
            token=token
        )

        project_dir = Path(__file__).resolve().parent

        print(f"📤 Загрузка файлов проекта в облако...")
        # Загружаем файлы проекта
        upload_folder(
            folder_path=str(project_dir),
            repo_id=repo_id,
            repo_type="space",
            ignore_patterns=[
                ".venv/**", "venv/**", "__pycache__/**", ".git/**",
                "scratch/**", "*.pyc", ".pytest_cache/**"
            ],
            token=token
        )

        public_url = f"https://huggingface.co/spaces/{repo_id}"
        direct_app_url = f"https://{username}-{space_name.replace('_', '-')}.hf.space"

        print("\n" + "=" * 60)
        print("🎉 ПОЗДРАВЛЯЕМ! PyForge успешно отправлен на хостинг 24/7!")
        print("=" * 60)
        print(f"🔗 Страница Space: {public_url}")
        print(f"⚡ Прямая ссылка на сайт: {direct_app_url}")
        print("⏳ Через 1-2 минуты контейнер соберется и сайт заработает онлайн!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Ошибка деплоя: {e}")

if __name__ == "__main__":
    main()
