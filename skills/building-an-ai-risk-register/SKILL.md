---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: building-an-ai-risk-register
name: building-an-ai-risk-register
version: "1.0"
domain: GRC
aicm_controls:
  - GRC-02
  - GRC-03
ssrm_ownership: AIC-Owned
aismm_category: Risk & Provider Assessment & Management
aismm_target_level: 3
summary: >-
  Use this skill when you need to create or maintain a structured AI risk
  register that captures, scores, and tracks mitigations for identified
  risks across an organization's AI portfolio.
references:
  - risk-register
  - NIST-AI-RMF
  - ISO-42001
  - risk-scoring
  - governance
  - AI-risk
---

## When to Use

Use this skill when:
- Your organization is deploying AI systems and has no formal mechanism to track AI-specific risks.
- A board, regulator, or auditor requires evidence of structured AI risk management.
- A new AI initiative must go through a risk intake and scoring process before approval.
- You are refreshing an existing risk register after a significant model update or new use case.

**Do not use** this skill as a substitute for a full AI impact assessment — the risk register tracks and scores known risks, it does not replace the discovery work needed to identify them.

## Inputs

- Inventory of AI systems in scope (names, use cases, data inputs, business criticality).
- Applicable risk taxonomy (NIST AI RMF, ISO 42001, or internal framework).
- Existing risk register or risk management tooling (Jira, ServiceNow, spreadsheet).

## Procedure

### Step 1: Define the AI risk taxonomy and scoring rubric

```yaml
# ai-risk-taxonomy.yaml
risk_categories:
  - id: SAFETY
    name: Safety & Harm
    description: Risk that AI outputs cause physical, psychological, or financial harm
  - id: BIAS
    name: Bias & Fairness
    description: Risk of discriminatory outcomes across demographic groups
  - id: PRIVACY
    name: Privacy & Data
    description: Risk of PII exposure or unauthorized data use
  - id: SECURITY
    name: Security & Adversarial
    description: Risk from prompt injection, model theft, or supply chain attack
  - id: RELIABILITY
    name: Reliability & Drift
    description: Risk of model degradation, hallucination, or unexpected behavior change
  - id: LEGAL
    name: Legal & Compliance
    description: Risk of regulatory violation (GDPR, EU AI Act, CCPA)

scoring:
  likelihood: {1: rare, 2: unlikely, 3: possible, 4: likely, 5: almost_certain}
  impact:      {1: negligible, 2: minor, 3: moderate, 4: major, 5: critical}
  # Risk score = likelihood × impact; 15+ = critical, 9-14 = high, 4-8 = medium, 1-3 = low
```

### Step 2: Intake a new AI risk

```python
from dataclasses import dataclass, field
import datetime, uuid

@dataclass
class AIRisk:
    risk_id: str = field(default_factory=lambda: f"AIR-{uuid.uuid4().hex[:6].upper()}")
    system: str = ""
    category: str = ""
    title: str = ""
    description: str = ""
    likelihood: int = 1      # 1-5
    impact: int = 1          # 1-5
    score: int = field(init=False)
    rating: str = field(init=False)
    owner: str = ""
    mitigations: list[str] = field(default_factory=list)
    residual_likelihood: int = 1
    residual_impact: int = 1
    status: str = "open"     # open | mitigated | accepted | closed
    review_date: str = ""
    created: str = field(default_factory=lambda: datetime.date.today().isoformat())

    def __post_init__(self):
        self.score = self.likelihood * self.impact
        self.rating = (
            "critical" if self.score >= 15 else
            "high" if self.score >= 9 else
            "medium" if self.score >= 4 else "low"
        )
```

### Step 3: Populate the register from a discovery workshop

```python
import csv

SAMPLE_RISKS = [
    AIRisk(system="HR-Chatbot", category="BIAS",
           title="Discriminatory candidate screening",
           description="Model may rank candidates unfairly based on gender or ethnicity proxies in resumes.",
           likelihood=3, impact=4, owner="HR-AI-Owner",
           mitigations=["Demographic parity audit quarterly", "Human review for all rejections"],
           review_date="2025-12-01"),
    AIRisk(system="CS-Agent", category="SECURITY",
           title="Prompt injection via customer input",
           description="Customer messages could override system instructions via injection.",
           likelihood=4, impact=3, owner="AppSec-Team",
           mitigations=["Input validation", "Output guardrails"],
           review_date="2025-09-01"),
]

def export_register_csv(risks: list[AIRisk], output_path: str):
    import dataclasses
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "risk_id","system","category","title","score","rating",
            "owner","status","review_date"
        ])
        writer.writeheader()
        for r in risks:
            row = dataclasses.asdict(r)
            writer.writerow({k: row[k] for k in writer.fieldnames})
```

### Step 4: Produce a risk heatmap

```python
import json

def generate_heatmap_data(risks: list[AIRisk]) -> dict:
    heatmap = {f"{l}x{i}": [] for l in range(1, 6) for i in range(1, 6)}
    for r in risks:
        key = f"{r.likelihood}x{r.impact}"
        heatmap[key].append(r.risk_id)
    return {
        "heatmap": heatmap,
        "critical": [r.risk_id for r in risks if r.rating == "critical"],
        "high": [r.risk_id for r in risks if r.rating == "high"],
    }
```

### Step 5: Schedule periodic review

```python
def get_due_for_review(risks: list[AIRisk]) -> list[AIRisk]:
    today = datetime.date.today().isoformat()
    return [r for r in risks if r.review_date and r.review_date <= today and r.status != "closed"]
```

## Outputs

- `ai-risk-taxonomy.yaml` with categories and scoring rubric.
- AI risk register CSV with risk ID, system, score, owner, mitigations, and review date.
- Heatmap data JSON showing risk distribution across likelihood/impact grid.
- Review-due report listing risks past their scheduled review date.

## Quality Checks

- [ ] Every AI system in scope has at least one entry in the register.
- [ ] All Critical and High risks have an assigned owner and at least one mitigation.
- [ ] Review dates are set for all open risks and not more than 6 months out.
- [ ] Register is stored in version-controlled or auditable tooling (not a private spreadsheet).
- [ ] Residual score is calculated for all risks with active mitigations.

**AI-CAIQ evidence:** This skill supports YES response to GRC-02 by producing a structured AI risk register with scored risks, assigned owners, mitigation records, and review schedules that demonstrate formal AI risk tracking aligned to NIST AI RMF or ISO 42001.
