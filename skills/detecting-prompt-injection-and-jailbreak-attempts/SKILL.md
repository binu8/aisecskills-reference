---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: detecting-prompt-injection-and-jailbreak-attempts
name: detecting-prompt-injection-and-jailbreak-attempts
version: "1.0"
domain: LOG
aicm_controls:
  - LOG-08
  - AIS-08
ssrm_ownership: AP-Owned
aismm_category: Security Monitoring
aismm_target_level: 4
pillar: security_for_ai
summary: >-
  Use this skill when you need to monitor LLM application logs for
  prompt injection and jailbreak attempts in real time, alert on patterns,
  and feed detections into a SIEM for incident response.
references:
  - prompt-injection
  - jailbreak-detection
  - SIEM
  - Sigma
  - log-analysis
  - OWASP-LLM-Top-10
---

## When to Use

Use this skill when:
- An LLM application is live and you need continuous security monitoring, not just pre-deployment defenses.
- A security operations team needs detection rules for a SIEM that covers LLM-specific attacks.
- A post-incident review requires evidence of when injection attempts began and who was targeted.
- You are building a threat detection layer on top of an existing prompt/response audit log.

**Do not use** this skill as a substitute for input-side prompt injection prevention (see `defending-against-prompt-injection`); this skill detects and logs attempts, it does not block them.

## Inputs

- LLM interaction audit log (JSONL or structured log from the logging skill).
- Access to raw prompts for pattern analysis (from the encrypted raw log store).
- SIEM or alerting platform (Splunk, Elastic, Sentinel, or Sigma rule engine).

## Procedure

### Step 1: Define injection and jailbreak detection signatures

```python
import re
from dataclasses import dataclass

@dataclass
class InjectionSignature:
    name: str
    pattern: re.Pattern
    severity: str  # high | medium | low

SIGNATURES = [
    InjectionSignature("ignore_instructions",
        re.compile(r"ignore (all )?(previous|prior|above) instructions?", re.IGNORECASE), "high"),
    InjectionSignature("role_override",
        re.compile(r"you are now (a|an) [A-Za-z ]{3,30}", re.IGNORECASE), "high"),
    InjectionSignature("jailbreak_dan",
        re.compile(r"\bDAN\b|do anything now", re.IGNORECASE), "high"),
    InjectionSignature("system_override_token",
        re.compile(r"<\|system\|>|<\|im_start\|>system|###\s*SYSTEM", re.IGNORECASE), "critical"),
    InjectionSignature("exfiltration_attempt",
        re.compile(r"(send|email|post|exfil).{0,30}(password|secret|api.?key)", re.IGNORECASE), "critical"),
    InjectionSignature("indirect_injection_markup",
        re.compile(r"<document>.*ignore.*instructions.*</document>", re.IGNORECASE | re.DOTALL), "high"),
]

def scan_prompt(prompt: str) -> list[dict]:
    findings = []
    for sig in SIGNATURES:
        if sig.pattern.search(prompt):
            findings.append({"signature": sig.name, "severity": sig.severity})
    return findings
```

### Step 2: Build a real-time log scanner

```python
import json, logging, datetime

detection_log = logging.getLogger("security.injection_detection")

def process_audit_log_stream(log_stream):
    """Process a stream of LLM audit log lines and emit alerts."""
    for line in log_stream:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        
        # Retrieve raw prompt from encrypted store by session_id
        raw_prompt = get_raw_prompt(entry["session_id"])
        findings = scan_prompt(raw_prompt)
        
        for finding in findings:
            alert = {
                "ts": datetime.datetime.utcnow().isoformat(),
                "alert_type": "prompt_injection_attempt",
                "severity": finding["severity"],
                "signature": finding["signature"],
                "session_id": entry["session_id"],
                "user_id_hash": entry["user_id"],
                "model": entry.get("model"),
            }
            detection_log.warning(json.dumps(alert))
```

### Step 3: Write Sigma detection rules for SIEM

```yaml
# sigma/prompt-injection-detection.yml
title: LLM Prompt Injection Attempt
id: 7a3f1b2c-9d8e-4f0a-b5c6-1e2d3a4b5c6d
status: stable
description: Detects prompt injection or jailbreak patterns in LLM audit logs
logsource:
    product: llm-application
    service: audit
detection:
    selection_ignore:
        signature: "ignore_instructions"
    selection_override:
        signature: "role_override"
    selection_critical:
        severity: "critical"
    condition: selection_ignore or selection_override or selection_critical
falsepositives:
    - Legitimate security testing or red-team exercises (tag as known)
level: high
tags:
    - attack.initial_access
    - attack.t1190
```

### Step 4: Set alert thresholds and escalation

```python
from collections import defaultdict
import datetime

# Alert on sustained injection campaign: >5 attempts from same session in 10 minutes
def detect_campaign(alert_buffer: list[dict], window_minutes: int = 10, threshold: int = 5) -> list[dict]:
    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(minutes=window_minutes)).isoformat()
    recent = [a for a in alert_buffer if a["ts"] >= cutoff]
    session_counts = defaultdict(int)
    for a in recent:
        session_counts[a["session_id"]] += 1
    return [
        {"session_id": sid, "count": count, "alert": "injection_campaign"}
        for sid, count in session_counts.items()
        if count >= threshold
    ]
```

### Step 5: Export to Splunk / Elastic

```bash
# Splunk: forward detection log via syslog or HEC
curl -k https://splunk-hec:8088/services/collector/event \
  -H "Authorization: Splunk $HEC_TOKEN" \
  -d '{"event": {"alert_type":"prompt_injection_attempt","severity":"high","signature":"ignore_instructions","session_id":"abc123"}}'
```

## Outputs

- Injection signature library with regex patterns and severity ratings.
- Real-time log scanner function processing the audit log stream.
- Sigma detection rules for SIEM deployment.
- Campaign detection function identifying sustained injection attempts per session.

## Quality Checks

- [ ] All OWASP LLM Top-10 injection patterns are covered by at least one signature.
- [ ] Sigma rule passes `sigma check` validation without errors.
- [ ] Scanner detects known injection strings from a test fixture with 0 false negatives.
- [ ] Campaign detector fires for 5+ attempts within 10 minutes in a simulation test.
- [ ] Detection alerts reach the SIEM within 60 seconds of the log entry being written.

**AI-CAIQ evidence:** This skill supports YES response to LOG-08 by producing an injection signature library, Sigma detection rules, and a real-time log scanner that creates alerting evidence demonstrating continuous monitoring of LLM interactions for prompt injection and jailbreak attempts.
