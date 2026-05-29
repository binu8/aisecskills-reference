---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: scoping-mcp-tool-authorization-least-privilege
name: scoping-mcp-tool-authorization-least-privilege
version: "1.0"
domain: IAM
aicm_controls:
  - IAM-09
ssrm_ownership: AP-Owned
aismm_category: IAM
aismm_target_level: 4
summary: >-
  Use this skill when you need to apply least-privilege principles to
  MCP tool grants, ensuring each AI agent can invoke only the specific
  tools and parameter ranges required for its assigned task.
references:
  - MCP
  - least-privilege
  - RBAC
  - ABAC
  - tool-authorization
  - agent-security
---

## When to Use

Use this skill when:
- An MCP server exposes many tools but individual agents should only access a subset.
- A security review requires evidence that tool access follows least-privilege principles.
- You are onboarding a new agent and need to define its minimum required tool permissions.
- An existing agent's tool scope has grown beyond its original purpose (scope creep).

**Do not use** this skill as a substitute for network-level MCP server access controls; this skill governs tool-level authorization within an already-authenticated session.

## Inputs

- Complete list of tools exposed by the MCP server.
- Each agent's documented task scope and required capabilities.
- Current tool grant configuration (if one exists).

## Procedure

### Step 1: Enumerate tools and required capabilities per agent

```yaml
# mcp-authorization-matrix.yaml
tools:
  - id: web_search
    risk: low
    data_egress: external
  - id: read_file
    risk: low
    data_egress: none
  - id: write_file
    risk: high
    data_egress: none
  - id: execute_shell
    risk: critical
    data_egress: none
  - id: send_email
    risk: high
    data_egress: external

agents:
  - id: agent-researcher
    allowed_tools:
      - web_search
      - read_file
    rationale: "Research agent only needs to search and read, never write or exec"
  - id: agent-writer
    allowed_tools:
      - read_file
      - write_file
    allowed_write_paths: ["^/workspace/drafts/.*"]
    rationale: "Writer can read and write draft files only"
  - id: agent-notifier
    allowed_tools:
      - send_email
    allowed_email_domains: ["@internal.mycompany.com"]
    rationale: "Notifier sends only to internal addresses"
```

### Step 2: Implement ABAC-style tool authorization

```python
import re, yaml

class MCPLeastPrivilege:
    def __init__(self, matrix_path: str):
        with open(matrix_path) as f:
            matrix = yaml.safe_load(f)
        self.tool_index = {t["id"]: t for t in matrix["tools"]}
        self.agent_index = {a["id"]: a for a in matrix["agents"]}

    def check(self, agent_id: str, tool_id: str, args: dict) -> bool:
        agent = self.agent_index.get(agent_id)
        if not agent:
            raise PermissionError(f"Unknown agent: {agent_id}")
        if tool_id not in agent.get("allowed_tools", []):
            raise PermissionError(f"Agent '{agent_id}' not authorized for tool '{tool_id}'")
        # Attribute checks
        if "allowed_write_paths" in agent and tool_id == "write_file":
            path = args.get("path", "")
            patterns = agent["allowed_write_paths"]
            if not any(re.match(p, path) for p in patterns):
                raise PermissionError(f"Write path '{path}' not allowed for '{agent_id}'")
        if "allowed_email_domains" in agent and tool_id == "send_email":
            to_addr = args.get("to", "")
            domains = agent["allowed_email_domains"]
            if not any(to_addr.endswith(d) for d in domains):
                raise PermissionError(f"Email domain for '{to_addr}' not allowed for '{agent_id}'")
        return True
```

### Step 3: Enforce scope at the MCP dispatch layer

```python
auth = MCPLeastPrivilege("mcp-authorization-matrix.yaml")

def dispatch_tool(agent_id: str, tool_id: str, args: dict):
    auth.check(agent_id, tool_id, args)  # raises PermissionError if not allowed
    return TOOL_REGISTRY[tool_id](**args)
```

### Step 4: Review and prune scope quarterly

```python
def audit_tool_usage(usage_log_path: str, matrix_path: str) -> dict:
    """Find tools granted to agents but never used in the past 90 days."""
    import json
    from collections import defaultdict
    
    used = defaultdict(set)
    with open(usage_log_path) as f:
        for line in f:
            rec = json.loads(line)
            used[rec["agent"]].add(rec["tool"])
    
    with open(matrix_path) as f:
        matrix = yaml.safe_load(f)
    
    unused = {}
    for agent in matrix["agents"]:
        granted = set(agent.get("allowed_tools", []))
        actually_used = used.get(agent["id"], set())
        unused_tools = granted - actually_used
        if unused_tools:
            unused[agent["id"]] = list(unused_tools)
    return unused
```

### Step 5: Generate least-privilege recommendation report

```python
def generate_scope_report(unused: dict) -> str:
    lines = ["# MCP Tool Scope Review — Unused Grants\n"]
    for agent_id, tools in unused.items():
        lines.append(f"## {agent_id}")
        for tool in tools:
            lines.append(f"- `{tool}` — not used in last 90 days; consider removing")
        lines.append("")
    return "\n".join(lines)
```

## Outputs

- `mcp-authorization-matrix.yaml` with per-agent tool grants and attribute constraints.
- `MCPLeastPrivilege` class with unit tests for each authorization rule.
- Quarterly scope audit report listing unused tool grants.
- Dispatch-layer enforcement code with PermissionError on policy violations.

## Quality Checks

- [ ] Every agent has an explicit `allowed_tools` list — no agent has wildcard or inherited access.
- [ ] Attribute constraints (path patterns, email domains) are tested with boundary-condition inputs.
- [ ] A tool call by an unauthorized agent raises `PermissionError` and is logged.
- [ ] Scope audit runs on a schedule and produces a report with unused-grant recommendations.
- [ ] Authorization matrix is version-controlled and reviewed at each agent release.

**AI-CAIQ evidence:** This skill supports YES response to IAM-09 by producing an authorization matrix with per-agent tool grants, an enforcement layer, and quarterly scope-audit reports demonstrating that MCP tool access follows least-privilege principles.
