---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: validating-training-data-provenance-and-lineage
name: validating-training-data-provenance-and-lineage
version: "1.0"
domain: DSP
aicm_controls:
  - DSP-03
  - STA-07
ssrm_ownership: MP-Owned
aismm_category: Data Security
aismm_target_level: 3
pillar: security_for_ai
summary: >-
  Use this skill when you need to establish or verify the chain of custody
  for a training dataset — confirming source, transformation history, and
  licensing before a model is trained or released.
references:
  - data-lineage
  - SBOM
  - DVC
  - Apache-Atlas
  - supply-chain-security
  - licensing
---

## When to Use

Use this skill when:
- You are preparing a dataset for model training and need to document its origin, transformations, and consent/license status.
- A compliance review requires evidence that training data was collected and processed lawfully.
- A supply-chain audit surfaces a third-party dataset whose provenance is unknown.
- You are responding to a copyright or privacy complaint about model outputs.

**Do not use** this skill for real-time inference data monitoring; it focuses on batch training dataset lineage, not streaming inference pipelines.

## Inputs

- Dataset files or object-store URIs (S3, GCS, Azure Blob).
- Any existing data catalog entries (Apache Atlas, DataHub, Alation, or a spreadsheet manifest).
- License files or data-use agreements for each source.

## Procedure

### Step 1: Inventory all data sources

Create a machine-readable manifest for every dataset component:

```yaml
# dataset-manifest.yaml
dataset_name: model-v2-training-corpus
version: "2.1.0"
sources:
  - id: cc-news-2023
    uri: s3://my-training-data/cc-news-2023/
    license: CC-BY-4.0
    origin: CommonCrawl
    collection_date: "2023-11-01"
    sha256_manifest: abc123...
  - id: internal-docs
    uri: s3://my-training-data/internal-docs/
    license: proprietary
    origin: internal-wiki
    pii_screened: true
    pii_screening_date: "2024-01-15"
```

### Step 2: Compute and store dataset fingerprints

```bash
# Generate SHA-256 checksums for all files in a dataset partition
find /data/cc-news-2023 -type f | sort | xargs sha256sum > cc-news-2023.sha256sums

# For large datasets, use DVC to track and version data
dvc add /data/cc-news-2023
git add /data/cc-news-2023.dvc .gitignore
git commit -m "Track cc-news-2023 dataset provenance"
```

### Step 3: Record transformation lineage

Each processing step must be logged with inputs, outputs, and code version:

```python
import hashlib, json, datetime

def log_transformation(step_name: str, input_paths: list, output_path: str, script_sha: str):
    record = {
        "step": step_name,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "inputs": input_paths,
        "output": output_path,
        "script_sha256": script_sha,
    }
    with open("lineage-log.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")
```

Use Apache Atlas or DataHub REST API to register lineage programmatically:

```python
# DataHub GMS REST example
import requests
payload = {
    "proposedSnapshot": {
        "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot": {
            "urn": "urn:li:dataset:(urn:li:dataPlatform:s3,my-training-data/cc-news-2023,PROD)",
            "aspects": [{"com.linkedin.pegasus2avro.common.Ownership": {"owners": [{"owner": "urn:li:corpuser:mlteam"}]}}]
        }
    }
}
requests.post("http://datahub-gms:8080/entities?action=ingest", json=payload)
```

### Step 4: Validate license compatibility

```python
LICENSE_ALLOW = {"CC-BY-4.0", "CC-BY-SA-4.0", "MIT", "Apache-2.0", "CC0-1.0"}
LICENSE_PROHIBIT_COMMERCIAL = {"CC-BY-NC-4.0", "CC-BY-NC-SA-4.0"}

def check_licenses(manifest_path: str) -> dict:
    import yaml
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    issues = []
    for src in manifest["sources"]:
        lic = src.get("license", "UNKNOWN")
        if lic == "UNKNOWN":
            issues.append({"source": src["id"], "issue": "license unknown"})
        elif lic in LICENSE_PROHIBIT_COMMERCIAL:
            issues.append({"source": src["id"], "issue": f"{lic} prohibits commercial use"})
    return {"total_sources": len(manifest["sources"]), "issues": issues}
```

### Step 5: Generate a Data Bill of Materials (DBoM)

```bash
# Produce a SPDX-compatible data BOM
python3 - <<'EOF'
import json, yaml, hashlib

with open("dataset-manifest.yaml") as f:
    manifest = yaml.safe_load(f)

sbom = {
    "spdxVersion": "SPDX-2.3",
    "dataLicense": "CC0-1.0",
    "SPDXID": "SPDXRef-DOCUMENT",
    "name": manifest["dataset_name"],
    "packages": [
        {
            "SPDXID": f"SPDXRef-{src['id']}",
            "name": src["id"],
            "downloadLocation": src["uri"],
            "licenseConcluded": src["license"],
        }
        for src in manifest["sources"]
    ]
}
print(json.dumps(sbom, indent=2))
EOF
```

## Outputs

- `dataset-manifest.yaml` with all sources, licenses, and PII screening records.
- `lineage-log.jsonl` recording every transformation step with input/output hashes.
- SHA-256 checksum file per dataset partition.
- License compatibility report listing any prohibited or unknown licenses.
- SPDX-formatted Data Bill of Materials.

## Quality Checks

- [ ] Every dataset source has a recorded license and origin in the manifest.
- [ ] SHA-256 checksums are stored and match current files (no undocumented modifications).
- [ ] License compatibility check returns zero commercial-use violations.
- [ ] Transformation lineage log covers every ETL/preprocessing step with script SHA.
- [ ] DBoM is machine-parseable valid SPDX or CycloneDX JSON.

**AI-CAIQ evidence:** This skill supports YES response to DSP-03 by producing a dataset manifest, lineage log, and SPDX Data Bill of Materials that document the origin, custody chain, and licensing status of all training data.
