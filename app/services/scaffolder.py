"""
Сервис сборщика и генератора проектов (Scaffolder).
Поддерживает генерацию напрямую в локальную папку или отдачу ZIP-архива.
"""

import io
import zipfile
from pathlib import Path
from typing import Dict, Optional
from ..data.generator_templates import PROJECT_TEMPLATES

class ScaffolderService:
    @staticmethod
    def get_template(template_id: str) -> Optional[dict]:
        return PROJECT_TEMPLATES.get(template_id)

    @staticmethod
    def list_templates() -> list[dict]:
        results = []
        for tid, tdata in PROJECT_TEMPLATES.items():
            results.append({
                "id": tid,
                "name": tdata["name"],
                "category": tdata["category"],
                "description": tdata["description"],
                "icon": tdata["icon"],
                "files_count": len(tdata["files"]),
                "file_names": list(tdata["files"].keys())
            })
        return results

    @classmethod
    def generate_to_directory(cls, template_id: str, target_dir: str, project_name: Optional[str] = None) -> dict:
        template = cls.get_template(template_id)
        if not template:
            raise ValueError(f"Шаблон '{template_id}' не найден.")

        target_path = Path(target_dir).resolve()
        if project_name:
            target_path = target_path / project_name

        target_path.mkdir(parents=True, exist_ok=True)

        created_files = []
        for relative_file_path, content in template["files"].items():
            file_dest = target_path / relative_file_path
            file_dest.parent.mkdir(parents=True, exist_ok=True)
            file_dest.write_text(content, encoding="utf-8")
            created_files.append(str(file_dest))

        return {
            "status": "success",
            "message": f"Проект '{template['name']}' успешно сгенерирован!",
            "directory": str(target_path),
            "files_created": created_files
        }

    @classmethod
    def generate_zip_bytes(cls, template_id: str, project_name: Optional[str] = "python_project") -> io.BytesIO:
        template = cls.get_template(template_id)
        if not template:
            raise ValueError(f"Шаблон '{template_id}' не найден.")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for relative_path, content in template["files"].items():
                archive_path = f"{project_name}/{relative_path}"
                zip_file.writestr(archive_path, content)

        zip_buffer.seek(0)
        return zip_buffer
