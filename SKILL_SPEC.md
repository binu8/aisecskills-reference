# Skill Schema Reference

Every skill in this library is a single `SKILL.md` file in its own directory. The file has two parts: a YAML frontmatter block and a Markdown body.

---

## Frontmatter fields

```yaml
---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: <string>          # Unique kebab-case identifier. Matches the directory name.
name: <string>        # Human-readable display name (usually the same as id).
version: "<semver>"   # Semantic version string, quoted.
subdomain: <string>   # Security function this skill belongs to (see list below).
summary: >-           # One-paragraph description written as "when would you use this?"
  <text>              # Used by agents for skill selection. Min 50 chars.
references:           # Lightweight tags: technologies, tactics, concepts.
  - <tag>             # No framework mapping tables. Tags only.
---
```

**Required fields:** `id`, `name`, `version`, `subdomain`, `summary`

**`references`** carries only surface-level tags (tool names, tactic names, concept keywords). It does **not** contain framework mapping tables such as ATT&CK technique IDs, NIST CSF controls, or D3FEND techniques. Those appear in the full library only.

### Allowed subdomains

`soc-operations`, `incident-response`, `threat-intelligence`, `threat-detection`,
`vulnerability-management`, `identity-access-management`, `cloud-security`,
`compliance-governance`, `network-security`, `digital-forensics`, `malware-analysis`,
`endpoint-security`, `devsecops`, `threat-hunting`, `red-teaming`, `penetration-testing`,
`web-application-security`, `api-security`, `container-security`, `cryptography`,
`mobile-security`, `ransomware-defense`, `supply-chain-security`, `wireless-security`,
`ot-ics-security`, `zero-trust-architecture`, `ai-security`, `data-protection`

---

## Body sections

Sections appear in this order. All are optional except **When to Use** and **Procedure**.

### `## When to Use`

Bullet list of conditions under which an analyst or agent should load this skill. Written as: "Use this skill when…" Include an explicit **Do not use** clause where helpful.

### `## Inputs`

What the skill expects as input: alert objects, log samples, ticket fields, file paths, etc. Omit if not applicable.

### `## Procedure`

Numbered steps the analyst or agent follows. Steps should be concrete: include commands, queries, or templates where the technique has a canonical form. Steps should be executable without ambiguity.

### `## Outputs`

What a correctly completed skill execution produces: the artifact, report section, ticket update, or decision record. Omit if not applicable.

### `## Quality Checks`

Checklist, criteria, or verification commands confirming the procedure was executed correctly. Format as a checklist (`- [ ] …`) where possible.

---

## Worked example

```
skills/
└── triaging-security-alerts-in-splunk/
    └── SKILL.md
```

```yaml
---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: triaging-security-alerts-in-splunk
name: triaging-security-alerts-in-splunk
version: "1.0"
subdomain: soc-operations
summary: >-
  Triages security alerts in Splunk Enterprise Security by classifying severity,
  investigating notable events, correlating related telemetry, and making escalation
  or closure decisions using SPL queries and the Incident Review dashboard. Use when
  SOC analysts face queued alerts that require prioritisation and documented disposition.
references:
  - soc
  - splunk
  - alert-triage
  - siem
  - incident-review
---

## When to Use

Use this skill when:
- SOC Tier 1 analysts need to process the Incident Review queue in Splunk ES
- Notable events require rapid severity classification before escalation
- Alert volume requires a systematic, documented triage methodology

**Do not use** for deep forensic investigation — escalate to Tier 2/3 after
initial triage confirms malicious activity.

## Procedure

### Step 1: Prioritise the queue

Sort the Incident Review dashboard by urgency (Critical → High → Medium).
Group related alerts by `src` or `dest` to detect attack chains.

### Step 2: Investigate the notable event

Pivot from the notable event to raw telemetry. Cross-reference the source
against asset, identity, and threat-intelligence lookups.

### Step 3: Classify and disposition

| Disposition | Criteria | Action |
|---|---|---|
| True Positive | Corroborating evidence confirms malicious activity | Escalate, create ticket |
| Benign True Positive | Alert fired correctly but activity is authorised | Close, add suppression |
| False Positive | Alert logic matched benign behaviour | Close, tune rule |
| Undetermined | Insufficient data | Assign to Tier 2 |

### Step 4: Document findings

Record in the notable event comment: source/destination, data sources checked,
correlation findings, disposition rationale, next steps.

## Outputs

A triage report covering: alert identity, investigated endpoints, evidence examined,
disposition decision, and any escalation ticket reference.

## Quality Checks

- [ ] All corroborating data sources were checked (not just the triggering source)
- [ ] Disposition label applied to notable event in Incident Review
- [ ] Comment recorded with rationale sufficient for Tier 2 handoff
- [ ] Recurring false-positive pattern documented for rule tuning
```
