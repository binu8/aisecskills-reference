---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: prioritizing-vulnerabilities-with-cvss-scoring
name: prioritizing-vulnerabilities-with-cvss-scoring
version: "1.0"
subdomain: vulnerability-management
summary: >-
  The Common Vulnerability Scoring System (CVSS) is the industry standard framework maintained by FIRST (Forum of Incident Response and Security Teams) for assessing vulnerability severity. CVSS v4.0 (r
references:
  - vulnerability-management
  - cve
  - cvss
  - risk
  - prioritization
  - nist
---

## When to Use


- When managing security operations that require prioritizing vulnerabilities with cvss scoring
- When improving security program maturity and operational processes
- When establishing standardized procedures for security team workflows
- When integrating threat intelligence or vulnerability data into operations

## Procedure


### Step 1: Assess Base Metrics
For each vulnerability, evaluate:

```
Example: CVE-2024-3094 (XZ Utils Backdoor)

Attack Vector:        Network (N)     - Exploitable over network
Attack Complexity:    High (H)        - Specific conditions required
Attack Requirements:  Present (P)     - Specific build/config needed
Privileges Required:  None (N)        - No authentication needed
User Interaction:     None (N)        - No victim action needed

Vulnerable System Impact:
  Confidentiality:    High (H)        - Complete access to SSH keys
  Integrity:          High (H)        - Arbitrary code execution
  Availability:       High (H)        - Full system compromise

Subsequent System Impact:
  Confidentiality:    High (H)        - Lateral movement possible
  Integrity:          High (H)        - Network-wide compromise
  Availability:       None (N)        - No downstream availability impact

Vector: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:N
```

### Step 2: Apply Threat Intelligence Context
Enrich CVSS with real-world threat data:

```
Exploit Maturity:     Attacked (A)    - Active exploitation in the wild
EPSS Score:           0.94            - 94% probability of exploitation in 30 days
CISA KEV:            Listed           - Mandatory remediation for federal agencies
```

### Step 3: Calculate Environmental Score
Adjust for organizational context:

```
Confidentiality Req:  High (H)        - Handles PII/financial data
Integrity Req:        High (H)        - Critical business process
Availability Req:     Medium (M)      - Has DR/failover capability

Modified Attack Vector: Network (N)   - Internet-facing deployment
```

### Step 4: Multi-Factor Prioritization Matrix

Combine CVSS with additional prioritization factors:

| Factor | Weight | Source |
|--------|--------|--------|
| CVSS Base Score | 25% | NVD/Scanner |
| EPSS Score | 25% | FIRST EPSS API |
| Asset Criticality | 20% | Asset inventory/CMDB |
| CISA KEV Listed | 15% | CISA catalog |
| Network Exposure | 15% | Network segmentation data |

### Step 5: Define Remediation SLAs

| Priority Level | CVSS Range | EPSS | Asset Tier | SLA |
|---------------|------------|------|------------|-----|
| P1 - Emergency | 9.0-10.0 | >0.5 | Tier 1 | 24-48 hours |
| P2 - Critical | 7.0-8.9 | >0.3 | Tier 1-2 | 7 days |
| P3 - High | 7.0-8.9 | <0.3 | Tier 2-3 | 14 days |
| P4 - Medium | 4.0-6.9 | Any | Any | 30 days |
| P5 - Low | 0.1-3.9 | Any | Any | 90 days |
