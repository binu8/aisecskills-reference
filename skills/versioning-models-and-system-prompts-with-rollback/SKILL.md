---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: versioning-models-and-system-prompts-with-rollback
name: versioning-models-and-system-prompts-with-rollback
version: "1.0"
domain: CCC
aicm_controls:
  - CCC-03
  - CCC-04
ssrm_ownership: AP-Owned
aismm_category: Organization Management
aismm_target_level: 3
summary: >-
  Use this skill when you need to implement version control and rollback
  capability for AI model artifacts and system prompts, so that a bad
  deployment can be reverted within minutes without manual intervention.
references:
  - version-control
  - MLflow
  - DVC
  - rollback
  - GitOps
  - change-management
---

## When to Use

Use this skill when:
- A model update or system prompt change caused a regression and needs to be rolled back quickly.
- A compliance requirement mandates that every change to a production AI system is versioned and auditable.
- You are building a new AI deployment pipeline and need to include rollback capability from the start.
- An audit requires evidence of change management for AI model and configuration updates.

**Do not use** this skill for data backup and recovery — this skill focuses on model artifact and configuration versioning, not training data preservation.

## Inputs

- Current model deployment pipeline (CI/CD configuration).
- System prompt files or configuration (YAML, JSON, or plain text).
- Model registry or artifact store (MLflow, S3, Azure ML, Vertex AI).

## Procedure

### Step 1: Version system prompts in Git

```bash
# Store all system prompts as versioned files
mkdir -p prompts/
cat > prompts/customer-support-v1.2.0.txt << 'EOF'
You are a helpful customer support assistant for Acme Corp.
You may only answer questions about Acme products.
Do not discuss competitors, pricing not listed in the Acme catalog, or internal processes.
EOF

git add prompts/
git commit -m "chore: system prompt customer-support v1.2.0

Changes from v1.1.0:
- Tightened competitor mention restriction
- Removed deprecated product category handling"
git tag prompt-customer-support-v1.2.0
```

### Step 2: Register model versions in MLflow

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

def register_model_version(model_path: str, model_name: str,
                            tags: dict, description: str) -> str:
    with mlflow.start_run() as run:
        mlflow.log_param("model_path", model_path)
        mlflow.log_dict(tags, "metadata.json")
        mlflow.log_artifact(model_path)
        model_uri = f"runs:/{run.info.run_id}/model"
    
    mv = mlflow.register_model(model_uri=model_uri, name=model_name)
    client.update_model_version(
        name=model_name,
        version=mv.version,
        description=description,
    )
    for k, v in tags.items():
        client.set_model_version_tag(model_name, mv.version, k, v)
    
    print(f"Registered {model_name} version {mv.version}")
    return mv.version

# Promote to production
def promote_to_production(model_name: str, version: str):
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage="Production",
        archive_existing_versions=True,
    )
```

### Step 3: Implement atomic deployment with version tagging

```yaml
# deployment-manifest.yaml — the single source of truth for what's deployed
deployment:
  service: customer-support-chatbot
  model:
    name: support-llm
    version: "7"
    registry: mlflow
  system_prompt:
    file: prompts/customer-support-v1.2.0.txt
    git_ref: prompt-customer-support-v1.2.0
  deployed_at: "2025-06-01T10:00:00Z"
  deployed_by: ci-pipeline
  previous_deployment:
    model_version: "6"
    system_prompt_git_ref: prompt-customer-support-v1.1.0
```

### Step 4: Implement automated rollback

```python
import subprocess, yaml, datetime

def rollback_deployment(manifest_path: str):
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    
    prev = manifest["deployment"]["previous_deployment"]
    
    print(f"Rolling back to model v{prev['model_version']} + prompt {prev['system_prompt_git_ref']}")
    
    # Restore previous model in MLflow
    client.transition_model_version_stage(
        name=manifest["deployment"]["model"]["name"],
        version=prev["model_version"],
        stage="Production",
        archive_existing_versions=True,
    )
    
    # Restore previous system prompt
    subprocess.run(["git", "checkout", prev["system_prompt_git_ref"], "--", "prompts/"], check=True)
    
    # Update manifest
    manifest["deployment"]["previous_deployment"] = manifest["deployment"].copy()
    manifest["deployment"]["model"]["version"] = prev["model_version"]
    manifest["deployment"]["system_prompt"]["git_ref"] = prev["system_prompt_git_ref"]
    manifest["deployment"]["deployed_at"] = datetime.datetime.utcnow().isoformat()
    manifest["deployment"]["deployed_by"] = "rollback-procedure"
    
    with open(manifest_path, "w") as f:
        yaml.dump(manifest, f)
    
    print("Rollback complete — verify application behavior")
```

### Step 5: Test rollback in staging

```bash
# Simulate a bad deployment and verify rollback restores expected behavior
python test_rollback.py --stage staging --expected-prompt-version v1.1.0
```

## Outputs

- Git-versioned system prompt files with tags per release.
- MLflow model registry entries with stage transitions and metadata.
- `deployment-manifest.yaml` recording current and previous deployment versions.
- `rollback_deployment()` function tested in staging.

## Quality Checks

- [ ] Every system prompt change is committed and tagged in Git before deployment.
- [ ] Every model version is registered in MLflow with description and tags.
- [ ] `deployment-manifest.yaml` always records the previous deployment for rollback reference.
- [ ] Rollback completes within the defined RTO (commonly <5 minutes).
- [ ] Rollback test in staging confirms the previous model and prompt version are restored.

**AI-CAIQ evidence:** This skill supports YES response to CCC-03 by producing versioned system prompt files, MLflow model registry records, and a tested rollback function demonstrating that changes to production AI models and configurations can be reverted rapidly with full audit history.
