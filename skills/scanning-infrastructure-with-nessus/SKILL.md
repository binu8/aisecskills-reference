---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: scanning-infrastructure-with-nessus
name: scanning-infrastructure-with-nessus
version: "1.0"
subdomain: vulnerability-management
summary: >-
  Tenable Nessus is the industry-leading vulnerability scanner used to identify security weaknesses across network infrastructure including servers, workstations, network devices, and operating systems.
references:
  - vulnerability-management
  - cve
  - nessus
  - tenable
  - infrastructure-scanning
  - risk
---

## When to Use


- When you need to scanning infrastructure with nessus
- When assessing, prioritizing, or tracking vulnerabilities and need a structured, step-by-step procedure
- Activates for requests involving Nessus in a vulnerability management context

## Procedure


### Step 1: Initial Configuration
```bash
# Start Nessus service
sudo systemctl start nessusd
sudo systemctl enable nessusd

# CLI management with nessuscli
/opt/nessus/sbin/nessuscli update --all
/opt/nessus/sbin/nessuscli fix --list

# Verify plugin count
/opt/nessus/sbin/nessuscli update --plugins-only
```

### Step 2: Create Scan Policy
Configure a custom scan policy through the Nessus web UI at https://localhost:8834:

1. Navigate to Policies > New Policy > Advanced Scan
2. Configure General settings: name, description, targets
3. Set Discovery settings:
   - Host Discovery: Ping methods (ICMP, TCP SYN on ports 22,80,443)
   - Port Scanning: SYN scan on common ports or all 65535 ports
   - Service Discovery: Probe all ports for services
4. Configure Assessment settings:
   - Accuracy: Override normal accuracy (reduce false positives)
   - Web Applications: Enable if scanning web servers
5. Select Plugin families relevant to target environment

### Step 3: Configure Credentials
For authenticated scanning, configure credentials under the Credentials tab:
- **SSH**: Username/password or SSH key pair
- **Windows**: Domain credentials via SMB, WMI
- **SNMP**: Community strings (v1/v2c) or USM credentials (v3)
- **Database**: Oracle, MySQL, PostgreSQL connection strings
- **VMware**: vCenter or ESXi credentials

### Step 4: Run the Scan
```
# Using Nessus REST API via curl
# Authenticate and get token
curl -k -X POST https://localhost:8834/session \
  -d '{"username":"admin","password":"password"}' \
  -H "Content-Type: application/json"

# Create scan
curl -k -X POST https://localhost:8834/scans \
  -H "X-Cookie: token=<TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "uuid": "<TEMPLATE_UUID>",
    "settings": {
      "name": "Infrastructure Scan Q1",
      "text_targets": "192.168.1.0/24",
      "enabled": true,
      "launch": "ON_DEMAND"
    }
  }'

# Launch scan
curl -k -X POST https://localhost:8834/scans/<SCAN_ID>/launch \
  -H "X-Cookie: token=<TOKEN>"

# Check scan status
curl -k -X GET https://localhost:8834/scans/<SCAN_ID> \
  -H "X-Cookie: token=<TOKEN>"
```

### Step 5: Analyze Results
Nessus categorizes findings by severity:
- **Critical (CVSS 9.0-10.0)**: Immediate remediation required
- **High (CVSS 7.0-8.9)**: Remediate within 7-14 days
- **Medium (CVSS 4.0-6.9)**: Remediate within 30 days
- **Low (CVSS 0.1-3.9)**: Remediate during next maintenance window
- **Informational**: No immediate action required

### Step 6: Export and Report
```bash
# Export via REST API
curl -k -X POST "https://localhost:8834/scans/<SCAN_ID>/export" \
  -H "X-Cookie: token=<TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"format":"nessus"}'

# Supported formats: nessus (XML), csv, html, pdf
```
