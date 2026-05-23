#!/usr/bin/env python3
"""Claude Policy Runtime (CPR) - Interactive Treasury Analyst CLI."""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.spinner import Spinner
from rich.columns import Columns

import anthropic

from runtime.engine import evaluate_trade, load_policies
from runtime.tools import TOOL_DEFINITIONS, handle_tool_call
from runtime.audit import log_entry

load_dotenv()

console = Console()

SYSTEM_PROMPT = """You are an AI Treasury Analyst operating within the Claude Policy Runtime (CPR). You have access to tools to:

1. Query treasury balances and market data
2. Propose trades to reallocate funds
3. Simulate portfolio outcomes before committing
4. Log decisions to the institutional audit trail

When asked about treasury operations:
- First use get_treasury_balances and get_market_data to understand the current state
- Analyze the situation and form a recommendation
- Use propose_trade to formally submit your recommendation
- The policy runtime will evaluate your proposal against institutional policies

Always state your confidence level (0-100%) with your proposals.
Be specific about amounts, instruments, expected yields, and risk factors.

You operate under strict institutional policies covering liquidity requirements, duration limits, concentration limits, and approval tiers. The policy runtime will enforce these automatically - you cannot override them.

When a trade is BLOCKED, explain why and suggest alternatives that would comply with policy.
When a trade is ESCALATED, explain what approval is needed and why."""


def display_banner():
    """Display the startup banner."""
    banner = Text()
    banner.append("Claude Policy Runtime", style="bold cyan")
    banner.append(" (CPR)\n", style="cyan")
    banner.append("AI Treasury Analyst with Policy Governance\n\n", style="dim")
    banner.append("Type your treasury query or instruction.\n", style="dim")
    banner.append("Type ", style="dim")
    banner.append("exit", style="bold red")
    banner.append(" or ", style="dim")
    banner.append("quit", style="bold red")
    banner.append(" to end the session.", style="dim")

    console.print(Panel(banner, border_style="cyan", padding=(1, 2)))


def display_policy_result(result: dict):
    """Display policy evaluation result with rich formatting."""
    status = result["status"]

    if status == "APPROVED":
        status_style = "bold green"
        status_icon = "[green]APPROVED[/green]"
        border_style = "green"
    elif status == "BLOCKED":
        status_style = "bold red"
        status_icon = "[red]BLOCKED[/red]"
        border_style = "red"
    else:
        status_style = "bold yellow"
        status_icon = "[yellow]ESCALATED[/yellow]"
        border_style = "yellow"

    # Build checks table
    table = Table(show_header=True, header_style="bold", border_style="dim")
    table.add_column("Check", style="cyan", width=20)
    table.add_column("Status", width=8, justify="center")
    table.add_column("Detail", style="dim")

    for check in result["checks"]:
        if check["status"] == "pass":
            icon = "[green]PASS[/green]"
        elif check["status"] == "fail":
            icon = "[red]FAIL[/red]"
        else:
            icon = "[yellow]ESCL[/yellow]"

        table.add_row(check["name"], icon, check["detail"])

    # Trade summary
    trade = result.get("trade", {})
    trade_text = (
        f"[bold]From:[/bold] {trade.get('from', 'N/A')}\n"
        f"[bold]To:[/bold] {trade.get('to', 'N/A')}\n"
        f"[bold]Amount:[/bold] ${trade.get('amount', 0):,.0f}\n"
        f"[bold]Confidence:[/bold] {trade.get('confidence', 0)}%"
    )

    # Main panel content
    content = Text()
    console.print()
    console.print(Panel(
        f"[bold]POLICY DECISION: {status_icon}[/bold]\n\n"
        f"{trade_text}\n\n"
        f"[bold]Reasoning:[/bold] {result['reasoning']}",
        title="Policy Runtime Evaluation",
        border_style=border_style,
        padding=(1, 2),
    ))
    console.print(table)

    if result.get("required_approver"):
        console.print(
            f"\n[yellow]Required Approver:[/yellow] {result['required_approver'].replace('_', ' ').title()}"
        )
    console.print()


def display_tool_call(tool_name: str, tool_input: dict):
    """Display tool call in a compact format."""
    if tool_name == "propose_trade":
        return  # Handled separately with policy display

    input_summary = ""
    if tool_input:
        parts = []
        for k, v in tool_input.items():
            if isinstance(v, str) and len(v) > 60:
                v = v[:57] + "..."
            parts.append(f"{k}={v}")
        input_summary = ", ".join(parts)

    console.print(f"  [dim]Tool:[/dim] [cyan]{tool_name}[/cyan]({input_summary})", highlight=False)


def run_conversation(client: anthropic.Anthropic, messages: list, user_input: str | None = None):
    """Run a single turn of conversation with Claude, handling tool calls."""
    if user_input:
        messages.append({"role": "user", "content": user_input})

    with console.status("[bold cyan]Thinking...", spinner="dots"):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

    # Process response
    assistant_content = response.content
    messages.append({"role": "assistant", "content": assistant_content})

    # Handle tool use
    tool_results = []
    has_tool_use = any(block.type == "tool_use" for block in assistant_content)

    for block in assistant_content:
        if block.type == "text" and block.text:
            console.print(Markdown(block.text))
        elif block.type == "tool_use":
            display_tool_call(block.name, block.input)

            if block.name == "propose_trade":
                # Run through policy engine
                result = evaluate_trade(block.input)
                display_policy_result(result)

                # Log to audit trail
                log_entry(
                    decision_type=f"trade_{result['status'].lower()}",
                    summary=f"{block.input['from_instrument']} -> {block.input['to_instrument']} (${block.input['amount']:,.0f})",
                    details=block.input.get("rationale", ""),
                    policy_result=result,
                )

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

    # If there were tool calls, send results back to Claude
    if has_tool_use and tool_results:
        messages.append({"role": "user", "content": tool_results})
        run_conversation(client, messages)


def main():
    """Main entry point."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    messages = []

    display_banner()

    # Load and display policy summary
    policies = load_policies()
    console.print(f"[dim]Loaded {len(policies)} policy files: {', '.join(policies.keys())}[/dim]\n")

    while True:
        try:
            user_input = console.input("[bold green]Treasury>[/bold green] ")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Session ended.[/dim]")
            break

        if not user_input.strip():
            continue

        if user_input.strip().lower() in ("exit", "quit", "q"):
            console.print("[dim]Session ended. Audit log saved.[/dim]")
            break

        try:
            run_conversation(client, messages, user_input)
        except anthropic.APIError as e:
            console.print(f"[red]API Error:[/red] {e}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

        console.print()


if __name__ == "__main__":
    main()
