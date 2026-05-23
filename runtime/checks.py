"""Individual policy check functions for the treasury policy runtime."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_balances() -> dict:
    with open(DATA_DIR / "balances.json") as f:
        return json.load(f)


def load_instruments() -> dict:
    with open(DATA_DIR / "instruments.json") as f:
        return json.load(f)


def check_liquidity(trade: dict, balances: dict) -> dict:
    """Check minimum overnight liquidity requirement: $50M above obligations."""
    liquid_types = {"overnight_deposit", "savings", "checking", "money_market"}
    liquid_total = sum(
        pos["balance"] for pos in balances["cash_positions"]
        if pos["type"] in liquid_types
    )

    # If selling a liquid position, reduce available liquidity
    from_instrument = trade.get("from_instrument", "").lower()
    amount = trade["amount"]

    for pos in balances["cash_positions"]:
        if pos["account"].lower() == from_instrument:
            liquid_total -= min(amount, pos["balance"])
            break

    obligations = balances["next_day_obligations"]
    buffer = liquid_total - obligations
    required_buffer = 50_000_000

    passed = buffer >= required_buffer

    return {
        "name": "liquidity",
        "status": "pass" if passed else "fail",
        "detail": (
            f"Liquid assets: ${liquid_total:,.0f} | Obligations: ${obligations:,.0f} | "
            f"Buffer: ${buffer:,.0f} (required: ${required_buffer:,.0f})"
        ),
    }


def check_duration(trade: dict, balances: dict) -> dict:
    """Check portfolio duration stays below 2.5 years."""
    instruments = load_instruments()
    amount = trade["amount"]
    to_instrument = trade.get("to_instrument", "").lower()
    from_instrument = trade.get("from_instrument", "").lower()

    total_value = balances["total_portfolio_value"]
    current_duration = balances["portfolio_duration_years"]

    # Find target instrument duration
    target_duration = current_duration  # default
    for inst in instruments["available_instruments"]:
        if inst["name"].lower() == to_instrument:
            target_duration = inst["duration_years"]
            break

    # Find source instrument duration
    source_duration = 0.0
    for h in balances["holdings"]:
        if h["instrument"].lower() == from_instrument:
            source_duration = h["duration_years"]
            break
    for pos in balances["cash_positions"]:
        if pos["account"].lower() == from_instrument:
            source_duration = 0.0  # cash has zero duration
            break

    # Calculate new weighted average duration
    new_duration = (
        (current_duration * total_value)
        - (amount * source_duration)
        + (amount * target_duration)
    ) / total_value

    max_duration = 2.5
    passed = new_duration <= max_duration

    return {
        "name": "duration",
        "status": "pass" if passed else "fail",
        "detail": (
            f"Current duration: {current_duration:.2f}y | "
            f"Post-trade duration: {new_duration:.2f}y | "
            f"Limit: {max_duration}y"
        ),
    }


def check_concentration(trade: dict, balances: dict) -> dict:
    """Check no single issuer > 15% and no instrument type > 40%."""
    instruments = load_instruments()
    amount = trade["amount"]
    to_instrument = trade.get("to_instrument", "").lower()
    total_value = balances["total_portfolio_value"]

    # Find target instrument type
    target_type = "unknown"
    for inst in instruments["available_instruments"]:
        if inst["name"].lower() == to_instrument:
            target_type = inst["type"]
            break

    # Calculate type concentration after trade
    type_totals = {}
    for h in balances["holdings"]:
        t = h["type"]
        type_totals[t] = type_totals.get(t, 0) + h["amount"]

    # Add the new allocation
    type_totals[target_type] = type_totals.get(target_type, 0) + amount

    # Subtract from source if it's a holding
    from_instrument = trade.get("from_instrument", "").lower()
    for h in balances["holdings"]:
        if h["instrument"].lower() == from_instrument:
            type_totals[h["type"]] = type_totals.get(h["type"], 0) - min(amount, h["amount"])
            break

    # Check type limits (government exempt)
    max_type_pct = 40.0
    violations = []
    for t, val in type_totals.items():
        if t in ("government", "government_agency"):
            continue
        pct = val / total_value * 100
        if pct > max_type_pct:
            violations.append(f"{t}: {pct:.1f}% (limit: {max_type_pct}%)")

    # Check issuer concentration (simplified: treat each instrument as its own issuer)
    max_issuer_pct = 15.0
    issuer_amount = 0
    for h in balances["holdings"]:
        if h["instrument"].lower() == to_instrument:
            issuer_amount = h["amount"] + amount
            break
    else:
        issuer_amount = amount

    issuer_pct = issuer_amount / total_value * 100
    if target_type not in ("government", "government_agency") and issuer_pct > max_issuer_pct:
        violations.append(f"Issuer '{trade['to_instrument']}': {issuer_pct:.1f}% (limit: {max_issuer_pct}%)")

    passed = len(violations) == 0

    if passed:
        detail = "All concentration limits within bounds."
    else:
        detail = "VIOLATIONS: " + "; ".join(violations)

    return {
        "name": "concentration",
        "status": "pass" if passed else "fail",
        "detail": detail,
    }


def check_government_minimum(trade: dict, balances: dict) -> dict:
    """Check government securities remain >= 30% of portfolio."""
    instruments = load_instruments()
    amount = trade["amount"]
    to_instrument = trade.get("to_instrument", "").lower()
    from_instrument = trade.get("from_instrument", "").lower()
    total_value = balances["total_portfolio_value"]

    gov_types = {"government", "government_agency"}

    gov_total = sum(h["amount"] for h in balances["holdings"] if h["type"] in gov_types)

    # Adjust for trade
    for h in balances["holdings"]:
        if h["instrument"].lower() == from_instrument and h["type"] in gov_types:
            gov_total -= min(amount, h["amount"])
            break

    # Check if target is government
    for inst in instruments["available_instruments"]:
        if inst["name"].lower() == to_instrument and inst["type"] in gov_types:
            gov_total += amount
            break

    gov_pct = gov_total / total_value * 100
    min_gov_pct = 30.0
    passed = gov_pct >= min_gov_pct

    return {
        "name": "government_minimum",
        "status": "pass" if passed else "fail",
        "detail": (
            f"Government allocation: {gov_pct:.1f}% | "
            f"Minimum required: {min_gov_pct}%"
        ),
    }


def check_approval_tier(trade: dict) -> dict:
    """Determine required approval tier based on trade size."""
    amount = trade["amount"]

    if amount < 5_000_000:
        tier = "auto_approved"
        detail = f"Trade size ${amount:,.0f} < $5M threshold. Auto-approval eligible."
    elif amount <= 25_000_000:
        tier = "treasury_manager"
        detail = f"Trade size ${amount:,.0f} requires Treasury Manager approval ($5M-$25M tier)."
    else:
        tier = "cfo"
        detail = f"Trade size ${amount:,.0f} requires CFO approval (>$25M tier)."

    return {
        "name": "approval_tier",
        "status": "pass" if tier == "auto_approved" else "escalate",
        "detail": detail,
        "required_approver": None if tier == "auto_approved" else tier,
    }


def check_confidence(confidence: float) -> dict:
    """Check confidence level against thresholds."""
    if confidence > 85:
        status = "pass"
        detail = f"Confidence {confidence}% > 85% threshold. Auto-execution eligible."
    elif confidence >= 60:
        status = "escalate"
        detail = f"Confidence {confidence}% in 60-85% range. Requires human review."
    else:
        status = "fail"
        detail = f"Confidence {confidence}% < 60% minimum. Trade blocked due to insufficient confidence."

    return {
        "name": "confidence",
        "status": status,
        "detail": detail,
    }
