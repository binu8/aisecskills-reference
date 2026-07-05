---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: mapping-controls-to-iso-42001
name: mapping-controls-to-iso-42001
version: "1.0"
domain: GRC
aicm_controls:
  - GRC-01
  - A&A-04
ssrm_ownership: AIC-Owned
aismm_category: Governance
aismm_target_level: 3
pillar: security_for_ai
summary: >-
  Use this skill when you need to map your organization's existing security
  and AI controls to ISO/IEC 42001 requirements and produce a gap analysis
  and compliance coverage report.
references:
  - ISO-42001
  - AI-management-system
  - controls-mapping
  - gap-analysis
  - governance
  - AIMS
---

## When to Use

Use this skill when:
- Your organization is pursuing ISO 42001 certification or self-attestation.
- A customer or regulator requires evidence of ISO 42001 alignment.
- You are building an AI Management System (AIMS) and need to understand which controls you already have.
- An annual review requires updating the controls gap analysis against the standard.

**Do not use** this skill as a substitute for a formal ISO 42001 certification audit — a Certification Body must conduct that assessment.

## Inputs

- Inventory of existing AI controls and policies (from your AI risk register, AICM assessment, or internal controls library).
- ISO 42001:2023 clause list (clauses 4–10 and Annex A controls).
- Evidence artifacts for controls you believe are already implemented.

## Procedure

### Step 1: Load the ISO 42001 clause structure

```python
ISO_42001_CLAUSES = {
    "4.1": "Understanding the organization and its context",
    "4.2": "Understanding needs and expectations of interested parties",
    "4.3": "Determining the scope of the AIMS",
    "4.4": "AI management system",
    "5.1": "Leadership and commitment",
    "5.2": "AI policy",
    "5.3": "Organizational roles, responsibilities and authorities",
    "6.1": "Actions to address risks and opportunities",
    "6.2": "AI objectives and plans to achieve them",
    "7.1": "Resources",
    "7.2": "Competence",
    "7.3": "Awareness",
    "7.4": "Communication",
    "7.5": "Documented information",
    "8.1": "Operational planning and control",
    "8.2": "AI risk assessment",
    "8.3": "AI risk treatment",
    "8.4": "AI system impact assessment",
    "9.1": "Monitoring, measurement, analysis and evaluation",
    "9.2": "Internal audit",
    "9.3": "Management review",
    "10.1": "Nonconformity and corrective action",
    "10.2": "Continual improvement",
}

ISO_42001_ANNEX_A = {
    "A.2.2": "Roles and responsibilities for AI",
    "A.3.2": "Internal AI impact assessment process",
    "A.4.1": "Intended use",
    "A.4.2": "AI risk classification",
    "A.5.1": "Data for AI systems",
    "A.5.2": "Data acquisition",
    "A.5.3": "Data preparation",
    "A.5.4": "Data annotation",
    "A.6.1": "AI system design",
    "A.6.2": "AI system verification and validation",
    "A.7.1": "Human oversight of AI systems",
    "A.7.2": "Addressing AI system concerns",
    "A.8.1": "Feedback processes for AI systems",
    "A.9.1": "Recording AI-related events",
    "A.10.1": "Documentation of AI systems",
}
```

### Step 2: Define your control inventory

```yaml
# controls-inventory.yaml (excerpt)
controls:
  - id: CTRL-001
    title: AI Risk Register
    description: Structured register of AI risks with owners and mitigations
    evidence: ai-risk-register.csv
    status: implemented
  - id: CTRL-002
    title: Model Safety Evaluation
    description: Pre-deployment safety and bias evaluation for all models
    evidence: safety-evaluation.json
    status: implemented
  - id: CTRL-003
    title: AIMS Scope Document
    description: Documented scope of the AI Management System
    evidence: aims-scope.pdf
    status: planned
```

### Step 3: Build the mapping

```python
CONTROL_TO_ISO_MAPPING = {
    "CTRL-001": ["6.1", "8.2", "8.3", "A.4.2"],
    "CTRL-002": ["8.4", "A.6.2", "A.7.1"],
    "CTRL-003": ["4.3", "4.4"],
    # ... continue for all controls
}

def build_gap_analysis(controls: list[dict], mapping: dict) -> dict:
    covered_clauses = set()
    for ctrl in controls:
        if ctrl["status"] == "implemented":
            for clause in mapping.get(ctrl["id"], []):
                covered_clauses.add(clause)
    
    all_clauses = set(ISO_42001_CLAUSES.keys()) | set(ISO_42001_ANNEX_A.keys())
    gaps = all_clauses - covered_clauses
    
    return {
        "total_clauses": len(all_clauses),
        "covered": len(covered_clauses),
        "coverage_pct": len(covered_clauses) / len(all_clauses),
        "gaps": sorted(gaps),
    }
```

### Step 4: Generate a coverage report

```python
import csv

def export_gap_analysis(controls: list, mapping: dict, output_path: str):
    all_clauses = {**ISO_42001_CLAUSES, **ISO_42001_ANNEX_A}
    clause_status = {clause: "gap" for clause in all_clauses}
    
    for ctrl in controls:
        if ctrl["status"] == "implemented":
            for clause in mapping.get(ctrl["id"], []):
                clause_status[clause] = "covered"
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["clause", "title", "status", "covering_controls"])
        writer.writeheader()
        for clause, status in sorted(clause_status.items()):
            covering = [c["id"] for c in controls
                        if clause in mapping.get(c["id"], []) and c["status"] == "implemented"]
            writer.writerow({
                "clause": clause,
                "title": all_clauses[clause],
                "status": status,
                "covering_controls": "; ".join(covering),
            })
```

### Step 5: Prioritize gap remediation

```python
CLAUSE_PRIORITY = {
    # Mandatory clauses for certification
    "4.3": "high", "5.2": "high", "6.1": "high", "8.2": "high", "9.2": "high", "10.1": "high",
    # Annex A recommended
    "A.4.2": "high", "A.7.1": "high", "A.9.1": "medium",
}

def prioritize_gaps(gaps: list[str]) -> list[dict]:
    return sorted([
        {"clause": g, "title": {**ISO_42001_CLAUSES, **ISO_42001_ANNEX_A}.get(g, ""),
         "priority": CLAUSE_PRIORITY.get(g, "low")}
        for g in gaps
    ], key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]])
```

## Outputs

- Controls mapping CSV linking each control to ISO 42001 clauses.
- Gap analysis report with coverage percentage and list of uncovered clauses.
- Prioritized remediation list for gaps.
- Evidence register linking artifact files to covered clauses.

## Quality Checks

- [ ] Every mandatory ISO 42001 clause (4–10) is addressed in the mapping.
- [ ] All Annex A controls relevant to the AIMS scope are included.
- [ ] Coverage percentage is calculated and documented.
- [ ] Gaps are prioritized and assigned to owners with target remediation dates.
- [ ] Evidence files referenced in the mapping exist and are accessible.

**AI-CAIQ evidence:** This skill supports YES response to GRC-01 by producing a controls-to-ISO-42001 mapping, gap analysis report, and evidence register demonstrating that the organization's AI governance framework is systematically aligned to the ISO 42001 AIMS standard.
