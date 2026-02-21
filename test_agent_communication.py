import unittest

from agent_communication import ACLMessage, Agent, run_demo


class TestACLMessage(unittest.TestCase):
    def test_round_trip_serialization(self) -> None:
        message = ACLMessage(
            performative="request",
            sender="PlannerAgent",
            receiver="WorkerAgent",
            content='Run task "A"',
        )
        parsed = ACLMessage.parse(message.serialize())

        self.assertEqual(parsed.performative, "REQUEST")
        self.assertEqual(parsed.sender, "PlannerAgent")
        self.assertEqual(parsed.receiver, "WorkerAgent")
        self.assertEqual(parsed.content, 'Run task "A"')

    def test_parse_invalid_message_raises(self) -> None:
        with self.assertRaises(ValueError):
            ACLMessage.parse("invalid format")


class TestAgentCommunication(unittest.TestCase):
    def test_request_and_inform_actions_are_logged(self) -> None:
        logs = run_demo()
        joined = "\n".join(logs)

        self.assertIn("Sent REQUEST to WorkerAgent", joined)
        self.assertIn("Processing REQUEST action", joined)
        self.assertIn("Sent INFORM to PlannerAgent", joined)
        self.assertIn("Acknowledged INFORM update", joined)

    def test_wrong_receiver_message_is_ignored(self) -> None:
        logs = []
        agent = Agent("WorkerAgent", logs)
        raw = (
            '(performative REQUEST :sender PlannerAgent '
            ':receiver OtherAgent :content "Ignore this")'
        )
        agent.receive(raw)

        self.assertTrue(any("Ignored message for OtherAgent" in entry for entry in logs))

    def test_malformed_message_is_rejected(self) -> None:
        logs = []
        agent = Agent("WorkerAgent", logs)
        agent.receive("not acl")

        self.assertTrue(any("Rejected malformed ACL message" in entry for entry in logs))


if __name__ == "__main__":
    unittest.main()
