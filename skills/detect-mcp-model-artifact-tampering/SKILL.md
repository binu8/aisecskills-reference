---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution. Detection script vendored from
# msaad00/cloud-ai-security-skills — see vendor/msaad00-mcp-detection/.
id: detect-mcp-model-artifact-tampering
name: detect-mcp-model-artifact-tampering
version: "1.0"
domain: MDS
aicm_controls:
  - MDS-05
  - STA-06
ssrm_ownership: Shared OSP-AP
aismm_category: Security Monitoring
aismm_target_level: 4
pillar: security_from_ai
atlas_techniques:
  - AML.T0010
summary: >-
  Use this skill when you need runtime detection of ML supply-chain compromise where an MCP server swaps a model artifact (weights, adapter, tokenizer) mid-session, by
  running the vendored detector to detect MCP tool calls whose returned model artifact hash diverges from a known-good baseline registered at session start (ML supply-chain tampering) and emit OCSF detection findings.
references:
  - MCP
  - supply-chain
  - owasp-llm-top10
  - OCSF
  - detection
---

## When to Use

Use this skill when:
- You need to detect ML supply-chain compromise where an MCP server swaps a model artifact (weights, adapter, tokenizer) mid-session.
- You have MCP proxy logs (or OCSF 1.8 Application Activity records) from an MCP deployment and need a runtime detection over them.

**Do not use** this skill on raw MCP proxy logs directly — normalize them first through the vendored `ingest-mcp-proxy-ocsf`; and do not treat it as a preventive control (it is detection, so pair it with `securing-mcp-server-and-tool-boundaries` and `bounding-agent-autonomy-and-tool-scopes-least-privilege`).

## Inputs

- MCP proxy logs in JSON Lines, normalized to OCSF 1.8 Application Activity (class 6002) via `ingest-mcp-proxy-ocsf`.
- The vendored detector at `vendor/msaad00-mcp-detection/skills/detection/detect-mcp-model-artifact-tampering/src/detect.py`.
- Configuration for this detector: The first event carrying a model artifact hash sets the session baseline; a later diverging hash fires one finding.

## Procedure

The detector is vendored (Apache-2.0, from `msaad00/cloud-ai-security-skills`) at
`vendor/msaad00-mcp-detection/skills/detection/detect-mcp-model-artifact-tampering/src/detect.py`. Run it over OCSF-normalized MCP activity:

```bash
python3 vendor/msaad00-mcp-detection/skills/ingestion/ingest-mcp-proxy-ocsf/src/ingest.py mcp-proxy.jsonl \
  | python3 vendor/msaad00-mcp-detection/skills/detection/detect-mcp-model-artifact-tampering/src/detect.py \
  > findings.ocsf.jsonl
```

The first event carrying a model artifact hash sets the session baseline; a later diverging hash fires one finding. The detector emits one OCSF 1.8 Detection Finding (class 2004) per detected event.

## Outputs

- OCSF 1.8 Detection Finding records (class 2004), one per detected event, ready for SIEM ingestion and triage.

## Quality Checks

- [ ] The vendored test suite passes: `python3 -m pytest vendor/msaad00-mcp-detection/skills/detection/detect-mcp-model-artifact-tampering/tests/`
- [ ] Raw proxy logs are normalized through `ingest-mcp-proxy-ocsf` before this detector runs.
- [ ] Findings are shipped to the SIEM or detection pipeline, not left on disk.
- [ ] The detector's configuration (the first event carrying a model artifact hash sets the session baseline) matches the deployment.

**AI-CAIQ evidence:** This skill supports a YES response to MDS-05 by producing OCSF detection findings that demonstrate runtime monitoring for ML supply-chain compromise where an MCP server swaps a model artifact (weights, adapter, tokenizer) mid-session.
