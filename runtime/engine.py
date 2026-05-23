"""Policy evaluation engine. Reads policies and runs all checks against trade proposals."""

import json
from pathlib import Path

from runtime.checks import (
    check_approval_tier,
    check_concentration,
    check_confidence,
    check_duration,
    check_government_minimum,
    check_liquidity,
    load_balances,
)


POLICIES_DIR = Path(__file__).parent.parent / "policies"


def load_policies() -> dict:
    """Load all policy files and return their contents."""
    policies = {}
    for policy_file in POLICIES_DIR.glob("*.md"):
        policies[policy_file.stem] = policy_file.read_text()
    return policies


def evaluate_trade(trade: dict) -> dict:
    """
    Run all policy checks against a proposed trade.

    Args:
        trade: dict with keys: from_instrument, to_instrument, amount, rationale, confidence

    Returns:
        dict with status (APPROVED/BLOCKED/ESCALATED), checks list, required_approver, reasoning
    """
    balances = load_balances()
    confidence = trade.get("confidence", 0)

    # Run all checks
    checks = [
        check_liquidity(trade, balances),
        check_duration(trade, balances),
        check_concentration(trade, balances),
        check_government_minimum(trade, balances),
        check_approval_tier(trade),
        check_confidence(confidence),
    ]

    # Determine overall status
    has_fail = any(c["status"] == "fail" for c in checks)
    has_escalate = any(c["status"] == "escalate" for c in checks)

    if has_fail:
        status = "BLOCKED"
    elif has_escalate:
        status = "ESCALATED"
    else:
        status = "APPROVED"

    # Determine required approver
    required_approver = None
    for c in checks:
        if c.get("required_approver"):
            required_approver = c["required_approver"]
            break

    # If confidence caused escalation but no other approver set
    if status == "ESCALATED" and not required_approver:
        required_approver = "treasury_manager"

    # Build reasoning
    failed_checks = [c for c in checks if c["status"] == "fail"]
    escalated_checks = [c for c in checks if c["status"] == "escalate"]

    if status == "BLOCKED":
        reasoning = "Trade BLOCKED due to policy violations: " + "; ".join(
            f"{c['name']}: {c['detail']}" for c in failed_checks
        )
    elif status == "ESCALATED":
        reasoning = "Trade requires human approval: " + "; ".join(
            f"{c['name']}: {c['detail']}" for c in escalated_checks
        )
    else:
        reasoning = "All policy checks passed. Trade is approved for execution."

    return {
        "status": status,
        "checks": checks,
        "required_approver": required_approver,
        "reasoning": reasoning,
        "trade": {
            "from": trade["from_instrument"],
            "to": trade["to_instrument"],
            "amount": trade["amount"],
            "confidence": confidence,
        },
    }
