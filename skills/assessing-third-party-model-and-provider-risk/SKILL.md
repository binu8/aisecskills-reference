---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: assessing-third-party-model-and-provider-risk
name: assessing-third-party-model-and-provider-risk
version: "1.0"
domain: STA
aicm_controls:
  - STA-03
  - GRC-08
ssrm_ownership: AIC-Owned
aismm_category: Risk & Provider Assessment & Management
aismm_target_level: 3
summary: >-
  Use this skill when you need to evaluate the security, privacy, and
  compliance risks of adopting a third-party AI model provider, API
  service, or pre-trained model before onboarding.
references:
  - vendor-risk
  - third-party-risk
  - AI-CAIQ
  - due-diligence
  - provider-assessment
  - SOC2
---

## When to Use

Use this skill when:
- Your organization is evaluating a new AI API provider (e.g., Anthropic, OpenAI, Cohere, Mistral) or an on-premises model vendor.
- A procurement process requires a security and privacy risk assessment before contract signing.
- An existing provider relationship is up for annual review.
- A new use case would send sensitive data to a provider not previously assessed.

**Do not use** this skill for open-weight models you host yourself — see `verifying-open-model-supply-chain-integrity` for self-hosted model supply chain assessment.

## Inputs

- Provider name and service description.
- Data types your application will send to the provider (PII, proprietary, regulated data).
- Provider's available documentation (security page, SOC 2 report, data processing agreement, AI-CAIQ response).

## Procedure

### Step 1: Define assessment criteria

```yaml
# provider-assessment-criteria.yaml
criteria:
  data_security:
    - Encryption in transit (TLS 1.2+)
    - Encryption at rest (AES-256)
    - Data retention and deletion policy
    - No training on customer prompts by default
    - GDPR/CCPA DPA available
  
  security_posture:
    - SOC 2 Type II report (less than 12 months old)
    - Penetration test summary available
    - Vulnerability disclosure program
    - Incident notification SLA (target: <72 hours)
  
  ai_specific:
    - Model card or system card published
    - Safety evaluation methodology documented
    - AI-CAIQ completed or AICM self-attestation available
    - Content filtering and output safety controls described
  
  operational:
    - SLA for availability (target: 99.9%)
    - Data residency options (EU, US, etc.)
    - Sub-processor list published
    - Business continuity plan
```

### Step 2: Collect evidence via questionnaire

```python
ASSESSMENT_QUESTIONNAIRE = [
    # Data Security
    ("DS-01", "Do you encrypt all customer data in transit using TLS 1.2 or higher?"),
    ("DS-02", "Do you encrypt customer data at rest using AES-256 or equivalent?"),
    ("DS-03", "Is customer prompt/completion data used to train or fine-tune your models by default?"),
    ("DS-04", "What is your data retention policy for API inputs and outputs?"),
    ("DS-05", "Do you offer a GDPR-compliant Data Processing Agreement?"),
    # Security
    ("SEC-01", "Do you have a SOC 2 Type II report available under NDA?"),
    ("SEC-02", "Do you conduct annual penetration testing by a third party?"),
    ("SEC-03", "What is your SLA for notifying customers of security incidents?"),
    # AI-specific
    ("AI-01", "Have you published a model card or system card for the models in this service?"),
    ("AI-02", "Do you have an AI-CAIQ response or equivalent self-attestation?"),
    ("AI-03", "What content filtering and safety controls does the service include?"),
]

def score_responses(responses: dict) -> dict:
    """Score boolean responses; partial credit for 'partial'."""
    scores = {}
    for q_id, _ in ASSESSMENT_QUESTIONNAIRE:
        ans = responses.get(q_id, "no").lower()
        scores[q_id] = 1.0 if ans == "yes" else 0.5 if ans == "partial" else 0.0
    total = sum(scores.values()) / len(scores)
    return {"scores": scores, "overall": total, "rating": "low" if total >= 0.8 else "medium" if total >= 0.5 else "high"}
```

### Step 3: Review the AI-CAIQ or security documentation

```python
def review_soc2_report(report_summary: dict) -> list[str]:
    """Check for material exceptions in a SOC 2 Type II summary."""
    issues = []
    if report_summary.get("opinion") != "unqualified":
        issues.append(f"SOC 2 opinion is not unqualified: {report_summary.get('opinion')}")
    report_age_days = report_summary.get("age_days", 999)
    if report_age_days > 365:
        issues.append(f"SOC 2 report is {report_age_days} days old — request updated report")
    exceptions = report_summary.get("exceptions", [])
    if exceptions:
        issues.extend([f"SOC 2 exception: {e}" for e in exceptions])
    return issues
```

### Step 4: Compute residual risk score

```python
DATA_SENSITIVITY_MULTIPLIER = {
    "public": 1.0, "internal": 1.5, "confidential": 2.0, "regulated": 3.0, "pii": 2.5
}

def compute_residual_risk(assessment_score: float, data_sensitivity: str) -> dict:
    base_risk = 1.0 - assessment_score  # 0 = no risk gap, 1 = all gaps
    multiplier = DATA_SENSITIVITY_MULTIPLIER.get(data_sensitivity, 1.0)
    residual = min(base_risk * multiplier, 1.0)
    return {
        "residual_risk_score": residual,
        "risk_rating": "critical" if residual >= 0.7 else "high" if residual >= 0.4 else "medium" if residual >= 0.2 else "low",
        "recommendation": "reject" if residual >= 0.7 else "conditional" if residual >= 0.4 else "approve",
    }
```

### Step 5: Generate the provider risk assessment report

```python
import json, datetime

def generate_report(provider: str, assessment: dict, residual: dict) -> dict:
    return {
        "provider": provider,
        "assessment_date": datetime.date.today().isoformat(),
        "overall_score": assessment["overall"],
        "score_rating": assessment["rating"],
        "residual_risk": residual,
        "recommendation": residual["recommendation"],
        "next_review": str(datetime.date.today().replace(year=datetime.date.today().year + 1)),
    }
```

## Outputs

- Assessment questionnaire responses with scoring.
- SOC 2 review summary with exception flags.
- Residual risk score and approve/conditional/reject recommendation.
- Provider risk assessment report for the vendor register.

## Quality Checks

- [ ] All criteria categories (data security, security posture, AI-specific, operational) are scored.
- [ ] SOC 2 Type II report age is verified to be within 12 months.
- [ ] AI-CAIQ or equivalent AI-specific self-attestation is reviewed.
- [ ] Residual risk accounts for the sensitivity of data being sent to the provider.
- [ ] Assessment report is stored in the vendor register with a scheduled review date.

**AI-CAIQ evidence:** This skill supports YES response to STA-03 by producing a structured provider risk assessment report with scored criteria, residual risk rating, and an approve/reject recommendation demonstrating due-diligence evaluation of third-party AI providers.
