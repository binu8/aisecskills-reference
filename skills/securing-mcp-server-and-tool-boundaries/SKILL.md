---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: securing-mcp-server-and-tool-boundaries
name: securing-mcp-server-and-tool-boundaries
version: "1.0"
domain: AIS
aicm_controls:
  - AIS-10
  - IAM-09
ssrm_ownership: Shared OSP-AP
aismm_category: App Security
aismm_target_level: 3
summary: >-
  Use this skill when you need to harden a Model Context Protocol server
  and its exposed tools against unauthorized invocation, privilege escalation,
  and data exfiltration through agent-initiated tool calls.
references:
  - MCP
  - tool-security
  - least-privilege
  - agent-security
  - input-validation
  - OAuth
---

## When to Use

Use this skill when:
- You are deploying or auditing an MCP server that exposes tools to an LLM agent.
- A security review must verify that agents cannot invoke tools outside their authorized scope.
- An agent has access to sensitive tools (file write, database query, API call) and lateral movement is a concern.
- You are building a multi-tenant platform where different agents must be isolated from each other's tool access.

**Do not use** this skill to design the agent orchestration logic itself (see `hardening-agent-orchestration-against-drift`); this skill focuses on the MCP server boundary.

## Inputs

- MCP server code or configuration listing all exposed tools and their parameters.
- Agent identity and authorization model (API keys, OAuth tokens, scopes).
- Tool sensitivity classification (read-only vs. write vs. destructive).

## Procedure

### Step 1: Inventory all exposed MCP tools and classify sensitivity

```yaml
# tool-registry.yaml
tools:
  - name: read_file
    sensitivity: low
    allowed_agents: ["*"]
    allowed_paths_pattern: "^/data/public/.*"
  - name: write_file
    sensitivity: high
    allowed_agents: ["agent-content-writer"]
    allowed_paths_pattern: "^/data/output/.*"
  - name: execute_sql
    sensitivity: critical
    allowed_agents: ["agent-reporting"]
    allowed_operations: ["SELECT"]
  - name: send_email
    sensitivity: high
    allowed_agents: ["agent-notifier"]
    rate_limit: "10/minute"
```

### Step 2: Implement per-tool authorization checks

```python
import fnmatch, re

class MCPToolAuthority:
    def __init__(self, registry_path: str):
        import yaml
        with open(registry_path) as f:
            self.registry = {t["name"]: t for t in yaml.safe_load(f)["tools"]}

    def authorize(self, agent_id: str, tool_name: str, tool_args: dict) -> bool:
        if tool_name not in self.registry:
            raise PermissionError(f"Tool '{tool_name}' not registered")
        tool = self.registry[tool_name]
        allowed = tool.get("allowed_agents", [])
        if "*" not in allowed and agent_id not in allowed:
            raise PermissionError(f"Agent '{agent_id}' not authorized for tool '{tool_name}'")
        # Validate path pattern if present
        if "allowed_paths_pattern" in tool:
            path = tool_args.get("path", "")
            if not re.match(tool["allowed_paths_pattern"], path):
                raise PermissionError(f"Path '{path}' not allowed for tool '{tool_name}'")
        return True
```

### Step 3: Validate and sanitize all tool arguments

```python
import re

DANGEROUS_PATTERNS = {
    "shell_meta": re.compile(r"[;&|`$(){}]"),
    "path_traversal": re.compile(r"\.\./"),
    "sql_injection": re.compile(r"(--|;|\bDROP\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)", re.IGNORECASE),
}

def sanitize_tool_args(tool_name: str, args: dict) -> dict:
    for k, v in args.items():
        if isinstance(v, str):
            for pattern_name, pattern in DANGEROUS_PATTERNS.items():
                if pattern.search(v):
                    raise ValueError(f"Dangerous pattern '{pattern_name}' in arg '{k}' for tool '{tool_name}'")
    return args
```

### Step 4: Enforce OAuth scopes for external tool calls

```python
# Verify agent's OAuth token has required scope before invoking external API tool
def verify_tool_scope(token: str, required_scope: str, jwks_uri: str) -> bool:
    from jose import jwt
    import httpx
    jwks = httpx.get(jwks_uri).json()
    claims = jwt.decode(token, jwks, algorithms=["RS256"])
    scopes = claims.get("scope", "").split()
    if required_scope not in scopes:
        raise PermissionError(f"Token missing required scope: {required_scope}")
    return True
```

### Step 5: Log every tool invocation with agent identity

```python
import logging, json, datetime

tool_log = logging.getLogger("mcp.tool.audit")

def logged_tool_call(agent_id: str, tool_name: str, args: dict, tool_fn):
    tool_log.info(json.dumps({
        "ts": datetime.datetime.utcnow().isoformat(),
        "agent": agent_id,
        "tool": tool_name,
        "args_hash": hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest(),
    }))
    result = tool_fn(**args)
    return result
```

## Outputs

- `tool-registry.yaml` with per-tool sensitivity classification and agent allow-lists.
- `MCPToolAuthority` authorization class with unit tests.
- Argument sanitization module covering shell, path, and SQL injection patterns.
- MCP tool invocation audit log with agent identity and argument hashes.

## Quality Checks

- [ ] Every tool invocation is gated by the authorization check — no unguarded tool calls.
- [ ] Path traversal and shell metacharacter tests fail at the sanitization layer.
- [ ] An agent not in the allow-list receives a PermissionError, not a silent failure.
- [ ] OAuth scope validation is tested with a token missing the required scope.
- [ ] Audit log captures agent ID and argument hash for every tool call.

**AI-CAIQ evidence:** This skill supports YES response to AIS-10 by producing a tool registry with authorization controls, argument sanitization, and audit logs demonstrating that every MCP tool invocation is gated by agent identity verification.
