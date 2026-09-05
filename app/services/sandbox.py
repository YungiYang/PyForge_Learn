"""
Сервис песочницы для безопасного выполнения пользовательского кода на Python с тайм-аутом.
"""

import sys
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any

class SandboxService:
    @staticmethod
    def run_code(code: str, timeout_seconds: float = 10.0) -> Dict[str, Any]:
        """
        Запускает фрагмент Python-кода во временном процессе с ограничением по времени (10 сек).
        """
        if not code.strip():
            return {
                "success": False,
                "stdout": "",
                "stderr": "Код пуст. Введите код для запуска.",
                "execution_time_ms": 0
            }

        # Предупреждение об input()
        if "input(" in code:
            code_wrapper = "# Mock input for non-interactive execution\ndef input(prompt=''): return 'test_input'\n" + code
        else:
            code_wrapper = code

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(code_wrapper)
            temp_file_path = Path(temp_file.name)

        start_time = time.perf_counter()
        try:
            process = subprocess.run(
                [sys.executable, str(temp_file_path)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                encoding="utf-8",
                errors="replace"
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode,
                "execution_time_ms": round(elapsed_ms, 2)
            }
        except subprocess.TimeoutExpired:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            hint = ""
            if "while" in code:
                hint = " Вероятно, в коде есть бесконечный цикл (проверьте условие `while` и инкремент счетчика `i += 1`)."
            elif "input(" in code:
                hint = " Функция `input()` ожидает ввода в консоль, что приводит к зависанию."
            return {
                "success": False,
                "stdout": "",
                "stderr": f"⏱️ Превышен лимит времени выполнения ({timeout_seconds:.1f} сек)!{hint}",
                "return_code": -1,
                "execution_time_ms": round(elapsed_ms, 2)
            }
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Ошибка выполнения: {str(e)}",
                "return_code": -1,
                "execution_time_ms": round(elapsed_ms, 2)
            }
        finally:
            try:
                temp_file_path.unlink(missing_ok=True)
            except Exception:
                pass
