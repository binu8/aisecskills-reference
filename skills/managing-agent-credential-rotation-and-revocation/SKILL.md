---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: managing-agent-credential-rotation-and-revocation
name: managing-agent-credential-rotation-and-revocation
version: "1.0"
domain: IAM
aicm_controls:
  - IAM-08
  - CEK-03
ssrm_ownership: AP-Owned
aismm_category: IAM
aismm_target_level: 3
summary: >-
  Use this skill when you need to rotate API keys or secrets used by AI
  agents on a schedule, or immediately revoke credentials when an agent
  is compromised, decommissioned, or behaves anomalously.
references:
  - credential-rotation
  - secrets-management
  - HashiCorp-Vault
  - AWS-Secrets-Manager
  - OIDC
  - incident-response
---

## When to Use

Use this skill when:
- Agent API keys have been in use longer than your rotation policy allows (commonly 30–90 days).
- A security incident or anomalous agent behavior requires immediate credential revocation.
- You are designing a new agent deployment and need to build automated rotation into the lifecycle.
- A compliance audit requires evidence of credential rotation records for non-human identities.

**Do not use** this skill to rotate human user passwords or MFA tokens — this skill is scoped to machine/agent credentials.

## Inputs

- Agent identity register (from `provisioning-non-human-identities-for-ai-agents`).
- Secrets manager or vault holding current agent credentials (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault).
- Rotation schedule policy (max credential age in days).

## Procedure

### Step 1: Store all agent credentials in a secrets manager (never in code)

```bash
# AWS Secrets Manager — create a secret for an agent
aws secretsmanager create-secret \
  --name "agents/agent-research-v1/api-key" \
  --description "API key for research agent v1" \
  --secret-string '{"api_key":"sk-...","created_at":"2025-06-01"}' \
  --tags Key=agent-id,Value=agent-research-v1

# Agent code reads the secret at runtime
import boto3, json

def get_agent_api_key(secret_name: str) -> str:
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])["api_key"]
```

### Step 2: Implement scheduled rotation with AWS Secrets Manager Lambda

```python
# rotation_lambda.py — invoked by Secrets Manager rotation schedule
import boto3, json, datetime

def lambda_handler(event, context):
    secret_id = event["SecretId"]
    step = event["Step"]
    client = boto3.client("secretsmanager")

    if step == "createSecret":
        new_key = generate_new_api_key()  # call provider API to issue new key
        client.put_secret_value(
            SecretId=secret_id,
            VersionStages=["AWSPENDING"],
            SecretString=json.dumps({"api_key": new_key, "created_at": datetime.date.today().isoformat()}),
        )
    elif step == "testSecret":
        pending = json.loads(client.get_secret_value(SecretId=secret_id,
                                                      VersionStage="AWSPENDING")["SecretString"])
        assert test_api_key(pending["api_key"]), "New key validation failed"
    elif step == "finishSecret":
        client.update_secret_version_stage(
            SecretId=secret_id,
            VersionStage="AWSCURRENT",
            MoveToVersionId=event["ClientRequestToken"],
            RemoveFromVersionId=get_current_version_id(client, secret_id),
        )
```

### Step 3: Use HashiCorp Vault dynamic secrets for short-lived credentials

```bash
# Enable database secrets engine and configure a role for the agent
vault secrets enable database
vault write database/config/my-postgres \
  plugin_name=postgresql-database-plugin \
  connection_url="postgresql://{{username}}:{{password}}@localhost/mydb" \
  allowed_roles="agent-reporting"

vault write database/roles/agent-reporting \
  db_name=my-postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" max_ttl="4h"
```

```python
# Agent requests a short-lived credential at runtime
import hvac

vault = hvac.Client(url="https://vault.internal:8200", token=VAULT_TOKEN)
creds = vault.secrets.database.generate_credentials(name="agent-reporting")
db_user = creds["data"]["username"]
db_pass = creds["data"]["password"]
```

### Step 4: Immediately revoke credentials on incident

```python
def revoke_agent_credentials(agent_id: str, reason: str):
    import boto3, datetime, logging
    
    client = boto3.client("secretsmanager")
    secret_name = f"agents/{agent_id}/api-key"
    
    # Mark as compromised and disable
    client.put_resource_policy(
        SecretId=secret_name,
        ResourcePolicy=json.dumps({"Version":"2012-10-17","Statement":[{
            "Effect":"Deny","Principal":"*","Action":"secretsmanager:GetSecretValue","Resource":"*"
        }]})
    )
    
    logging.getLogger("iam.revocation").warning(json.dumps({
        "ts": datetime.datetime.utcnow().isoformat(),
        "agent": agent_id,
        "action": "credential_revoked",
        "reason": reason,
    }))
```

### Step 5: Verify rotation compliance

```python
import boto3, json, datetime

def audit_rotation_compliance(max_age_days: int = 90) -> list[dict]:
    client = boto3.client("secretsmanager")
    violations = []
    paginator = client.get_paginator("list_secrets")
    for page in paginator.paginate(Filters=[{"Key": "tag-key", "Values": ["agent-id"]}]):
        for secret in page["SecretList"]:
            meta = json.loads(client.get_secret_value(SecretId=secret["Name"])["SecretString"])
            created = datetime.date.fromisoformat(meta["created_at"])
            age = (datetime.date.today() - created).days
            if age > max_age_days:
                violations.append({"secret": secret["Name"], "age_days": age})
    return violations
```

## Outputs

- Secrets manager configuration with all agent credentials stored centrally.
- Rotation Lambda or Vault dynamic secrets configuration for automated rotation.
- Revocation function with audit log for incident response.
- Rotation compliance audit report flagging credentials older than the policy maximum.

## Quality Checks

- [ ] No agent credentials exist outside the secrets manager (verified by CI scan).
- [ ] Automated rotation is configured for all agent secrets with a schedule ≤ 90 days.
- [ ] Rotation test verifies the new credential is functional before promoting it to CURRENT.
- [ ] Revocation function fires within 5 minutes of an incident trigger in tabletop test.
- [ ] Compliance audit finds zero credentials older than the maximum age policy.

**AI-CAIQ evidence:** This skill supports YES response to IAM-08 by producing a secrets manager configuration, automated rotation schedule, and a revocation function with audit logs demonstrating that agent credentials are rotated on policy and can be immediately revoked during incidents.
