---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: implementing-on-behalf-of-delegation-and-consent
name: implementing-on-behalf-of-delegation-and-consent
version: "1.0"
domain: IAM
aicm_controls:
  - IAM-05
  - IAM-13
ssrm_ownership: Shared AP-AIC
aismm_category: IAM
aismm_target_level: 4
summary: >-
  Use this skill when an AI agent must act on behalf of a human user,
  requiring explicit OAuth delegation flows, consent capture, and
  auditable on-behalf-of token chains to prevent privilege escalation.
references:
  - OAuth2
  - OBO-token
  - delegation
  - consent
  - Microsoft-Identity
  - agent-authorization
---

## When to Use

Use this skill when:
- An AI assistant needs to call APIs (calendar, email, CRM) using the authenticated user's permissions.
- An agentic workflow delegates from one AI agent to another and you need to preserve the originating user context.
- A compliance review requires evidence that agents cannot exceed the permissions of the human who authorized them.
- You are implementing a new agent integration with an identity provider that supports OAuth 2.0 on-behalf-of.

**Do not use** this skill for agent-to-agent communication where no human user is involved — use service-account workload identities instead (see `provisioning-non-human-identities-for-ai-agents`).

## Inputs

- Identity provider supporting OAuth 2.0 OBO flow (Microsoft Identity Platform, Auth0, Okta).
- User identity token (access token or ID token) obtained at the start of the user session.
- Scopes the agent needs to act on behalf of the user.

## Procedure

### Step 1: Obtain user consent for required scopes upfront

```python
# Frontend: initiate authorization code flow with explicit agent scopes
from urllib.parse import urlencode

SCOPES = ["openid", "profile", "Calendars.ReadWrite", "Mail.Send"]

auth_url = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?" + urlencode({
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": " ".join(SCOPES),
    "prompt": "consent",  # force consent screen so user explicitly authorizes agent
    "state": session_state,
})
# Redirect user to auth_url
```

### Step 2: Exchange user token for on-behalf-of agent token (Microsoft OBO)

```python
import httpx

def get_obo_token(user_access_token: str, target_scope: str) -> str:
    """Exchange a user token for an OBO token the agent can use."""
    response = httpx.post(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "client_id": AGENT_CLIENT_ID,
            "client_secret": AGENT_CLIENT_SECRET,
            "assertion": user_access_token,
            "requested_token_use": "on_behalf_of",
            "scope": target_scope,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]
```

### Step 3: Propagate user context through multi-agent chains

```python
from dataclasses import dataclass

@dataclass
class DelegationContext:
    originating_user_id: str
    delegating_agent_id: str
    authorized_scopes: list[str]
    obo_token: str
    delegation_chain: list[str]  # list of agent IDs in order

def delegate_to_sub_agent(parent_ctx: DelegationContext,
                           sub_agent_id: str, required_scope: str) -> DelegationContext:
    # Sub-agent can only inherit scopes already in parent context
    if required_scope not in parent_ctx.authorized_scopes:
        raise PermissionError(
            f"Sub-agent '{sub_agent_id}' requires scope '{required_scope}' "
            f"not present in delegation context"
        )
    new_token = get_obo_token(parent_ctx.obo_token, required_scope)
    return DelegationContext(
        originating_user_id=parent_ctx.originating_user_id,
        delegating_agent_id=sub_agent_id,
        authorized_scopes=[required_scope],
        obo_token=new_token,
        delegation_chain=parent_ctx.delegation_chain + [sub_agent_id],
    )
```

### Step 4: Validate OBO token claims before use

```python
from jose import jwt
import httpx

def validate_obo_token(token: str, expected_scopes: list[str]) -> dict:
    jwks = httpx.get(f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys").json()
    claims = jwt.decode(token, jwks, algorithms=["RS256"], audience=AGENT_CLIENT_ID)
    token_scopes = claims.get("scp", "").split()
    missing = [s for s in expected_scopes if s not in token_scopes]
    if missing:
        raise PermissionError(f"OBO token missing required scopes: {missing}")
    return claims
```

### Step 5: Audit delegation events

```python
import logging, json, datetime

delegation_log = logging.getLogger("iam.delegation")

def log_delegation(ctx: DelegationContext, action: str, resource: str):
    delegation_log.info(json.dumps({
        "ts": datetime.datetime.utcnow().isoformat(),
        "originating_user": ctx.originating_user_id,
        "delegation_chain": ctx.delegation_chain,
        "action": action,
        "resource": resource,
        "scopes": ctx.authorized_scopes,
    }))
```

## Outputs

- OAuth OBO token exchange implementation with scope inheritance enforcement.
- `DelegationContext` dataclass propagating user identity through multi-agent chains.
- Delegation audit log capturing user, agent chain, action, and resource.
- Consent capture configuration ensuring users explicitly authorize agent scopes.

## Quality Checks

- [ ] OBO token exchange is used — agents never receive the user's primary access token directly.
- [ ] Sub-agents cannot inherit scopes not present in the parent delegation context.
- [ ] Delegation chain is logged end-to-end for every cross-agent action.
- [ ] Token validation confirms `scp` claim contains only authorized scopes.
- [ ] Consent prompt is shown to users explicitly listing what the agent is authorized to do.

**AI-CAIQ evidence:** This skill supports YES response to IAM-05 by producing an OBO token exchange implementation, delegation context enforcement, and audit logs demonstrating that agent actions are traceable to the originating human user's explicit consent and cannot exceed the user's authorized scopes.
