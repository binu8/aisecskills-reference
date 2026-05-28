---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: conducting-post-incident-lessons-learned
name: conducting-post-incident-lessons-learned
version: "1.0"
subdomain: incident-response
summary: >-
  Facilitate structured post-incident reviews to identify root causes, document what worked and failed, and produce actionable recommendations to improve future incident response.
references:
  - incident-response
  - lessons-learned
  - post-incident
  - after-action-review
  - process-improvement
---

## When to Use

- After any security incident has been fully resolved and recovery completed
- Following tabletop exercises or IR simulations
- After significant near-miss events
- Quarterly review of accumulated incident trends
- When IR playbooks need updating based on real-world experience

## Procedure


### Step 1: Gather Incident Data
```bash
# Export incident timeline from ticketing system
curl -s "https://thehive.local/api/v1/case/$CASE_ID/timeline" \
  -H "Authorization: Bearer $THEHIVE_API_KEY" | jq '.' > incident_timeline.json

# Extract detection and response metrics from SIEM
index=notable incident_id="IR-2024-042"
| stats min(_time) as first_alert, max(_time) as last_alert,
  count as total_alerts, dc(src) as unique_sources

# Compile all responder actions and timestamps
grep -E "timestamp|action|analyst" /var/log/ir/IR-2024-042/*.json | \
  python3 -m json.tool > compiled_actions.json
```

### Step 2: Conduct Blameless Post-Mortem Meeting
```
Structured Agenda (90 minutes):
1. Incident summary (5 min) - Factual overview
2. Timeline walkthrough (20 min) - Chronological events
3. What worked well (15 min) - Positive outcomes
4. What needs improvement (15 min) - Gaps and failures
5. Root cause analysis (15 min) - 5 Whys or fishbone
6. Action items (10 min) - Specific improvements with owners
7. Playbook updates (10 min) - Changes to IR procedures

Blameless Principles:
- Focus on systems and processes, not individuals
- Assume best intentions with available information
- Seek to understand, not to blame
```

### Step 3: Perform Root Cause Analysis
```bash
# 5 Whys analysis example:
# Why 1: Why did ransomware encrypt production servers?
#   Answer: Attacker had domain admin credentials
# Why 2: Why did attacker have domain admin credentials?
#   Answer: Kerberoasted a service account and cracked it
# Why 3: Why was the service account password crackable?
#   Answer: Used a 12-character dictionary-based password
# Why 4: Why was the service account password weak?
#   Answer: No enforcement of service account password policy
# Why 5: Why was there no service account password policy?
#   Answer: PAM was not implemented for service accounts
# ROOT CAUSE: Lack of privileged access management
```

### Step 4: Calculate Response Metrics
```python
from datetime import datetime
events = {
    'compromise': '2024-01-10 14:00:00',
    'detection': '2024-01-15 08:30:00',
    'triage': '2024-01-15 08:45:00',
    'containment': '2024-01-15 09:30:00',
    'eradication': '2024-01-16 14:00:00',
    'recovery': '2024-01-18 16:00:00',
    'closure': '2024-01-25 10:00:00',
}
fmt = '%Y-%m-%d %H:%M:%S'
times = {k: datetime.strptime(v, fmt) for k, v in events.items()}
print(f"Dwell Time: {times['detection'] - times['compromise']}")
print(f"MTTD: {times['triage'] - times['detection']}")
print(f"MTTC: {times['containment'] - times['detection']}")
print(f"MTTR: {times['recovery'] - times['eradication']}")
print(f"Total Duration: {times['closure'] - times['detection']}")
```

### Step 5: Document Findings and Create Action Items
```bash
# Create tracked action items in project management
curl -X POST "https://jira.local/rest/api/2/issue" \
  -H "Authorization: Bearer $JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "project": {"key": "SEC"},
      "summary": "Implement PAM for service accounts (IR-2024-042)",
      "issuetype": {"name": "Task"},
      "priority": {"name": "High"},
      "assignee": {"name": "security_engineer"},
      "duedate": "2024-03-15"
    }
  }'
```

### Step 6: Update Playbooks and Detection Rules
```yaml
# New Sigma detection rule based on incident learnings
title: Kerberoasting Activity Detected
status: stable
description: Detects Kerberoasting based on IR-2024-042 lessons
logsource:
  product: windows
  service: security
detection:
  selection:
    EventID: 4769
    TicketEncryptionType: '0x17'
  condition: selection
level: high
tags:
  - attack.credential_access
  - attack.t1558.003
```

## Outputs

- Post-incident review meeting minutes
- Root cause analysis document
- Incident metrics report (MTTD, MTTC, MTTR)
- Action items list with owners and deadlines
- Updated IR playbooks and detection rules
- Executive summary for leadership
