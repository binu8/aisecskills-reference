---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: investigating-compromised-ai-agent-credentials
name: investigating-compromised-ai-agent-credentials
version: "1.0"
domain: SEF
aicm_controls:
  - SEF-04
  - IAM-08
ssrm_ownership: Shared AP-AIC
aismm_category: Incident Response
aismm_target_level: 4
summary: >-
  Use this skill when you suspect or have confirmed that credentials used
  by an AI agent have been stolen or misused, and need to contain the
  incident, reconstruct the timeline, and restore secure operations.
references:
  - incident-response
  - credential-compromise
  - CloudTrail
  - SIEM
  - forensics
  - IAM
---

## When to Use

Use this skill when:
- SIEM or CloudTrail alerts fire on API calls from an agent identity at unusual times, from unusual IPs, or for unusual actions.
- An agent is observed making API calls that are outside its authorized tool set.
- A secrets manager alert indicates that an agent secret was accessed from an unexpected source.
- A security researcher or internal report indicates agent credentials were found in a code repository or log.

**Do not use** this skill for investigating human account compromise — the focus is specifically on non-human AI agent identities and their unique patterns.

## Inputs

- Agent identity (IAM role ARN, service account name, API key prefix).
- SIEM or cloud provider activity logs covering the suspected compromise window.
- Agent identity register (from `provisioning-non-human-identities-for-ai-agents`).

## Procedure

### Step 1: Immediately revoke the compromised credential

```python
import boto3, json, datetime, logging

def emergency_revoke(agent_id: str, reason: str):
    iam = boto3.client("iam")
    sts = boto3.client("sts")
    
    # Attach a deny-all policy to block all active sessions immediately
    iam.put_role_policy(
        RoleName=agent_id,
        PolicyName="EMERGENCY-DENY-ALL",
        PolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Deny", "Action": "*", "Resource": "*"}]
        })
    )
    
    logging.warning(json.dumps({
        "event": "emergency_credential_revocation",
        "agent": agent_id,
        "ts": datetime.datetime.utcnow().isoformat(),
        "reason": reason,
    }))
    print(f"REVOKED: {agent_id} — all active sessions blocked")
```

### Step 2: Pull the activity timeline from CloudTrail

```bash
# Query CloudTrail for all API calls made by the agent role in the past 7 days
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue="arn:aws:iam::123456789012:role/agent-research-v1" \
  --start-time "$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --output json > agent-cloudtrail.json
```

```python
import json
from collections import Counter

def analyze_cloudtrail(events_path: str) -> dict:
    with open(events_path) as f:
        data = json.load(f)
    events = data.get("Events", [])
    
    actions = Counter(e["EventName"] for e in events)
    source_ips = Counter(e.get("SourceIPAddress", "unknown") for e in events)
    user_agents = Counter(e.get("UserAgent", "unknown") for e in events)
    
    # Flag unusual actions not in the agent's authorized tool set
    AUTHORIZED_ACTIONS = {"GetObject", "InvokeModel"}  # expected for research agent
    unauthorized = {action for action in actions if action not in AUTHORIZED_ACTIONS}
    
    return {
        "total_events": len(events),
        "action_counts": dict(actions.most_common(20)),
        "source_ips": dict(source_ips.most_common(10)),
        "unauthorized_actions": list(unauthorized),
        "first_event": min(e["EventTime"] for e in events) if events else None,
        "last_event": max(e["EventTime"] for e in events) if events else None,
    }
```

### Step 3: Identify the exfiltration or lateral movement

```python
HIGH_RISK_ACTIONS = [
    "AssumeRole", "CreateUser", "AttachUserPolicy", "CreateAccessKey",
    "PutBucketPolicy", "GetSecretValue", "CreateRole",
    "InvokeFunction", "StartInstances",
]

def identify_high_risk_events(events_path: str) -> list[dict]:
    with open(events_path) as f:
        data = json.load(f)
    return [
        {
            "event": e["EventName"],
            "time": e["EventTime"],
            "ip": e.get("SourceIPAddress"),
            "resources": [r.get("ARN", "") for r in e.get("Resources", [])],
        }
        for e in data.get("Events", [])
        if e["EventName"] in HIGH_RISK_ACTIONS
    ]
```

### Step 4: Determine the compromise vector

```python
COMPROMISE_INDICATORS = {
    "hardcoded_in_code": "Check git history for accidental credential commit",
    "leaked_in_logs": "Search log aggregator for key prefix in plain-text log lines",
    "stolen_from_instance": "Check EC2 metadata service access logs for IMDS requests from unexpected IPs",
    "supply_chain": "Check if a dependency was recently updated and has known issues",
}

def assess_compromise_vector(timeline: dict) -> str:
    """
    Heuristic: if first unauthorized event coincides with a deployment or code commit,
    suspect hardcoded credential; if from a new IP, suspect exfiltration.
    """
    if len(timeline.get("source_ips", {})) > 3:
        return "multiple_ips — possible credential sharing or exfiltration"
    return "single_ip — insider threat or stolen from running workload"
```

### Step 5: Issue a replacement credential and verify clean state

```python
def restore_agent_identity(agent_id: str, region: str = "us-east-1"):
    """Remove the emergency deny policy and issue a new secret after investigation."""
    iam = boto3.client("iam")
    
    # Remove emergency deny
    iam.delete_role_policy(RoleName=agent_id, PolicyName="EMERGENCY-DENY-ALL")
    
    # Rotate the secret in Secrets Manager
    sm = boto3.client("secretsmanager", region_name=region)
    sm.rotate_secret(SecretId=f"agents/{agent_id}/api-key")
    
    print(f"Restored: {agent_id} — new credentials issued, emergency deny removed")
```

## Outputs

- CloudTrail activity timeline with all API calls made by the compromised identity.
- High-risk action report flagging lateral movement or data exfiltration events.
- Compromise vector assessment.
- Post-incident record with revocation timestamp, timeline, and remediation actions.

## Quality Checks

- [ ] Emergency revocation fires within 5 minutes of incident declaration.
- [ ] CloudTrail query covers the full compromise window, not just 24 hours.
- [ ] All unauthorized actions are identified against the agent's known-good tool set.
- [ ] Compromise vector assessment is documented for the post-incident report.
- [ ] New credential is issued only after the revocation and investigation are complete.

**AI-CAIQ evidence:** This skill supports YES response to SEF-04 by producing a CloudTrail-based incident timeline, unauthorized action report, and documented revocation procedure demonstrating that compromised AI agent credentials are contained and investigated with a reproducible forensic process.
