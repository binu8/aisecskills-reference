---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: provisioning-non-human-identities-for-ai-agents
name: provisioning-non-human-identities-for-ai-agents
version: "1.0"
domain: IAM
aicm_controls:
  - IAM-03
  - IAM-12
ssrm_ownership: AP-Owned
aismm_category: IAM
aismm_target_level: 4
summary: >-
  Use this skill when you need to create, scope, and govern dedicated
  non-human identities for AI agents — service accounts, workload identities,
  or machine credentials — separate from human user accounts.
references:
  - workload-identity
  - SPIFFE
  - service-accounts
  - AWS-IAM
  - Azure-Managed-Identity
  - least-privilege
---

## When to Use

Use this skill when:
- An AI agent needs to call APIs, read databases, or write to cloud storage with its own auditable identity.
- A security review flagged that agents share credentials with human users or other services.
- You are setting up a new autonomous agent in production and need to provision its identity from scratch.
- An IAM audit requires evidence that non-human identities are tracked in a central register.

**Do not use** this skill for managing the credentials themselves after provisioning — see `managing-agent-credential-rotation-and-revocation` for lifecycle management.

## Inputs

- Agent name, purpose, and owning team.
- List of resources and APIs the agent requires access to.
- Cloud provider or identity platform (AWS IAM, Azure AD, GCP Workload Identity, Kubernetes SPIFFE).

## Procedure

### Step 1: Register the agent identity in a central inventory

```yaml
# agent-identity-register.yaml (entry per agent)
- agent_id: agent-research-v1
  display_name: "Research Agent v1"
  owner_team: ai-platform
  created_date: "2025-06-01"
  purpose: "Retrieves and summarizes internal knowledge base articles"
  identity_type: service_account
  platform: aws
  aws_iam_role: arn:aws:iam::123456789012:role/agent-research-v1
  allowed_resources:
    - arn:aws:s3:::kb-documents/*
    - arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku
  review_date: "2025-12-01"
```

### Step 2: Create a least-privilege IAM role (AWS example)

```bash
# Create the role with a workload-scoped trust policy
aws iam create-role \
  --role-name agent-research-v1 \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole",
      "Condition": {"StringEquals": {"aws:RequestedRegion": "us-east-1"}}
    }]
  }'

# Attach only the permissions required
aws iam put-role-policy \
  --role-name agent-research-v1 \
  --policy-name agent-research-v1-policy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {"Effect":"Allow","Action":["s3:GetObject"],"Resource":"arn:aws:s3:::kb-documents/*"},
      {"Effect":"Allow","Action":["bedrock:InvokeModel"],"Resource":"arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku"}
    ]
  }'
```

### Step 3: Use SPIFFE/SPIRE for platform-agnostic workload identity

```bash
# Install SPIRE server and agent, then issue an SVID for the agent workload
spire-server entry create \
  -spiffeID spiffe://myorg.com/agent/research-v1 \
  -parentID spiffe://myorg.com/spire/agent/k8s \
  -selector k8s:ns:ai-agents \
  -selector k8s:sa:agent-research-v1

# Agent code retrieves its X.509 SVID from the SPIFFE Workload API
from pyspiffe.workloadapi import WorkloadApiClient

with WorkloadApiClient() as client:
    svid = client.fetch_x509_svid()
    print(f"Agent SPIFFE ID: {svid.spiffe_id}")
```

### Step 4: Tag identities for discoverability and governance

```bash
aws iam tag-role \
  --role-name agent-research-v1 \
  --tags \
    Key=agent-id,Value=agent-research-v1 \
    Key=owner-team,Value=ai-platform \
    Key=review-date,Value=2025-12-01 \
    Key=purpose,Value=kb-retrieval
```

### Step 5: Enforce that agents never use human credentials

```python
# CI check: assert no agent code references personal access tokens or user API keys
import ast, pathlib, sys

FORBIDDEN_PATTERNS = ["AWS_ACCESS_KEY_ID", "AZURE_CLIENT_SECRET", "OPENAI_API_KEY"]
violations = []
for py_file in pathlib.Path("agents/").rglob("*.py"):
    text = py_file.read_text()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in text and "os.environ" not in text:
            violations.append(f"{py_file}: hardcoded credential pattern '{pattern}'")

if violations:
    print("\n".join(violations))
    sys.exit(1)
```

## Outputs

- `agent-identity-register.yaml` entry for each provisioned agent.
- IAM role or SPIFFE SVID configuration with least-privilege policy.
- Tagged cloud identity resources for governance and review scheduling.
- CI check confirming no hardcoded or human credentials in agent code.

## Quality Checks

- [ ] Every agent has a unique, named identity — no shared credentials across agents.
- [ ] IAM policy is scoped to the minimum required resources and actions.
- [ ] Identity register entry includes owner, purpose, and scheduled review date.
- [ ] SPIFFE SVID or workload identity is configured for short-lived credential issuance.
- [ ] CI check blocks hardcoded credential patterns from being committed.

**AI-CAIQ evidence:** This skill supports YES response to IAM-03 by producing an agent identity register, least-privilege IAM role configurations, and a CI check demonstrating that AI agents are provisioned with dedicated, scoped non-human identities separate from human accounts.
