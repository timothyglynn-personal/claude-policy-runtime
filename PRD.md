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

Models are becoming economically capable faster than enterprises can safely authorize them. The missing layer is not a smarter model—it's a trust runtime that sits between the AI's intent and the action's execution.

## Solution

A policy runtime that governs whether an AI agent is allowed to perform economically consequential actions. Policies are written in plain language (markdown) that compliance teams can read, approve, and update without engineering involvement. Every action is evaluated, logged, and either approved, blocked, or escalated to a named human approver.

**Core mechanics:**

* AI analyzes balances, market conditions, and forms a recommendation
* Every proposed action routes through the policy engine before execution
* Policy checks run against liquidity, duration, concentration, approval tiers, and confidence thresholds
* Three outcomes: approved (execute), blocked (refuse + explain), escalated (route to human)
* Full audit trail in structured format for regulatory review

## Why now

* Frontier models are capable enough to form real treasury recommendations
* Enterprises are actively exploring AI agents for finance operations
* Regulatory pressure is increasing around AI governance and auditability
* No foundation model company owns the trust/authorization layer yet

## Why this is hard to replicate

* Requires deep understanding of financial policy, regulation, and institutional risk frameworks
* The value is in the *refusal logic*, not the model intelligence—generic AI wrappers optimize for "yes"
* Auditability and regulator-readability are design constraints, not features bolted on after
* Progressive trust (agents earning broader authority over time) requires sophisticated identity and permission systems

## Evolution path

| Phase | Capability |
|-------|-----------|
| 1. Policy Runtime | Static policy evaluation, human-readable audit trail |
| 2. Agent Risk Onboarding | Dynamic policy loading, progressive trust, multi-agent coordination |
| 3. Continuous Trust Infrastructure | Real-time policy updates, cross-org federation, anomaly detection, regulatory reporting |

## Positioning

* Okta for AI agents
* Stripe Radar for AI actions
* AWS IAM for economically consequential AI systems
