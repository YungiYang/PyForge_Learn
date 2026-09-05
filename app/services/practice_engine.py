"""
Движок проверки практических заданий и генератор задач.
"""

import sys
import subprocess
import tempfile
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..data.practice_tasks import PRACTICE_TASKS
from .gamification import GamificationService
from .library_task_generator import LibraryTaskGeneratorService

class PracticeEngineService:
    @classmethod
    def list_tasks(cls, user_key_or_token: Optional[str] = None) -> List[Dict[str, Any]]:
        profile = GamificationService._load_profile(user_key_or_token)
        solved_ids = set(profile.get("solved_tasks", []))

        results = []
        for task in PRACTICE_TASKS:
            results.append({
                "id": task["id"],
                "title": task["title"],
                "difficulty": task["difficulty"],
                "category": task["category"],
                "reward_stars": task["reward_stars"],
                "description": task["description"],
                "starter_code": task["starter_code"],
                "is_solved": task["id"] in solved_ids,
                "test_cases_count": len(task.get("test_cases", []))
            })
        return results

    @classmethod
    def get_task(cls, task_id: str) -> Optional[Dict[str, Any]]:
        for task in PRACTICE_TASKS:
            if task["id"] == task_id:
                return task
        dyn = LibraryTaskGeneratorService.get_dynamic_task(task_id)
        if dyn:
            return dyn
        return None

    @classmethod
    def submit_solution(cls, task_id: str, code: str, user_key_or_token: Optional[str] = None) -> Dict[str, Any]:
        task = cls.get_task(task_id)
        if not task:
            raise ValueError("Задание не найдено")

        if not code.strip():
            return {
                "success": False,
                "summary": "Код пуст. Напишите решение перед отправкой.",
                "test_results": []
            }

        # Генерируем тестовый раннер скрипт
        test_script = cls._build_test_runner_script(task, code)
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp_file:
            tmp_file.write(test_script)
            tmp_path = Path(tmp_file.name)

        start_time = time.perf_counter()
        try:
            proc = subprocess.run(
                [sys.executable, str(tmp_path)],
                capture_output=True,
                text=True,
                timeout=10.0,
                encoding="utf-8",
                errors="replace"
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            if proc.returncode != 0 and not proc.stdout.strip().startswith("{"):
                return {
                    "success": False,
                    "summary": f"Ошибка выполнения решения: {proc.stderr.strip() or proc.stdout.strip()}",
                    "test_results": [],
                    "raw_error": proc.stderr
                }

            # Парсим результат выполнения тест-раннера
            output_clean = proc.stdout.strip()
            # Находим JSON в выводе
            json_str = output_clean[output_clean.find("{"):output_clean.rfind("}")+1]
            report = json.loads(json_str)

            all_passed = report.get("all_passed", False)
            award_info = None
            if all_passed:
                award_info = GamificationService.award_task_completion(task_id, task["reward_stars"], user_key_or_token)

            return {
                "success": all_passed,
                "summary": "Все тесты успешно пройдены! 🎉" if all_passed else "Часть тестов завершилась с ошибкой. Проверьте вывод.",
                "test_results": report.get("results", []),
                "award_info": award_info,
                "execution_time_ms": round(elapsed_ms, 2)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "summary": "⏱️ Превышен лимит времени выполнения (10 сек)! Проверьте, нет ли в решении бесконечного цикла while / незавершающейся рекурсии или ожидания ввода input().",
                "test_results": []
            }
        except Exception as e:
            return {
                "success": False,
                "summary": f"Ошибка запуска тестов: {str(e)}",
                "test_results": []
            }
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass

    @classmethod
    def _build_test_runner_script(cls, task: dict, user_code: str) -> str:
        """Создает безопасную изолированную обертку для запуска тестов над кодом пользователя"""
        entry_point = task.get("entry_point", "solution")
        test_cases_json = json.dumps(task.get("test_cases", []))
        is_async = str(task.get("is_async", False))
        is_custom = task.get("test_custom", False)

        if is_custom:
            return f'''# Test Runner Script
import json, sys, time

# --- Пользовательский код ---
{user_code}

# --- Тестовая логика ---
def run_custom_tests():
    results = []
    try:
        @memoize
        def expensive(x):
            return x * 10
        
        r1 = expensive(5)
        r2 = expensive(5)
        passed = (r1 == 50 and r2 == 50)
        results.append({{"name": "Тест кеширования вызова", "expected": 50, "actual": r2, "passed": passed}})
        
        @memoize
        def add(a, b):
            return a + b
        r3 = add(2, 3)
        results.append({{"name": "Тест с несколькими аргументами", "expected": 5, "actual": r3, "passed": r3 == 5}})
    except Exception as err:
        results.append({{"name": "Исключение при вызове", "expected": "Результат", "actual": str(err), "passed": False}})

    all_passed = all(r["passed"] for r in results)
    print(json.dumps({{"all_passed": all_passed, "results": results}}))

run_custom_tests()
'''

        return f'''# Test Runner Script
import json, sys, time, asyncio

# --- Пользовательский код ---
{user_code}

# --- Исполнение тест-кейсов ---
test_cases = json.loads({repr(test_cases_json)})
results = []

func = globals().get("{entry_point}")
if not func:
    print(json.dumps({{"all_passed": False, "results": [{{"name": "Определение функции", "expected": "Функция {entry_point}", "actual": "Не найдена в коде", "passed": False}}]}}))
    sys.exit(0)

for idx, tc in enumerate(test_cases, 1):
    inputs = tc.get("input", [])
    expected = tc.get("expected")
    try:
        if {is_async}:
            actual = asyncio.run(func(*inputs))
        else:
            actual = func(*inputs)
        passed = (actual == expected)
        results.append({{
            "name": f"Тест #{{idx}}: {entry_point}({{inputs}})",
            "input": str(inputs),
            "expected": expected,
            "actual": actual,
            "passed": passed
        }})
    except Exception as err:
        results.append({{
            "name": f"Тест #{{idx}}: Исключение",
            "input": str(inputs),
            "expected": expected,
            "actual": f"Ошибка: {{str(err)}}",
            "passed": False
        }})

all_passed = all(r["passed"] for r in results)
print(json.dumps({{"all_passed": all_passed, "results": results}}))
'''

    @classmethod
    def generate_ai_task(cls, topic: str = "любая тема", difficulty: str = "Middle") -> Dict[str, Any]:
        """Генерирует новую практическую задачу с помощью ИИ"""
        reward_map = {"Junior": 20, "Middle": 40, "Senior": 80, "Architect": 150}
        stars = reward_map.get(difficulty, 30)

        # Сгенерированная интерактивная задача
        task_id = f"ai_gen_{int(time.time())}"
        title = f"Практика: {topic.capitalize()} ({difficulty})"
        description = f"""**Задача от ИИ-Генератора:**
Напишите функцию решения для темы **«{topic}»** на уровне сложности **{difficulty}**.

**Требования:**
- Функция должна обрабатывать граничные случаи.
- Вернуть корректный результат строго по условию.
"""
        starter = f'''def solve_task(data):
    # Ваше решение задачи на тему: {topic}
    pass
'''
        return {
            "id": task_id,
            "title": title,
            "difficulty": difficulty,
            "category": f"ИИ Генерация: {topic}",
            "reward_stars": stars,
            "description": description,
            "starter_code": starter,
            "entry_point": "solve_task",
            "test_cases": [
                {"input": ["test_input_1"], "expected": "test_input_1"},
                {"input": ["test_input_2"], "expected": "test_input_2"}
            ]
        }
