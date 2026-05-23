"""Audit logging for the policy runtime."""

import json
from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG_PATH = Path(__file__).parent.parent / "audit_log.jsonl"


def log_entry(
    decision_type: str,
    summary: str,
    details: str,
    policy_result: dict | None = None,
) -> None:
    """Write a structured audit log entry."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision_type": decision_type,
        "summary": summary,
        "details": details,
    }
    if policy_result:
        entry["policy_result"] = {
            "status": policy_result.get("status"),
            "checks": policy_result.get("checks"),
            "required_approver": policy_result.get("required_approver"),
        }

    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def get_recent_entries(n: int = 10) -> list[dict]:
    """Read the most recent N audit log entries."""
    if not AUDIT_LOG_PATH.exists():
        return []

    entries = []
    with open(AUDIT_LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    return entries[-n:]
