# Vendored: MCP threat-detection skills (msaad00/cloud-ai-security-skills)

This directory contains a **vendored, third-party** subset of
[`msaad00/cloud-ai-security-skills`](https://github.com/msaad00/cloud-ai-security-skills),
licensed under the Apache License 2.0 (see [`LICENSE`](LICENSE)). It is kept as a
self-contained subtree so the detection scripts run and self-verify without modification.

## Provenance

- **Source:** https://github.com/msaad00/cloud-ai-security-skills
- **Commit:** `c5e5d03208719c298bb07e72d9ce32cf2b0e31e5` (branch `main`)
- **License:** Apache-2.0 (upstream has no NOTICE file)

## What was included

- The ten MCP / prompt-injection detection skills under `skills/detection/`:
  `detect-mcp-shadow-tool-injection`, `detect-mcp-tool-drift`,
  `detect-mcp-model-artifact-tampering`, `detect-mcp-adversarial-input-corpus`,
  `detect-mcp-unbounded-tool-output`, `detect-mcp-model-token-flood`,
  `detect-mcp-plugin-supply-chain`, `detect-prompt-injection-mcp-proxy`,
  `detect-system-prompt-extraction`, `detect-tool-output-exfiltration-instructions`
  (each with `src/`, `tests/`, and golden fixtures).
- The shared ingestion skill `skills/ingestion/ingest-mcp-proxy-ocsf/`.
- The shared runtime package `skills/_shared/` imported by the detectors.
- The shared OCSF golden fixtures and contract used by the tests
  (`skills/detection-engineering/`), and the root pytest scaffolding
  (`conftest.py`, `tests/_pytest_isolation.py`).

## Changes from upstream

Structure and code are **unmodified**. The only change is **removal** of upstream
material not needed by these skills: unrelated detection skills, the cloud/IAM/k8s
integration and conformance test suites, and golden fixtures for other detectors.

## Running the detectors and tests

```bash
# From this directory (vendor/msaad00-mcp-detection/)
python3 -m pytest skills/detection/detect-mcp-tool-drift/tests/ -q

# Run a detector over OCSF-normalized MCP proxy logs
python3 skills/ingestion/ingest-mcp-proxy-ocsf/src/ingest.py mcp-proxy.jsonl \
  | python3 skills/detection/detect-mcp-tool-drift/src/detect.py \
  > drift-findings.ocsf.jsonl
```

The reference-library wrappers for these skills live in the top-level `skills/`
directory and point at the scripts here.
