import unittest
from datetime import date
from contextlib import redirect_stdout
from io import StringIO

from summer_camp_agent.activity import list_activities, load_activity
from summer_camp_agent.cli import main
from summer_camp_agent.demo import run_demo
from summer_camp_agent.engine import AnswerEngine
from summer_camp_agent.knowledge import KnowledgeBase


class ActivityProfileTest(unittest.TestCase):
    def test_builtin_profiles_cover_online_offline_and_hybrid(self):
        profiles = {profile.id: profile for profile in list_activities()}

        self.assertEqual(profiles["online-workshop"].formats, ("online",))
        self.assertEqual(profiles["offline-meetup"].formats, ("offline",))
        self.assertEqual(profiles["hybrid-summit"].formats, ("online", "offline"))
        self.assertEqual(profiles["summer-camp"].formats, ("online", "offline"))

    def test_activity_packs_do_not_share_answers(self):
        online = load_activity("online-workshop")
        offline = load_activity("offline-meetup")
        online_reply = AnswerEngine(
            KnowledgeBase.from_json(online.knowledge_path),
            organizer=online.organizer,
            notice_channel=online.notice_channel,
        ).answer("有线下会场吗？")
        offline_reply = AnswerEngine(
            KnowledgeBase.from_json(offline.knowledge_path),
            organizer=offline.organizer,
            notice_channel=offline.notice_channel,
        ).answer("有直播链接吗？")

        self.assertEqual(online_reply.intent, "format.online_only")
        self.assertIn("不设置线下会场", online_reply.reply)
        self.assertEqual(offline_reply.intent, "format.offline_only")
        self.assertIn("不提供线上直播", offline_reply.reply)
        self.assertNotIn("metax-tech.com", online_reply.reply)

    def test_expired_camp_fact_still_answers_on_the_message_date(self):
        engine = AnswerEngine(KnowledgeBase.from_default(), today=date(2026, 10, 27))

        current = engine.answer("线下夏令营在哪里举办？")
        historical = engine.answer("线下夏令营在哪里举办？", on_date=date(2026, 7, 29))

        self.assertEqual(current.action, "needs_info")
        self.assertEqual(historical.action, "auto_reply")
        self.assertEqual(historical.intent, "offline.location")

    def test_demo_command_passes_for_every_activity_format(self):
        rows = run_demo()

        self.assertGreaterEqual(len(rows), 8)
        self.assertTrue(all(row.ok for row in rows))
        covered = {fmt for row in rows for fmt in row.formats}
        self.assertEqual(covered, {"online", "offline"})

    def test_cli_lists_and_answers_selected_activity(self):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(["activities"])
        self.assertEqual(exit_code, 0)
        self.assertIn("online-workshop", output.getvalue())
        self.assertIn("offline-meetup", output.getvalue())
        self.assertIn("hybrid-summit", output.getvalue())

        ask_output = StringIO()
        with redirect_stdout(ask_output):
            ask_code = main(["ask", "--activity", "offline-meetup", "活动地点在哪里？"])
        self.assertEqual(ask_code, 0)
        self.assertIn("action: auto_reply", ask_output.getvalue())
        self.assertIn("intent: venue.address", ask_output.getvalue())
        self.assertIn("示例路 1 号", ask_output.getvalue())

    def test_unknown_activity_is_rejected(self):
        exit_code = main(["ask", "--activity", "missing-event", "你好"])
        self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
