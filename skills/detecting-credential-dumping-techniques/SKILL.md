---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: detecting-credential-dumping-techniques
name: detecting-credential-dumping-techniques
version: "1.0"
subdomain: threat-detection
summary: >-
  Detect LSASS credential dumping, SAM database extraction, and NTDS.dit theft using Sysmon Event ID 10, Windows Security logs, and SIEM correlation rules
references:
  - credential-dumping
  - lsass
  - mimikatz
  - sysmon
  - active-directory
  - windows-security
  - defense-evasion
---

## When to Use


- When you need to detect credential dumping techniques
- When building or tuning detections for this attack pattern and need a structured, step-by-step procedure
- Activates for requests involving: credential-dumping, lsass, mimikatz, sysmon
