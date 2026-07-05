# Key learnings from building the Claude Policy Runtime

**@timothyglynn | Last updated: Jul 5, 2026**

---

## 1. Policies as markdown, not code

The most powerful design choice was making policies human-readable markdown files that compliance teams can review and approve. Changes take effect immediately without code deploys. This makes the system auditable by non-engineers.

## 2. The "emotional moment" is the intelligent refusal

The demo's impact comes from seeing the AI *refuse* to do something unsafe, explain why, and suggest compliant alternatives. Scenario 4 (four simultaneous violations) is more compelling than Scenario 1 (approval).

## 3. Three-outcome model (approved/blocked/escalated) is essential

Binary pass/fail misses the real-world nuance. Escalation to a named human approver is where enterprise trust gets built.

## 4. Tool-level interception is the right architecture

Rather than post-hoc filtering, the runtime intercepts at the `propose_trade` tool call. The AI literally cannot bypass the policy engine because it's the execution layer, not a wrapper.

## 5. Confidence as a first-class policy input

Having the AI self-report confidence (and the runtime enforce thresholds on it) creates a natural escalation path for uncertain situations.

## 6. Static HTML deploys well as a vision demo

A single `index.html` with no build step deployed instantly to Vercel/GitHub Pages. For a "terrifyingly convincing vision demo," this was the right call over a full Next.js app.

## 7. Strategic framing matters

"The bottleneck is not intelligence—it's delegated authority" resonates because it reframes the problem from "can AI do this?" to "should AI be allowed to do this?"
