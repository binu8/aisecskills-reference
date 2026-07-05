---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution. Detection script vendored from
# msaad00/cloud-ai-security-skills — see vendor/msaad00-mcp-detection/.
id: detect-mcp-model-token-flood
name: detect-mcp-model-token-flood
version: "1.0"
domain: MDS
aicm_controls:
  - MDS-07
  - AIS-07
ssrm_ownership: Shared OSP-AP
aismm_category: Security Monitoring
aismm_target_level: 4
pillar: security_from_ai
summary: >-
  Use this skill when you need runtime detection of unbounded prompt-token consumption against a model endpoint over MCP (OWASP LLM10), by
  running the vendored detector to detect unbounded prompt-token consumption against a model endpoint over MCP (the OWASP LLM10 pattern on the model-input side) and emit OCSF detection findings.
references:
  - MCP
  - denial-of-service
  - owasp-llm-top10
  - OCSF
  - detection
---

## When to Use

Use this skill when:
- You need to detect unbounded prompt-token consumption against a model endpoint over MCP (OWASP LLM10).
- You have MCP proxy logs (or OCSF 1.8 Application Activity records) from an MCP deployment and need a runtime detection over them.

**Do not use** this skill on raw MCP proxy logs directly — normalize them first through the vendored `ingest-mcp-proxy-ocsf`; and do not treat it as a preventive control (it is detection, so pair it with `securing-mcp-server-and-tool-boundaries` and `bounding-agent-autonomy-and-tool-scopes-least-privilege`).

## Inputs

- MCP proxy logs in JSON Lines, normalized to OCSF 1.8 Application Activity (class 6002) via `ingest-mcp-proxy-ocsf`.
- The vendored detector at `vendor/msaad00-mcp-detection/skills/detection/detect-mcp-model-token-flood/src/detect.py`.
- Configuration for this detector: Tracks prompt-token volume per session against a configurable ceiling; fires when the ceiling is systematically breached.

## Procedure

The detector is vendored (Apache-2.0, from `msaad00/cloud-ai-security-skills`) at
`vendor/msaad00-mcp-detection/skills/detection/detect-mcp-model-token-flood/src/detect.py`. Run it over OCSF-normalized MCP activity:

```bash
python3 vendor/msaad00-mcp-detection/skills/ingestion/ingest-mcp-proxy-ocsf/src/ingest.py mcp-proxy.jsonl \
  | python3 vendor/msaad00-mcp-detection/skills/detection/detect-mcp-model-token-flood/src/detect.py \
  > findings.ocsf.jsonl
```

Tracks prompt-token volume per session against a configurable ceiling; fires when the ceiling is systematically breached. The detector emits one OCSF 1.8 Detection Finding (class 2004) per detected event.

## Outputs

- OCSF 1.8 Detection Finding records (class 2004), one per detected event, ready for SIEM ingestion and triage.

## Quality Checks

- [ ] The vendored test suite passes: `python3 -m pytest vendor/msaad00-mcp-detection/skills/detection/detect-mcp-model-token-flood/tests/`
- [ ] Raw proxy logs are normalized through `ingest-mcp-proxy-ocsf` before this detector runs.
- [ ] Findings are shipped to the SIEM or detection pipeline, not left on disk.
- [ ] The detector's configuration (tracks prompt-token volume per session against a configurable ceiling) matches the deployment.

**AI-CAIQ evidence:** This skill supports a YES response to MDS-07 by producing OCSF detection findings that demonstrate runtime monitoring for unbounded prompt-token consumption against a model endpoint over MCP (OWASP LLM10).
