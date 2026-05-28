---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: implementing-cloud-security-posture-management
name: implementing-cloud-security-posture-management
version: "1.0"
subdomain: cloud-security
summary: >-
  Implementing Cloud Security Posture Management (CSPM) to continuously monitor multi-cloud environments for misconfigurations, compliance violations, and security risks using Prowler, ScoutSuite, AWS Security Hub, Azure Defender, and GCP Security Command Center.
references:
  - cloud-security
  - cspm
  - multi-cloud
  - compliance
  - prowler
  - scoutsuite
---

## When to Use


- When establishing continuous security monitoring across AWS, Azure, and GCP environments
- When compliance requirements demand automated posture assessment against CIS, SOC 2, or PCI DSS
- When security teams need visibility into cloud misconfigurations across multiple accounts and subscriptions
- When building a security operations workflow that detects and remediates drift from security baselines
- When migrating workloads to the cloud and need to enforce security guardrails

**Do not use** for runtime workload protection (use CWPP tools like Falco or Aqua), for application security testing (use DAST/SAST tools), or for network intrusion detection (use cloud-native IDS like GuardDuty or Network Watcher).

## Procedure


### Step 1: Deploy Cloud-Native CSPM Services

Enable the built-in CSPM capabilities in each cloud provider for baseline posture assessment.

```bash
# AWS: Enable Security Hub with FSBP and CIS standards
aws securityhub enable-security-hub --enable-default-standards
aws securityhub batch-enable-standards --standards-subscription-requests \
  '[{"StandardsArn":"arn:aws:securityhub:::standards/cis-aws-foundations-benchmark/v/1.4.0"}]'

# Azure: Enable Microsoft Defender for Cloud (CSPM tier)
az security pricing create --name CloudPosture --tier standard
az security auto-provisioning-setting update --name default --auto-provision on

# GCP: Enable Security Command Center Premium
gcloud services enable securitycenter.googleapis.com
gcloud scc settings update --organization=ORG_ID \
  --enable-asset-discovery
```

### Step 2: Run Prowler for Multi-Cloud Assessment

Execute Prowler to perform comprehensive security checks across all three cloud providers.

```bash
# AWS assessment with all CIS checks
prowler aws \
  --profile production \
  -M json-ocsf csv html \
  -o ./prowler-results/aws/ \
  --compliance cis_1.4_aws cis_1.5_aws

# Azure assessment
prowler azure \
  --subscription-ids SUB_ID_1 SUB_ID_2 \
  -M json-ocsf csv html \
  -o ./prowler-results/azure/ \
  --compliance cis_2.0_azure

# GCP assessment
prowler gcp \
  --project-ids project-1 project-2 \
  -M json-ocsf csv html \
  -o ./prowler-results/gcp/ \
  --compliance cis_2.0_gcp

# View summary across all providers
prowler aws --list-compliance
```

### Step 3: Run ScoutSuite for Cross-Cloud Comparison

Use ScoutSuite for a unified multi-cloud security assessment with visual reporting.

```bash
# Scan AWS
python3 -m ScoutSuite aws --profile production \
  --report-dir ./scoutsuite/aws/

# Scan Azure
python3 -m ScoutSuite azure --cli \
  --all-subscriptions \
  --report-dir ./scoutsuite/azure/

# Scan GCP
python3 -m ScoutSuite gcp --user-account \
  --all-projects \
  --report-dir ./scoutsuite/gcp/

# Each produces an HTML report with risk-scored findings
```

### Step 4: Build Automated Compliance Monitoring Pipeline

Create a scheduled pipeline that runs CSPM checks daily and routes findings to appropriate channels.

```bash
# Create a daily Prowler scan with EventBridge + CodeBuild (AWS)
cat > buildspec.yml << 'EOF'
version: 0.2
phases:
  install:
    commands:
      - pip install prowler
  build:
    commands:
      - prowler aws -M json-ocsf -o s3://security-findings-bucket/prowler/$(date +%Y%m%d)/
      - prowler aws --compliance cis_1.5_aws -M csv -o s3://security-findings-bucket/prowler/compliance/
  post_build:
    commands:
      - |
        CRITICAL=$(cat output/*.json | grep -c '"CRITICAL"')
        if [ "$CRITICAL" -gt 0 ]; then
          aws sns publish --topic-arn arn:aws:sns:us-east-1:ACCOUNT:security-alerts \
            --subject "Prowler: $CRITICAL critical findings" \
            --message "Review at s3://security-findings-bucket/prowler/$(date +%Y%m%d)/"
        fi
EOF

# Schedule with EventBridge
aws events put-rule \
  --name daily-prowler-scan \
  --schedule-expression "cron(0 6 * * ? *)" \
  --state ENABLED
```

