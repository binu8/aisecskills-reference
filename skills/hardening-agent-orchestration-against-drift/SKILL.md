---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: hardening-agent-orchestration-against-drift
name: hardening-agent-orchestration-against-drift
version: "1.0"
domain: AIS
aicm_controls:
  - AIS-08
  - AIS-09
ssrm_ownership: OSP-Owned
aismm_category: App Security
aismm_target_level: 4
pillar: security_for_ai
summary: >-
  Use this skill when you need to prevent an AI agent orchestration system
  from drifting outside its intended scope through goal hijacking, runaway
  loops, or unauthorized sub-agent delegation.
references:
  - agent-orchestration
  - LangGraph
  - AutoGen
  - prompt-injection
  - agent-security
  - task-boundaries
---

## When to Use

Use this skill when:
- An autonomous agent or multi-agent system can spawn sub-agents, call tools, or take real-world actions.
- A red-team exercise found that an agent continued executing after its task completed or took unintended side actions.
- You are designing a long-running agent workflow and need to define hard operational boundaries.
- A production incident showed an agent consuming excessive resources or performing unauthorized API calls.

**Do not use** this skill for single-turn LLM applications without agentic loops — the controls here target iterative, planning-capable agent systems.

## Inputs

- Agent orchestration framework and current workflow definition (LangGraph, AutoGen, CrewAI, or custom).
- List of tools and sub-agents the orchestrator can invoke.
- Intended task scope and success criteria.

## Procedure

### Step 1: Define explicit task boundaries and termination conditions

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class AgentBoundary:
    max_iterations: int = 20
    max_tool_calls: int = 50
    allowed_tools: set = None
    allowed_sub_agents: set = None
    timeout_seconds: int = 300
    success_criteria: Callable = None
    hard_stop_keywords: list = None  # if these appear in output, stop immediately

RESEARCH_AGENT_BOUNDARY = AgentBoundary(
    max_iterations=15,
    max_tool_calls=30,
    allowed_tools={"web_search", "read_file", "summarize"},
    allowed_sub_agents=set(),  # no sub-agent delegation allowed
    timeout_seconds=120,
    hard_stop_keywords=["I will now", "executing", "sending email"],
)
```

### Step 2: Implement iteration and resource guards

```python
import time

class BoundedOrchestrator:
    def __init__(self, agent_fn, boundary: AgentBoundary):
        self.agent_fn = agent_fn
        self.boundary = boundary
        self.iteration = 0
        self.tool_call_count = 0
        self.start_time = None

    def run(self, task: str) -> str:
        self.start_time = time.time()
        state = {"task": task, "history": []}
        
        while self.iteration < self.boundary.max_iterations:
            elapsed = time.time() - self.start_time
            if elapsed > self.boundary.timeout_seconds:
                raise TimeoutError(f"Agent exceeded {self.boundary.timeout_seconds}s timeout")
            
            output = self.agent_fn(state)
            self.iteration += 1
            
            # Check hard-stop keywords
            if self.boundary.hard_stop_keywords:
                for kw in self.boundary.hard_stop_keywords:
                    if kw.lower() in output.lower():
                        raise RuntimeError(f"Hard-stop keyword detected: '{kw}'")
            
            if self._is_complete(output, state):
                return output
            
            state["history"].append(output)
        
        raise RuntimeError(f"Agent exceeded max iterations ({self.boundary.max_iterations})")

    def _is_complete(self, output: str, state: dict) -> bool:
        if self.boundary.success_criteria:
            return self.boundary.success_criteria(output, state)
        return "TASK_COMPLETE" in output
```

### Step 3: Gate sub-agent delegation with explicit consent

```python
def authorize_sub_agent_spawn(parent_agent_id: str, sub_agent_type: str,
                               boundary: AgentBoundary) -> bool:
    if boundary.allowed_sub_agents is not None and sub_agent_type not in boundary.allowed_sub_agents:
        raise PermissionError(
            f"Agent '{parent_agent_id}' is not authorized to spawn sub-agent '{sub_agent_type}'"
        )
    return True
```

### Step 4: Enforce tool allow-list at the orchestrator layer

```python
def gated_tool_call(tool_name: str, tool_args: dict,
                     orchestrator: BoundedOrchestrator) -> any:
    if (orchestrator.boundary.allowed_tools is not None
            and tool_name not in orchestrator.boundary.allowed_tools):
        raise PermissionError(f"Tool '{tool_name}' not in agent's allowed set")
    
    orchestrator.tool_call_count += 1
    if orchestrator.tool_call_count > orchestrator.boundary.max_tool_calls:
        raise RuntimeError(f"Agent exceeded max tool calls ({orchestrator.boundary.max_tool_calls})")
    
    return TOOL_REGISTRY[tool_name](**tool_args)
```

### Step 5: Log every iteration and anomaly

```python
import logging, json

agent_log = logging.getLogger("agent.orchestration")

def log_iteration(agent_id: str, iteration: int, tool_calls: int,
                  output_snippet: str, anomaly: str = None):
    agent_log.info(json.dumps({
        "agent": agent_id,
        "iteration": iteration,
        "tool_calls": tool_calls,
        "output_snippet": output_snippet[:200],
        "anomaly": anomaly,
    }))
```

## Outputs

- `AgentBoundary` configuration dataclass with max iterations, tool allow-lists, and timeout.
- `BoundedOrchestrator` wrapper class with iteration guards and hard-stop detection.
- Sub-agent delegation authorization function.
- Agent iteration log with anomaly flags for out-of-boundary behavior.

## Quality Checks

- [ ] Agent terminates within `max_iterations` in both success and loop-injection tests.
- [ ] Hard-stop keywords are tested with a simulated goal-hijacking prompt.
- [ ] Tool calls outside the allow-list raise `PermissionError` and are logged.
- [ ] Sub-agent spawn is blocked for agents where `allowed_sub_agents` is empty.
- [ ] Timeout fires correctly in a test where the agent runs an infinite loop.

**AI-CAIQ evidence:** This skill supports YES response to AIS-08 by producing a `BoundedOrchestrator` implementation with documented iteration limits, tool allow-lists, and hard-stop controls that prevent agent goal hijacking and runaway execution.
