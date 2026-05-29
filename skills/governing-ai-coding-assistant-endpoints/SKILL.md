---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: governing-ai-coding-assistant-endpoints
name: governing-ai-coding-assistant-endpoints
version: "1.0"
domain: UEM
aicm_controls:
  - UEM-03
  - UEM-09
ssrm_ownership: AIC-Owned
aismm_category: Organization Management
aismm_target_level: 3
summary: >-
  Use this skill when you need to govern which AI coding assistant endpoints
  developers may connect to from managed devices, preventing data leakage to
  unapproved external AI services through IDE plugins and CLI tools.
references:
  - endpoint-management
  - MDM
  - developer-tools
  - data-loss-prevention
  - AI-governance
  - proxy
---

## When to Use

Use this skill when:
- Developers are using AI coding assistants (GitHub Copilot, Cursor, Continue, Tabnine) from managed corporate laptops.
- A security audit found that proprietary source code is being sent to unapproved AI provider endpoints.
- A DLP review requires inventory and control of all AI-bound network traffic from developer endpoints.
- You are rolling out an AI coding assistant program and need to approve the endpoint before the first commit.

**Do not use** this skill as the sole control for code security — AI-assisted code still requires security review; this skill governs the data flow, not the code output.

## Inputs

- MDM or UEM platform (Jamf, Intune, Kandji, or similar).
- Corporate network proxy or DNS filtering solution (Zscaler, Palo Alto, Cisco Umbrella).
- List of approved AI coding assistant tools and their API endpoints.

## Procedure

### Step 1: Build the approved AI endpoint registry

```yaml
# approved-ai-coding-endpoints.yaml
approved:
  - tool: GitHub Copilot
    endpoints:
      - api.githubcopilot.com
      - copilot-proxy.githubusercontent.com
    data_handling: "No code retention; Business tier with DPA"
    max_data_class: confidential

  - tool: Continue (self-hosted)
    endpoints:
      - llm-gateway.internal.mycompany.com
    data_handling: "Internal endpoint; data stays on-prem"
    max_data_class: restricted

blocked:
  - ChatGPT web (chat.openai.com) — no DPA for code use
  - Cursor (cursor.sh) — pending provider review
  - Codeium — not approved, no DPA signed
```

### Step 2: Configure DNS/proxy blocking for unapproved AI endpoints

```bash
# Zscaler Cloud Firewall — block unapproved AI coding endpoints
# (Configure via Zscaler Admin Portal or API)

# Cisco Umbrella: add custom block list via API
curl -X POST "https://management.api.umbrella.com/v1/organizations/{orgId}/destinationlists/{listId}/destinations" \
  -H "Authorization: Basic $(echo -n 'key:secret' | base64)" \
  -H "Content-Type: application/json" \
  -d '{
    "destinations": [
      {"destination": "cursor.sh", "comment": "Pending AI tool review"},
      {"destination": "www.codeium.com", "comment": "Not approved — no DPA"}
    ]
  }'
```

```bash
# Pi-hole / local DNS for dev network: add block list
cat >> /etc/pihole/custom.list << 'EOF'
0.0.0.0 cursor.sh
0.0.0.0 codeium.com
EOF
pihole restartdns
```

### Step 3: Deploy MDM configuration profile to restrict IDE plugin installs

```xml
<!-- Jamf configuration profile — macOS extension attribute for IDE plugin audit -->
<!-- Deploy via Jamf Policy to developer machines -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
        <dict>
            <key>PayloadType</key>
            <string>com.apple.systempolicy.control</string>
            <key>AllowIdentifiedDevelopers</key>
            <true/>
        </dict>
    </array>
</dict>
</plist>
```

### Step 4: Audit AI tool endpoint connections with DLP

```python
# Parse proxy logs to identify AI-bound traffic from developer endpoints
import re, csv

AI_ENDPOINT_PATTERNS = [
    re.compile(r"api\.githubcopilot\.com"),
    re.compile(r"api\.openai\.com"),
    re.compile(r"api\.anthropic\.com"),
    re.compile(r"aip\.samsung\.com"),
    re.compile(r"cursor\.sh"),
]

def audit_proxy_logs(log_path: str, output_csv: str):
    hits = []
    with open(log_path) as f:
        for line in f:
            for pattern in AI_ENDPOINT_PATTERNS:
                if pattern.search(line):
                    hits.append({"line": line[:300], "pattern": pattern.pattern})
    
    with open(output_csv, "w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=["pattern", "line"])
        writer.writeheader()
        writer.writerows(hits)
    print(f"{len(hits)} AI endpoint connections found in proxy logs")
```

### Step 5: Enforce a code-commit hook that flags AI-generated markers

```bash
# .git/hooks/pre-commit — warn if GitHub Copilot suggestion markers are present
#!/bin/bash
if git diff --cached | grep -q "# Copilot"; then
  echo "WARNING: Possible AI-generated code marker found. Review before committing."
  echo "Run 'git diff --cached' to inspect."
  exit 0  # warn only, don't block — adjust to exit 1 to block
fi
```

## Outputs

- `approved-ai-coding-endpoints.yaml` with approved tools, endpoints, and data class limits.
- DNS/proxy block list configuration for unapproved AI endpoints.
- MDM configuration profile for developer machine governance.
- Proxy log audit report showing AI endpoint connection counts per tool.

## Quality Checks

- [ ] All approved AI coding assistant endpoints are listed with their data class maximum.
- [ ] Unapproved endpoints are blocked at the DNS or proxy layer and verified by test query.
- [ ] MDM enrollment covers ≥95% of developer-class managed devices.
- [ ] Proxy log audit runs at least monthly and results are reviewed by the security team.
- [ ] Approved endpoint registry is reviewed whenever a new AI coding tool is requested.

**AI-CAIQ evidence:** This skill supports YES response to UEM-03 by producing an approved AI endpoint registry, DNS/proxy block configurations, and proxy audit reports demonstrating that AI coding assistant data flows from managed developer endpoints are inventoried, controlled, and reviewed.
