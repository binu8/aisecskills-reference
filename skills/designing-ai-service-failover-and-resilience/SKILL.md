---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: designing-ai-service-failover-and-resilience
name: designing-ai-service-failover-and-resilience
version: "1.0"
domain: BCR
aicm_controls:
  - BCR-03
  - BCR-08
ssrm_ownership: Shared OSP-AP
aismm_category: Infrastructure Security & Resilience
aismm_target_level: 3
summary: >-
  Use this skill when you need to design failover and resilience patterns
  for AI services — including LLM API fallback, model endpoint redundancy,
  and graceful degradation under provider outages.
references:
  - resilience
  - failover
  - LiteLLM
  - circuit-breaker
  - SLA
  - multi-provider
---

## When to Use

Use this skill when:
- An LLM-powered application has a single provider dependency and no fallback path.
- A business continuity review requires documented recovery time objectives (RTO) for AI services.
- An AI API provider experienced an outage that impacted production, and you need to prevent recurrence.
- You are designing a new AI application with availability requirements above 99.5%.

**Do not use** this skill for designing data backup strategies — it focuses on service availability and failover, not data recovery.

## Inputs

- Current AI service architecture (provider(s), models, endpoints).
- RTO/RPO requirements for the AI application.
- Budget and provider options for redundancy.

## Procedure

### Step 1: Define availability requirements and failover tiers

```yaml
# ai-resilience-policy.yaml
services:
  - name: customer-support-chatbot
    rto_minutes: 5
    rpo_minutes: 0          # stateless inference — no data to recover
    criticality: high
    primary_provider: anthropic
    primary_model: claude-3-5-sonnet-20241022
    fallback_tiers:
      - provider: openai
        model: gpt-4o
        trigger: primary_unavailable
      - provider: internal-llama3
        model: llama3.1-70b
        trigger: all_cloud_unavailable
    degraded_mode: "Static FAQ responses from cache"
```

### Step 2: Implement multi-provider failover with LiteLLM

```bash
pip install litellm
```

```python
import litellm
from litellm import completion

# LiteLLM handles provider routing transparently
litellm.set_verbose = False

def resilient_completion(prompt: str, fallback_models: list[str]) -> str:
    """Try models in order; raise only if all fail."""
    for model in fallback_models:
        try:
            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                timeout=10,
                num_retries=2,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Model {model} failed: {e} — trying next")
    raise RuntimeError("All model providers failed")

# Usage
MODELS = ["claude-3-5-sonnet-20241022", "gpt-4o", "ollama/llama3.1:70b"]
response = resilient_completion("Summarize this ticket.", MODELS)
```

### Step 3: Implement a circuit breaker

```python
import time
from collections import deque

class ProviderCircuitBreaker:
    def __init__(self, provider: str, failure_threshold: int = 5, cooldown_seconds: int = 60):
        self.provider = provider
        self.failures = deque(maxlen=failure_threshold)
        self.threshold = failure_threshold
        self.cooldown = cooldown_seconds
        self.opened_at: float = 0.0
        self.state = "closed"  # closed | open | half-open

    def call(self, fn, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.opened_at > self.cooldown:
                self.state = "half-open"
            else:
                raise RuntimeError(f"Circuit OPEN for {self.provider}")
        try:
            result = fn(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failures.clear()
            return result
        except Exception as e:
            self.failures.append(time.time())
            if len(self.failures) >= self.threshold:
                self.state = "open"
                self.opened_at = time.time()
            raise
```

### Step 4: Configure a response cache for degraded mode

```python
import hashlib, json
from functools import lru_cache

class AIResponseCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl_seconds = 3600

    def get(self, prompt: str) -> str | None:
        key = hashlib.sha256(prompt.encode()).hexdigest()
        cached = self.redis.get(f"ai_cache:{key}")
        return cached.decode() if cached else None

    def set(self, prompt: str, response: str):
        key = hashlib.sha256(prompt.encode()).hexdigest()
        self.redis.setex(f"ai_cache:{key}", self.ttl_seconds, response)

def call_with_cache(prompt: str, cache: AIResponseCache, provider_fn) -> str:
    cached = cache.get(prompt)
    if cached:
        return cached
    response = provider_fn(prompt)
    cache.set(prompt, response)
    return response
```

### Step 5: Test failover in staging

```python
def test_failover():
    """Simulate primary provider failure and verify fallback activates."""
    import unittest.mock as mock

    with mock.patch("litellm.completion") as mock_completion:
        # First call (primary) raises; second call (fallback) succeeds
        mock_completion.side_effect = [
            Exception("Provider unavailable"),
            mock.MagicMock(choices=[mock.MagicMock(message=mock.MagicMock(content="Fallback response"))])
        ]
        result = resilient_completion("test", ["claude-3-5-sonnet-20241022", "gpt-4o"])
        assert result == "Fallback response", "Failover did not activate"
    print("Failover test: PASS")
```

## Outputs

- `ai-resilience-policy.yaml` with RTO/RPO requirements and fallback tiers per service.
- Multi-provider failover implementation using LiteLLM.
- Circuit breaker class with configurable failure threshold and cooldown.
- Response cache for degraded-mode operation.
- Failover test suite verifying fallback activation.

## Quality Checks

- [ ] Every production AI service has at least one documented fallback tier.
- [ ] Circuit breaker opens after the configured failure threshold in a test.
- [ ] Fallback test passes within 60 seconds (simulating provider outage).
- [ ] Degraded-mode cache serves valid responses when all providers fail.
- [ ] RTO is measured in a failover drill and confirmed to meet the policy target.

**AI-CAIQ evidence:** This skill supports YES response to BCR-03 by producing a resilience policy with documented failover tiers, a circuit breaker implementation, and a tested degraded-mode cache demonstrating that AI services have defined continuity controls meeting stated RTO/RPO objectives.
