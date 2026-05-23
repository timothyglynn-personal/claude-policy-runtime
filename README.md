# Claude Policy Runtime (CPR)

**AI Treasury Analyst with Policy Governance**

The bottleneck to enterprise AI agents is not intelligence—it is delegated authority.

Uber built Finch for read-only financial data access. CPR goes further: governing AI **actions**. This runtime demonstrates an AI Treasury Analyst that can analyze markets, form recommendations, and propose trades—but every action passes through a policy engine that enforces institutional rules before execution.

## How it works

```
                    ┌─────────────────────┐
                    │   Human Operator    │
                    │   "Optimize yield   │
                    │    on idle cash"    │
                    └─────────┬───────────┘
                              │
                              v
                    ┌─────────────────────┐
                    │   Claude Analyst    │
                    │  - Reads balances   │
                    │  - Analyzes market  │
                    │  - Forms proposal   │
                    └─────────┬───────────┘
                              │
                              v
              ┌───────────────────────────────────┐
              │        POLICY RUNTIME             │
              │                                   │
              │  Liquidity check ......... PASS   │
              │  Duration check .......... PASS   │
              │  Concentration check ..... PASS   │
              │  Government minimum ...... PASS   │
              │  Approval tier ........... PASS   │
              │  Confidence check ........ PASS   │
              │                                   │
              │  STATUS: APPROVED                 │
              └───────────────┬───────────────────┘
                              │
                              v
                    ┌─────────────────────┐
                    │   Audit Log Entry   │
                    │   (immutable)       │
                    └─────────────────────┘
```

The AI is intelligent. The runtime is the guardrail. Policy is written in plain markdown that compliance teams can read and approve. Changes to policy take effect immediately—no code deploys.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your Anthropic API key to .env
python run.py
```

## Demo scenarios

Run pre-built scenarios showing all four outcomes:

```bash
python demo/scenarios.py
```

Scenarios:
1. **APPROVED** - $3M from savings to T-Bills (compliant, high confidence)
2. **BLOCKED** - $50M overnight deposit withdrawal (liquidity violation)
3. **ESCALATED** - $15M reallocation (requires Treasury Manager approval)
4. **BLOCKED** - $35M into high-yield (four simultaneous violations)

See `demo/transcript.md` for pre-generated output.

## Policy editing

Policies live in `policies/` as plain markdown. Edit them to change behavior:

```
policies/
├── treasury_policy.md     # Core rules: liquidity, duration, concentration
├── approval_matrix.md     # Who can approve what
└── risk_limits.md         # Quantitative risk parameters
```

Changes take effect immediately on next query. No code changes needed.

## Architecture

```
claude-policy-runtime/
├── run.py                  # Interactive CLI (rich terminal UI)
├── policies/               # Human-readable policy rules (markdown)
├── runtime/
│   ├── engine.py           # Policy evaluation orchestrator
│   ├── tools.py            # Claude tool definitions + handlers
│   ├── checks.py           # Individual policy check functions
│   └── audit.py            # Structured audit logging
├── data/                   # Mock treasury data (JSON)
└── demo/                   # Pre-built demo scenarios
```

**Key design decisions:**

* Policies are markdown, not code. Compliance teams can read and approve them.
* Every tool call is observable. The runtime sees everything Claude does.
* The AI cannot bypass the policy engine. `propose_trade` always routes through checks.
* Audit log is append-only JSONL. Every decision is recorded with full context.
* Checks are modular. Add new policy rules by adding check functions.

## Evolution path

**Phase 1: Policy Runtime** (this repo)
- Static policy evaluation
- Pre-defined check functions
- Human-readable audit trail

**Phase 2: Agent Risk Onboarding**
- Dynamic policy loading from institutional systems
- Progressive trust: agents earn broader authority over time
- Multi-agent coordination with shared policy constraints

**Phase 3: Continuous Trust Infrastructure**
- Real-time policy updates from compliance systems
- Cross-organizational policy federation
- Anomaly detection on agent behavior patterns
- Regulatory reporting automation
