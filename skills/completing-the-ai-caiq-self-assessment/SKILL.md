---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: completing-the-ai-caiq-self-assessment
name: completing-the-ai-caiq-self-assessment
version: "1.0"
domain: A&A
aicm_controls:
  - A&A-01
  - A&A-06
ssrm_ownership: AIC-Owned
aismm_category: Privacy, Compliance and Audit
aismm_target_level: 3
summary: >-
  Use this skill when you need to complete the CSA AI Consensus Assessments
  Initiative Questionnaire (AI-CAIQ) for your organization, producing a
  shareable, verifiable self-attestation of AI security controls.
references:
  - AI-CAIQ
  - CSA
  - self-assessment
  - attestation
  - compliance
  - AI-governance
---

## When to Use

Use this skill when:
- A customer, partner, or regulator requests your AI-CAIQ response as part of due diligence.
- Your organization wants to proactively publish an AI-CAIQ to demonstrate AI security maturity.
- You are completing an annual AI governance review that includes a self-attestation component.
- A procurement process requires your AI-CAIQ before awarding a contract.

**Do not use** this skill to generate fraudulent or unsupported YES responses — every YES answer must be backed by evidence. Inaccurate AI-CAIQ responses create legal and reputational risk.

## Inputs

- Evidence inventory from your AICM control assessment (see `conducting-an-aicm-control-assessment`).
- Current AI security policies, configurations, and audit results.
- SME availability to validate answers per domain.

## Procedure

### Step 1: Download and structure the AI-CAIQ

```bash
# The official AI-CAIQ is available from CSA at:
# https://cloudsecurityalliance.org/research/working-groups/ai-safety-initiative/

# Structure for programmatic completion:
python3 - <<'EOF'
AI_CAIQ_QUESTIONS = {
    "AIS-01": "Do you have a documented AI acceptable use policy?",
    "AIS-02": "Is AI system documentation maintained and updated?",
    "DSP-07": "Are access controls enforced to prevent unauthorized data retrieval via AI systems?",
    "DSP-10": "Is training data scanned for PII before use?",
    "IAM-03": "Are non-human AI agent identities provisioned and managed separately from human users?",
    "IAM-09": "Are AI agent tool authorizations scoped to least privilege?",
    "LOG-03": "Are all LLM prompts and responses logged for audit purposes?",
    "LOG-08": "Are AI system logs monitored for anomalous behavior?",
    "MDS-03": "Are AI model artifacts signed and integrity-verified before deployment?",
    "MDS-05": "Is adversarial robustness testing conducted before model deployment?",
    "MDS-09": "Are AI models evaluated for bias and harmful output potential?",
    "TVM-03": "Is adversarial testing (red-teaming) conducted on AI applications?",
    # ... (full AI-CAIQ has 150+ questions)
}
print(f"Loaded {len(AI_CAIQ_QUESTIONS)} AI-CAIQ questions")
EOF
```

### Step 2: Define the response schema

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class CAIQResponse:
    control_id: str
    question: str
    answer: str                     # YES | NO | N/A | PARTIAL
    answer_rationale: str           # required — explains the YES/NO
    evidence_artifacts: list[str]   # file paths, URLs, or document references
    ssrm_ownership: str             # which party's responsibility
    last_reviewed: str
    reviewer: str
```

### Step 3: Populate responses with evidence

```python
SAMPLE_RESPONSES = [
    CAIQResponse(
        control_id="DSP-07",
        question="Are access controls enforced to prevent unauthorized data retrieval via AI systems?",
        answer="YES",
        answer_rationale=(
            "The RAG pipeline applies per-user metadata filters on every vector store query. "
            "Filters enforce group-based ACLs stored in document metadata. "
            "Cross-user isolation is validated by automated tests in CI."
        ),
        evidence_artifacts=[
            "rag-pipeline/retriever.py (lines 45-72)",
            "tests/test_rag_isolation.py",
            "ci-results/rag-isolation-2025-06-01.json",
        ],
        ssrm_ownership="AP-Owned",
        last_reviewed="2025-06-01",
        reviewer="Jane Smith, Security Architect",
    ),
    CAIQResponse(
        control_id="MDS-03",
        question="Are AI model artifacts signed and integrity-verified before deployment?",
        answer="YES",
        answer_rationale=(
            "All model artifacts are signed with Sigstore cosign at build time. "
            "The deployment pipeline verifies the signature and SHA-256 manifest before promotion. "
            "Rekor transparency log entries are retained for all model releases."
        ),
        evidence_artifacts=[
            ".github/workflows/model-promotion.yml",
            "docs/model-signing-policy.md",
            "audit/model-signatures/llama3-2025-06-01.sig",
        ],
        ssrm_ownership="MP-Owned",
        last_reviewed="2025-06-01",
        reviewer="Bob Chen, MLOps Engineer",
    ),
]
```

### Step 4: Validate completeness and export

```python
import csv, json, datetime

def validate_caiq(responses: list[CAIQResponse]) -> dict:
    issues = []
    for r in responses:
        if r.answer == "YES" and not r.evidence_artifacts:
            issues.append(f"{r.control_id}: YES answer has no evidence artifacts")
        if len(r.answer_rationale) < 50:
            issues.append(f"{r.control_id}: Rationale is too short (<50 chars)")
        if not r.reviewer:
            issues.append(f"{r.control_id}: No reviewer assigned")
    return {"valid": len(issues) == 0, "issues": issues}

def export_caiq_csv(responses: list[CAIQResponse], output_path: str):
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "control_id", "question", "answer", "answer_rationale",
            "evidence_artifacts", "ssrm_ownership", "last_reviewed", "reviewer"
        ])
        writer.writeheader()
        for r in responses:
            import dataclasses
            row = dataclasses.asdict(r)
            row["evidence_artifacts"] = " | ".join(row["evidence_artifacts"])
            writer.writerow(row)
```

### Step 5: Sign and publish the attestation

```python
import hashlib

def sign_attestation(caiq_csv_path: str, signer_name: str, signer_title: str) -> dict:
    with open(caiq_csv_path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    
    attestation = {
        "document": caiq_csv_path,
        "sha256": digest,
        "signed_by": signer_name,
        "signer_title": signer_title,
        "organization": "My Company Inc.",
        "date": datetime.date.today().isoformat(),
        "statement": (
            "I attest that the answers in this AI-CAIQ represent an accurate "
            "description of our AI security controls to the best of my knowledge."
        ),
    }
    with open("ai-caiq-attestation.json", "w") as f:
        json.dump(attestation, f, indent=2)
    return attestation
```

## Outputs

- AI-CAIQ CSV with per-control responses, rationale, evidence artifacts, and reviewer.
- Validation report confirming all YES answers have supporting evidence.
- Signed attestation JSON with SHA-256 digest of the completed questionnaire.

## Quality Checks

- [ ] Every YES answer has at least one evidence artifact reference.
- [ ] No rationale field is shorter than 50 characters.
- [ ] All responses have an assigned reviewer and review date.
- [ ] Validation function returns `valid: true` before the attestation is signed.
- [ ] Signed attestation is stored alongside the questionnaire and accessible to auditors.

**AI-CAIQ evidence:** This skill supports YES response to A&A-01 by producing a completed AI-CAIQ with evidenced responses, a validation report confirming completeness, and a signed attestation demonstrating that the organization has formally assessed and documented its AI security posture against the CSA framework.
