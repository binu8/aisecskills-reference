---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: bounding-agent-autonomy-and-tool-scopes-least-privilege
name: bounding-agent-autonomy-and-tool-scopes-least-privilege
version: "1.0"
domain: IAM
aicm_controls:
  - IAM-09
  - AIS-10
ssrm_ownership: AP-Owned
aismm_category: IAM
aismm_target_level: 4
pillar: security_from_ai
nist_ai_rmf:
  - MANAGE-2.4
summary: >-
  Use this skill when an AI agent can invoke tools that change state outside
  the conversation and you need to bound its blast radius — giving every
  callable tool a least-privilege scope, a per-action rate limit, and an
  aggregate budget, enforced by a broker that fails closed on out-of-scope
  calls, with autonomy capped per maturity tier.
references:
  - agent-autonomy
  - least-privilege
  - owasp-llm06
  - action-broker
  - excessive-agency
---

## When to Use

Use this skill when:
- An LLM agent invokes tools that change state (write to a database, send a message, run a script, modify infrastructure).
- OWASP LLM06 Excessive Agency is on the risk register.
- AICM IAM/AIS evidence is required for agent-action least-privilege.

**Do not use** this skill for read-only or pure-suggestion agents (there is nothing to bound), and do not treat it as a substitute for kill-switch and rollback (see `implementing-kill-switch-and-rollback-for-autonomous-agents`) — the two are complementary.

## Inputs

- An action broker / tool gateway that every tool call routes through.
- A signed scope-policy file per agent declaring permitted tools, per-tool rate limits, and aggregate budgets.
- The maturity/autonomy tier the agent operates at (used to cap the tool surface).
- SIEM ingestion of broker decisions.

## Procedure

### Step 1: Inventory the tools

For each tool record: name, side effects, reversibility class (trivial / scripted / manual), scope dimension (tenant / region / global), and per-call cost.

### Step 2: Author the scope policy

```yaml
agent: triage-bot
autonomy_tier: L3
tools:
  - id: open-jira-ticket
    max_per_hour: 20
    max_per_day: 100
    allowed_projects: [TRIAGE]
    reversibility: scripted
  - id: restart-pod
    max_per_hour: 5
    max_per_day: 10
    allowed_namespaces: [staging]
    reversibility: trivial
```

### Step 3: Enforce at the broker

Every tool call → the broker checks: is the tool agent-allowed, within its rate window, within budget, and within its scope dimension? → allow or deny. There are no unbrokered tool calls.

### Step 4: Cap by autonomy tier

Map the agent's tier to a ceiling — for example: L1 = no tools; L2 = read and propose; L3 = reversible action, narrow scope; L4 = broader action, requires a pre-authorized playbook. A higher tier must not silently inherit a wider tool surface.

### Step 5: Fail closed and instrument

On broker outage, deny all writes and degrade reads gracefully. Emit every decision to the SIEM as `{agentId, tier, toolId, scope, decision, reason}` and run anomaly detection on call-rate spikes.

### Step 6: Review quarterly

Review the scope policy against incident data; tighten unused scopes; widen only with a documented business case and signoff.

## Outputs

- A signed, version-controlled scope-policy file per agent.
- A broker enforcement path with allow/deny decisions on every tool call.
- A SIEM stream of broker decisions plus call-rate anomaly alerts.
- A quarterly scope-review record showing unused scopes tightened.

## Quality Checks

- [ ] A test agent attempting a tool outside its scope is denied at the broker.
- [ ] A test agent exceeding its per-hour rate is denied and logged.
- [ ] A test agent at a lower tier attempting a higher-tier-only tool is denied by the tier cap.
- [ ] A simulated broker outage denies all writes within a bounded time.
- [ ] A quarterly review record exists with unused scopes tightened.

**AI-CAIQ evidence:** This skill supports a YES response to IAM-09 by producing a per-agent least-privilege scope policy and broker enforcement logs demonstrating that agent tool invocations are constrained by scope, rate, and budget.
