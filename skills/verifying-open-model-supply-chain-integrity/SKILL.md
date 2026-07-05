---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: verifying-open-model-supply-chain-integrity
name: verifying-open-model-supply-chain-integrity
version: "1.0"
domain: STA
aicm_controls:
  - STA-07
  - MDS-03
ssrm_ownership: Shared Across Supply Chain
aismm_category: AI Supported Development & Supply Chain Security
aismm_target_level: 3
pillar: security_for_ai
summary: >-
  Use this skill when you need to verify that an open-weight model downloaded
  from a public registry has not been tampered with, backdoored, or substituted
  before it is deployed in your environment.
references:
  - supply-chain-security
  - model-signing
  - HuggingFace
  - sigstore
  - ModelScan
  - SLSA
---

## When to Use

Use this skill when:
- You are downloading an open-weight model from HuggingFace Hub, Ollama, or another registry for production use.
- A security policy requires integrity verification of all model artifacts before deployment.
- A published security advisory mentions potential supply chain compromise of an open model.
- You need to establish a reproducible verification step in your model deployment pipeline.

**Do not use** this skill to evaluate model safety or behavioral properties — it focuses on artifact integrity, not output behavior.

## Inputs

- Model repository ID (e.g., `meta-llama/Llama-3.1-8B-Instruct`) or local artifact path.
- Publisher's published SHA-256 hashes or sigstore signatures (from the model card or release page).
- Optional: ModelScan or custom serialization vulnerability scanner.

## Procedure

### Step 1: Download the model and verify official checksums

```bash
# Download from HuggingFace with huggingface_hub CLI
pip install huggingface_hub

python3 - <<'EOF'
from huggingface_hub import snapshot_download
import hashlib, pathlib

model_id = "meta-llama/Llama-3.1-8B-Instruct"
local_dir = f"./models/{model_id.replace('/', '--')}"

snapshot_download(repo_id=model_id, local_dir=local_dir)

# Compute SHA-256 for every file
for path in sorted(pathlib.Path(local_dir).rglob("*")):
    if path.is_file():
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        print(f"{h}  {path}")
EOF
```

### Step 2: Cross-reference hashes against the published manifest

```python
import hashlib, json, pathlib, requests

def fetch_hf_manifest(model_id: str, revision: str = "main") -> dict:
    """Fetch the model's file manifest from HuggingFace API."""
    url = f"https://huggingface.co/api/models/{model_id}/revision/{revision}"
    resp = requests.get(url)
    resp.raise_for_status()
    return {f["rfilename"]: f.get("lfs", {}).get("sha256", "") for f in resp.json().get("siblings", [])}

def verify_local_against_manifest(local_dir: str, manifest: dict) -> list[str]:
    violations = []
    for filename, expected_sha in manifest.items():
        if not expected_sha:
            continue
        local_path = pathlib.Path(local_dir) / filename
        if not local_path.exists():
            violations.append(f"MISSING: {filename}")
            continue
        actual = hashlib.sha256(local_path.read_bytes()).hexdigest()
        if actual != expected_sha:
            violations.append(f"HASH_MISMATCH: {filename}\n  expected: {expected_sha}\n  actual:   {actual}")
    return violations
```

### Step 3: Scan for malicious serialization payloads with ModelScan

```bash
pip install modelscan

# Scan all model files for pickle-based exploits and unsafe serialization
modelscan scan -p ./models/meta-llama--Llama-3.1-8B-Instruct/

# Fails with non-zero exit code if unsafe patterns found
```

```python
import subprocess, sys

def run_modelscan(model_dir: str) -> bool:
    result = subprocess.run(
        ["modelscan", "scan", "-p", model_dir, "--output", "json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("ModelScan FAILED:", result.stdout)
        return False
    scan_result = json.loads(result.stdout)
    if scan_result.get("summary", {}).get("total_issues", 0) > 0:
        print("ModelScan found issues:", json.dumps(scan_result["issues"], indent=2))
        return False
    return True
```

### Step 4: Verify sigstore signature (if published by the model author)

```bash
# Check if model-signing is available for this model
pip install model-signing

python3 - <<'EOF'
import model_signing
# Verify a signed model artifact
verifier = model_signing.verifier.SigstoreVerifier(
    identity="releases@meta.com",
    oidc_issuer="https://accounts.google.com",
)
verifier.verify("./models/meta-llama--Llama-3.1-8B-Instruct/")
print("Signature verification: PASS")
EOF
```

### Step 5: Record verification in the deployment pipeline

```python
import json, datetime

def record_verification(model_id: str, local_dir: str,
                         violations: list, modelscan_pass: bool) -> dict:
    record = {
        "model_id": model_id,
        "verified_at": datetime.datetime.utcnow().isoformat(),
        "hash_violations": violations,
        "modelscan_pass": modelscan_pass,
        "overall_pass": len(violations) == 0 and modelscan_pass,
    }
    with open(f"{local_dir}/verification-record.json", "w") as f:
        json.dump(record, f, indent=2)
    if not record["overall_pass"]:
        raise RuntimeError(f"Model verification FAILED: {record}")
    return record
```

## Outputs

- SHA-256 manifest comparison report listing any hash mismatches.
- ModelScan report identifying unsafe serialization payloads.
- `verification-record.json` stored with the model artifact.
- CI gate that blocks deployment when verification fails.

## Quality Checks

- [ ] SHA-256 hashes are verified against the authoritative HuggingFace manifest, not a mirror.
- [ ] ModelScan reports zero unsafe serialization issues.
- [ ] Sigstore verification is attempted when the model author publishes signatures.
- [ ] `verification-record.json` is present and `overall_pass: true` before deployment proceeds.
- [ ] Any hash violation halts the deployment pipeline with a clear error message.

**AI-CAIQ evidence:** This skill supports YES response to STA-07 by producing hash verification reports, ModelScan results, and a `verification-record.json` demonstrating that open-weight model artifacts are validated for integrity and absence of malicious payloads before deployment.