### Step 5: Configure Finding Aggregation and Deduplication

Aggregate findings from multiple CSPM tools and cloud providers into a unified view.

```python
# findings_aggregator.py - Normalize and deduplicate CSPM findings
import json
import hashlib
from datetime import datetime

def normalize_finding(finding, source):
    """Normalize findings from different CSPM tools to a common format."""
    normalized = {
        'id': hashlib.sha256(f"{finding.get('ResourceId','')}{finding.get('CheckId','')}".encode()).hexdigest()[:16],
        'source': source,
        'cloud': finding.get('Provider', 'unknown'),
        'account': finding.get('AccountId', finding.get('SubscriptionId', '')),
        'region': finding.get('Region', ''),
        'resource_type': finding.get('ResourceType', ''),
        'resource_id': finding.get('ResourceId', ''),
        'severity': finding.get('Severity', 'INFO').upper(),
        'status': finding.get('Status', 'FAIL'),
        'title': finding.get('CheckTitle', finding.get('Title', '')),
        'description': finding.get('StatusExtended', ''),
        'compliance': finding.get('Compliance', {}),
        'remediation': finding.get('Remediation', {}).get('Recommendation', {}).get('Text', ''),
        'timestamp': datetime.utcnow().isoformat()
    }
    return normalized

def aggregate_findings(prowler_file, scoutsuite_file):
    findings = {}
    for file_path, source in [(prowler_file, 'prowler'), (scoutsuite_file, 'scoutsuite')]:
        with open(file_path) as f:
            for line in f:
                raw = json.loads(line)
                normalized = normalize_finding(raw, source)
                if normalized['status'] == 'FAIL':
                    findings[normalized['id']] = normalized
    return sorted(findings.values(), key=lambda x: {'CRITICAL':0,'HIGH':1,'MEDIUM':2,'LOW':3}.get(x['severity'],4))
```

### Step 6: Implement Drift Detection and Auto-Remediation

Set up automated responses to configuration drift that violates security baselines.

```bash
# AWS Config auto-remediation for non-compliant S3 buckets
aws configservice put-remediation-configurations --remediation-configurations '[{
  "ConfigRuleName": "s3-bucket-public-read-prohibited",
  "TargetType": "SSM_DOCUMENT",
  "TargetId": "AWS-DisableS3BucketPublicReadWrite",
  "Parameters": {
    "S3BucketName": {"ResourceValue": {"Value": "RESOURCE_ID"}}
  },
  "Automatic": true,
  "MaximumAutomaticAttempts": 3,
  "RetryAttemptSeconds": 60
}]'

# Azure Policy for auto-remediation
az policy assignment create \
  --name "enforce-storage-encryption" \
  --policy "/providers/Microsoft.Authorization/policyDefinitions/404c3081-a854-4457-ae30-26a93ef643f9" \
  --scope "/subscriptions/SUB_ID" \
  --enforcement-mode Default

# GCP Organization Policy constraint
gcloud resource-manager org-policies set-policy policy.yaml --organization=ORG_ID
# policy.yaml: constraint: constraints/storage.publicAccessPrevention, enforcement: true
```

## Outputs


```
Cloud Security Posture Management Dashboard
==============================================
Organization: Acme Corp
Assessment Date: 2026-02-23
Environments: AWS (12 accounts), Azure (8 subscriptions), GCP (5 projects)

POSTURE SCORES:
  AWS:   82/100  (+3 from last week)
  Azure: 76/100  (-1 from last week)
  GCP:   79/100  (+5 from last week)
  Overall: 79/100

FINDINGS BY SEVERITY:
  Critical:  18 (AWS: 7, Azure: 8, GCP: 3)
  High:      67 (AWS: 28, Azure: 24, GCP: 15)
  Medium:   234 (AWS: 98, Azure: 87, GCP: 49)
  Low:      412 (AWS: 178, Azure: 134, GCP: 100)

TOP FAILING CATEGORIES:
  1. IAM overly permissive policies     (43 findings)
  2. Encryption not enabled at rest      (38 findings)
  3. Public network exposure             (29 findings)
  4. Logging and monitoring gaps         (24 findings)
  5. Unused credentials and keys         (19 findings)

AUTO-REMEDIATION (Last 7 Days):
  Findings auto-remediated:  34
  Manual remediation pending: 51
  Exceptions approved:        8
```
