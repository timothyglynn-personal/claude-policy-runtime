"""Tool definitions for the Claude Treasury Analyst."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_json(filename: str) -> dict:
    with open(DATA_DIR / filename) as f:
        return json.load(f)


TOOL_DEFINITIONS = [
    {
        "name": "get_treasury_balances",
        "description": "Get current treasury balances, cash positions, and portfolio holdings. Returns account balances, yields, durations, and next-day obligations.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_market_data",
        "description": "Get current market data including interest rates, credit spreads, yield curve shape, and economic indicators.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_available_instruments",
        "description": "Get list of available investment instruments with yields, durations, risk ratings, and minimum investments.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "propose_trade",
        "description": "Propose a trade to reallocate treasury funds. The policy runtime will evaluate the proposal against all institutional policies and return APPROVED, BLOCKED, or ESCALATED.",
        "input_schema": {
            "type": "object",
            "properties": {
                "from_instrument": {
                    "type": "string",
                    "description": "The instrument or account to sell/withdraw from",
                },
                "to_instrument": {
                    "type": "string",
                    "description": "The instrument or account to buy/deposit into",
                },
                "amount": {
                    "type": "number",
                    "description": "The dollar amount of the trade",
                },
                "rationale": {
                    "type": "string",
                    "description": "Detailed reasoning for this trade recommendation",
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence level 0-100 that this trade is beneficial",
                },
            },
            "required": ["from_instrument", "to_instrument", "amount", "rationale", "confidence"],
        },
    },
    {
        "name": "simulate_outcome",
        "description": "Simulate the portfolio state after a proposed trade. Shows projected balances, duration, concentration, and yield impact.",
        "input_schema": {
            "type": "object",
            "properties": {
                "from_instrument": {
                    "type": "string",
                    "description": "The instrument to sell/withdraw from",
                },
                "to_instrument": {
                    "type": "string",
                    "description": "The instrument to buy/deposit into",
                },
                "amount": {
                    "type": "number",
                    "description": "The dollar amount of the trade",
                },
            },
            "required": ["from_instrument", "to_instrument", "amount"],
        },
    },
    {
        "name": "request_approval",
        "description": "Escalate a trade proposal to a human approver. Use when policy checks indicate escalation is needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "trade_summary": {
                    "type": "string",
                    "description": "Summary of the proposed trade",
                },
                "approver_level": {
                    "type": "string",
                    "enum": ["treasury_manager", "vp_treasury", "cfo"],
                    "description": "Required approver level",
                },
                "urgency": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Urgency of the approval request",
                },
            },
            "required": ["trade_summary", "approver_level", "urgency"],
        },
    },
    {
        "name": "log_decision",
        "description": "Log a decision to the audit trail with full context and reasoning.",
        "input_schema": {
            "type": "object",
            "properties": {
                "decision_type": {
                    "type": "string",
                    "enum": ["trade_executed", "trade_blocked", "trade_escalated", "analysis_complete"],
                    "description": "Type of decision being logged",
                },
                "summary": {
                    "type": "string",
                    "description": "Brief summary of the decision",
                },
                "details": {
                    "type": "string",
                    "description": "Full details and reasoning",
                },
            },
            "required": ["decision_type", "summary", "details"],
        },
    },
]


def handle_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return its result as a string."""
    if tool_name == "get_treasury_balances":
        return json.dumps(load_json("balances.json"), indent=2)

    elif tool_name == "get_market_data":
        return json.dumps(load_json("market_data.json"), indent=2)

    elif tool_name == "get_available_instruments":
        return json.dumps(load_json("instruments.json"), indent=2)

    elif tool_name == "simulate_outcome":
        return _simulate_outcome(tool_input)

    elif tool_name == "request_approval":
        return _request_approval(tool_input)

    elif tool_name == "log_decision":
        from runtime.audit import log_entry
        log_entry(
            decision_type=tool_input["decision_type"],
            summary=tool_input["summary"],
            details=tool_input["details"],
        )
        return json.dumps({"status": "logged", "message": "Decision recorded to audit trail."})

    # propose_trade is handled separately in run.py (goes through policy engine)
    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def _simulate_outcome(tool_input: dict) -> str:
    """Simulate portfolio after a trade."""
    balances = load_json("balances.json")
    instruments = load_json("instruments.json")
    amount = tool_input["amount"]
    to_instrument = tool_input["to_instrument"]

    # Find the target instrument
    target = None
    for inst in instruments["available_instruments"]:
        if inst["name"].lower() == to_instrument.lower():
            target = inst
            break

    if not target:
        target = {"duration_years": 1.0, "current_yield": 0.05, "type": "unknown"}

    # Calculate new portfolio metrics
    total_value = balances["total_portfolio_value"]
    current_duration = balances["portfolio_duration_years"]

    # Simplified duration calculation
    new_duration = (
        (current_duration * total_value) - (amount * current_duration) + (amount * target.get("duration_years", 1.0))
    ) / total_value

    # Calculate government percentage
    gov_total = sum(h["amount"] for h in balances["holdings"] if h["type"] == "government")
    if target.get("type") == "government":
        gov_total += amount
    from_instrument = tool_input.get("from_instrument", "")
    for h in balances["holdings"]:
        if h["instrument"].lower() == from_instrument.lower() and h["type"] == "government":
            gov_total -= min(amount, h["amount"])
            break

    gov_pct = gov_total / total_value * 100

    result = {
        "projected_portfolio": {
            "total_value": total_value,
            "new_duration_years": round(new_duration, 2),
            "government_allocation_pct": round(gov_pct, 1),
            "duration_limit": 2.5,
            "duration_compliant": new_duration <= 2.5,
        },
        "trade_impact": {
            "amount": amount,
            "to_instrument": to_instrument,
            "target_yield": target.get("current_yield", "unknown"),
            "target_duration": target.get("duration_years", "unknown"),
        },
    }
    return json.dumps(result, indent=2)


def _request_approval(tool_input: dict) -> str:
    """Simulate requesting human approval."""
    return json.dumps({
        "status": "escalated",
        "approver_level": tool_input["approver_level"],
        "message": f"Trade escalated to {tool_input['approver_level'].replace('_', ' ').title()}. "
                   f"Urgency: {tool_input['urgency']}. Awaiting human decision.",
        "trade_summary": tool_input["trade_summary"],
        "estimated_response_time": "15 minutes" if tool_input["urgency"] == "high" else "2 hours",
    })
