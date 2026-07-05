---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: applying-zero-trust-to-ai-workloads
name: applying-zero-trust-to-ai-workloads
version: "1.0"
domain: I&S
aicm_controls:
  - I&S-04
  - IAM-03
ssrm_ownership: Shared Across Supply Chain
aismm_category: Infrastructure Security & Resilience
aismm_target_level: 4
pillar: security_for_ai
summary: >-
  Use this skill when you need to apply zero-trust principles to AI workload
  networking — ensuring no implicit trust between AI services, agents, and
  data stores, with continuous verification at every layer.
references:
  - zero-trust
  - mTLS
  - SPIFFE
  - service-mesh
  - Istio
  - network-policy
---

## When to Use

Use this skill when:
- An AI system spans multiple microservices (embedding service, retrieval service, LLM gateway, agent orchestrator) and uses implicit network trust.
- A security review found that AI services communicate over unencrypted internal networks.
- You are implementing a new AI platform and want zero-trust networking from the start.
- A compliance framework (NIST 800-207, DoD ZTA) requires zero-trust architecture evidence for AI systems.

**Do not use** this skill for perimeter network design — it focuses on the service-to-service trust model within an AI workload, not external firewall rules.

## Inputs

- Current AI service architecture and service communication map.
- Service mesh availability (Istio, Linkerd, Consul Connect) or willingness to deploy one.
- Identity platform (SPIFFE/SPIRE or cloud-native workload identity).

## Procedure

### Step 1: Map all AI service communications

```yaml
# ai-service-communication-map.yaml
services:
  - from: agent-orchestrator
    to: llm-gateway
    protocol: HTTPS
    port: 443
    auth: bearer-token
    current_trust: implicit (same VPC)

  - from: llm-gateway
    to: embedding-service
    protocol: HTTP
    port: 8080
    auth: none
    current_trust: implicit (same namespace)

  - from: retrieval-service
    to: vector-db
    protocol: TCP
    port: 6333
    auth: api-key
    current_trust: network-level only
```

Flag every connection where `auth: none` or `current_trust: implicit`.

### Step 2: Issue workload identities with SPIFFE/SPIRE

```bash
# Register each AI service as a SPIFFE workload
spire-server entry create \
  -spiffeID spiffe://myorg.com/ai/llm-gateway \
  -parentID spiffe://myorg.com/spire/agent/k8s \
  -selector k8s:ns:ai-workloads \
  -selector k8s:sa:llm-gateway

spire-server entry create \
  -spiffeID spiffe://myorg.com/ai/agent-orchestrator \
  -parentID spiffe://myorg.com/spire/agent/k8s \
  -selector k8s:ns:ai-workloads \
  -selector k8s:sa:agent-orchestrator
```

### Step 3: Enforce mTLS between all AI services with Istio

```yaml
# Enable strict mTLS for the ai-workloads namespace
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: ai-workloads-strict-mtls
  namespace: ai-workloads
spec:
  mtls:
    mode: STRICT  # all traffic must use mTLS — no plaintext
---
# AuthorizationPolicy: only allow llm-gateway to call embedding-service
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: embedding-service-authz
  namespace: ai-workloads
spec:
  selector:
    matchLabels:
      app: embedding-service
  rules:
    - from:
        - source:
            principals:
              - "cluster.local/ns/ai-workloads/sa/llm-gateway"
      to:
        - operation:
            methods: ["POST"]
            paths: ["/embed"]
```

### Step 4: Apply continuous verification with token binding

```python
# At every AI service boundary — validate the caller's JWT, not just the network source
from jose import jwt
import httpx

def verify_service_token(token: str, expected_spiffe_id: str, jwks_uri: str) -> dict:
    jwks = httpx.get(jwks_uri).json()
    claims = jwt.decode(token, jwks, algorithms=["RS256"])
    if claims.get("sub") != expected_spiffe_id:
        raise PermissionError(
            f"Token subject {claims.get('sub')} != expected {expected_spiffe_id}"
        )
    return claims

# FastAPI middleware example
from fastapi import Request, HTTPException

async def zero_trust_middleware(request: Request, call_next):
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    if not token:
        raise HTTPException(status_code=401, detail="Missing service token")
    try:
        verify_service_token(token, EXPECTED_CALLER_SPIFFE_ID, JWKS_URI)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return await call_next(request)
```

### Step 5: Verify zero-trust posture with network probe tests

```bash
# Test: agent-orchestrator should NOT be able to call vector-db directly
kubectl run zt-probe --image=curlimages/curl -n ai-workloads --rm -it \
  --serviceaccount=agent-orchestrator --restart=Never \
  -- curl -m 5 http://vector-db.ai-workloads.svc.cluster.local:6333/collections
# Expected: 403 Forbidden (AuthorizationPolicy blocks direct access)
```

## Outputs

- Service communication map annotated with trust gaps.
- SPIFFE SVID configuration for all AI services.
- Istio PeerAuthentication (strict mTLS) and AuthorizationPolicy YAMLs.
- Zero-trust middleware function validating caller identity at every service boundary.
- Network probe test results confirming unauthorized service paths are blocked.

## Quality Checks

- [ ] All inter-service communication uses mTLS — no plaintext HTTP between AI services.
- [ ] Every service has a SPIFFE workload identity.
- [ ] AuthorizationPolicies exist for all service pairs — no "allow all" policies.
- [ ] Zero-trust middleware tests confirm unauthorized callers receive 403.
- [ ] Service communication map is updated after every architectural change.

**AI-CAIQ evidence:** This skill supports YES response to I&S-04 by producing SPIFFE workload identity configurations, Istio strict mTLS policies, per-service authorization policies, and probe test results demonstrating that AI workload communications operate on a zero-trust model with no implicit network trust.
