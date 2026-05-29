# Skill Schema Reference — v2

Every skill in this library is a single `SKILL.md` file in its own directory. The file has two parts: a YAML frontmatter block and a Markdown body.

---

## Frontmatter fields

```yaml
---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: <string>                  # Unique kebab-case identifier. Matches the directory name.
name: <string>                # Human-readable display name (same as id).
version: "<semver>"           # Semantic version string, quoted.
domain: <AICM domain ID>      # One of the 18 AICM control domain IDs (see list below).
aicm_controls:                # AICM v1.0.3 control objective IDs this skill provides
  - <CONTROL-ID>              # evidence for. Proposed — verify against official spec.
  - <CONTROL-ID>
ssrm_ownership: <value>       # SSRM ownership role (see allowed list below).
aismm_category: <value>       # AISMM category (see allowed list below).
aismm_target_level: <1-5>     # AISMM maturity level this skill is designed for.
summary: >-                   # One-paragraph "when to use this" description.
  <text>                      # Min 50 chars. Used by agents for skill selection.
references:                   # Surface tags: tool names, concepts, standard names.
  - <tag>                     # No framework mapping tables. Tags only.
---
```

**Required fields:** `id`, `name`, `version`, `domain`, `aicm_controls`, `ssrm_ownership`, `aismm_category`, `aismm_target_level`, `summary`

**`references`** carries only surface-level tags. It does **not** contain framework mapping tables. Framework crosswalks (AICM, AI-CAIQ, AISMM, ISO 42001, NIST AI RMF) are metadata expressed via the structured fields above.

---

## Allowed `domain` values — 18 AICM control domains (AICM v1.0.3)

| ID | Canonical name |
|---|---|
| A&A | Audit & Assurance |
| AIS | Application & Interface Security |
| BCR | Business Continuity Management and Operational Resilience |
| CCC | Change Control and Configuration Management |
| CEK | Cryptography, Encryption & Key Management |
| DCS | Datacenter Security |
| DSP | Data Security and Privacy Lifecycle Management |
| GRC | Governance, Risk and Compliance |
| HRS | Human Resources |
| IAM | Identity & Access Management |
| IPY | Interoperability & Portability |
| I&S | Infrastructure Security |
| LOG | Logging and Monitoring |
| MDS | Model Security |
| SEF | Security Incident Management, E-Discovery, & Cloud Forensics |
| STA | Supply Chain Management, Transparency, and Accountability |
| TVM | Threat & Vulnerability Management |
| UEM | Universal Endpoint Management |

---

## Allowed `ssrm_ownership` values (CSA SSRM)

Supply-chain role that owns the primary control responsibility for this skill.

`CSP-Owned` · `MP-Owned` · `OSP-Owned` · `AP-Owned` · `AIC-Owned` ·
`Shared CSP-MP` · `Shared MP-OSP` · `Shared OSP-AP` · `Shared AP-AIC` ·
`Shared Across Supply Chain` · `ND`

**Role abbreviations:** CSP = Cloud Service Provider · MP = Model Provider ·
OSP = Orchestrated Service Provider · AP = Application Provider ·
AIC = AI Customer

---

## Allowed `aismm_category` values — 12 AISMM categories

| AISMM domain | Category |
|---|---|
| Foundational | Governance |
| Foundational | Organization Management |
| Foundational | IAM |
| Foundational | Security Monitoring |
| Structural | Infrastructure Security & Resilience |
| Structural | Model Security |
| Structural | App Security |
| Structural | Data Security |
| Procedural | Risk & Provider Assessment & Management |
| Procedural | AI Supported Development & Supply Chain Security |
| Procedural | Privacy, Compliance and Audit |
| Procedural | Incident Response |

---

## Allowed `aismm_target_level` values

| Level | Label | Meaning |
|---|---|---|
| 1 | Initial | Ad-hoc, undocumented |
| 2 | Repeatable | Documented, inconsistently applied |
| 3 | Defined | Standardised, consistently applied |
| 4 | Capable | Measured, monitored, partially automated |
| 5 | Efficient | Optimised, continuously improved |

---

## Body sections

Sections appear in this order. **When to Use** and **Procedure** are required.

### `## When to Use`

Bullet list of conditions under which an analyst or agent should load this skill. Written as "Use this skill when…". Include an explicit **Do not use** clause.

### `## Inputs`

What the skill expects as input: artefact types, API responses, config files, log samples, etc.

### `## Procedure`

Numbered steps. Steps must be concrete and executable — include real commands, tool invocations, API calls, or templates. Steps should not require ambiguous interpretation.

### `## Outputs`

What a correctly completed execution produces: the artefact, decision record, evidence document, etc.

### `## Quality Checks`

Checklist confirming correct execution. Format as `- [ ] …` where possible.

### AI-CAIQ evidence (optional footer line)

A single line noting which AICM control objective(s) this skill's output supports as evidence in an AI-CAIQ self-assessment.

---

## Worked example

```
skills/
└── defending-against-prompt-injection/
    └── SKILL.md
```

The skill maps to AICM domain AIS (Application & Interface Security), control AIS-08, owned by the Application Provider, targeting AISMM Level 4 (Capable). When used and documented, it produces evidence that the AP has implemented input-validation controls — a YES response to AIS-08 in the AI-CAIQ self-assessment.

---

## Notes on `aicm_controls` accuracy

The control-objective IDs in this library are **proposed mappings** based on the published AICM v1.0.3 domain structure. They should be verified against the official CSA AICM v1.0.3 specification before use in formal self-assessments or regulatory submissions.
