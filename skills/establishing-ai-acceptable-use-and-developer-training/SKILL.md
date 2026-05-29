---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: establishing-ai-acceptable-use-and-developer-training
name: establishing-ai-acceptable-use-and-developer-training
version: "1.0"
domain: HRS
aicm_controls:
  - HRS-04
  - HRS-11
ssrm_ownership: AIC-Owned
aismm_category: Governance
aismm_target_level: 3
summary: >-
  Use this skill when you need to create an AI acceptable use policy,
  security training curriculum, and attestation process for developers
  and staff who build or use AI systems.
references:
  - acceptable-use-policy
  - security-training
  - AI-governance
  - developer-education
  - NIST-AI-RMF
  - policy
---

## When to Use

Use this skill when:
- Your organization has deployed AI tools (coding assistants, chatbots, LLM APIs) but has no formal policy governing their use.
- A compliance review requires evidence that staff received AI security awareness training.
- A security incident involved an employee inadvertently sending sensitive data to an external AI service.
- You are building an AI governance program and need the human-controls layer.

**Do not use** this skill to implement technical controls — it addresses the people and process layer; pair it with technical controls from other skills.

## Inputs

- List of AI tools currently in use or being evaluated (internal and external).
- Existing acceptable use or information security policies to align with.
- Roles involved: developers, data scientists, business analysts, general staff.

## Procedure

### Step 1: Draft the AI Acceptable Use Policy

```markdown
# AI Acceptable Use Policy v1.0

## Scope
This policy applies to all employees, contractors, and vendors who use AI-assisted tools
(including but not limited to: GitHub Copilot, Claude, ChatGPT, Gemini, Midjourney)
in the course of their work.

## Approved Tools
Only tools on the approved AI tool registry may be used for work purposes.
Employees must not submit work-related data to unapproved AI services.

## Prohibited Uses
- Uploading customer PII, PHI, or financial records to external AI services without a signed DPA
- Using AI to generate content that will be published without human review
- Using AI tools to attempt to access or exfiltrate company data beyond your authorized scope
- Sharing proprietary source code with external AI services unless the tool is on the approved list
  and has been reviewed for data handling

## Data Classification Rules
| Data Class | May be used with approved AI tool? |
|---|---|
| Public | Yes |
| Internal | Yes, approved tools only |
| Confidential | No, unless tool is in Confidential-approved tier |
| Regulated (PHI/PII/PCI) | No, without explicit CISO waiver |

## Developer-Specific Rules
- AI-generated code must be reviewed by a human before merge
- Secrets and credentials must never be pasted into AI prompts
- AI coding assistant output is not a substitute for security review

## Attestation
All in-scope staff must complete AI Security Awareness Training and sign this policy annually.
```

### Step 2: Build the AI Security Training curriculum

```yaml
# ai-security-training-curriculum.yaml
modules:
  - id: M1
    title: "AI Basics and Risk Overview"
    audience: [all_staff]
    duration_minutes: 20
    topics:
      - What are LLMs and how do they work (briefly)
      - Why AI tools create new security risks
      - Real-world AI security incidents (prompt injection, data leakage)
    quiz_pass_score: 80

  - id: M2
    title: "Data Classification and AI Tool Use"
    audience: [all_staff]
    duration_minutes: 15
    topics:
      - Data classification tiers and which AI tools can process each
      - PII, PHI, trade secrets — what never to paste into an AI chat
      - How to use the approved AI tool registry
    quiz_pass_score: 85

  - id: M3
    title: "Secure AI Development Practices"
    audience: [developers, data_scientists]
    duration_minutes: 30
    topics:
      - Prompt injection — what it is and how to prevent it
      - Reviewing AI-generated code for security issues
      - Not committing secrets — even to "private" AI chats
      - Using AI coding assistants safely with proprietary code
    quiz_pass_score: 85

  - id: M4
    title: "AI Incident Response Basics"
    audience: [developers, security_team]
    duration_minutes: 20
    topics:
      - How to report an AI security incident
      - What constitutes an AI-related data breach
      - The AI incident response playbook overview
    quiz_pass_score: 80
```

### Step 3: Implement a policy attestation tracker

```python
from dataclasses import dataclass, field
import datetime, csv

@dataclass
class TrainingRecord:
    employee_id: str
    name: str
    role: str
    modules_completed: list[str] = field(default_factory=list)
    policy_signed_date: str = ""
    attestation_due: str = ""
    status: str = "pending"  # pending | completed | overdue

def check_compliance(records: list[TrainingRecord]) -> dict:
    today = datetime.date.today().isoformat()
    required_modules_by_role = {
        "developer": ["M1", "M2", "M3", "M4"],
        "data_scientist": ["M1", "M2", "M3"],
        "all_staff": ["M1", "M2"],
    }
    
    non_compliant = []
    for r in records:
        required = required_modules_by_role.get(r.role, required_modules_by_role["all_staff"])
        missing = [m for m in required if m not in r.modules_completed]
        if missing or not r.policy_signed_date:
            non_compliant.append({"employee": r.employee_id, "missing_modules": missing,
                                   "policy_signed": bool(r.policy_signed_date)})
    
    return {
        "total": len(records),
        "compliant": len(records) - len(non_compliant),
        "compliance_rate": (len(records) - len(non_compliant)) / len(records),
        "non_compliant": non_compliant,
    }
```

### Step 4: Define the approved AI tool registry

```yaml
# approved-ai-tool-registry.yaml
tools:
  - name: GitHub Copilot
    vendor: GitHub / Microsoft
    approved_for: [internal, public]
    dpa_signed: true
    review_date: "2025-06-01"
    notes: "Training data opt-out enabled; no proprietary code to external endpoint"
  - name: Claude (Anthropic API)
    vendor: Anthropic
    approved_for: [internal, confidential]
    dpa_signed: true
    review_date: "2025-06-01"
    notes: "Zero-retention API tier in use; see provider risk assessment"
  - name: ChatGPT (web UI)
    vendor: OpenAI
    approved_for: [public, internal]
    dpa_signed: false
    notes: "Do not input Confidential or Regulated data; no DPA for web UI"
```

## Outputs

- AI Acceptable Use Policy document with data classification rules.
- Training curriculum YAML with module content and pass-score thresholds.
- Attestation tracker with compliance rate calculation.
- Approved AI tool registry YAML.

## Quality Checks

- [ ] Policy covers all four data classification tiers with explicit AI tool restrictions.
- [ ] Training completion rate is ≥95% for in-scope staff (verified from tracker).
- [ ] Policy attestation is renewed annually and records are retained for audit.
- [ ] Approved tool registry is reviewed when a new AI tool is adopted.
- [ ] Developer module (M3) is required for all staff with code repository access.

**AI-CAIQ evidence:** This skill supports YES response to HRS-04 by producing an AI Acceptable Use Policy, training curriculum, attestation tracker, and compliance rate report demonstrating that staff receive documented AI security training and formally attest to policy compliance.
