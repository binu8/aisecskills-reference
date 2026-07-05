---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution. Detection script vendored from
# msaad00/cloud-ai-security-skills — see vendor/msaad00-mcp-detection/.
id: detect-mcp-shadow-tool-injection
name: detect-mcp-shadow-tool-injection
version: "1.0"
domain: AIS
aicm_controls:
  - AIS-10
  - STA-06
ssrm_ownership: Shared OSP-AP
aismm_category: Security Monitoring
aismm_target_level: 4
pillar: security_from_ai
summary: >-
  Use this skill when you need runtime detection of MCP tool poisoning where a tool's description or inputSchema is mutated mid-session away from a server-registered baseline, by
  running the vendored detector to detect MCP tools whose description or inputSchema has been mutated mid-session relative to a server-registered baseline (the shadow-tool / tool-poisoning attack) and emit OCSF detection findings.
references:
  - MCP
  - tool-poisoning
  - owasp-mcp-top10
  - OCSF
  - detection
---

## When to Use

Use this skill when:
- You need to detect MCP tool poisoning where a tool's description or inputSchema is mutated mid-session away from a server-registered baseline.
- You have MCP proxy logs (or OCSF 1.8 Application Activity records) from an MCP deployment and need a runtime detection over them.

**Do not use** this skill on raw MCP proxy logs directly — normalize them first through the vendored `ingest-mcp-proxy-ocsf`; and do not treat it as a preventive control (it is detection, so pair it with `securing-mcp-server-and-tool-boundaries` and `bounding-agent-autonomy-and-tool-scopes-least-privilege`).

## Inputs

- MCP proxy logs in JSON Lines, normalized to OCSF 1.8 Application Activity (class 6002) via `ingest-mcp-proxy-ocsf`.
- The vendored detector at `vendor/msaad00-mcp-detection/skills/detection/detect-mcp-shadow-tool-injection/src/detect.py`.
- Configuration for this detector: Requires a server-registered baseline JSON at `MCP_TOOL_BASELINE_PATH`; fires when a live tool's description or schema hash diverges from the baseline.

## Procedure

The detector is vendored (Apache-2.0, from `msaad00/cloud-ai-security-skills`) at
`vendor/msaad00-mcp-detection/skills/detection/detect-mcp-shadow-tool-injection/src/detect.py`. Run it over OCSF-normalized MCP activity:

```bash
python3 vendor/msaad00-mcp-detection/skills/ingestion/ingest-mcp-proxy-ocsf/src/ingest.py mcp-proxy.jsonl \
  | python3 vendor/msaad00-mcp-detection/skills/detection/detect-mcp-shadow-tool-injection/src/detect.py \
  > findings.ocsf.jsonl
```

Requires a server-registered baseline JSON at `MCP_TOOL_BASELINE_PATH`; fires when a live tool's description or schema hash diverges from the baseline. The detector emits one OCSF 1.8 Detection Finding (class 2004) per detected event.

## Outputs

- OCSF 1.8 Detection Finding records (class 2004), one per detected event, ready for SIEM ingestion and triage.

## Quality Checks

- [ ] The vendored test suite passes: `python3 -m pytest vendor/msaad00-mcp-detection/skills/detection/detect-mcp-shadow-tool-injection/tests/`
- [ ] Raw proxy logs are normalized through `ingest-mcp-proxy-ocsf` before this detector runs.
- [ ] Findings are shipped to the SIEM or detection pipeline, not left on disk.
- [ ] The detector's configuration (requires a server-registered baseline json at `mcp_tool_baseline_path`) matches the deployment.

**AI-CAIQ evidence:** This skill supports a YES response to AIS-10 by producing OCSF detection findings that demonstrate runtime monitoring for MCP tool poisoning where a tool's description or inputSchema is mutated mid-session away from a server-registered baseline.
