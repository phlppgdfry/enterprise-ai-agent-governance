import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent import Agent, evaluate, submit_request


class AgentTests(unittest.TestCase):
    def test_evaluation_gate(self):
        result = evaluate()
        self.assertGreaterEqual(result["total"], 20)
        self.assertEqual(result["total"], result["passed"], result)

    def test_citations_resolve_to_committed_sources(self):
        root = Path(__file__).resolve().parents[1]
        for doc in Agent().knowledge:
            if doc["published"]:
                path, anchor = doc["source"].split("#")
                content = (root / path).read_text().casefold()
                self.assertIn("## " + anchor, content)

    def test_acl_before_matching(self):
        self.assertEqual("abstain", Agent().answer("escalatie", "employee").outcome)
        self.assertEqual("answered", Agent().answer("escalatie", "approver").outcome)
        self.assertNotIn("twee werkdagen", Agent().answer("escalatie", "employee").text)

    def test_unpublished_content_is_never_retrieved(self):
        answer = Agent().answer("onkosten")
        self.assertNotIn("500", answer.text)
        self.assertNotIn("unpublished", answer.citations)

    def test_missing_and_unknown_roles(self):
        for question in ["", " ", None, "x" * 2001]:
            with self.assertRaises(ValueError):
                Agent().answer(question)
        with self.assertRaises(ValueError):
            Agent().answer("onkosten", "admin")

    def test_ambiguous_match_requires_clarification(self):
        self.assertEqual("clarify", Agent().answer("onkosten en toegang").outcome)

    @patch("urllib.request.urlopen")
    def test_no_network_without_confirmation(self, network):
        with self.assertRaises(ValueError):
            submit_request("x", "materials", 1, confirmed=False, token="demo-alice", idempotency_key="x")
        network.assert_not_called()

    @patch("urllib.request.urlopen")
    def test_no_privileged_identity_or_external_destination(self, network):
        for kwargs in [dict(token="demo-manager"), dict(base_url="https://example.com"),
                       dict(base_url="http://127.0.0.1:5088@evil.example"), dict(idempotency_key="")]:
            args = dict(confirmed=True, token="demo-alice", idempotency_key="x")
            args.update(kwargs)
            with self.assertRaises(ValueError):
                submit_request("x", "materials", 1, **args)
        network.assert_not_called()

    @patch("urllib.request.urlopen")
    def test_tool_forwards_user_identity_and_retry_key(self, network):
        network.return_value.__enter__.return_value.read.return_value = b'{"status":"pending"}'
        result = submit_request("x", "materials", 1, confirmed=True, token="demo-bob", idempotency_key="stable")
        request = network.call_args.args[0]
        self.assertEqual("Bearer demo-bob", request.get_header("Authorization"))
        self.assertEqual("stable", request.get_header("Idempotency-key"))
        self.assertEqual("pending", result["status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
