#!/usr/bin/env python3
"""Pre-built demo scenarios showing APPROVED, BLOCKED, ESCALATED, and MULTI-VIOLATION outcomes."""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

import anthropic

from runtime.engine import evaluate_trade
from runtime.tools import TOOL_DEFINITIONS, handle_tool_call
from runtime.audit import log_entry

load_dotenv()

console = Console()

SYSTEM_PROMPT = """You are an AI Treasury Analyst operating within the Claude Policy Runtime (CPR). You have access to tools to query balances, market data, propose trades, and log decisions.

Respond concisely. When given a specific instruction, execute it directly using the appropriate tools."""

SCENARIOS = [
    {
        "title": "Scenario 1: APPROVED - Small Low-Risk Reallocation",
        "description": "Move $3M from savings to T-Bills for better yield",
        "prompt": "I'd like to move $3 million from our BofA Savings account into US 3-Month T-Bills to capture the yield differential. Please propose this trade with your analysis.",
        "expected": "APPROVED",
    },
    {
        "title": "Scenario 2: BLOCKED - Liquidity Violation",
        "description": "Attempt to move $50M from overnight deposits, violating liquidity floor",
        "prompt": "Move $50 million from Chase Overnight deposits into Corporate Bond Fund A. The yield pickup is significant. Propose this trade.",
        "expected": "BLOCKED",
    },
    {
        "title": "Scenario 3: ESCALATED - Large Trade Requiring Approval",
        "description": "$10M trade requiring Treasury Manager approval with moderate confidence",
        "prompt": "Propose moving $10 million from BofA Savings to Corporate Bond Fund A to improve yield. I'm fairly confident this is the right move - about 75% confidence.",
        "expected": "ESCALATED",
    },
    {
        "title": "Scenario 4: BLOCKED - Multiple Policy Violations",
        "description": "Large trade into high-yield that violates duration, concentration, and confidence",
        "prompt": "I want to move $35 million from US 3-Month T-Bills into the High-Yield Corporate Fund. The yield is much better. Propose this with 50% confidence.",
        "expected": "BLOCKED",
    },
]


def run_scenario(client: anthropic.Anthropic, scenario: dict):
    """Run a single scenario and display results."""
    console.print(Rule(style="cyan"))
    console.print(Panel(
        f"[bold]{scenario['title']}[/bold]\n\n"
        f"[dim]{scenario['description']}[/dim]\n\n"
        f"[bold]Expected outcome:[/bold] {scenario['expected']}",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()

    messages = [{"role": "user", "content": scenario["prompt"]}]

    console.print(f"[green]Treasury>[/green] {scenario['prompt']}\n")

    # Run conversation with Claude
    with console.status("[bold cyan]Analyst thinking...", spinner="dots"):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

    # Process up to 5 turns of tool use
    for turn in range(5):
        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        has_tool_use = any(block.type == "tool_use" for block in assistant_content)
        if not has_tool_use:
            # Print final text
            for block in assistant_content:
                if block.type == "text" and block.text:
                    console.print(f"[dim]{block.text[:500]}{'...' if len(block.text) > 500 else ''}[/dim]")
            break

        tool_results = []
        for block in assistant_content:
            if block.type == "text" and block.text:
                console.print(f"[dim]{block.text[:200]}[/dim]")
            elif block.type == "tool_use":
                console.print(f"  [cyan]Tool: {block.name}[/cyan]")

                if block.name == "propose_trade":
                    result = evaluate_trade(block.input)
                    display_policy_result_compact(result)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    })
                else:
                    result = handle_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

        if tool_results:
            messages.append({"role": "user", "content": tool_results})
            with console.status("[bold cyan]Analyst processing...", spinner="dots"):
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    tools=TOOL_DEFINITIONS,
                    messages=messages,
                )
        else:
            break

    console.print()


def display_policy_result_compact(result: dict):
    """Compact policy result display for demo mode."""
    status = result["status"]
    if status == "APPROVED":
        icon = "[green]APPROVED[/green]"
        border = "green"
    elif status == "BLOCKED":
        icon = "[red]BLOCKED[/red]"
        border = "red"
    else:
        icon = "[yellow]ESCALATED[/yellow]"
        border = "yellow"

    table = Table(show_header=False, border_style="dim", padding=(0, 1))
    table.add_column("Check", width=20)
    table.add_column("Result", width=6)

    for check in result["checks"]:
        if check["status"] == "pass":
            s = "[green]PASS[/green]"
        elif check["status"] == "fail":
            s = "[red]FAIL[/red]"
        else:
            s = "[yellow]ESCL[/yellow]"
        table.add_row(check["name"], s)

    console.print(Panel(
        f"Policy Decision: {icon}",
        border_style=border,
    ))
    console.print(table)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    console.print(Panel(
        "[bold cyan]Claude Policy Runtime - Demo Scenarios[/bold cyan]\n\n"
        "Running 4 scenarios demonstrating policy enforcement:\n"
        "1. APPROVED - compliant small trade\n"
        "2. BLOCKED - liquidity violation\n"
        "3. ESCALATED - approval tier exceeded\n"
        "4. BLOCKED - multiple violations",
        border_style="cyan",
        padding=(1, 2),
    ))

    for scenario in SCENARIOS:
        run_scenario(client, scenario)

    console.print(Rule(style="cyan"))
    console.print("[bold green]Demo complete.[/bold green] All scenarios executed.\n")


if __name__ == "__main__":
    main()
