---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: implementing-prompt-and-response-logging
name: implementing-prompt-and-response-logging
version: "1.0"
domain: LOG
aicm_controls:
  - LOG-03
  - LOG-05
ssrm_ownership: AP-Owned
aismm_category: Security Monitoring
aismm_target_level: 3
summary: >-
  Use this skill when you need to implement structured, tamper-resistant
  logging of LLM prompts and responses to support security monitoring,
  incident investigation, and compliance audits.
references:
  - audit-logging
  - OpenTelemetry
  - SIEM
  - structured-logging
  - LLM-observability
  - privacy
---

## When to Use

Use this skill when:
- A new LLM application requires an audit trail for regulatory or internal compliance purposes.
- An incident investigation requires reconstructing what prompts were sent and what responses were returned.
- You need to feed LLM interaction data into a SIEM or observability platform.
- A privacy review requires confirmation that PII is not persisted in plain text in logs.

**Do not use** this skill as a substitute for application-level access controls — logging records what happened, it does not prevent unauthorized access.

## Inputs

- LLM application code with current call sites.
- Compliance requirements specifying retention period, PII handling, and access controls on logs.
- Target log destination (SIEM, S3, Splunk, Elastic, OpenTelemetry collector).

## Procedure

### Step 1: Define the log schema

```python
from dataclasses import dataclass, asdict
import datetime, hashlib, json

@dataclass
class LLMInteractionLog:
    ts: str                    # ISO-8601 UTC
    session_id: str
    user_id: str               # anonymized if needed
    model: str
    prompt_hash: str           # SHA-256 of full prompt — NOT the raw prompt
    response_hash: str         # SHA-256 of full response
    prompt_token_count: int
    response_token_count: int
    latency_ms: float
    finish_reason: str         # stop / length / content_filter
    policy_flags: list[str]    # guardrail findings, if any
    # Raw prompt/response stored separately in encrypted log store
```

### Step 2: Instrument the LLM call wrapper

```python
import time

def logged_llm_call(prompt: str, user_id: str, session_id: str,
                    model: str, raw_log_store) -> str:
    start = time.time()
    response = call_llm(model=model, prompt=prompt)
    latency_ms = (time.time() - start) * 1000

    log_entry = LLMInteractionLog(
        ts=datetime.datetime.utcnow().isoformat(),
        session_id=session_id,
        user_id=hashlib.sha256(user_id.encode()).hexdigest()[:16],  # pseudonymize
        model=model,
        prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
        response_hash=hashlib.sha256(response.encode()).hexdigest(),
        prompt_token_count=count_tokens(prompt),
        response_token_count=count_tokens(response),
        latency_ms=latency_ms,
        finish_reason=response.finish_reason,
        policy_flags=[],
    )

    # Write structured log to SIEM-friendly sink
    import logging
    llm_audit = logging.getLogger("llm.audit")
    llm_audit.info(json.dumps(asdict(log_entry)))

    # Write full content to encrypted store (separate from audit log)
    raw_log_store.write(session_id, prompt, response)

    return response.content
```

### Step 3: Configure structured logging with OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

tracer_provider = TracerProvider()
tracer_provider.add_span_exporter(OTLPSpanExporter(endpoint="http://otel-collector:4317"))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer("llm.application")

def traced_llm_call(prompt: str, user_id: str, model: str) -> str:
    with tracer.start_as_current_span("llm.call") as span:
        span.set_attribute("llm.model", model)
        span.set_attribute("llm.prompt_hash", hashlib.sha256(prompt.encode()).hexdigest())
        span.set_attribute("user.id_hash", hashlib.sha256(user_id.encode()).hexdigest()[:16])
        response = call_llm(model=model, prompt=prompt)
        span.set_attribute("llm.finish_reason", response.finish_reason)
        return response.content
```

### Step 4: Secure the raw prompt/response store

```python
# Encrypt raw content before writing to S3
import boto3
from cryptography.fernet import Fernet

class EncryptedRawLogStore:
    def __init__(self, bucket: str, kms_key_id: str):
        self.s3 = boto3.client("s3")
        self.kms = boto3.client("kms")
        self.bucket = bucket
        self.kms_key_id = kms_key_id

    def write(self, session_id: str, prompt: str, response: str):
        payload = json.dumps({"prompt": prompt, "response": response}).encode()
        encrypted = self.kms.encrypt(KeyId=self.kms_key_id, Plaintext=payload)["CiphertextBlob"]
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"raw-logs/{session_id}/{datetime.datetime.utcnow().isoformat()}.enc",
            Body=encrypted,
            ServerSideEncryption="aws:kms",
        )
```

### Step 5: Set log retention and access policies

```bash
# S3 bucket lifecycle: retain 90 days, then transition to Glacier
aws s3api put-bucket-lifecycle-configuration \
  --bucket llm-raw-logs \
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "llm-log-retention",
      "Status": "Enabled",
      "Expiration": {"Days": 365},
      "Transitions": [{"Days": 90, "StorageClass": "GLACIER"}]
    }]
  }'

# Restrict raw log access to security team only
aws s3api put-bucket-policy --bucket llm-raw-logs --policy '{
  "Statement": [{"Effect":"Deny","Principal":"*","Action":"s3:GetObject",
    "Resource":"arn:aws:s3:::llm-raw-logs/*",
    "Condition":{"StringNotLike":{"aws:PrincipalArn":"arn:aws:iam::*:role/security-*"}}}]
}'
```

## Outputs

- Structured audit log schema (`LLMInteractionLog`) with hashes instead of raw content in the main log.
- Instrumented LLM call wrapper with OpenTelemetry span attributes.
- Encrypted raw prompt/response store with KMS-backed encryption.
- S3 retention and access policy configuration for log data.

## Quality Checks

- [ ] Raw prompts and responses are not written to the main SIEM log — only hashes appear.
- [ ] Raw content store is encrypted at rest with customer-managed KMS keys.
- [ ] Retention policy matches the compliance requirement (e.g., 90 or 365 days).
- [ ] Access to raw logs is restricted to an explicit allowlist of roles.
- [ ] A test query against the audit log returns session, model, latency, and finish reason for a known call.

**AI-CAIQ evidence:** This skill supports YES response to LOG-03 by producing a structured audit logging implementation with prompt/response hashes, encrypted raw content storage, and retention policies demonstrating that LLM interactions are captured in a tamper-resistant, compliance-ready log.
