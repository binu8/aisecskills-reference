# ai · security · skills — reference library

An open sample of a larger structured skill library for AI-native security operations. Forty skills across nine security functions, in a format designed to be loaded directly as context for LLM-based agents.

→ **[Quickstart in ~10 minutes](quickstart/README.md)**

---

## What this is

Each skill is a `SKILL.md` file: a structured document that tells an AI agent *exactly* how to perform a specific security task — alert triage, incident containment, threat-actor profiling, access review, and so on. An agent loads the skill as context, receives the analyst's input, and executes the procedure.

This repository contains **40 curated skills** across nine InfoSec functions:

| Function | Count |
|---|---|
| Security Operations | 8 |
| Incident Response | 5 |
| Threat Intelligence | 5 |
| Detection Engineering | 4 |
| Vulnerability Management | 4 |
| Identity & Access Management | 4 |
| Cloud Security | 4 |
| Governance & Compliance | 3 |
| Foundations | 3 |

Skills are licensed **Apache 2.0** and derived from the open upstream library (see NOTICE).

---

## What this is NOT

- **Not the full library.** The full library covers 750+ skills across 27 security domains, with framework crosswalks (NIST CSF, ATT&CK, AI RMF), audit tooling, a maturity model, and a governance layer. This repository is a representative sample.
- **Not a product.** There is no subscription, agent runtime, or tooling here — only structured knowledge in a portable plain-text format.
- **Not a certification.** Nothing here constitutes compliance advice or regulatory certification.

---

## How to use it

**With an AI agent (recommended):**

1. Clone this repository.
2. Open the skill that matches your task (e.g. `skills/triaging-security-alerts-in-splunk/SKILL.md`).
3. Load the skill's full content as your system prompt or agent context.
4. Provide your input (alert, log excerpt, ticket, etc.) as the user message.
5. The agent follows the Procedure section and produces output in the format described in the skill.

See the [quickstart](quickstart/README.md) for a fully worked example you can run in about ten minutes.

**Browsing the library:**

`index.json` at the repo root lists all 40 skills with their subdomain and summary — useful for programmatic selection.

---

## Skill format

Skills follow a documented schema: see [SKILL_SPEC.md](SKILL_SPEC.md).

The format is intentionally portable — any agent runtime that can accept a system prompt can use these skills.

---

## Provenance

This library is built on an open Apache-2.0 upstream base
([Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills)),
extended with curation, quality review, subdomain classification, and additional materials.
The work contributed here — selection, editing, and supplementary content — is released
under the same Apache-2.0 license. See [NOTICE](NOTICE) for full upstream attribution.

---

## The full methodology

The 40 skills here are drawn from a larger operating model that includes:

- A five-level maturity model (L1 reference → L5 closed-loop)
- 750+ vetted skills across 27 security domains
- Framework crosswalks: NIST AI RMF, NIST CSF 2.0, EU AI Act, ISO/IEC 42001, SEC rules
- Governance and audit artifacts for board-level reporting

Learn more or book a maturity assessment at **[aisecurityskills.com](https://www.aisecurityskills.com)**.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
