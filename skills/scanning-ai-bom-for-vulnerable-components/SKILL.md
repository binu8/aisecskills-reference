---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: scanning-ai-bom-for-vulnerable-components
name: scanning-ai-bom-for-vulnerable-components
version: "1.0"
domain: TVM
aicm_controls:
  - TVM-04
  - STA-09
ssrm_ownership: AP-Owned
aismm_category: AI Supported Development & Supply Chain Security
aismm_target_level: 4
summary: >-
  Use this skill when you need to generate an AI Bill of Materials and
  scan it for known CVEs, malicious packages, and supply chain risks in
  ML frameworks, model dependencies, and data pipeline libraries.
references:
  - SBOM
  - CycloneDX
  - Grype
  - Syft
  - CVE
  - supply-chain-security
---

## When to Use

Use this skill when:
- An AI application is being prepared for deployment and requires a vulnerability scan of its dependencies.
- A supply chain security audit needs a machine-readable inventory of all ML components.
- A new CVE is published for a common ML framework (PyTorch, TensorFlow, Transformers) and you need to assess exposure.
- CI/CD gates require an SBOM with a clean vulnerability report before promotion.

**Do not use** this skill to assess model behavioral risks — it focuses on software component vulnerabilities, not model safety.

## Inputs

- Python environment (`requirements.txt`, `pyproject.toml`, `conda.yaml`) or container image.
- Target vulnerability severity threshold (e.g., block on Critical/High).

## Procedure

### Step 1: Generate an SBOM with Syft

```bash
pip install syft  # or use the standalone binary

# Generate CycloneDX SBOM from a Python virtual environment
syft dir:./myproject -o cyclonedx-json > ai-bom.cyclonedx.json

# Or from a container image
syft ghcr.io/myorg/my-ai-app:latest -o cyclonedx-json > ai-bom.cyclonedx.json
```

### Step 2: Scan the SBOM for CVEs with Grype

```bash
# Install Grype
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Scan the SBOM — fail if Critical or High CVEs found
grype sbom:ai-bom.cyclonedx.json \
  --fail-on high \
  -o json > grype-results.json

# Human-readable table output
grype sbom:ai-bom.cyclonedx.json -o table
```

### Step 3: Check for ML-specific malicious packages (typosquatting)

```python
# Known typosquatted ML package names (partial list — keep updated)
TYPOSQUATTED_ML_PACKAGES = [
    "transformes", "tramsformers", "pytoch", "tesnorflow",
    "langchan", "langchian", "openal", "openal-api",
]

import subprocess, json

def check_typosquatting(requirements_path: str) -> list[str]:
    with open(requirements_path) as f:
        installed = [line.strip().split("==")[0].split(">=")[0].lower()
                     for line in f if line.strip() and not line.startswith("#")]
    return [pkg for pkg in installed if pkg in TYPOSQUATTED_ML_PACKAGES]
```

### Step 4: Verify package integrity against PyPI hashes

```bash
# pip-audit checks installed packages against PyPI Advisory Database
pip install pip-audit

pip-audit --format json -o pip-audit-results.json
pip-audit  # print table to stdout

# For requirements.txt
pip-audit -r requirements.txt --format json -o pip-audit-results.json
```

### Step 5: Integrate into CI/CD as a gate

```yaml
# .github/workflows/ai-sbom-scan.yml
name: AI BOM Vulnerability Scan
on: [push, pull_request]
jobs:
  sbom-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate SBOM
        run: syft dir:. -o cyclonedx-json > ai-bom.cyclonedx.json
      - name: Scan SBOM
        run: |
          grype sbom:ai-bom.cyclonedx.json --fail-on high -o json > grype-results.json
      - name: Upload SBOM artifact
        uses: actions/upload-artifact@v4
        with:
          name: ai-bom
          path: |
            ai-bom.cyclonedx.json
            grype-results.json
```

### Step 6: Parse results and generate a compliance report

```python
import json

def summarize_grype_results(results_path: str) -> dict:
    with open(results_path) as f:
        data = json.load(f)
    matches = data.get("matches", [])
    by_severity = {}
    for m in matches:
        sev = m["vulnerability"]["severity"]
        by_severity[sev] = by_severity.get(sev, 0) + 1
    return {
        "total_vulnerabilities": len(matches),
        "by_severity": by_severity,
        "pass": by_severity.get("Critical", 0) == 0 and by_severity.get("High", 0) == 0,
    }
```

## Outputs

- `ai-bom.cyclonedx.json` — CycloneDX SBOM for all ML components.
- `grype-results.json` — CVE scan results with severity breakdown.
- `pip-audit-results.json` — PyPI advisory database scan.
- Typosquatting check results.
- CI/CD gate configuration that blocks promotion on Critical/High CVEs.

## Quality Checks

- [ ] SBOM is generated from the exact artifact being deployed (not a dev environment).
- [ ] Grype scan fails the CI build when Critical or High CVEs are present.
- [ ] pip-audit covers all packages in `requirements.txt` with no skipped packages.
- [ ] Typosquatting check runs against the full package list.
- [ ] SBOM artifact is stored and linked to the deployment record.

**AI-CAIQ evidence:** This skill supports YES response to TVM-04 by producing a CycloneDX SBOM, CVE scan reports, and a CI gate configuration demonstrating that all AI application components are inventoried and scanned for known vulnerabilities before deployment.
