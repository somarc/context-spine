import unittest

from helpers import load_script_module


verify = load_script_module("verify", "verify.py")


class VerifyHelpersTest(unittest.TestCase):
    def test_tail_lines_returns_last_nonempty_lines(self):
        payload = verify.tail_lines("one\n\ntwo\nthree\n", limit=2)
        self.assertEqual(payload, ["two", "three"])

    def test_summarize_output_prefers_stdout_then_stderr(self):
        self.assertEqual(verify.summarize_output("alpha\nbeta\n", "", 0), "beta")
        self.assertEqual(verify.summarize_output("", "error\nboom\n", 1), "boom")
        self.assertEqual(verify.summarize_output("", "", 2), "Command exited with code 2.")

    def test_verification_event_payload_condenses_steps(self):
        class Handle:
            run_id = "ctx-demo"
            path = "/tmp/demo.json"

        payload = verify.verification_event_payload(
            Handle(),
            [{"name": "tests", "status": "success", "summary": "OK", "duration_seconds": 0.2}],
            [],
            "Verification passed.",
        )

        self.assertEqual(payload["source_command"], "context:verify")
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["run_id"], "ctx-demo")
        self.assertEqual(payload["verification_steps"][0]["name"], "tests")


if __name__ == "__main__":
    unittest.main()
