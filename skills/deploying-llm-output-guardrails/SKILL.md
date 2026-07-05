---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: deploying-llm-output-guardrails
name: deploying-llm-output-guardrails
version: "1.0"
domain: AIS
aicm_controls:
  - AIS-09
ssrm_ownership: AP-Owned
aismm_category: App Security
aismm_target_level: 4
pillar: security_for_ai
summary: >-
  Use this skill when you need to intercept, classify, and block or rewrite
  unsafe, off-topic, or policy-violating LLM outputs before they reach end
  users, using layered guardrail controls.
references:
  - NeMo-Guardrails
  - Guardrails-AI
  - output-filtering
  - content-moderation
  - Perspective-API
  - LLM-safety
---

## When to Use

Use this skill when:
- An LLM application must comply with content policies (no harmful advice, no competitor mentions, no PII disclosure).
- You need a defense layer that operates independently of the base model's built-in safety training.
- A production incident showed the model returned policy-violating content that reached users.
- Regulatory requirements mandate an auditable output-filtering control.

**Do not use** this skill as a replacement for input-side prompt injection defense; guardrails operate on the output side and should be layered with input controls.

## Inputs

- LLM application code and current system prompt.
- Content policy document or list of prohibited output categories.
- (Optional) NeMo Guardrails or Guardrails-AI configuration files.

## Procedure

### Step 1: Define output policy categories

```python
OUTPUT_POLICY = {
    "hate_speech":      {"action": "block",   "threshold": 0.80},
    "self_harm":        {"action": "block",   "threshold": 0.70},
    "pii_disclosure":   {"action": "block",   "threshold": 0.85},
    "competitor_mention": {"action": "rewrite", "threshold": 0.90},
    "off_topic":        {"action": "warn",    "threshold": 0.75},
}
```

### Step 2: Implement a multi-layer output scanner

```python
from transformers import pipeline
from presidio_analyzer import AnalyzerEngine

toxicity_clf = pipeline("text-classification", model="unitary/toxic-bert")
pii_analyzer = AnalyzerEngine()

def scan_output(text: str) -> list[dict]:
    findings = []
    
    # Layer 1: Toxicity
    tox = toxicity_clf(text[:512])[0]
    if tox["label"] == "toxic" and tox["score"] >= OUTPUT_POLICY["hate_speech"]["threshold"]:
        findings.append({"category": "hate_speech", "score": tox["score"], "action": "block"})
    
    # Layer 2: PII
    pii_hits = [h for h in pii_analyzer.analyze(text=text, language="en") if h.score >= 0.7]
    if pii_hits:
        findings.append({"category": "pii_disclosure", "score": max(h.score for h in pii_hits), "action": "block"})
    
    return findings
```

### Step 3: Deploy NeMo Guardrails for dialog-level control

```bash
pip install nemoguardrails
```

```yaml
# config/config.yml
models:
  - type: main
    engine: openai
    model: gpt-4o

rails:
  output:
    flows:
      - self check output
```

```colang
# config/rails.co
define bot refuse harmful output
  "I'm sorry, I can't provide that information."

define flow self check output
  $allowed = execute output_check(response=$bot_message)
  if not $allowed
    bot refuse harmful output
    stop
```

### Step 4: Use Guardrails-AI for structured output validation

```python
from guardrails import Guard
from guardrails.hub import ToxicLanguage, DetectPII

guard = Guard().use_many(
    ToxicLanguage(threshold=0.5, validation_method="sentence", on_fail="exception"),
    DetectPII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN"], on_fail="fix"),
)

raw_llm_output = call_llm(prompt)
validated_output, *_ = guard.parse(raw_llm_output)
```

### Step 5: Wrap the LLM call with guardrail enforcement

```python
import logging

guardrail_log = logging.getLogger("guardrail.audit")

def safe_llm_call(prompt: str, user_id: str) -> str:
    raw = call_llm(prompt)
    findings = scan_output(raw)
    
    blocked = [f for f in findings if f["action"] == "block"]
    if blocked:
        guardrail_log.warning("Output blocked", extra={
            "user": user_id,
            "categories": [f["category"] for f in blocked],
            "response_hash": hashlib.sha256(raw.encode()).hexdigest(),
        })
        return "I'm unable to provide that response."
    
    return raw
```

## Outputs

- Output scanner module with toxicity, PII, and policy-category checks.
- NeMo Guardrails or Guardrails-AI configuration files.
- Guardrail audit log with blocked response hashes and categories.
- Test suite verifying each policy category is correctly blocked or rewritten.

## Quality Checks

- [ ] Every LLM response passes through the guardrail before returning to the user.
- [ ] Each policy category has a corresponding unit test with a known violating example.
- [ ] Blocked responses are logged with category and response hash (no raw content).
- [ ] Guardrail latency overhead is measured and within acceptable SLA (e.g., <200ms p99).
- [ ] Rewrite actions produce policy-compliant output verified by re-scan.

**AI-CAIQ evidence:** This skill supports YES response to AIS-09 by producing a guardrail enforcement layer with audit logs demonstrating that policy-violating outputs are detected, blocked or rewritten, and logged before reaching end users.
