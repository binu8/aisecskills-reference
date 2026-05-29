---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: generating-an-ai-bill-of-materials
name: generating-an-ai-bill-of-materials
version: "1.0"
domain: STA
aicm_controls:
  - STA-07
  - STA-09
ssrm_ownership: AP-Owned
aismm_category: AI Supported Development & Supply Chain Security
aismm_target_level: 4
summary: >-
  Use this skill when you need to produce a machine-readable AI Bill of
  Materials that inventories all models, datasets, libraries, and supply
  chain dependencies for an AI system deployment.
references:
  - AI-BOM
  - CycloneDX
  - SPDX
  - Syft
  - supply-chain-security
  - model-card
---

## When to Use

Use this skill when:
- A deployment pipeline requires an SBOM or AI-BOM artifact before a release is approved.
- A security team needs a complete inventory of all third-party models and datasets used in a system.
- A customer or regulator requests a machine-readable declaration of AI system components.
- You need to assess exposure when a CVE or security advisory is published for an ML component.

**Do not use** this skill as a substitute for behavioral model evaluation — the AI-BOM documents components, not model outputs or safety properties.

## Inputs

- AI application codebase and dependency files (`requirements.txt`, `pyproject.toml`, `conda.yaml`).
- Model cards or HuggingFace model IDs for all models used.
- Dataset metadata (name, version, license, source URL) for training and grounding data.

## Procedure

### Step 1: Collect model component metadata

```python
from dataclasses import dataclass, field

@dataclass
class ModelComponent:
    name: str
    version: str
    source: str          # huggingface, openai-api, internal, etc.
    model_id: str        # e.g. "meta-llama/Llama-3-8B"
    license: str
    sha256: str = ""     # of weights archive, if locally stored
    task: str = ""       # text-generation, embedding, classification
    provider: str = ""

@dataclass
class DatasetComponent:
    name: str
    version: str
    source_url: str
    license: str
    purpose: str         # training, fine-tuning, grounding, evaluation
    pii_screened: bool = False

@dataclass
class AIBom:
    system_name: str
    system_version: str
    generated_at: str
    models: list[ModelComponent] = field(default_factory=list)
    datasets: list[DatasetComponent] = field(default_factory=list)
    software_packages: list[dict] = field(default_factory=list)
```

### Step 2: Generate software component BOM with Syft

```bash
# Install Syft
brew install syft  # macOS
# or: curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh

# Generate CycloneDX JSON BOM from the Python environment
syft dir:./myproject -o cyclonedx-json > software-bom.cyclonedx.json

# Merge model and dataset components below
```

### Step 3: Build the full AI-BOM

```python
import json, datetime, hashlib

def build_ai_bom(system_name: str, system_version: str,
                 models: list[ModelComponent], datasets: list[DatasetComponent],
                 software_bom_path: str) -> dict:
    import dataclasses

    with open(software_bom_path) as f:
        sw_bom = json.load(f)

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{hashlib.sha256(system_name.encode()).hexdigest()[:32]}",
        "metadata": {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "component": {"type": "application", "name": system_name, "version": system_version},
        },
        "components": [
            {
                "type": "machine-learning-model",
                "name": m.name,
                "version": m.version,
                "supplier": {"name": m.provider},
                "licenses": [{"license": {"id": m.license}}],
                "externalReferences": [{"type": "distribution", "url": f"https://huggingface.co/{m.model_id}"}],
                "properties": [
                    {"name": "ai:task", "value": m.task},
                    {"name": "ai:sha256", "value": m.sha256},
                ],
            }
            for m in models
        ] + [
            {
                "type": "data",
                "name": d.name,
                "version": d.version,
                "licenses": [{"license": {"id": d.license}}],
                "externalReferences": [{"type": "distribution", "url": d.source_url}],
                "properties": [
                    {"name": "ai:dataset-purpose", "value": d.purpose},
                    {"name": "ai:pii-screened", "value": str(d.pii_screened)},
                ],
            }
            for d in datasets
        ] + sw_bom.get("components", []),
    }
```

### Step 4: Validate the AI-BOM

```bash
# Validate CycloneDX JSON against the schema
pip install cyclonedx-bom

# Validate structure
python -c "
import json
from cyclonedx.model.bom import Bom
with open('ai-bom.cyclonedx.json') as f:
    data = json.load(f)
print('Component count:', len(data.get('components', [])))
print('Format:', data.get('bomFormat'))
"
```

### Step 5: Attach the AI-BOM to the release artifact

```bash
# Sign and attach to a container image with cosign
cosign attest \
  --predicate ai-bom.cyclonedx.json \
  --type cyclonedx \
  ghcr.io/myorg/my-ai-app:1.0.0
```

## Outputs

- `ai-bom.cyclonedx.json` — CycloneDX 1.5 AI-BOM with model, dataset, and software components.
- Signed attestation attached to the container image or model artifact.
- Component inventory CSV for human review.

## Quality Checks

- [ ] Every model used in the system is listed with name, version, license, and source.
- [ ] Every training/grounding dataset is listed with PII screening status.
- [ ] Software components are generated from the actual deployed artifact, not dev dependencies.
- [ ] CycloneDX JSON is valid against the schema (no parse errors).
- [ ] BOM is signed and its signature is verifiable from the release artifact.

**AI-CAIQ evidence:** This skill supports YES response to STA-07 by producing a signed CycloneDX AI-BOM that provides a complete, machine-readable inventory of all models, datasets, and software components in the AI system, supporting supply chain transparency and vulnerability tracking.
