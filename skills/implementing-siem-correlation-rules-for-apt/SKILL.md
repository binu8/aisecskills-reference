---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: implementing-siem-correlation-rules-for-apt
name: implementing-siem-correlation-rules-for-apt
version: "1.0"
subdomain: security-operations
summary: >-
  Write multi-event correlation rules that detect APT lateral movement by chaining Windows authentication events, process execution telemetry, and network connection logs across hosts. Uses Splunk SPL and Sigma rule format to correlate Event IDs 4624, 4648, 4688, and Sysmon Events 1/3 within sliding time windows to surface attack sequences invisible to single-event detections.
references:
  - implementing
  - siem
  - correlation
  - rules
---

## When to Use


- When you need to write multi-event correlation rules that detect APT lateral movement by chaining Windows authentication events, process execution telemetry, and network connection logs across hosts.
- When correlating logs or investigating security alerts in a SIEM and need a structured, step-by-step procedure
- Activates for requests involving Splunk, Sigma in a security operations context
