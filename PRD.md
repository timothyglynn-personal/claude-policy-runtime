# Claude Policy Runtime — Product Requirements Document

**@timothyglynn | Last updated: Jul 5, 2026**

---

## Problem

Finance teams manage cash positions across a patchwork of bank portals, treasury management systems, investment platforms, and internal approval workflows. The policies governing what can move where—liquidity minimums, duration limits, concentration caps, approval thresholds—live in PDF manuals, spreadsheets, tribal knowledge, and disconnected rule engines.

This creates three compounding problems:

* **Automation is fragile.** Rules are hard-coded into scripts that break when policies change. Compliance updates require engineering cycles, not just policy edits.
* **Oversight is expensive.** Every cash movement requires manual checks against multiple policy documents. Senior staff spend hours on routine approvals that could be pre-validated.
* **AI adoption is blocked.** Teams see the potential of AI for treasury optimization but cannot safely delegate authority. The risk of an AI executing a non-compliant trade—even once—makes adoption a non-starter.

Uber solved the *read* side of this with Finch: a conversational AI that answers questions about financial data. But nobody has solved the *write* side—safely authorizing AI to take economically meaningful actions under institutional constraints.

## Insight

The bottleneck to AI agents in financial services is not intelligence. It is delegated authority.

## Solution

A conversational treasury tool that covers both sides:

* **Read** — Ask questions like "what's my cash balance?" or "show me current rates" and get answers pulled from across all connected systems. No more stitching spreadsheets together. This is the Finch-equivalent layer.
* **Write** — Ask it to take action ("optimize idle cash", "sweep overnight surplus") and a policy runtime evaluates every proposed action against institutional rules before execution. Three outcomes: approved, blocked, or escalated to a named human approver.

Both live in the same interface. The graduation from "what's our cash position?" to "optimize our cash position" is one sentence—not a different product.

## Form factor

**Medium term: Slack.** This is where finance teams already work. A Slack bot that can answer treasury questions and propose/execute actions (with policy governance) fits naturally into existing workflows. No new tool to adopt.

**For now: Web dashboard demo.** You need to *see* this working to believe it. The dashboard at [treasury-analyst.vercel.app](https://treasury-analyst.vercel.app) demonstrates both the read side (conversational data access) and the write side (policy-checked actions with audit trail). The visual demo is how you sell the vision; Slack is how you deliver it.

## Build sequence

| Phase | What | Why this order |
|-------|------|----------------|
| 1. Read layer | Connect data sources, answer questions, prove accuracy | No policy engine needed. No compliance approval. Immediate value. Builds trust. |
| 2. Policy runtime | Same interface adds action proposals with policy checks | Users trust the accuracy. Graduation feels natural. |
| 3. Automations | Rules that trigger actions automatically (still policy-governed) | Only works once trust is established in phases 1-2. |

## Prior art

* **Uber Finch** — Conversational read access to financial data. Solves the "pull data from 4 systems" problem. Does not handle actions or policy governance.
* **Decagon** — Agent operating principles as plain-text rules. Similar concept of human-readable policy, but applied to customer support, not financially consequential actions.

## Positioning

* Uber Finch + policy governance in one interface
* Okta for AI agents
* Stripe Radar for AI actions
