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

    def test_auth_service(self):
        from app.services.auth_service import AuthService
        import time

        test_user = f"tester_{int(time.time())}"
        # 1. Register new user
        reg_res = AuthService.register(test_user, "password123", "Тестовый Разработчик")
        self.assertTrue(reg_res["success"])
        self.assertIn("token", reg_res)
        self.assertEqual(reg_res["user"]["username"], test_user)

        # 2. Reject duplicate registration
        with self.assertRaises(ValueError):
            AuthService.register(test_user, "password123")

        # 3. Reject short password
        with self.assertRaises(ValueError):
            AuthService.register(f"user_short_{int(time.time())}", "12")

        # 4. Login with correct password
        login_res = AuthService.login(test_user, "password123")
        self.assertTrue(login_res["success"])
        self.assertIn("token", login_res)

        # 5. Login with incorrect password
        with self.assertRaises(ValueError):
            AuthService.login(test_user, "wrong_pass")

        # 6. Retrieve user by token
        user = AuthService.get_user_by_token(login_res["token"])
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], test_user)

        # 7. Logout
        logout_ok = AuthService.logout(login_res["token"])
        self.assertTrue(logout_ok)
        self.assertIsNone(AuthService.get_user_by_token(login_res["token"]))

    def test_leaderboard_service(self):
        from app.services.leaderboard_service import LeaderboardService
        from app.services.auth_service import AuthService
        import time

        uname = f"lb_user_{int(time.time())}"
        AuthService.register(uname, "password123", "Leaderboard Tester")

        leaderboard = LeaderboardService.get_leaderboard(current_username=uname)
        self.assertTrue(leaderboard["success"])
        self.assertGreaterEqual(leaderboard["total_players"], 1)
        self.assertGreaterEqual(len(leaderboard["rankings"]), 1)
        self.assertEqual(leaderboard["rankings"][0]["rank"], 1)

        # Check ranking order (descending by stars)
        stars = [r["stars"] for r in leaderboard["rankings"]]
        self.assertEqual(stars, sorted(stars, reverse=True))

        # Check current user rank info
        self.assertIsNotNone(leaderboard["current_user_rank"])
        self.assertEqual(leaderboard["current_user_rank"]["username"], uname)

    def test_forum_service(self):
        from app.services.forum_service import ForumService
        from app.services.auth_service import AuthService
        import time

        u_author = f"author_{int(time.time())}"
        u_commenter = f"comm_{int(time.time())}"
        AuthService.register(u_author, "password123", "Author Dev")
        AuthService.register(u_commenter, "password123", "Commenter Dev")

        # 1. Categories
        cats = ForumService.get_categories()
        self.assertGreaterEqual(len(cats), 5)

        # 2. Create new topic
        new_topic = ForumService.create_topic(
            title="Тестовый вопрос по FastAPI и Asyncio",
            category="web",
            content="Как настроить middleware для проверки токенов?",
            author_username=u_author,
            tags=["fastapi", "test"]
        )
        self.assertIn("topic_", new_topic["id"])
        self.assertEqual(new_topic["category"], "web")

        # 3. List topics
        topics = ForumService.list_topics(category="web")
        self.assertGreaterEqual(len(topics), 1)

        # 4. Get topic details (increases views)
        topic_detail = ForumService.get_topic(new_topic["id"])
        self.assertIsNotNone(topic_detail)
        self.assertGreaterEqual(topic_detail["views"], 1)

        # 5. Add comment
        comment = ForumService.add_comment(
            topic_id=new_topic["id"],
            content="Используйте `Depends` или `HTTPBearer`!",
            author_username=u_commenter
        )
        self.assertIn("comm_", comment["id"])

        # 6. Upvote topic
        upvote_res = ForumService.upvote_topic(new_topic["id"], u_commenter)
        self.assertTrue(upvote_res["success"])
        self.assertTrue(upvote_res["voted"])

    def test_ideas_service(self):
        from app.services.ideas_service import IdeasService
        from app.services.auth_service import AuthService
        import time

        u_idea = f"idea_user_{int(time.time())}"
        u_voter = f"voter_{int(time.time())}"
        AuthService.register(u_idea, "password123", "Idea Creator")
        AuthService.register(u_voter, "password123", "Voter")

        # 1. Submit new idea
        new_idea = IdeasService.submit_idea(
            title="Интеграция с GitHub Gist",
            description="Возможность экспортировать сниппеты прямо в свой аккаунт GitHub Gist.",
            category="tools",
            author_username=u_idea
        )
        self.assertIn("idea_", new_idea["id"])
        self.assertEqual(new_idea["status"], "under_review")

        # 2. List ideas
        ideas = IdeasService.list_ideas(status="all", sort_by="popular")
        self.assertGreaterEqual(len(ideas), 1)

        # 3. Vote for idea
        vote_res = IdeasService.vote_idea(new_idea["id"], u_voter)
        self.assertTrue(vote_res["success"])
        self.assertTrue(vote_res["has_voted"])

        # 4. Toggle vote off
        unvote_res = IdeasService.vote_idea(new_idea["id"], u_voter)
        self.assertTrue(unvote_res["success"])
        self.assertFalse(unvote_res["has_voted"])

    def test_auth_and_gamification_integration(self):
        from app.services.auth_service import AuthService
        from app.services.gamification import GamificationService
        from app.services.practice_engine import PracticeEngineService
        import time

        uname = f"gamer_{int(time.time())}"
        reg = AuthService.register(uname, "pass123", "Gamer Pro")
        token = reg["token"]

        # User starts with 0 stars
        profile = GamificationService.get_full_profile(token)
        self.assertEqual(profile["stars"], 0)

        # Solve task with user token
        code = '''def is_palindrome(text: str) -> bool:
    clean = "".join(ch.lower() for ch in text if ch.isalnum())
    return clean == clean[::-1]
'''
        res = PracticeEngineService.submit_solution("task_palindrome", code, token)
        self.assertTrue(res["success"])
        self.assertIsNotNone(res["award_info"])
        self.assertGreater(res["award_info"]["awarded_stars"], 0)

        # Profile updated
        updated_profile = GamificationService.get_full_profile(token)
        self.assertEqual(updated_profile["stars"], res["award_info"]["awarded_stars"])

    def test_api_endpoints_auth_forum_ideas_leaderboard(self):
        from app.main import (
            auth_register,
            auth_login,
            auth_me,
            get_leaderboard,
            get_forum_categories,
            list_forum_topics,
            create_forum_topic,
            add_forum_comment,
            upvote_forum_topic,
            list_ideas,
            create_idea,
            vote_idea,
            RegisterRequest,
            LoginRequest,
            CreateTopicRequest,
            AddCommentRequest,
            UpvoteTopicRequest,
            CreateIdeaRequest,
            VoteIdeaRequest
        )
        import time

        # 1. Register API
        u = f"api_user_{int(time.time())}"
        reg_dto = RegisterRequest(username=u, password="password123", display_name="API User")
        reg_res = asyncio.run(auth_register(reg_dto))
        self.assertTrue(reg_res["success"])
        token = reg_res["token"]

        # 2. Login API
        login_dto = LoginRequest(username=u, password="password123")
        login_res = asyncio.run(auth_login(login_dto))
        self.assertTrue(login_res["success"])

        # 3. Me API
        me_res = asyncio.run(auth_me(authorization=f"Bearer {token}", token=None))
        self.assertTrue(me_res["success"])
        self.assertEqual(me_res["user"]["username"], u)

        # 4. Leaderboard API
        lb_res = asyncio.run(get_leaderboard(authorization=f"Bearer {token}", token=None))
        self.assertTrue(lb_res["success"])
        self.assertIsNotNone(lb_res["current_user_rank"])
        self.assertEqual(lb_res["current_user_rank"]["username"], u)

        # 5. Forum Categories API
        cats = asyncio.run(get_forum_categories())
        self.assertGreater(len(cats), 0)

        # 6. Create Forum Topic API
        topic_dto = CreateTopicRequest(
            title="FastAPI Route Testing",
            category="web",
            content="Testing route creation and comments.",
            tags=["fastapi", "routes"]
        )
        created_topic = asyncio.run(create_forum_topic(topic_dto, authorization=f"Bearer {token}"))
        self.assertIn("topic_", created_topic["id"])

        # 7. Add Comment API
        comm_dto = AddCommentRequest(topic_id=created_topic["id"], content="Отличный вопрос!")
        created_comm = asyncio.run(add_forum_comment(comm_dto, authorization=f"Bearer {token}"))
        self.assertIn("comm_", created_comm["id"])

        # 8. Upvote Topic API
        upv_dto = UpvoteTopicRequest(topic_id=created_topic["id"])
        upv_res = asyncio.run(upvote_forum_topic(upv_dto, authorization=f"Bearer {token}"))
        self.assertTrue(upv_res["success"])

        # 9. Create Idea API
        idea_dto = CreateIdeaRequest(title="Новая фича в конструктор", description="Подробности идеи", category="general")
        created_idea = asyncio.run(create_idea(idea_dto, authorization=f"Bearer {token}"))
        self.assertIn("idea_", created_idea["id"])

        # 10. List Ideas API
        ideas = asyncio.run(list_ideas(category="all", status="all", sort_by="popular"))
        self.assertGreater(len(ideas), 0)

        # 11. Vote Idea API
        vote_dto = VoteIdeaRequest(idea_id=created_idea["id"])
        vote_res = asyncio.run(vote_idea(vote_dto, authorization=f"Bearer {token}"))
        self.assertTrue(vote_res["success"])

if __name__ == "__main__":
    unittest.main()


