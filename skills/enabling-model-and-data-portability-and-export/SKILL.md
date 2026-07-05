---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: enabling-model-and-data-portability-and-export
name: enabling-model-and-data-portability-and-export
version: "1.0"
domain: IPY
aicm_controls:
  - IPY-02
  - IPY-04
ssrm_ownership: Shared MP-OSP
aismm_category: Data Security
aismm_target_level: 3
pillar: security_for_ai
summary: >-
  Use this skill when you need to implement model and training data export
  capabilities so that an organization can migrate away from a provider,
  exercise data portability rights, or fulfill GDPR data export obligations.
references:
  - data-portability
  - GDPR
  - model-export
  - ONNX
  - interoperability
  - vendor-lock-in
---

## When to Use

Use this skill when:
- Your organization needs to migrate an AI workload from one cloud provider to another.
- A GDPR or CCPA request requires exporting personal data used in AI training or stored in AI system outputs.
- A contract with an AI provider is ending and you need to extract model artifacts and data.
- An AI governance policy requires that all AI systems support portability as a design requirement.

**Do not use** this skill to export data that belongs to a third party — verify data ownership before executing any export.

## Inputs

- Model artifact location (proprietary format, HuggingFace, or provider-hosted).
- Training and grounding data storage (S3, GCS, Azure Blob, database).
- Target destination for the exported artifacts.

## Procedure

### Step 1: Assess portability status of each AI component

```python
PORTABILITY_CHECKLIST = {
    "model_weights": {
        "questions": [
            "Are weights stored in an open format (safetensors, GGUF, ONNX)?",
            "Does the provider allow weight export?",
            "Is the export path documented in the service agreement?",
        ]
    },
    "training_data": {
        "questions": [
            "Is training data stored in provider-agnostic formats (Parquet, JSONL, CSV)?",
            "Does your DPA require the provider to return/delete data on request?",
            "Are data storage costs paid separately or bundled?",
        ]
    },
    "fine_tuning_adapters": {
        "questions": [
            "Are LoRA/adapter weights exportable separately from base model?",
            "Are fine-tuning hyperparameters and configs versioned?",
        ]
    },
    "vector_store": {
        "questions": [
            "Does the vector store support bulk export of vectors + metadata?",
            "Are embeddings re-computable from source documents?",
        ]
    },
}
```

### Step 2: Export model weights to a portable format

```python
# HuggingFace → ONNX export
from transformers import AutoModelForCausalLM, AutoTokenizer
from optimum.exporters.onnx import main_export

model_id = "my-org/my-finetuned-model"
output_dir = "./exports/my-model-onnx"

main_export(
    model_name_or_path=model_id,
    output=output_dir,
    task="text-generation",
)
print(f"Model exported to ONNX at {output_dir}")
```

```bash
# SafeTensors — already portable; verify all shards are exported
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="my-org/my-finetuned-model",
    local_dir="./exports/my-model-safetensors",
    ignore_patterns=["*.bin"],  # prefer safetensors over pytorch .bin
)
```

### Step 3: Export vector store contents

```python
# Pinecone: export all vectors and metadata
import pinecone, json

def export_pinecone_index(index_name: str, namespace: str, output_path: str):
    index = pinecone.Index(index_name)
    stats = index.describe_index_stats()
    total = stats["namespaces"].get(namespace, {}).get("vector_count", 0)
    
    all_vectors = []
    # Fetch in batches (Pinecone fetch is by ID — use list endpoint or a scan pattern)
    # For production use, iterate through known IDs from your metadata store
    results = index.query(vector=[0.0]*1536, top_k=min(total, 10000),
                          namespace=namespace, include_values=True, include_metadata=True)
    all_vectors.extend(results["matches"])
    
    with open(output_path, "w") as f:
        json.dump(all_vectors, f)
    print(f"Exported {len(all_vectors)} vectors to {output_path}")
```

### Step 4: Export training data with data subject identification for GDPR

```python
import pandas as pd

def export_training_data_gdpr(parquet_path: str, data_subject_id: str,
                               id_column: str, output_path: str):
    """Export all training records associated with a specific data subject."""
    df = pd.read_parquet(parquet_path)
    subject_records = df[df[id_column] == data_subject_id]
    subject_records.to_json(output_path, orient="records", lines=True)
    print(f"Exported {len(subject_records)} records for subject {data_subject_id}")
    return len(subject_records)
```

### Step 5: Validate the export is complete and usable

```python
import hashlib, pathlib

def validate_export(source_manifest_path: str, export_dir: str) -> dict:
    with open(source_manifest_path) as f:
        manifest = json.load(f)
    
    issues = []
    for entry in manifest["files"]:
        exported = pathlib.Path(export_dir) / entry["filename"]
        if not exported.exists():
            issues.append(f"MISSING: {entry['filename']}")
            continue
        actual_sha = hashlib.sha256(exported.read_bytes()).hexdigest()
        if actual_sha != entry["sha256"]:
            issues.append(f"HASH_MISMATCH: {entry['filename']}")
    
    return {"total": len(manifest["files"]), "issues": issues,
            "valid": len(issues) == 0}
```

## Outputs

- Model weights in ONNX or SafeTensors format ready for import to any compatible runtime.
- Vector store export JSON with vectors and metadata.
- GDPR data-subject export for training data records.
- Export validation report confirming completeness and hash integrity.

## Quality Checks

- [ ] Exported model loads and produces equivalent output in the target environment.
- [ ] Vector store export covers 100% of vectors (count verified against index stats).
- [ ] GDPR export is complete within 30 days and covers all identified subject records.
- [ ] Export validation SHA-256 check passes with zero hash mismatches.
- [ ] Export process is documented and could be repeated by a different team member.

**AI-CAIQ evidence:** This skill supports YES response to IPY-02 by producing model weight exports in portable open formats, vector store exports, and a validation report demonstrating that AI model artifacts and associated data can be extracted and migrated without dependency on a single provider.
