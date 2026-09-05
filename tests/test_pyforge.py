"""
Автоматические тесты для PyForge (чистый Python standard library без внешних тестовых зависимостей).
"""

import unittest
import asyncio
import tempfile
from pathlib import Path

from app.main import (
    get_overview,
    get_architecture,
    get_frameworks,
    get_snippets,
    list_templates,
    search_all,
    run_sandbox_code,
    RunCodeRequest
)
from app.services.scaffolder import ScaffolderService
from app.services.sandbox import SandboxService
from app.services.ai_scout import AIScoutService

class TestPyForge(unittest.TestCase):

    def test_overview_endpoint(self):
        data = asyncio.run(get_overview())
        self.assertIn("stats", data)
        self.assertGreater(data["stats"]["frameworks_count"], 0)
        self.assertGreater(data["stats"]["templates_count"], 0)

    def test_architecture_endpoint(self):
        topics = asyncio.run(get_architecture())
        self.assertGreaterEqual(len(topics), 4)
        topic_ids = [t["id"] for t in topics]
        self.assertIn("project-layout", topic_ids)
        self.assertIn("clean-architecture", topic_ids)

    def test_frameworks_endpoint(self):
        frameworks = asyncio.run(get_frameworks())
        self.assertGreaterEqual(len(frameworks), 6)
        names = [f["name"] for f in frameworks]
        self.assertTrue(any("PySide6" in n for n in names))
        self.assertTrue(any("FastAPI" in n for n in names))

    def test_snippets_endpoint(self):
        snippets = asyncio.run(get_snippets())
        self.assertGreater(len(snippets), 0)

    def test_templates_and_scaffolder(self):
        templates = asyncio.run(list_templates())
        self.assertGreaterEqual(len(templates), 4)

        with tempfile.TemporaryDirectory() as tmpdir:
            res = ScaffolderService.generate_to_directory("pyside6_app", tmpdir, "test_pyside_project")
            self.assertEqual(res["status"], "success")
            project_dir = Path(tmpdir) / "test_pyside_project"
            self.assertTrue((project_dir / "src" / "main.py").exists())
            self.assertTrue((project_dir / "requirements.txt").exists())
            self.assertTrue((project_dir / "README.md").exists())

    def test_scaffolder_zip_generation(self):
        zip_bytes = ScaffolderService.generate_zip_bytes("fastapi_backend", "test_fastapi")
        self.assertGreater(zip_bytes.getbuffer().nbytes, 100)

    def test_sandbox_execution(self):
        req = RunCodeRequest(code='print("Hello from Sandbox!")')
        res = asyncio.run(run_sandbox_code(req))
        self.assertTrue(res["success"])
        self.assertIn("Hello from Sandbox!", res["stdout"])

    def test_sandbox_timeout(self):
        req = RunCodeRequest(code='import time\ntime.sleep(2)', timeout=0.5)
        res = asyncio.run(run_sandbox_code(req))
        self.assertFalse(res["success"])
        self.assertIn("Превышен лимит", res["stderr"])

    def test_search_endpoint(self):
        results = asyncio.run(search_all(q="pyside"))
        self.assertGreater(len(results), 0)

    def test_ai_scout_service(self):
        # 1. Suggestions
        suggestions = AIScoutService.get_suggestions()
        self.assertGreater(len(suggestions), 0)

        # 2. Semantic Smart Search for OCR
        res_ocr = AIScoutService.search("распознавание текста с картинок ocr", mode="smart")
        self.assertEqual(res_ocr["mode"], "smart")
        self.assertGreater(len(res_ocr["libraries"]), 0)
        lib_names = [l["name"] for l in res_ocr["libraries"]]
        self.assertTrue(any("EasyOCR" in n or "pytesseract" in n for n in lib_names))

        # 3. Semantic Smart Search for PDF
        res_pdf = AIScoutService.search("генерация pdf отчетов", mode="smart")
        self.assertGreater(len(res_pdf["libraries"]), 0)

    def test_ai_scout_endpoints(self):
        from app.main import get_ai_suggestions, scout_libraries, AIScoutRequest

        # Test suggestions API
        suggs = asyncio.run(get_ai_suggestions())
        self.assertGreater(len(suggs), 0)

        # Test scout search API
        req = AIScoutRequest(query="работа с excel и таблицами", mode="smart")
        res = asyncio.run(scout_libraries(req))
        self.assertIn("libraries", res)
        self.assertGreater(len(res["libraries"]), 0)
        lib_names = [l["name"] for l in res["libraries"]]
        self.assertTrue(any("openpyxl" in n for n in lib_names))

    def test_practice_and_gamification(self):
        from app.services.practice_engine import PracticeEngineService
        from app.services.gamification import GamificationService

        # 1. List tasks
        tasks = PracticeEngineService.list_tasks()
        self.assertGreaterEqual(len(tasks), 4)

        # 2. Test successful solution submission for palindrome task
        good_code = '''def is_palindrome(text: str) -> bool:
    clean = "".join(ch.lower() for ch in text if ch.isalnum())
    return clean == clean[::-1]
'''
        res_good = PracticeEngineService.submit_solution("task_palindrome", good_code)
        self.assertTrue(res_good["success"])
        self.assertGreater(len(res_good["test_results"]), 0)

        # 3. Test wrong solution
        bad_code = '''def is_palindrome(text: str) -> bool:
    return False
'''
        res_bad = PracticeEngineService.submit_solution("task_palindrome", bad_code)
        self.assertFalse(res_bad["success"])

        # 4. Check profile and stars
        profile = GamificationService.get_full_profile()
        self.assertIn("stars", profile)
        self.assertIn("shop_titles", profile)
        self.assertGreaterEqual(len(profile["shop_titles"]), 5)

    def test_live_error_mentor(self):
        from app.services.live_error_mentor import LiveErrorMentorService

        # 1. Missing colon SyntaxError
        err_code = "def calculate(a, b)\n    return a + b"
        report = LiveErrorMentorService.inspect_code(err_code)
        self.assertTrue(report["has_errors"])
        self.assertIn("двоеточие", report["message"].lower())
        self.assertIsNotNone(report["suggested_fix"])

        # 2. Assignment in if statement
        if_err_code = "if x = 5:\n    print(x)"
        report_if = LiveErrorMentorService.inspect_code(if_err_code)
        self.assertTrue(report_if["has_errors"])
        self.assertIn("==", report_if["message"] + report_if["hint"])

        # 3. Typo in variable name (difflib)
        typo_code = "user_counter = 42\nprint(user_countr + 1)\n"
        report_typo = LiveErrorMentorService.inspect_code(typo_code)
        self.assertTrue(report_typo["has_errors"])
        self.assertTrue(any("user_counter" in iss.get("advice", "") for iss in report_typo["issues"]))

        # 4. Missing import of common module (e.g. re)
        missing_import_code = "def test():\n    return re.findall(r'\\d+', 'abc 123')\n"
        report_import = LiveErrorMentorService.inspect_code(missing_import_code)
        self.assertTrue(report_import["has_errors"])
        self.assertTrue(any("import re" in iss.get("advice", "") for iss in report_import["issues"]))

        # 5. Clean code
        clean_code = "def calculate(a, b):\n    return a + b\n"
        report_clean = LiveErrorMentorService.inspect_code(clean_code)
        self.assertFalse(report_clean["has_errors"])
        self.assertEqual(report_clean["status"], "clean")

    def test_library_task_generator_and_submission(self):
        from app.services.library_task_generator import LibraryTaskGeneratorService
        from app.services.practice_engine import PracticeEngineService

        # 1. Supported libraries list
        libs = LibraryTaskGeneratorService.get_supported_libraries()
        self.assertGreaterEqual(len(libs), 10)
        lib_ids = [l["id"] for l in libs]
        self.assertIn("fastapi", lib_ids)
        self.assertIn("re", lib_ids)
        self.assertIn("kivy", lib_ids)
        self.assertIn("openpyxl", lib_ids)
        self.assertIn("pathlib", lib_ids)

        # 2. Generate task for 're'
        task_re = LibraryTaskGeneratorService.generate_random_task("re")
        self.assertIn("task_re_", task_re["id"])
        self.assertGreater(len(task_re["test_cases"]), 0)

        # Submit starter code solution (which is pre-implemented for our catalog tests)
        res = PracticeEngineService.submit_solution(task_re["id"], task_re["starter_code"])
        self.assertTrue(res["success"])
        self.assertGreater(len(res["test_results"]), 0)

        # 3. Generate task for 'fastapi'
        task_fastapi = LibraryTaskGeneratorService.generate_random_task("fastapi")
        self.assertIn("task_fastapi_", task_fastapi["id"])
        res_fastapi = PracticeEngineService.submit_solution(task_fastapi["id"], task_fastapi["starter_code"])
        self.assertTrue(res_fastapi["success"])

        # 4. Generate dynamic task for arbitrary library
        task_custom = LibraryTaskGeneratorService.generate_random_task("my_custom_lib", "Middle")
        self.assertEqual(task_custom["library"], "my_custom_lib")
        res_custom = PracticeEngineService.submit_solution(task_custom["id"], task_custom["starter_code"])
        self.assertTrue(res_custom["success"])

    def test_vscode_bridge_service(self):
        from app.services.vscode_bridge import VSCodeBridgeService

        # 1. Status
        status = VSCodeBridgeService.get_status()
        self.assertEqual(status["status"], "online")
        self.assertEqual(status["server_url"], "http://127.0.0.1:8000")

        # 2. Inspect file
        run_py_res = VSCodeBridgeService.inspect_file("run.py")
        self.assertTrue(run_py_res["success"])
        self.assertIn("code", run_py_res)
        self.assertIn("analysis", run_py_res)

        # 3. Inspect workspace
        ws_res = VSCodeBridgeService.inspect_workspace(".", max_files=15)
        self.assertTrue(ws_res["success"])
        self.assertGreater(ws_res["total_scanned"], 0)

        # 4. Apply file fix to a temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write("def foo():\n    pass\n")
            tmp_path = tmp.name

        try:
            fix_res = VSCodeBridgeService.apply_file_fix(tmp_path, "def foo():\n    return 'fixed'\n")
            self.assertTrue(fix_res["success"])
            with open(tmp_path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "def foo():\n    return 'fixed'\n")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

if __name__ == "__main__":
    unittest.main()


