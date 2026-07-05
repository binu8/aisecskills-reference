---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: classifying-ai-systems-under-eu-ai-act
name: classifying-ai-systems-under-eu-ai-act
version: "1.0"
domain: GRC
aicm_controls:
  - GRC-05
  - A&A-04
ssrm_ownership: AIC-Owned
aismm_category: Privacy, Compliance and Audit
aismm_target_level: 3
pillar: security_from_ai
summary: >-
  Use this skill when you need to classify an AI system under the EU AI
  Act risk tiers — unacceptable, high-risk, limited, or minimal — and
  determine the resulting compliance obligations.
references:
  - EU-AI-Act
  - risk-classification
  - compliance
  - GPAI
  - high-risk-AI
  - regulatory
---

## When to Use

Use this skill when:
- Your organization is deploying an AI system in the EU and must determine its regulatory obligations.
- A compliance team needs a documented classification rationale for an EU AI Act audit.
- A new AI use case is proposed and must be screened before development begins.
- An existing system needs re-classification after a material change in its use case or capabilities.

**Do not use** this skill for GDPR data-protection impact assessments — EU AI Act classification is distinct from DPIA requirements (though both may be needed).

## Inputs

- AI system description: intended purpose, deployment context, user types, outputs/decisions made.
- Sector and domain of deployment (healthcare, employment, education, law enforcement, etc.).
- Whether the system is a general-purpose AI model (GPAI) or a purpose-specific application.

## Procedure

### Step 1: Screen for prohibited practices (Article 5)

```python
PROHIBITED_PRACTICES = [
    "subliminal manipulation causing harm",
    "exploitation of vulnerable groups",
    "social scoring by public authorities",
    "real-time remote biometric identification in public spaces (law enforcement)",
    "emotion recognition in workplace or education",
    "biometric categorization inferring race/political opinions/religion",
]

def screen_prohibited(system_description: str, use_case: str) -> dict:
    """
    Manual screening — return a checklist for legal review.
    This is not an automated decision; it flags items for human review.
    """
    flags = []
    if "biometric" in use_case.lower() and "public" in use_case.lower():
        flags.append("Potential real-time remote biometric ID — legal review required")
    if "emotion" in use_case.lower() and any(ctx in use_case.lower() for ctx in ["workplace", "school", "education"]):
        flags.append("Emotion recognition in restricted context — may be prohibited")
    return {"prohibited_flags": flags, "requires_legal_review": len(flags) > 0}
```

### Step 2: Check Annex III high-risk categories

```yaml
# annex-iii-high-risk-categories.yaml
high_risk_domains:
  - id: HR1
    name: Critical infrastructure (energy, water, transport)
    keywords: [power grid, water treatment, railway, aviation]
  - id: HR2
    name: Education and vocational training
    keywords: [exam scoring, admissions, student assessment]
  - id: HR3
    name: Employment and worker management
    keywords: [recruitment screening, performance evaluation, promotion]
  - id: HR4
    name: Essential private and public services
    keywords: [credit scoring, insurance risk, welfare benefits, emergency dispatch]
  - id: HR5
    name: Law enforcement
    keywords: [policing, crime prediction, evidence evaluation]
  - id: HR6
    name: Migration and border management
    keywords: [visa screening, asylum, border control]
  - id: HR7
    name: Administration of justice
    keywords: [court decisions, sentencing, legal research for courts]
  - id: HR8
    name: Democratic processes
    keywords: [election, voting, political campaign targeting]
```

```python
import yaml

def classify_high_risk(use_case: str, deployment_context: str) -> dict:
    with open("annex-iii-high-risk-categories.yaml") as f:
        categories = yaml.safe_load(f)["high_risk_domains"]
    
    matched = []
    text = (use_case + " " + deployment_context).lower()
    for cat in categories:
        if any(kw in text for kw in cat["keywords"]):
            matched.append({"id": cat["id"], "name": cat["name"]})
    
    return {
        "is_high_risk": len(matched) > 0,
        "matched_categories": matched,
    }
```

### Step 3: Check for GPAI model obligations

```python
def classify_gpai(is_foundation_model: bool, systemic_risk_threshold_flops: float = 1e25) -> dict:
    """
    GPAI models above 10^25 FLOPs training compute are presumed to have systemic risk.
    """
    obligations = []
    if is_foundation_model:
        obligations.extend([
            "Technical documentation (Article 53)",
            "Copyright compliance summary",
            "Training data transparency",
        ])
    # Systemic risk tier adds adversarial testing, incident reporting, model evaluation
    return {"is_gpai": is_foundation_model, "obligations": obligations}
```

### Step 4: Determine classification and obligations

```python
def classify_system(system: dict) -> dict:
    prohibited = screen_prohibited(system["description"], system["use_case"])
    if prohibited["prohibited_flags"]:
        return {"tier": "PROHIBITED", **prohibited}
    
    high_risk = classify_high_risk(system["use_case"], system["deployment_context"])
    if high_risk["is_high_risk"]:
        obligations = [
            "Conformity assessment (Article 43)",
            "CE marking",
            "EU Declaration of Conformity",
            "Registration in EU database",
            "Risk management system (Article 9)",
            "Data governance (Article 10)",
            "Technical documentation (Article 11)",
            "Transparency to users (Article 13)",
            "Human oversight measures (Article 14)",
            "Accuracy, robustness, cybersecurity (Article 15)",
        ]
        return {"tier": "HIGH_RISK", "matched_categories": high_risk["matched_categories"], "obligations": obligations}
    
    if system.get("interacts_with_humans"):
        return {"tier": "LIMITED_RISK", "obligations": ["Transparency disclosure to users (Article 50)"]}
    
    return {"tier": "MINIMAL_RISK", "obligations": []}
```

### Step 5: Generate classification record

```python
import json, datetime

def generate_classification_record(system: dict, classification: dict) -> dict:
    return {
        "system_name": system["name"],
        "classification_date": datetime.date.today().isoformat(),
        "tier": classification["tier"],
        "obligations": classification.get("obligations", []),
        "rationale": classification,
        "next_review": str((datetime.date.today().replace(year=datetime.date.today().year + 1))),
    }
```

## Outputs

- EU AI Act tier classification (Prohibited / High-Risk / Limited / Minimal) with rationale.
- Applicable compliance obligations list per tier.
- Classification record JSON suitable for audit evidence.
- Prohibited-practice screening checklist for legal review.

## Quality Checks

- [ ] Prohibited-practice screen is reviewed by legal counsel, not solely automated.
- [ ] All Annex III category keywords are checked against the system description.
- [ ] Classification rationale references the specific EU AI Act articles and Annex III entries.
- [ ] Classification record is stored and linked to the system's compliance documentation.
- [ ] Re-classification is triggered when the system's use case or deployment context changes materially.

**AI-CAIQ evidence:** This skill supports YES response to GRC-05 by producing a classification record with EU AI Act tier determination, applicable obligations, and a documented rationale that satisfies the transparency and conformity requirements of the Act.
