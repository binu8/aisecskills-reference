---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: verifying-model-integrity-and-provenance-signing
name: verifying-model-integrity-and-provenance-signing
version: "1.0"
domain: MDS
aicm_controls:
  - MDS-03
  - CCC-04
ssrm_ownership: MP-Owned
aismm_category: Model Security
aismm_target_level: 4
pillar: security_for_ai
summary: >-
  Use this skill when you need to cryptographically verify that a model
  artifact has not been tampered with since it was produced, and to sign
  new model artifacts so downstream consumers can establish provenance.
references:
  - sigstore
  - cosign
  - in-toto
  - SLSA
  - model-signing
  - supply-chain-security
---

## When to Use

Use this skill when:
- You are deploying a third-party or open-weight model and need to confirm the weights are authentic.
- Your MLOps pipeline needs to gate model promotion on a valid provenance signature.
- A security audit requires evidence that model artifacts cannot be substituted without detection.
- You are publishing a model and want to give consumers a verifiable chain of custody.

**Do not use** this skill to evaluate model behavior or safety — it addresses artifact integrity only, not runtime correctness.

## Inputs

- Model artifact file(s): weights (`.safetensors`, `.pt`, `.gguf`), config JSON, tokenizer files.
- Signing identity: OIDC token (Sigstore/Fulcio) or a PGP/GPG key pair.
- Optional: existing signature bundle or SLSA provenance attestation to verify.

## Procedure

### Step 1: Compute a cryptographic digest of the model artifact

```bash
# Single file
sha256sum model.safetensors > model.safetensors.sha256

# Directory of sharded weights (HuggingFace format)
find ./model-dir -type f | sort | xargs sha256sum > model-dir.sha256manifest
```

Store the manifest in version control alongside the artifact reference.

### Step 2: Sign with Sigstore cosign (keyless, OIDC-based)

```bash
pip install sigstore  # Python sigstore client

# Sign a model file — produces model.safetensors.sig and records to Rekor transparency log
python -m sigstore sign model.safetensors

# Verify the signature (requires network access to Rekor + Fulcio)
python -m sigstore verify identity \
  --cert-identity "ml-pipeline@mycompany.com" \
  --cert-oidc-issuer "https://accounts.google.com" \
  model.safetensors
```

### Step 3: Generate an in-toto attestation for the build step

```bash
pip install in-toto

# Record the training/export step
in-toto-record start \
  --name export-model \
  --signing-key functional-key.pem \
  --materials training-data.jsonl model-config.json

python export_model.py   # the actual build step

in-toto-record stop \
  --name export-model \
  --signing-key functional-key.pem \
  --products model.safetensors

# Produces link metadata: export-model.<keyid>.link
```

### Step 4: Verify a third-party model before use

```python
import hashlib, requests

KNOWN_HASHES = {
    "model.safetensors": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
}

def verify_artifact(path: str, expected_sha256: str) -> bool:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    actual = h.hexdigest()
    if actual != expected_sha256:
        raise RuntimeError(f"INTEGRITY FAILURE: {path}\n  expected: {expected_sha256}\n  got:      {actual}")
    return True
```

### Step 5: Gate model promotion in CI/CD

```yaml
# .github/workflows/model-promotion.yml (excerpt)
- name: Verify model integrity
  run: |
    python -m sigstore verify identity \
      --cert-identity "${{ secrets.ML_PIPELINE_EMAIL }}" \
      --cert-oidc-issuer "https://token.actions.githubusercontent.com" \
      model.safetensors
    echo "Integrity verified — promoting to staging"
```

## Outputs

- SHA-256 manifest file for all model artifacts.
- Sigstore signature bundle (`.sig` / `.crt`) and Rekor log entry URL.
- in-toto link metadata recording the build step.
- CI gate configuration that blocks promotion when verification fails.

## Quality Checks

- [ ] SHA-256 digest matches the published manifest before any deployment.
- [ ] Sigstore verification completes without error against the expected OIDC identity.
- [ ] Rekor transparency log entry is retrievable and matches the local signature.
- [ ] CI pipeline fails the promotion step when a tampered artifact is substituted.
- [ ] in-toto link metadata covers at least the final export/packaging step.

**AI-CAIQ evidence:** This skill supports YES response to MDS-03 by producing signed artifacts, Rekor log entries, and CI gate configurations that demonstrate model artifacts are cryptographically verified before deployment and that tampering is detectable.
