import unittest

from agent_communication import ACLMessage, Agent, EventLogger, run_demo


class TestACLMessage(unittest.TestCase):
    def test_round_trip_serialization(self) -> None:
        message = ACLMessage(
            performative="request",
            sender="PlannerAgent",
            receiver="WorkerAgent",
            content='Run task "A" with path C:\\temp',
        )
        parsed = ACLMessage.parse(message.serialize())

        self.assertEqual(parsed.performative, "REQUEST")
        self.assertEqual(parsed.sender, "PlannerAgent")
        self.assertEqual(parsed.receiver, "WorkerAgent")
        self.assertEqual(parsed.content, 'Run task "A" with path C:\\temp')

    def test_parse_invalid_message_raises(self) -> None:
        with self.assertRaises(ValueError):
            ACLMessage.parse("invalid format")

    def test_parse_unsupported_performative_raises(self) -> None:
        raw = '(performative PROPOSE :sender A1 :receiver A2 :content "hello")'
        with self.assertRaises(ValueError):
            ACLMessage.parse(raw)


class TestAgentCommunication(unittest.TestCase):
    def test_request_and_inform_actions_are_logged(self) -> None:
        logs = run_demo()
        joined = "\n".join(logs)

        self.assertIn("Sent REQUEST to WorkerAgent", joined)
        self.assertIn("Processing REQUEST action", joined)
        self.assertIn("Sent INFORM to PlannerAgent", joined)
        self.assertIn("Acknowledged INFORM update", joined)

    def test_wrong_receiver_message_is_ignored(self) -> None:
        logger = EventLogger()
        agent = Agent("WorkerAgent", logger)
        raw = (
            '(performative REQUEST :sender PlannerAgent '
            ':receiver OtherAgent :content "Ignore this")'
        )
        agent.receive(raw)

        self.assertTrue(
            any("Ignored message for OtherAgent" in entry for entry in logger.entries)
        )

    def test_malformed_message_is_rejected(self) -> None:
        logger = EventLogger()
        agent = Agent("WorkerAgent", logger)
        agent.receive("not acl")

        self.assertTrue(
            any("Rejected malformed ACL message" in entry for entry in logger.entries)
        )

    def test_demo_logs_have_deterministic_timestamps(self) -> None:
        logs = run_demo()
        self.assertEqual(logs[0][:21], "[2026-01-01 10:00:00]")
        self.assertEqual(logs[-1][:21], "[2026-01-01 10:00:05]")


if __name__ == "__main__":
    unittest.main()
