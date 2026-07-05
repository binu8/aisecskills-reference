---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: building-an-ai-incident-response-playbook
name: building-an-ai-incident-response-playbook
version: "1.0"
domain: SEF
aicm_controls:
  - SEF-03
  - SEF-06
ssrm_ownership: AIC-Owned
aismm_category: Incident Response
aismm_target_level: 3
pillar: security_from_ai
summary: >-
  Use this skill when you need to create or update an incident response
  playbook that covers AI-specific incident types — model compromise,
  prompt injection attacks, data leakage through LLM outputs, and
  agent credential theft.
references:
  - incident-response
  - playbook
  - NIST-800-61
  - AI-safety
  - CSIRT
  - PagerDuty
---

## When to Use

Use this skill when:
- Your organization has an LLM application in production but no AI-specific incident response procedures.
- An existing general IR playbook must be extended to cover AI-unique incident types.
- A tabletop exercise requires scenario scripts for AI incident scenarios.
- A compliance review requires documented AI incident response procedures.

**Do not use** this skill to investigate an active incident — use the playbook produced by this skill, or see `investigating-compromised-ai-agent-credentials` for that specific scenario.

## Inputs

- Existing general incident response policy or playbook (if any).
- List of deployed AI systems, their data sensitivity, and their business criticality.
- Current on-call and escalation structure.

## Procedure

### Step 1: Define AI-specific incident categories

```yaml
# ai-incident-categories.yaml
categories:
  - id: AI-INC-01
    name: Prompt Injection / Jailbreak Success
    description: An attacker successfully overrides system instructions or elicits policy-violating output
    severity_default: high
    detection_source: [guardrail_alert, log_anomaly, user_report]

  - id: AI-INC-02
    name: Model Data Leakage
    description: LLM response contains PII, trade secrets, or data from unauthorized document sets
    severity_default: critical
    detection_source: [output_scanner, user_report, DLP_alert]

  - id: AI-INC-03
    name: Agent Credential Compromise
    description: Non-human identity used by an AI agent is stolen or misused
    severity_default: critical
    detection_source: [CloudTrail_anomaly, SIEM_alert, anomaly_detection]

  - id: AI-INC-04
    name: Model Supply Chain Compromise
    description: A model artifact or dependency is found to be tampered or backdoored
    severity_default: critical
    detection_source: [ModelScan, hash_mismatch, external_advisory]

  - id: AI-INC-05
    name: Runaway Agent / Goal Hijacking
    description: An autonomous agent takes unintended actions beyond its authorized scope
    severity_default: high
    detection_source: [telemetry_alert, resource_anomaly, user_report]

  - id: AI-INC-06
    name: Model Degradation / Poisoning Detected
    description: Drift monitoring detects a sudden performance drop or behavioral anomaly
    severity_default: medium
    detection_source: [drift_monitor, accuracy_alert]
```

### Step 2: Write the response playbook per incident type

```markdown
# AI Incident Response Playbook — AI-INC-02: Model Data Leakage

## Detection Triggers
- DLP system flags LLM response containing SSN, credit card, or health data pattern
- Output scanner blocks a response with PII confidence >0.85
- User reports receiving information they should not have access to

## Severity Assessment
- **Critical**: Regulated data (PHI, PII, financial) confirmed leaked to unauthorized user
- **High**: Possible leakage, unconfirmed data type
- **Medium**: Policy-adjacent content, no regulated data

## Immediate Actions (0–15 minutes)
1. Alert on-call AI Security Engineer via PagerDuty policy `ai-data-leakage`
2. Retrieve the session ID and user ID from the guardrail/output-scanner alert
3. Pull the raw prompt and response from the encrypted log store (requires security-admin role)
4. Determine the sensitivity of leaked content (PII / PHI / proprietary)

## Containment (15–60 minutes)
1. If regulated data confirmed: immediately disable the affected session/API key
2. If RAG pipeline is the source: identify the document ID and remove from the index
   ```bash
   # Pinecone: delete the offending vector
   index.delete(ids=["doc-id-123"], namespace="tenant-abc")
   ```
3. Block further queries from the affected user pending investigation
4. Notify Privacy/Legal if PHI or financial data is involved (regulatory clock starts now)

## Investigation
1. Trace the leaked content back to its source document via chunk metadata
2. Determine how the document reached the retrieval results (ACL misconfiguration? Filter bypass?)
3. Check if the same document was returned to other users — scope the blast radius

## Recovery
1. Fix the retrieval ACL or filter configuration
2. Re-scan the document store for similarly misconfigured documents
3. Re-enable affected application after fix is verified in staging

## Post-Incident
1. File incident report within 24 hours
2. Update retrieval security tests to cover the missed case
3. Notify affected users per privacy policy
```

### Step 3: Build an incident response automation stub

```python
import json, datetime, requests

PAGERDUTY_ROUTING_KEY = "your-pd-routing-key"

def trigger_ai_incident(incident_type: str, severity: str,
                          details: dict, summary: str):
    payload = {
        "routing_key": PAGERDUTY_ROUTING_KEY,
        "event_action": "trigger",
        "payload": {
            "summary": f"[{incident_type}] {summary}",
            "severity": severity.lower(),
            "source": "ai-security-monitor",
            "custom_details": details,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        },
        "dedup_key": f"{incident_type}-{datetime.date.today().isoformat()}",
    }
    resp = requests.post("https://events.pagerduty.com/v2/enqueue", json=payload)
    resp.raise_for_status()
    return resp.json()
```

### Step 4: Define escalation matrix

```yaml
# escalation-matrix.yaml
escalation:
  critical:
    immediate: [AI-Security-Engineer, Privacy-Officer]
    30min: [CISO, Legal]
    1hr: [CEO-if-regulatory-breach]
  high:
    immediate: [AI-Security-Engineer]
    2hr: [Engineering-Manager, Privacy-Officer]
  medium:
    next_business_day: [AI-Security-Engineer]
```

## Outputs

- `ai-incident-categories.yaml` with 6 AI-specific incident types.
- Playbook document per incident type with detection triggers, containment steps, and recovery actions.
- PagerDuty (or equivalent) automation trigger function.
- Escalation matrix YAML.

## Quality Checks

- [ ] Every deployed AI system maps to at least one playbook incident type.
- [ ] Each playbook includes specific detection sources, not just "monitor the system."
- [ ] Containment steps include concrete commands (API calls, index operations, key revocations).
- [ ] Escalation matrix is reviewed and approved by CISO and Privacy Officer.
- [ ] Tabletop exercise has been conducted for at least two scenario types.

**AI-CAIQ evidence:** This skill supports YES response to SEF-03 by producing documented AI-specific incident response playbooks with detection triggers, containment steps, and escalation matrices that demonstrate the organization has defined procedures for responding to AI security incidents.
