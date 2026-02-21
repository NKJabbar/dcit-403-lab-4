# DCIT 403 Lab 4 - Agent Communication Using FIPA-ACL

This lab demonstrates inter-agent communication using a minimal FIPA-ACL style message format.

## Deliverables

- `agent_communication.py`: Agent communication code.
- `message_logs.txt`: Generated message logs for REQUEST and INFORM exchanges.
- `test_agent_communication.py`: Automated tests for ACL parsing and agent behavior.

## What is implemented

1. ACL message exchange between two agents (`PlannerAgent` and `WorkerAgent`).
2. REQUEST and INFORM performatives.
3. Parsing incoming FIPA-ACL style messages and triggering corresponding agent actions.
4. Handling malformed messages and wrong receiver routing.
5. Reproducible timestamped logs for consistent grading outputs.

## Run demo

```bash
python3 agent_communication.py
```

The script prints generated logs and writes them to `message_logs.txt`.

## Run tests

```bash
python3 -m unittest -v
```
