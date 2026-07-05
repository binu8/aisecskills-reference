---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: capturing-agent-action-and-delegation-telemetry
name: capturing-agent-action-and-delegation-telemetry
version: "1.0"
domain: LOG
aicm_controls:
  - LOG-05
  - LOG-13
ssrm_ownership: Shared OSP-AP
aismm_category: Security Monitoring
aismm_target_level: 4
pillar: security_for_ai
summary: >-
  Use this skill when you need to instrument an AI agent system to capture
  every tool call, sub-agent delegation, and state transition as structured
  telemetry for security investigation and compliance purposes.
references:
  - OpenTelemetry
  - distributed-tracing
  - agent-observability
  - LangSmith
  - SIEM
  - audit-trail
---

## When to Use

Use this skill when:
- An autonomous agent takes multi-step actions across tools and sub-agents and you need a full audit trail.
- A security investigation requires reconstructing the sequence of actions an agent took.
- Compliance requires evidence of human oversight over agent-initiated external actions.
- You need to detect anomalous agent behavior (unexpected tool calls, unusual delegation chains).

**Do not use** this skill as the only logging layer — it should complement, not replace, application-level prompt/response logging (see `implementing-prompt-and-response-logging`).

## Inputs

- Agent orchestration framework (LangGraph, AutoGen, CrewAI, or custom).
- List of tools and sub-agents in the system.
- OpenTelemetry collector or SIEM endpoint.

## Procedure

### Step 1: Define the agent action telemetry schema

```python
from dataclasses import dataclass, field
import datetime

@dataclass
class AgentActionEvent:
    ts: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    trace_id: str = ""           # distributed trace ID (spans the whole task)
    span_id: str = ""            # this action's span
    parent_span_id: str = ""     # parent action or delegation
    agent_id: str = ""
    originating_user: str = ""
    action_type: str = ""        # tool_call | delegation | state_transition | completion
    tool_name: str = ""
    tool_args_hash: str = ""     # SHA-256 of serialized args
    sub_agent_id: str = ""       # populated for delegation events
    result_summary: str = ""     # truncated, non-sensitive summary
    anomaly_flags: list = field(default_factory=list)
```

### Step 2: Instrument tool calls with OpenTelemetry spans

```python
from opentelemetry import trace
import hashlib, json

tracer = trace.get_tracer("agent.actions")

def traced_tool_call(agent_id: str, tool_name: str, args: dict,
                     tool_fn, originating_user: str = "") -> any:
    with tracer.start_as_current_span(f"tool.{tool_name}") as span:
        span.set_attribute("agent.id", agent_id)
        span.set_attribute("agent.originating_user", originating_user)
        span.set_attribute("tool.name", tool_name)
        span.set_attribute("tool.args_hash",
            hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest())
        
        result = tool_fn(**args)
        
        span.set_attribute("tool.success", True)
        return result
```

### Step 3: Instrument delegation events

```python
def traced_delegation(parent_agent_id: str, sub_agent_id: str,
                       task: str, originating_user: str) -> str:
    with tracer.start_as_current_span("agent.delegation") as span:
        span.set_attribute("agent.parent_id", parent_agent_id)
        span.set_attribute("agent.sub_id", sub_agent_id)
        span.set_attribute("agent.originating_user", originating_user)
        span.set_attribute("task_hash",
            hashlib.sha256(task.encode()).hexdigest())
        
        result = run_sub_agent(sub_agent_id, task)
        return result
```

### Step 4: Emit structured JSONL events for SIEM ingestion

```python
import logging

agent_telemetry = logging.getLogger("agent.telemetry")

def emit_action_event(event: AgentActionEvent):
    import dataclasses
    agent_telemetry.info(json.dumps(dataclasses.asdict(event)))
```

### Step 5: Detect anomalous patterns with threshold rules

```python
from collections import defaultdict

def detect_anomalies(events: list[AgentActionEvent]) -> list[dict]:
    alerts = []
    tool_call_counts = defaultdict(int)
    delegation_depth = defaultdict(int)
    
    for e in events:
        if e.action_type == "tool_call":
            tool_call_counts[e.agent_id] += 1
            if tool_call_counts[e.agent_id] > 50:
                alerts.append({"type": "excessive_tool_calls", "agent": e.agent_id,
                                "count": tool_call_counts[e.agent_id]})
        if e.action_type == "delegation":
            delegation_depth[e.trace_id] += 1
            if delegation_depth[e.trace_id] > 5:
                alerts.append({"type": "deep_delegation_chain", "trace": e.trace_id,
                                "depth": delegation_depth[e.trace_id]})
    return alerts
```

## Outputs

- `AgentActionEvent` schema with distributed trace IDs linking all actions in a task.
- OpenTelemetry instrumentation on all tool calls and delegation events.
- JSONL event stream for SIEM ingestion.
- Anomaly detection function with configurable thresholds for excessive calls and deep delegation.

## Quality Checks

- [ ] Every tool call emits a span with agent ID, tool name, and args hash.
- [ ] Delegation events include both parent and sub-agent IDs and originating user.
- [ ] Trace IDs correctly link all spans within a single task execution.
- [ ] Anomaly detection fires an alert when tool call count exceeds the threshold in a test.
- [ ] Telemetry events reach the SIEM/collector within 30 seconds of occurrence.

**AI-CAIQ evidence:** This skill supports YES response to LOG-05 by producing instrumented agent action telemetry with distributed trace IDs, delegation event logs, and anomaly detection configurations that provide a complete, structured audit trail of every action an AI agent takes.
