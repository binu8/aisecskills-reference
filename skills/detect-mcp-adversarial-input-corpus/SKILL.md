---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution. Detection script vendored from
# msaad00/cloud-ai-security-skills — see vendor/msaad00-mcp-detection/.
id: detect-mcp-adversarial-input-corpus
name: detect-mcp-adversarial-input-corpus
version: "1.0"
domain: AIS
aicm_controls:
  - AIS-08
ssrm_ownership: Shared OSP-AP
aismm_category: Security Monitoring
aismm_target_level: 4
pillar: security_from_ai
atlas_techniques:
  - AML.T0043
summary: >-
  Use this skill when you need runtime detection of adversarial prompts / jailbreak attempts matching a curated fingerprint catalog, by
  running the vendored detector to detect MCP requests whose prompt matches an entry in a curated adversarial-input fingerprint catalog (prompt injection, jailbreak, role-play hijack) and emit OCSF detection findings.
references:
  - MCP
  - prompt-injection
  - jailbreak
  - OCSF
  - detection
---

## When to Use

Use this skill when:
- You need to detect adversarial prompts / jailbreak attempts matching a curated fingerprint catalog.
- You have MCP proxy logs (or OCSF 1.8 Application Activity records) from an MCP deployment and need a runtime detection over them.

**Do not use** this skill on raw MCP proxy logs directly — normalize them first through the vendored `ingest-mcp-proxy-ocsf`; and do not treat it as a preventive control (it is detection, so pair it with `securing-mcp-server-and-tool-boundaries` and `bounding-agent-autonomy-and-tool-scopes-least-privilege`).

## Inputs

- MCP proxy logs in JSON Lines, normalized to OCSF 1.8 Application Activity (class 6002) via `ingest-mcp-proxy-ocsf`.
- The vendored detector at `vendor/msaad00-mcp-detection/skills/detection/detect-mcp-adversarial-input-corpus/src/detect.py`.
- Configuration for this detector: Deterministic pattern scanner over a frozen fingerprint catalog; fails open (no findings, no crash) if the catalog is missing.

## Procedure

The detector is vendored (Apache-2.0, from `msaad00/cloud-ai-security-skills`) at
`vendor/msaad00-mcp-detection/skills/detection/detect-mcp-adversarial-input-corpus/src/detect.py`. Run it over OCSF-normalized MCP activity:

```bash
python3 vendor/msaad00-mcp-detection/skills/ingestion/ingest-mcp-proxy-ocsf/src/ingest.py mcp-proxy.jsonl \
  | python3 vendor/msaad00-mcp-detection/skills/detection/detect-mcp-adversarial-input-corpus/src/detect.py \
  > findings.ocsf.jsonl
```

Deterministic pattern scanner over a frozen fingerprint catalog; fails open (no findings, no crash) if the catalog is missing. The detector emits one OCSF 1.8 Detection Finding (class 2004) per detected event.

## Outputs

- OCSF 1.8 Detection Finding records (class 2004), one per detected event, ready for SIEM ingestion and triage.

## Quality Checks

- [ ] The vendored test suite passes: `python3 -m pytest vendor/msaad00-mcp-detection/skills/detection/detect-mcp-adversarial-input-corpus/tests/`
- [ ] Raw proxy logs are normalized through `ingest-mcp-proxy-ocsf` before this detector runs.
- [ ] Findings are shipped to the SIEM or detection pipeline, not left on disk.
- [ ] The detector's configuration (deterministic pattern scanner over a frozen fingerprint catalog) matches the deployment.

**AI-CAIQ evidence:** This skill supports a YES response to AIS-08 by producing OCSF detection findings that demonstrate runtime monitoring for adversarial prompts / jailbreak attempts matching a curated fingerprint catalog.
