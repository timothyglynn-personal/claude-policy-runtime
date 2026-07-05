# Claude Policy Runtime — Product Requirements Document

**@timothyglynn | Last updated: Jul 5, 2026**

---

## Problem

Finance teams manage cash positions across a patchwork of bank portals, treasury management systems, investment platforms, and internal approval workflows. The policies governing what can move where—liquidity minimums, duration limits, concentration caps, approval thresholds—live in PDF manuals, spreadsheets, tribal knowledge, and disconnected rule engines.

This creates three compounding problems:

* **Automation is fragile.** Rules are hard-coded into scripts that break when policies change. Compliance updates require engineering cycles, not just policy edits.
* **Oversight is expensive.** Every cash movement requires manual checks against multiple policy documents. Senior staff spend hours on routine approvals that could be pre-validated.
* **AI adoption is blocked.** Teams see the potential of AI for treasury optimization but cannot safely delegate authority. The risk of an AI executing a non-compliant trade—even once—makes adoption a non-starter.

The real workflow today looks like this: pull data from four systems into a spreadsheet, cross-reference against policy docs in a PDF, email someone for approval, log the decision somewhere else. Four disconnected steps across four tools. The issue isn't that Excel is bad at math—it's that Excel can't coordinate across systems, enforce policies dynamically, or maintain an audit trail of *why* a decision was made.

Uber solved the *read* side of this with Finch: a conversational AI that answers questions about financial data. But nobody has solved the *write* side—safely authorizing AI to take economically meaningful actions under institutional constraints.

## Insight

The bottleneck to AI agents in financial services is not intelligence. It is delegated authority.

Models are becoming economically capable faster than enterprises can safely authorize them. The missing layer is not a smarter model—it's a trust runtime that sits between the AI's intent and the action's execution.

## Solution

A unified conversational interface for treasury operations that handles both **read** (data retrieval, analysis, Q&A) and **write** (propose actions, enforce policy, route approvals) from the same surface. The graduation from "what's our cash position?" to "optimize our cash position" should feel like a natural continuation of the same conversation—not a different product.

Underneath, a policy runtime governs whether the AI agent is allowed to perform economically consequential actions. Policies are written in plain language (markdown) that compliance teams can read, approve, and update without engineering involvement. Every action is evaluated, logged, and either approved, blocked, or escalated to a named human approver.

**Core mechanics:**

* AI connects to bank portals, TMS, ERPs, and investment platforms as data sources
* Users ask questions in natural language and get answers without manual data extraction
* When the AI proposes an action, it routes through the policy engine before execution
* Policy checks run against liquidity, duration, concentration, approval tiers, and confidence thresholds
* Three outcomes: approved (execute), blocked (refuse + explain), escalated (route to human)
* Full audit trail in structured format for regulatory review
* Context carries forward—if the AI just identified a yield gap, proposing a fix is one sentence away

## Product shape

Anthropic's approach to financial services is platform-first: APIs and agent frameworks that firms integrate into existing systems, rather than pre-built vertical software. This product follows that pattern but adds an opinionated trust layer on top.

**The right shape is a tool-use agent with a policy runtime middleware:**

* **Interface layer:** A conversational agent (API-first, with optional chat UI) that finance teams interact with naturally. Not a dashboard with buttons—a reasoning partner that understands treasury context.
* **Data layer (MCP connectors):** Model Context Protocol servers that connect to bank APIs, treasury management systems, ERPs, and market data. This is the Finch-equivalent read capability—the AI can pull and synthesize data from disparate sources without the user touching a spreadsheet.
* **Policy layer (the differentiator):** A rules engine that intercepts every proposed action. Policies are human-readable markdown. Compliance teams edit policy files; engineers never need to deploy code for policy changes. This is what makes the write side safe.
* **Audit layer:** Append-only structured logs that satisfy regulatory requirements. Every decision—approved, blocked, or escalated—is recorded with full reasoning context.

**Why this shape, not a traditional SaaS dashboard:**

* Dashboards are rigid—they show what was pre-designed. A conversational agent handles questions and scenarios nobody anticipated.
* The coordination problem (data in one place, policy in another, approval in a third) is solved by collapsing all three into one interaction loop.
* Anthropic's existing enterprise customers already use Claude via API. This extends their existing integration pattern rather than introducing a new product surface.
* Long context windows (200K+ tokens) mean the agent can ingest entire policy documents, prospectuses, and regulatory filings in a single conversation—something no dashboard UI can replicate.

## Build sequence

Starting with the read layer is easier and strategically correct:

| Phase | What ships | Why this order |
|-------|-----------|----------------|
| 1. Read layer | Connect data sources, answer questions, prove accuracy | No policy engine needed. No compliance approval required. Immediate value: teams stop wasting hours on data extraction. Builds the data integration layer that write needs anyway. |
| 2. Policy runtime | Same interface, but AI can propose actions that get checked | Users have already developed trust in accuracy. The graduation feels natural—same conversation, new capability. |
| 3. Progressive trust | Agents earn broader authority over time based on track record | Dynamic policy loading, multi-agent coordination, anomaly detection on agent behavior patterns. |

The read layer is a subset of the write layer. If you build a system that can analyze balances, propose trades, and enforce policies, it trivially also answers questions without proposing actions. The policy runtime simply doesn't trigger when the AI is in "answer" mode.

Users opt into write mode when trust is established—not before.

## Why now

* Frontier models are capable enough to form real treasury recommendations
* Enterprises are actively exploring AI agents for finance operations
* Regulatory pressure is increasing around AI governance and auditability
* No foundation model company owns the trust/authorization layer yet
* MCP (Model Context Protocol) makes data source integration standardized rather than bespoke

## Why this is hard to replicate

* Requires deep understanding of financial policy, regulation, and institutional risk frameworks
* The value is in the *refusal logic*, not the model intelligence—generic AI wrappers optimize for "yes"
* Auditability and regulator-readability are design constraints, not features bolted on after
* Progressive trust (agents earning broader authority over time) requires sophisticated identity and permission systems
* Data source integrations compound—each new connector makes the read layer more valuable, which makes the write layer more trustworthy

## Positioning

* Okta for AI agents
* Stripe Radar for AI actions
* AWS IAM for economically consequential AI systems
* Uber Finch + policy governance in one interface
