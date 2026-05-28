---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: analyzing-powershell-script-block-logging
name: analyzing-powershell-script-block-logging
version: "1.0"
subdomain: security-operations
summary: >-
  Parse Windows PowerShell Script Block Logs (Event ID 4104) from EVTX files to detect obfuscated commands, encoded payloads, and living-off-the-land techniques. Uses python-evtx to extract and reconstruct multi-block scripts, applies entropy analysis and pattern matching for Base64-encoded commands, Invoke-Expression abuse, download cradles, and AMSI bypass attempts.
references:
  - powershell
  - script-block-logging
  - event-id-4104
  - obfuscation-detection
  - windows-forensics
  - endpoint-security
---

## When to Use


- When you need to analyze powershell script block logging
- When correlating logs or investigating security alerts in a SIEM and need a structured, step-by-step procedure
- Activates for requests involving: powershell, obfuscation-detection, windows-forensics, endpoint-security
