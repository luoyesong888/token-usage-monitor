import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from api_usage_client import build_usage_payload  # noqa: E402


class APIUsageClientTests(unittest.TestCase):
    def test_builds_deepseek_payload_without_message_content(self):
        response = {
            "id": "req-deepseek-1",
            "model": "deepseek-chat",
            "choices": [{"message": {"content": "must not be recorded"}}],
            "usage": {
                "prompt_tokens": 100,
                "prompt_cache_hit_tokens": 60,
                "completion_tokens": 25,
                "total_tokens": 125,
            },
        }
        payload = build_usage_payload("deepseek", response, task_name="知识库问答")
        self.assertEqual(payload["model"], "deepseek-chat")
        self.assertEqual(payload["request_id"], "req-deepseek-1")
        self.assertEqual(payload["usage"]["prompt_cache_hit_tokens"], 60)
        self.assertNotIn("choices", payload)
        self.assertNotIn("must not be recorded", str(payload))

    def test_requires_usage_object(self):
        with self.assertRaises(ValueError):
            build_usage_payload("deepseek", {"id": "no-usage"})


if __name__ == "__main__":
    unittest.main()
