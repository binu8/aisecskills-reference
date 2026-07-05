---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: implementing-kill-switch-and-rollback-for-autonomous-agents
name: implementing-kill-switch-and-rollback-for-autonomous-agents
version: "1.0"
domain: SEF
aicm_controls:
  - SEF-03
  - SEF-06
ssrm_ownership: AP-Owned
aismm_category: Incident Response
aismm_target_level: 4
pillar: security_from_ai
nist_ai_rmf:
  - MANAGE-2.4
summary: >-
  Use this skill when an autonomous AI agent holds write, deploy, or
  state-changing permissions in production and you need an emergency-halt and
  recovery capability — a globally-accessible kill switch the SOC can flip
  within seconds and a paired rollback artifact per reversible action, with a
  stricter rollback surface at higher autonomy tiers.
references:
  - kill-switch
  - rollback
  - autonomous-agents
  - owasp-llm06
  - incident-response
---

## When to Use

Use this skill when:
- An autonomous AI agent has write, deploy, or state-changing permissions in production.
- The agent's autonomy rung is augmented or fully autonomous.
- AICM SEF evidence is required for an emergency-halt and recovery capability.

**Do not use** this skill for pure-recommender agents that cannot act — there is nothing to halt or roll back. Pair it with `bounding-agent-autonomy-and-tool-scopes-least-privilege`, which limits what the agent can do in the first place.

## Inputs

- A feature-flag system the SOC can flip without a redeploy.
- A state-change-capable tool surface (the agent actually modifies state).
- A rollback registry: a per-tool inverse op or snapshot strategy.
- The action broker from `bounding-agent-autonomy-and-tool-scopes-least-privilege`.
- SIEM logging of every action with its rollback-artifact id.

## Procedure

### Step 1: Global kill switch

Expose an `agent.<id>.enabled` flag, default ON in healthy steady state. The SOC flips it OFF via the feature-flag console; the agent SDK polls the flag on a short interval and stops taking new actions when it reads OFF.

### Step 2: Per-tier kill scope

- Augmented tier — global kill stops new actions; in-flight reversible actions are allowed to complete or auto-roll-back on the flag change.
- Autonomous tier — global kill stops new actions **and** begins auto-rollback of the last N actions per the rollback policy.

### Step 3: Record a rollback artifact per action

Every state-change action records, alongside its log entry, the inverse op:
- Database write → transaction id (rollback = DB rollback or compensating write).
- File mutation → original-content snapshot.
- API call → idempotency key plus a reverse endpoint (if available) or a compensating notification.

### Step 4: Auto-disable triggers

Beyond the manual switch: N consecutive tool failures, an anomalous action rate (3-sigma above baseline), or an out-of-scope-attempt rate above threshold each auto-disable the agent.

### Step 5: Rollback runbook

Document the SOC runbook: identify the last K reversible actions, replay their rollback artifacts in reverse order, verify state, then re-enable with reduced scope.

### Step 6: Drill quarterly

Run a tabletop plus a live drill on staging; measure kill-to-halt latency, rollback completeness, and mean time to recovery.

## Outputs

- A kill-switch flag and an agent SDK that honors it on a bounded polling interval.
- A per-action rollback registry mapping each state change to its inverse op or snapshot.
- Auto-disable rules wired to failure, rate, and out-of-scope signals.
- A rollback runbook and an archived quarterly drill report with latency and MTTR.

## Quality Checks

- [ ] Flipping the kill switch halts new agent actions within a bounded time.
- [ ] A simulated runaway-action sequence trips the auto-disable threshold within a bounded number of actions.
- [ ] A staging rollback drill restores database and file state to the pre-incident baseline; any deviation is logged.
- [ ] At the autonomous tier, auto-rollback runs on kill-switch flip; at the augmented tier, in-flight actions are allowed to complete.
- [ ] A quarterly drill report is archived with kill-to-halt latency and MTTR.

**AI-CAIQ evidence:** This skill supports a YES response to SEF-03 by producing an emergency-halt capability, a per-action rollback registry, and drill records demonstrating that an autonomous agent can be stopped and its actions reverted within bounded time.
