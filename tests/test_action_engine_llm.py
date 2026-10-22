"""Tes jalur LLM ActionPlanEngine (Gemini -> Groq -> template).

Semua panggilan jaringan dimock via unittest.mock pada requests.post;
tidak ada request HTTP nyata dan tidak ada API key asli yang dipakai.
"""

import json
import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.action_engine import ActionPlanEngine

ENV_KEYS = ("GEMINI_API_KEY", "GROQ_API_KEY", "GEMINI_MODEL", "GROQ_MODEL")

LLM_OUTPUT = {
    "root_cause_analysis": [
        "Aspek Kemasan: wadah berkuah bocor saat pengantaran (root cause dari LLM)."
    ],
    "kitchen_action_checklist": [
        "CHECKLIST DARI LLM: segel silang semua tutup mangkok berkuah.",
        "CHECKLIST DARI LLM: pisahkan kuah ke wadah terpisah.",
    ],
    "sop_recommendations": ["SOP DARI LLM: tilt-test sebelum serah ke driver."],
}


def _eval_results():
    return {
        "kitchen_health_score": 62.4,
        "aspect_breakdown": {
            "rasa": {
                "positive": 10, "neutral": 2, "negative": 3,
                "total_mentioned": 15, "satisfaction_score": 73.3,
                "negative_rate": 20.0,
            },
            "kemasan": {
                "positive": 4, "neutral": 1, "negative": 9,
                "total_mentioned": 14, "satisfaction_score": 32.1,
                "negative_rate": 64.3,
            },
            "pelayanan": {
                "positive": 8, "neutral": 1, "negative": 5,
                "total_mentioned": 14, "satisfaction_score": 60.7,
                "negative_rate": 35.7,
            },
        },
    }


COMPLAINTS = ["Kemasan tumpah kuah di jalan", "Driver menunggu terlalu lama"]


def _gemini_response(text, status=200):
    resp = Mock()
    resp.status_code = status
    resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": text}]}}]
    }
    return resp


def _groq_response(text, status=200):
    resp = Mock()
    resp.status_code = status
    resp.json.return_value = {
        "choices": [{"message": {"content": text}}]
    }
    return resp


class TestActionEngineLLM(unittest.TestCase):
    def setUp(self):
        self._saved_env = {k: os.environ.get(k) for k in ENV_KEYS}
        for key in ENV_KEYS:
            os.environ.pop(key, None)

    def tearDown(self):
        for key, value in self._saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_no_key_uses_template(self):
        engine = ActionPlanEngine()
        with patch("src.action_engine.requests.post") as mock_post:
            plan = engine.generate_action_plan(
                "Resto Uji", _eval_results(), COMPLAINTS
            )
        mock_post.assert_not_called()
        self.assertEqual(plan["generation_mode"], "template")
        self.assertIsNone(plan["llm_provider"])
        self.assertTrue(plan["kitchen_action_checklist"])
        self.assertTrue(plan["root_cause_analysis"])
        self.assertTrue(plan["sop_recommendations"])
        self.assertIn("priority_risk_areas", plan)
        self.assertIn("summary_note", plan)

    def test_gemini_success_uses_llm(self):
        os.environ["GEMINI_API_KEY"] = "dummy-gemini-key"
        engine = ActionPlanEngine()
        with patch(
            "src.action_engine.requests.post",
            return_value=_gemini_response(json.dumps(LLM_OUTPUT)),
        ) as mock_post:
            plan = engine.generate_action_plan(
                "Resto Uji", _eval_results(), COMPLAINTS
            )
        self.assertEqual(plan["generation_mode"], "llm")
        self.assertEqual(plan["llm_provider"], "gemini")
        self.assertEqual(
            plan["kitchen_action_checklist"], LLM_OUTPUT["kitchen_action_checklist"]
        )
        self.assertEqual(plan["root_cause_analysis"], LLM_OUTPUT["root_cause_analysis"])
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs.get("timeout"), 30)

    def test_gemini_broken_response_falls_back_to_template(self):
        os.environ["GEMINI_API_KEY"] = "dummy-gemini-key"
        engine = ActionPlanEngine()
        with patch(
            "src.action_engine.requests.post",
            return_value=_gemini_response("ini bukan JSON sama sekali {"),
        ):
            plan = engine.generate_action_plan(
                "Resto Uji", _eval_results(), COMPLAINTS
            )
        self.assertEqual(plan["generation_mode"], "template")
        self.assertIsNone(plan["llm_provider"])
        self.assertTrue(plan["kitchen_action_checklist"])

    def test_gemini_failure_then_groq_success(self):
        os.environ["GEMINI_API_KEY"] = "dummy-gemini-key"
        os.environ["GROQ_API_KEY"] = "dummy-groq-key"
        engine = ActionPlanEngine()
        with patch(
            "src.action_engine.requests.post",
            side_effect=[
                _gemini_response("", status=500),
                _groq_response(json.dumps(LLM_OUTPUT)),
            ],
        ):
            plan = engine.generate_action_plan(
                "Resto Uji", _eval_results(), COMPLAINTS
            )
        self.assertEqual(plan["generation_mode"], "llm")
        self.assertEqual(plan["llm_provider"], "groq")
        self.assertEqual(
            plan["kitchen_action_checklist"], LLM_OUTPUT["kitchen_action_checklist"]
        )

    def test_cache_same_payload_single_post(self):
        os.environ["GEMINI_API_KEY"] = "dummy-gemini-key"
        engine = ActionPlanEngine()
        with patch(
            "src.action_engine.requests.post",
            return_value=_gemini_response(json.dumps(LLM_OUTPUT)),
        ) as mock_post:
            plan1 = engine.generate_action_plan(
                "Resto Uji", _eval_results(), COMPLAINTS
            )
            plan2 = engine.generate_action_plan(
                "Resto Uji", _eval_results(), COMPLAINTS
            )
        self.assertEqual(mock_post.call_count, 1)
        self.assertEqual(plan1["generation_mode"], "llm")
        self.assertEqual(plan2["generation_mode"], "llm")
        self.assertEqual(
            plan2["kitchen_action_checklist"], LLM_OUTPUT["kitchen_action_checklist"]
        )


if __name__ == "__main__":
    unittest.main()
