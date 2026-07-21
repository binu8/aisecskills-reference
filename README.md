# ai · security · skills — reference library v2

An open sample of a structured AI security skill library, aligned to the CSA AI assurance stack: **AICM v1.0.3** (18 control domains), the **AI-CAIQ v1.0.2** self-assessment instrument, and the **AISMM** (5-level Initial→Efficient maturity scale).

→ **[Quickstart in ~10 minutes](quickstart/README.md)**

---

## What this is

Each skill is a `SKILL.md` file: a structured document that tells an AI agent *exactly* how to perform a specific AI security task. An agent loads the skill as context, receives the practitioner's input, and executes the procedure.

This repository contains **56 AI-native skills** (count derived from `skills/*/SKILL.md` via `scripts/rebuild_index.py`). Skills are grouped under the three pillars defined in [SKILL_SPEC.md](SKILL_SPEC.md) / [PILLARS.md](PILLARS.md), and each skill also maps to exactly one of the 18 AICM control domains present in this sample:

### By pillar

| Pillar | Focus | Skills |
|---|---|---|
| **Security for AI** | Protecting AI systems throughout their lifecycle | 35 |
| **AI for Security** | Deploying AI as a security capability | 1 |
| **Security from AI** | Managing AI-specific risks and harms | 20 |

See [PILLARS.md](PILLARS.md) for the full per-skill lists.

### By AICM domain

| AICM domain | ID | Skills |
|---|---|---|
| Application & Interface Security | AIS | 11 |
| Model Security | MDS | 6 |
| Data Security and Privacy Lifecycle Management | DSP | 5 |
| Identity & Access Management | IAM | 5 |
| Logging and Monitoring | LOG | 5 |
| Supply Chain Management, Transparency, and Accountability | STA | 4 |
| Threat & Vulnerability Management | TVM | 4 |
| Governance, Risk and Compliance | GRC | 3 |
| Security Incident Management, E-Discovery, & Cloud Forensics | SEF | 3 |
| Audit & Assurance | A&A | 2 |
| Business Continuity Management and Operational Resilience | BCR | 1 |
| Change Control and Configuration Management | CCC | 1 |
| Cryptography, Encryption & Key Management | CEK | 1 |
| Datacenter Security | DCS | 1 |
| Human Resources | HRS | 1 |
| Infrastructure Security | I&S | 1 |
| Interoperability & Portability | IPY | 1 |
| Universal Endpoint Management | UEM | 1 |

Skills are licensed **Apache 2.0**.

---

## What this is NOT

- **Not the full library.** The full working library is substantially larger, with framework crosswalks, the MECE AICM partition, AISMM scoring, and a governance layer. This repository is a representative sample (56 skills on disk).
- **Not a product.** There is no subscription, agent runtime, or tooling here — only structured knowledge in a portable plain-text format.
- **Not a certification.** Nothing here constitutes compliance advice, regulatory certification, or a completed audit. STAR for AI Level 1 is a self-assessment registry listing.

---

## The CSA AI assurance stack

Skills in this library are mapped to three complementary CSA instruments:

**AICM v1.0.3 — what controls exist**
18 control domains and the published CSA control-objective set define the AI security control landscape. Each skill lists which control objectives it provides evidence for (`aicm_controls`).

**AI-CAIQ v1.0.2 — are they answered**
The AI Cloud Infrastructure and Controls Questionnaire asks each control objective: YES / NO / NA, with SSRM ownership (who in the supply chain owns it) and an evidence artefact. A skill's output is the evidence that supports a YES response.

**AISMM — how well**
The AI Security Maturity Model places each AISMM category on a five-level scale: Initial (Level 1) → Repeatable → Defined → Capable → Efficient (Level 5). Each skill carries an `aismm_target_level` indicating the maturity level it is designed to achieve.

**SSRM — who owns it**
The Shared Security Responsibility Model for AI identifies five supply-chain roles: AI Customer (AIC), Application Provider (AP), Orchestrated Service Provider (OSP), Model Provider (MP), Cloud Service Provider (CSP). Each skill carries an `ssrm_ownership` field.

---

## How to use a skill

**As AI agent context:**

1. Clone this repository.
2. Open the skill matching your task — e.g. `skills/defending-against-prompt-injection/SKILL.md`.
3. Load the full file as your system prompt or agent context.
4. Provide your input (target application, log excerpt, config file, etc.) as the user message.
5. The agent follows the Procedure and produces output in the format described in the skill.

See the [quickstart](quickstart/README.md) for a worked example.

**As AI-CAIQ evidence:**

When you execute a skill and document the output, that output supports a YES response to the corresponding AICM control objective in your AI-CAIQ self-assessment. The `aicm_controls` field in each skill's frontmatter identifies which control objectives it covers.

**Browsing:**

`index.json` lists all 56 skills with their AICM domain, controls, SSRM role, AISMM category, target level, pillar, and summary — useful for programmatic selection. Regenerate it with `python3 scripts/rebuild_index.py` after adding or editing skills.

---

## Skill format

Skills follow a documented schema: see [SKILL_SPEC.md](SKILL_SPEC.md).

The format is intentionally portable — any agent runtime that accepts a system prompt can use these skills.

---

## Accuracy note on control-ID mappings

The `aicm_controls` and `ssrm_ownership` values in this library are **proposed mappings** and should be verified against the official AICM v1.0.3 specification and CSA SSRM guidance before use in formal self-assessments, regulatory submissions, or STAR for AI Level 1 filings.

---

## Supported crosswalks

Skills in this library cross-reference the following standards where applicable:

- **AICM v1.0.3** — CSA AI Controls Matrix (primary mapping)
- **AI-CAIQ v1.0.2** — CSA AI Cloud Infrastructure Controls Questionnaire
- **AISMM** — CSA AI Security Maturity Model
- **ISO/IEC 42001** — AI management system standard
- **ISO/IEC 27001** — Information security management
- **NIST AI RMF 1.0** — Govern, Map, Measure, Manage
- **EU AI Act** — High-risk AI system obligations

---

## Provenance

This repository previously contained skills derived from an open Apache-2.0 upstream library ([Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills)). The v2 skills in this release are originally authored for the AICM/AI-CAIQ/AISMM framework, and no longer derived from that upstream base. See [NOTICE](NOTICE) for full attribution, including the vendored `vendor/msaad00-mcp-detection/` skills.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
