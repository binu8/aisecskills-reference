---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: detecting-cascading-and-feedback-loop-agent-behavior
name: detecting-cascading-and-feedback-loop-agent-behavior
version: "1.0"
domain: LOG
aicm_controls:
  - LOG-03
  - LOG-13
ssrm_ownership: AP-Owned
aismm_category: Security Monitoring
aismm_target_level: 4
pillar: security_from_ai
nist_ai_rmf:
  - MANAGE-2.4
summary: >-
  Use this skill when agents can chain actions or both read from and write to
  a shared data source, and you need to detect cascades (one action triggering
  another) and feedback loops (agents amplifying content they themselves
  wrote) — combining call-graph depth analysis, write-then-read pattern
  detection, and rate-of-change anomalies behind a circuit-breaker.
references:
  - cascade
  - feedback-loop
  - agent-monitoring
  - owasp-llm06
  - circuit-breaker
---

## When to Use

Use this skill when:
- Multiple agents, or one agent across multiple invocations, can chain actions.
- Agents both read from and write to a shared source (knowledge base, ticket queue, alert system).
- Operational metrics show occasional sharp spikes the team cannot yet explain.

**Do not use** this skill for single-shot Q&A agents with no write access — no cascade or feedback loop is possible there.

## Inputs

- A tracing system that propagates `requestId` and `parentRequestId` across agent invocations.
- Data-plane logging that distinguishes agent reads and writes from human writes.
- A metrics pipeline with rate-of-change anomaly detection.
- The action broker from `bounding-agent-autonomy-and-tool-scopes-least-privilege`.

## Procedure

### Step 1: Trace every invocation

Each call carries `{requestId, parentRequestId, agentId, depth}`; depth increments per chained invocation.

### Step 2: Detect cascades

- Depth > `MAX_DEPTH` (default 5) → pause and investigate.
- Fan-out: one parent triggering more than N children at depth+1 → pause.
- Cycle: a `requestId` appears twice in the same parent chain → halt immediately.

### Step 3: Detect feedback loops

- Identify each shared source where agents both read and write.
- Track write-rate versus read-rate by agent class.
- Alert when agent writes exceed 50% of total writes **and** agent reads exceed 50% of total reads in the same window — agents are mostly reading what agents wrote.
- Track topic concentration on agent-written content; alert on entropy collapse (a narrow set of topics being amplified).

### Step 4: Detect rate-of-change anomalies

For key metrics (ticket count, alert count, message volume) track the first derivative; a 3-sigma jump correlated with elevated agent activity → pause.

### Step 5: Trip the circuit-breaker

Any trigger pauses the agent class via the broker and notifies the SOC with the trace and the suspected pattern.

### Step 6: Review quarterly

Analyze false positives, tune thresholds, and document observed patterns.

## Outputs

- Per-request call-graph traces with depth and parent chains.
- Cascade, feedback-loop, and rate-of-change alerts routed to the SOC.
- A circuit-breaker action record (which agent class was paused, and why).
- A quarterly false-positive report with threshold-tuning history.

## Quality Checks

- [ ] A test agent in a 6-deep chain trips the depth circuit-breaker.
- [ ] A simulated agent-write → agent-read loop trips the feedback-loop detector within a bounded number of windows.
- [ ] A controlled metric spike correlated with agent activity trips the rate-of-change anomaly.
- [ ] The circuit-breaker pauses the agent class via the broker within a bounded time.
- [ ] A quarterly false-positive report exists with threshold-tuning history.

**AI-CAIQ evidence:** This skill supports a YES response to LOG-03 by producing monitoring detections and circuit-breaker records demonstrating that runaway cascading and feedback-loop agent behavior is detected and contained.
