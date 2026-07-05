---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: conducting-an-aicm-control-assessment
name: conducting-an-aicm-control-assessment
version: "1.0"
domain: A&A
aicm_controls:
  - A&A-02
  - A&A-05
ssrm_ownership: AIC-Owned
aismm_category: Privacy, Compliance and Audit
aismm_target_level: 3
pillar: security_for_ai
summary: >-
  Use this skill when you need to conduct a structured assessment of your
  organization's AI controls against the CSA AICM control framework,
  producing a scored maturity profile and gap remediation plan.
references:
  - AICM
  - CSA
  - controls-assessment
  - maturity-model
  - audit
  - AI-governance
---

## When to Use

Use this skill when:
- Your organization needs a baseline maturity score against the CSA AI Controls Matrix.
- A customer or auditor requests evidence of a formal AICM-aligned control assessment.
- You are preparing for an AI security certification or third-party audit.
- You need to prioritize AI security investments based on a structured gap analysis.

**Do not use** this skill as a substitute for an accredited third-party audit — this skill produces a self-assessment, not a certification.

## Inputs

- AICM control list (current version from CSA).
- Evidence inventory: policies, technical configurations, logs, test results.
- Assessor assignments (technical SME per domain).

## Procedure

### Step 1: Structure the assessment workbook

```python
from dataclasses import dataclass, field
from typing import Optional

AICM_DOMAINS = ["DSP", "MDS", "AIS", "IAM", "LOG", "TVM", "GRC", "STA", "SEF", "A&A", "BCR", "CCC", "CEK", "DCS", "HRS", "IPY", "I&S", "UEM"]

MATURITY_LEVELS = {
    1: "Incomplete — control is not defined",
    2: "Defined — policy exists but not consistently implemented",
    3: "Implemented — control is consistently applied",
    4: "Measured — effectiveness is monitored and metrics exist",
    5: "Optimized — continuous improvement process in place",
}

@dataclass
class ControlAssessment:
    control_id: str
    control_name: str
    domain: str
    ssrm_ownership: str
    current_maturity: int = 1          # 1-5
    target_maturity: int = 3           # organization's target
    evidence: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    remediation_actions: list[str] = field(default_factory=list)
    priority: str = "medium"           # high | medium | low
    owner: str = ""
    target_date: str = ""
```

### Step 2: Interview-based evidence collection template

```yaml
# assessment-interview-guide.yaml
control_id: DSP-07
control_name: Data Access and Handling
interview_questions:
  - "How do you ensure that RAG retrieval results are scoped to the requesting user's permissions?"
  - "What access control mechanisms are applied to the vector store?"
  - "How are access control policies tested and validated?"
evidence_request:
  - "Retrieval filter configuration or code"
  - "ACL policy document"
  - "Test results demonstrating cross-user isolation"
pass_criteria:
  - "Metadata filters applied on every retrieval call"
  - "ACL policies are defined and version-controlled"
  - "Cross-user isolation test passes in CI"
```

### Step 3: Score each control

```python
def score_control(assessment: ControlAssessment, evidence_present: bool,
                   evidence_tested: bool, metrics_exist: bool,
                   continuous_improvement: bool) -> int:
    if not evidence_present:
        return 1
    if not evidence_tested:
        return 2
    if not metrics_exist:
        return 3
    if not continuous_improvement:
        return 4
    return 5
```

### Step 4: Compute domain and overall maturity scores

```python
import statistics
from collections import defaultdict

def compute_scores(assessments: list[ControlAssessment]) -> dict:
    by_domain = defaultdict(list)
    for a in assessments:
        by_domain[a.domain].append(a.current_maturity)
    
    domain_scores = {
        domain: round(statistics.mean(scores), 2)
        for domain, scores in by_domain.items()
    }
    overall = round(statistics.mean(a.current_maturity for a in assessments), 2)
    
    gaps = [a for a in assessments if a.current_maturity < a.target_maturity]
    gap_by_priority = defaultdict(list)
    for g in gaps:
        gap_by_priority[g.priority].append(g.control_id)
    
    return {
        "overall_score": overall,
        "domain_scores": domain_scores,
        "gap_count": len(gaps),
        "gaps_by_priority": dict(gap_by_priority),
    }
```

### Step 5: Generate the assessment report

```python
import json, datetime, csv

def export_assessment(assessments: list[ControlAssessment], output_csv: str):
    import dataclasses
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "control_id", "control_name", "domain", "current_maturity",
            "target_maturity", "priority", "owner", "target_date"
        ])
        writer.writeheader()
        for a in assessments:
            row = dataclasses.asdict(a)
            writer.writerow({k: row[k] for k in writer.fieldnames})

def generate_report(assessments: list, scores: dict) -> dict:
    return {
        "assessment_date": datetime.date.today().isoformat(),
        "framework": "CSA AICM v2",
        "overall_maturity": scores["overall_score"],
        "domain_scores": scores["domain_scores"],
        "total_controls": len(assessments),
        "gap_count": scores["gap_count"],
        "high_priority_gaps": scores["gaps_by_priority"].get("high", []),
    }
```

## Outputs

- Assessment workbook CSV with per-control maturity scores, evidence, and gaps.
- Domain maturity scores and overall AICM maturity score.
- Prioritized gap remediation plan with owners and target dates.
- Assessment report JSON for executive and auditor review.

## Quality Checks

- [ ] Every AICM control in scope has at least one evidence artifact linked.
- [ ] Maturity scores are based on objective criteria, not assessor judgment alone.
- [ ] High-priority gaps have assigned owners and dates.
- [ ] Domain scores are reviewed with the owning team before the report is finalized.
- [ ] Assessment report is signed off by the CISO or equivalent.

**AI-CAIQ evidence:** This skill supports YES response to A&A-02 by producing a structured AICM control assessment with per-control maturity scores, evidence references, and a gap remediation plan demonstrating systematic evaluation of AI controls against the CSA AICM framework.
