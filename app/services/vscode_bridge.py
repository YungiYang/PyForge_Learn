"""
Сервис моста (Bridge) между VS Code и PyForge.
Позволяет инспектировать файлы на диске, анализировать воркспейсы и синхронизировать диагностику в реальном времени.
"""

import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from .live_error_mentor import LiveErrorMentorService

class VSCodeBridgeService:
    _last_inspections: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Возвращает статус подключения и статистику моста"""
        return {
            "status": "online",
            "bridge_version": "1.0.0",
            "server_url": "http://127.0.0.1:8000",
            "active_inspections": len(cls._last_inspections),
            "features": [
                "Real-time AST & Bytecode analysis",
                "Undefined variable & typo detection",
                "Missing import auto-resolution",
                "Async/Await verification",
                "1-click quick fixes"
            ]
        }

    @classmethod
    def inspect_file(cls, file_path: str) -> Dict[str, Any]:
        """Считывает файл с диска и проводит полный ИИ-анализ на ошибки"""
        target = Path(file_path).resolve()
        if not target.exists() or not target.is_file():
            return {
                "success": False,
                "file_path": str(target),
                "error": f"Файл не найден: {file_path}",
                "diagnostics": []
            }

        try:
            with open(target, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            analysis = LiveErrorMentorService.inspect_code(content)
            
            result = {
                "success": True,
                "file_path": str(target),
                "file_name": target.name,
                "file_size": target.stat().st_size,
                "last_modified": target.stat().st_mtime,
                "code": content,
                "analysis": analysis
            }
            cls._last_inspections[str(target)] = {
                "time": time.time(),
                "errors_count": len(analysis.get("issues", [])),
                "has_critical": analysis.get("has_syntax_error", False)
            }
            return result
        except Exception as e:
            return {
                "success": False,
                "file_path": str(target),
                "error": f"Ошибка чтения файла: {str(e)}",
                "diagnostics": []
            }

    @classmethod
    def inspect_workspace(cls, workspace_dir: str, max_files: int = 30) -> Dict[str, Any]:
        """Сканирует все .py файлы в указанной папке/проекте VS Code"""
        root = Path(workspace_dir).resolve()
        if not root.exists() or not root.is_dir():
            return {
                "success": False,
                "error": f"Папка проекта не найдена: {workspace_dir}",
                "scanned_files": []
            }

        results = []
        py_files = list(root.glob("**/*.py"))[:max_files]

        for py_path in py_files:
            # Игнорируем виртуальные окружения и кэши
            str_path = str(py_path)
            if any(ignore in str_path for ignore in [".venv", "venv", "__pycache__", ".git", ".tox"]):
                continue

            try:
                with open(py_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                
                # Быстрая проверка
                analysis = LiveErrorMentorService.inspect_code(content)
                issue_count = len(analysis.get("issues", []))
                results.append({
                    "file_path": str(py_path),
                    "relative_path": str(py_path.relative_to(root)),
                    "file_name": py_path.name,
                    "issues_count": issue_count,
                    "has_syntax_error": analysis.get("has_syntax_error", False),
                    "issues": analysis.get("issues", [])[:5]  # Топ 5 проблем
                })
            except Exception:
                pass

        return {
            "success": True,
            "workspace": str(root),
            "total_scanned": len(results),
            "files": sorted(results, key=lambda x: x["issues_count"], reverse=True)
        }

    @classmethod
    def apply_file_fix(cls, file_path: str, fixed_code: str) -> Dict[str, Any]:
        """Применяет исправленный код напрямую в файл на диске"""
        target = Path(file_path).resolve()
        if not target.exists() or not target.is_file():
            return {"success": False, "error": f"Файл не найден: {file_path}"}

        try:
            with open(target, "w", encoding="utf-8") as f:
                f.write(fixed_code)

            return {
                "success": True,
                "message": f"Файл {target.name} успешно обновлен на диске!",
                "file_path": str(target)
            }
        except Exception as e:
            return {"success": False, "error": f"Не удалось сохранить файл: {str(e)}"}
