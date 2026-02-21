from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Callable, Dict, List, Optional


ACL_PATTERN = re.compile(
    r"\(performative\s+(?P<performative>\w+)\s+"
    r":sender\s+(?P<sender>[\w-]+)\s+"
    r":receiver\s+(?P<receiver>[\w-]+)\s+"
    r':content\s+"(?P<content>.*)"\)$'
)


@dataclass
class ACLMessage:
    """A minimal FIPA-ACL-style message container."""

    performative: str
    sender: str
    receiver: str
    content: str

    def serialize(self) -> str:
        escaped_content = self.content.replace('"', r'\"')
        return (
            f"(performative {self.performative.upper()} "
            f":sender {self.sender} "
            f":receiver {self.receiver} "
            f':content "{escaped_content}")'
        )

    @staticmethod
    def parse(raw_message: str) -> "ACLMessage":
        """Parse a serialized FIPA-ACL-style message."""
        match = ACL_PATTERN.match(raw_message.strip())
        if not match:
            raise ValueError(f"Invalid ACL message format: {raw_message}")

        content = match.group("content").replace(r'\"', '"')
        return ACLMessage(
            performative=match.group("performative").upper(),
            sender=match.group("sender"),
            receiver=match.group("receiver"),
            content=content,
        )


class Agent:
    def __init__(self, name: str, event_log: List[str]):
        self.name = name
        self.event_log = event_log
        self.handlers: Dict[str, Callable[[ACLMessage], None]] = {
            "REQUEST": self._handle_request,
            "INFORM": self._handle_inform,
        }

    def log(self, event: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.event_log.append(f"[{timestamp}] {self.name}: {event}")

    def send(self, other: "Agent", message: ACLMessage) -> None:
        if message.sender != self.name:
            raise ValueError(
                f"Sender mismatch: message sender '{message.sender}' does not match '{self.name}'"
            )
        self.log(f"Sent {message.performative.upper()} to {other.name} | {message.content}")
        other.receive(message.serialize())

    def receive(self, raw_message: str) -> None:
        try:
            message = ACLMessage.parse(raw_message)
        except ValueError as exc:
            self.log(f"Rejected malformed ACL message | {exc}")
            return

        if message.receiver != self.name:
            self.log(
                f"Ignored message for {message.receiver} from {message.sender} | {message.content}"
            )
            return

        self.log(
            f"Received {message.performative} from {message.sender} | {message.content}"
        )

        handler = self.handlers.get(message.performative)
        if handler:
            handler(message)
        else:
            self.log(f"No handler for performative: {message.performative}")

    def _handle_request(self, message: ACLMessage) -> None:
        self.log(f"Processing REQUEST action: {message.content}")

    def _handle_inform(self, message: ACLMessage) -> None:
        self.log(f"Acknowledged INFORM update: {message.content}")


def run_demo() -> List[str]:
    event_log: List[str] = []
    planner_agent = Agent("PlannerAgent", event_log)
    worker_agent = Agent("WorkerAgent", event_log)

    planner_agent.send(
        worker_agent,
        ACLMessage(
            performative="REQUEST",
            sender=planner_agent.name,
            receiver=worker_agent.name,
            content="Collect temperature readings in Zone A",
        ),
    )

    worker_agent.send(
        planner_agent,
        ACLMessage(
            performative="INFORM",
            sender=worker_agent.name,
            receiver=planner_agent.name,
            content="Zone A readings complete: avg=24.3C",
        ),
    )

    return event_log


def save_logs(path: str = "message_logs.txt", logs: Optional[List[str]] = None) -> None:
    logs = logs if logs is not None else run_demo()
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(logs) + "\n")


if __name__ == "__main__":
    generated_logs = run_demo()
    print("\n".join(generated_logs))
    save_logs(logs=generated_logs)
