---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: triaging-security-incident-with-ir-playbook
name: triaging-security-incident-with-ir-playbook
version: "1.0"
subdomain: incident-response
summary: >-
  Classify and prioritize security incidents using structured IR playbooks to determine severity, assign response teams, and initiate appropriate response procedures.
references:
  - incident-response
  - triage
  - playbook
  - severity-classification
  - soc
---

## When to Use

- New security alert received from SIEM, EDR, or other detection sources
- SOC analyst needs to determine if an alert is a true positive requiring response
- Incident needs severity classification and team assignment
- Multiple concurrent incidents require prioritization
- Automated triage rules need validation or tuning

## Procedure


### Step 1: Receive and Acknowledge Alert
```bash
# Query Splunk for new critical/high severity alerts
index=notable status=new severity IN ("critical","high")
| table _time, rule_name, src, dest, severity, description
| sort -_time

# Query TheHive for new cases
curl -s -H "Authorization: Bearer $THEHIVE_API_KEY" \
  "https://thehive.local/api/v1/query?name=list-alerts" \
  -H "Content-Type: application/json" \
  -d '{"query":[{"_name":"listAlert"},{"_name":"filter","_field":"status","_value":"New"}]}'

# Acknowledge alert in SIEM to prevent duplicate triage
curl -X POST "https://splunk.local:8089/services/notable_update" \
  -H "Authorization: Bearer $SPLUNK_TOKEN" \
  -d "ruleUIDs=$RULE_UID&status=1&comment=Triage+initiated+by+analyst"
```

### Step 2: Enrich Alert Data
```bash
# Enrich source IP with VirusTotal
curl -s "https://www.virustotal.com/api/v3/ip_addresses/$SRC_IP" \
  -H "x-apikey: $VT_API_KEY" | jq '.data.attributes.last_analysis_stats'

# Check IP reputation with AbuseIPDB
curl -s "https://api.abuseipdb.com/api/v2/check?ipAddress=$SRC_IP&maxAgeInDays=90" \
  -H "Key: $ABUSEIPDB_KEY" -H "Accept: application/json" | jq '.data'

# Enrich file hash with threat intelligence
curl -s "https://www.virustotal.com/api/v3/files/$FILE_HASH" \
  -H "x-apikey: $VT_API_KEY" | jq '.data.attributes.last_analysis_stats'

# Query internal asset database for affected systems
curl -s "https://cmdb.local/api/assets?ip=$DEST_IP" \
  -H "Authorization: Bearer $CMDB_TOKEN" | jq '.asset_criticality, .owner, .environment'
```

### Step 3: Classify Incident Type
```bash
# Map alert to incident category using playbook lookup
# Categories: Malware, Phishing, Unauthorized Access, Data Exfiltration,
# DoS/DDoS, Insider Threat, Ransomware, Account Compromise, Web Attack

# Check if alert matches known playbook trigger conditions
grep -i "$ALERT_SIGNATURE" /opt/ir/playbooks/trigger_conditions.yaml

# Determine incident type from MITRE ATT&CK technique
curl -s "https://attack.mitre.org/api/techniques/$TECHNIQUE_ID" | jq '.name, .tactic'
```

### Step 4: Assign Severity Level
```bash
# Severity matrix factors:
# 1. Asset criticality (Critical/High/Medium/Low)
# 2. Data sensitivity (PII/PHI/PCI/Confidential/Public)
# 3. Number of affected systems
# 4. Active vs historical threat
# 5. Confirmed vs suspected compromise

# Automated severity calculation
python3 -c "
severity_score = 0
# Asset criticality: Critical=4, High=3, Medium=2, Low=1
severity_score += 4  # Critical server
# Data sensitivity: PII/PHI=4, PCI=3, Confidential=2, Public=1
severity_score += 3  # PCI data
# Scope: Enterprise=4, Department=3, Single system=2, Single user=1
severity_score += 2  # Single system
# Threat status: Active=4, Recent=3, Historical=2, Potential=1
severity_score += 4  # Active threat

if severity_score >= 12: print('CRITICAL - P1')
elif severity_score >= 9: print('HIGH - P2')
elif severity_score >= 6: print('MEDIUM - P3')
else: print('LOW - P4')
print(f'Score: {severity_score}/16')
"
```

### Step 5: Select and Initiate Playbook
```bash
# Load appropriate playbook based on incident type
cat /opt/ir/playbooks/ransomware_playbook.yaml
cat /opt/ir/playbooks/phishing_playbook.yaml
cat /opt/ir/playbooks/unauthorized_access_playbook.yaml

# Create incident ticket in TheHive
curl -X POST "https://thehive.local/api/v1/case" \
  -H "Authorization: Bearer $THEHIVE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "IR-2024-XXX: [Incident Type] - [Brief Description]",
    "description": "Triage summary and initial findings",
    "severity": 3,
    "tlp": 2,
    "pap": 2,
    "tags": ["ransomware", "triage-complete"],
    "customFields": {
      "playbook": {"string": "ransomware_v2"},
      "affected_systems": {"integer": 5}
    }
  }'
```

### Step 6: Assign Response Team
```bash
# Check on-call schedule
curl -s "https://pagerduty.com/api/v2/oncalls?schedule_ids[]=$SCHEDULE_ID" \
  -H "Authorization: Token token=$PD_TOKEN" | jq '.oncalls[].user.summary'

# Page incident responders based on severity
# P1/Critical: Page IR lead + senior analysts + CISO
# P2/High: Page IR lead + available analysts
# P3/Medium: Assign to next available analyst
# P4/Low: Queue for business hours processing

curl -X POST "https://events.pagerduty.com/v2/enqueue" \
  -H "Content-Type: application/json" \
  -d '{
    "routing_key": "'$PD_ROUTING_KEY'",
    "event_action": "trigger",
    "payload": {
      "summary": "P1 Security Incident: Ransomware detected on PROD-DB-01",
      "severity": "critical",
      "source": "SIEM-Splunk",
      "custom_details": {"incident_id": "IR-2024-042", "playbook": "ransomware_v2"}
    }
  }'
```

### Step 7: Document Triage Decision and Hand Off
```bash
# Update incident ticket with triage summary
curl -X PATCH "https://thehive.local/api/v1/case/$CASE_ID" \
  -H "Authorization: Bearer $THEHIVE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "InProgress",
    "customFields": {
      "triage_analyst": {"string": "analyst_name"},
      "triage_time": {"date": '$(date +%s000)'},
      "severity_justification": {"string": "Critical asset + active threat + PCI data"}
    }
  }'
```

## Outputs

- Triage decision document with severity justification
- Incident ticket with assigned playbook and team
- IOC enrichment summary attached to case
- Escalation notification to appropriate stakeholders
- Initial timeline of events from alert data
