import unittest
import asyncio
from fastapi import HTTPException
from app.main import (
    dev_set_stars,
    dev_create_title,
    dev_create_task,
    dev_respond_idea,
    dev_list_users,
    get_daily_quests_endpoint,
    claim_quest_reward_endpoint,
    create_idea,
    list_ideas,
    DevSetStarsRequest,
    DevCreateTitleRequest,
    DevCreateTaskRequest,
    DevRespondIdeaRequest,
    ClaimQuestRequest,
    CreateIdeaRequest
)
from app.services.auth_service import AuthService
from app.services.dev_service import DevService
from app.services.daily_quests_service import DailyQuestsService
from app.data.practice_tasks import get_all_practice_tasks
from app.data.titles_catalog import get_all_titles

class TestDevAndQuests(unittest.TestCase):
    def setUp(self):
        try:
            self.creator_auth = AuthService.register("Chevels", "creatorpass123", "Chevels Creator")
        except ValueError:
            self.creator_auth = AuthService.login("Chevels", "creatorpass123")
        self.creator_token = self.creator_auth.get("token")

        try:
            self.normal_auth = AuthService.register("RegularDev", "userpass123", "Regular Dev")
        except ValueError:
            self.normal_auth = AuthService.login("RegularDev", "userpass123")
        self.normal_token = self.normal_auth.get("token")

    def test_dev_panel_creator_permission_strict(self):
        req = DevSetStarsRequest(username="RegularDev", amount=500)
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(dev_set_stars(req, authorization=f"Bearer {self.normal_token}"))
        self.assertEqual(ctx.exception.status_code, 403)

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(dev_set_stars(req, authorization=None))
        self.assertEqual(ctx.exception.status_code, 403)

        req2 = DevSetStarsRequest(username="Chevels", amount=1000)
        res = asyncio.run(dev_set_stars(req2, authorization=f"Bearer {self.creator_token}"))
        self.assertTrue(res.get("success"))
        self.assertGreaterEqual(res.get("user_stars"), 1000)

    def test_dev_exact_stars_and_target_user(self):
        req = DevSetStarsRequest(username="RegularDev", exact_amount=7777)
        res = asyncio.run(dev_set_stars(req, authorization=f"Bearer {self.creator_token}"))
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("user_stars"), 7777)

        reg_user = AuthService.get_user_by_token(self.normal_token)
        self.assertEqual(reg_user.get("stars"), 7777)

    def test_dev_create_title_and_auto_unlock(self):
        title_id = "test_creator_title_999"
        req = DevCreateTitleRequest(
            id=title_id,
            name="Тестовый Титул Бога",
            icon="⚡",
            rarity="mythic",
            cost_stars=9999,
            description="Эксклюзивный титул для тестов",
            color_class="from-amber-400 to-yellow-500",
            auto_unlock_for_creator=True
        )
        res = asyncio.run(dev_create_title(req, authorization=f"Bearer {self.creator_token}"))
        self.assertTrue(res.get("success"))

        chevels = AuthService.get_user_by_token(self.creator_token)
        self.assertIn(title_id, chevels.get("unlocked_titles", []))

    def test_dev_create_practice_task(self):
        task_id = "test_custom_dev_task_1"
        req = DevCreateTaskRequest(
            id=task_id,
            title="Сложение двух чисел",
            category="algorithms",
            difficulty="easy",
            xp_reward=150,
            stars_reward=50,
            description="Сложите a и b.",
            starter_code="def solution(a, b):\n    return a + b",
            test_cases=[{"input": "2 + 3", "expected": "5", "name": "Тест 2+3"}]
        )
        res = asyncio.run(dev_create_task(req, authorization=f"Bearer {self.creator_token}"))
        self.assertTrue(res.get("success"))

        tasks = get_all_practice_tasks()
        ids = [t["id"] for t in tasks]
        self.assertIn(task_id, ids)

    def test_dev_ideas_moderation_and_response(self):
        idea_req = CreateIdeaRequest(
            title="Добавить генератор API клиентов",
            category="tools",
            description="Было бы круто генерировать клиенты"
        )
        idea_res = asyncio.run(create_idea(idea_req, authorization=f"Bearer {self.normal_token}"))
        idea_id = idea_res.get("id")
        self.assertIsNotNone(idea_id)

        mod_req = DevRespondIdeaRequest(
            idea_id=idea_id,
            status="in_progress",
            dev_response="Отличная идея! Скоро будет."
        )
        mod_res = asyncio.run(dev_respond_idea(mod_req, authorization=f"Bearer {self.creator_token}"))
        self.assertTrue(mod_res.get("success"))

        ideas = asyncio.run(list_ideas())
        matched = [i for i in ideas if i["id"] == idea_id]
        self.assertTrue(len(matched) > 0)
        self.assertEqual(matched[0]["status"], "in_progress")
        self.assertIn("Отличная идея", matched[0]["dev_response"])

    def test_daily_quests_lifecycle(self):
        q_data = asyncio.run(get_daily_quests_endpoint(authorization=f"Bearer {self.normal_token}"))
        self.assertIn("quests", q_data)
        self.assertGreaterEqual(len(q_data["quests"]), 3)

        DailyQuestsService.record_activity("RegularDev", "solve_task", amount=2)
        q_data2 = asyncio.run(get_daily_quests_endpoint(authorization=f"Bearer {self.normal_token}"))
        solve_quest = next((q for q in q_data2["quests"] if q["id"] == "solve_task"), None)
        self.assertIsNotNone(solve_quest)
        self.assertTrue(solve_quest["completed"])

        initial_stars = AuthService.get_user_by_token(self.normal_token).get("stars", 0)
        claim_req = ClaimQuestRequest(quest_id=solve_quest["id"])
        claim_res = asyncio.run(claim_quest_reward_endpoint(claim_req, authorization=f"Bearer {self.normal_token}"))
        self.assertTrue(claim_res.get("success"))

        new_stars = AuthService.get_user_by_token(self.normal_token).get("stars", 0)
        self.assertEqual(new_stars, initial_stars + solve_quest["reward_stars"])

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(claim_quest_reward_endpoint(claim_req, authorization=f"Bearer {self.normal_token}"))
        self.assertEqual(ctx.exception.status_code, 400)

if __name__ == "__main__":
    unittest.main()
