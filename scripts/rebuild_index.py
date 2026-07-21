#!/usr/bin/env python3
"""Rebuild index.json (and optionally README.md / PILLARS.md) from skills/*/SKILL.md.

Every field is taken from frontmatter on disk — nothing is invented. Skills that
fail required-field checks are reported and omitted from the written index
(exit code 1); fix the frontmatter and re-run.

Stdlib + optional PyYAML (preferred for `>-` folded summaries). Run from repo root:

    python3 scripts/rebuild_index.py           # index.json only
    python3 scripts/rebuild_index.py --docs    # also rewrite README.md + PILLARS.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
INDEX = REPO / "index.json"
README = REPO / "README.md"
PILLARS_MD = REPO / "PILLARS.md"

SCHEMA_VERSION = "2.1"
LICENSE = "Apache-2.0"
NOTE = (
    "aicm_controls and ssrm_ownership are proposed mappings — verify against "
    "AICM v1.0.3 before formal self-assessments."
)

AICM_DOMAIN_NAMES: dict[str, str] = {
    "A&A": "Audit & Assurance",
    "AIS": "Application & Interface Security",
    "BCR": "Business Continuity Management and Operational Resilience",
    "CCC": "Change Control and Configuration Management",
    "CEK": "Cryptography, Encryption & Key Management",
    "DCS": "Datacenter Security",
    "DSP": "Data Security and Privacy Lifecycle Management",
    "GRC": "Governance, Risk and Compliance",
    "HRS": "Human Resources",
    "IAM": "Identity & Access Management",
    "IPY": "Interoperability & Portability",
    "I&S": "Infrastructure Security",
    "LOG": "Logging and Monitoring",
    "MDS": "Model Security",
    "SEF": "Security Incident Management, E-Discovery, & Cloud Forensics",
    "STA": "Supply Chain Management, Transparency, and Accountability",
    "TVM": "Threat & Vulnerability Management",
    "UEM": "Universal Endpoint Management",
}

PILLAR_META = [
    ("security_for_ai", "Security for AI", "Protecting AI systems throughout their lifecycle"),
    ("ai_for_security", "AI for Security", "Deploying AI as a security capability"),
    ("security_from_ai", "Security from AI", "Managing AI-specific risks and harms"),
]

REQUIRED = [
    "id",
    "name",
    "version",
    "domain",
    "aicm_controls",
    "ssrm_ownership",
    "aismm_category",
    "aismm_target_level",
    "summary",
]


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        raise ValueError("missing frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("unclosed frontmatter")
    block = text[3:end]
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(block) or {}
        if not isinstance(data, dict):
            raise ValueError("frontmatter is not a mapping")
        return data
    except ImportError:
        return _parse_frontmatter_stdlib(block)


def _parse_frontmatter_stdlib(block: str) -> dict:
    """Best-effort scalar/list/`>-` parser when PyYAML is unavailable."""
    data: dict = {}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in " \t":
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2).strip()
        if rest in (">-", ">", "|", "|-"):
            parts: list[str] = []
            i += 1
            while i < len(lines) and (
                lines[i].startswith("  ")
                or lines[i].startswith("\t")
                or lines[i].strip() == ""
            ):
                if lines[i].strip():
                    parts.append(lines[i].strip())
                i += 1
            data[key] = " ".join(parts)
            continue
        if rest == "":
            items: list[str] = []
            i += 1
            while i < len(lines) and re.match(r"^\s+-\s+", lines[i]):
                items.append(
                    re.sub(r"^\s+-\s+", "", lines[i]).strip().strip('"').strip("'")
                )
                i += 1
            data[key] = items
            continue
        val = rest.strip('"').strip("'")
        if key == "aismm_target_level" and re.fullmatch(r"[1-5]", val):
            data[key] = int(val)
        else:
            data[key] = val
        i += 1
    return data


def audit_skills() -> tuple[list[dict], list[str]]:
    """Return (valid index entries, validation failure messages)."""
    failures: list[str] = []
    entries: list[dict] = []

    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    if not skill_files:
        failures.append(f"no SKILL.md files under {SKILLS_DIR}")
        return [], failures

    for path in skill_files:
        slug = path.parent.name
        try:
            fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 — report parse errors as failures
            failures.append(f"{slug}: frontmatter parse error: {exc}")
            continue

        sid = fm.get("id")
        if sid != slug:
            failures.append(f"{slug}: id {sid!r} != directory name")
        missing = [f for f in REQUIRED if f not in fm or fm[f] in (None, "", [])]
        if missing:
            failures.append(f"{slug}: missing required field(s): {missing}")
            continue
        if not isinstance(fm["aicm_controls"], list) or not fm["aicm_controls"]:
            failures.append(f"{slug}: aicm_controls must be a non-empty list")
            continue
        if not isinstance(fm["summary"], str) or len(fm["summary"].strip()) < 50:
            failures.append(f"{slug}: summary must be a string ≥ 50 chars")
            continue
        level = fm["aismm_target_level"]
        if isinstance(level, str) and level.isdigit():
            level = int(level)
        if level not in (1, 2, 3, 4, 5):
            failures.append(f"{slug}: aismm_target_level must be 1–5, got {level!r}")
            continue

        entry = {
            "id": sid,
            "name": fm["name"],
            "version": str(fm["version"]),
            "domain": fm["domain"],
            "aicm_controls": list(fm["aicm_controls"]),
            "ssrm_ownership": fm["ssrm_ownership"],
            "aismm_category": fm["aismm_category"],
            "aismm_target_level": level,
            "summary": fm["summary"].strip(),
        }
        if "pillar" in fm and fm["pillar"] not in (None, ""):
            entry["pillar"] = fm["pillar"]
        entries.append(entry)

    entries.sort(key=lambda e: e["id"])
    return entries, failures


def write_index(entries: list[dict]) -> None:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "skill_count": len(entries),
        "license": LICENSE,
        "note": NOTE,
        "skills": entries,
    }
    INDEX.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _domain_table(entries: list[dict]) -> str:
    counts = Counter(e["domain"] for e in entries)
    # Sort by count desc, then domain id — derived, not hand-ordered for “importance”.
    rows = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    lines = ["| AICM domain | ID | Skills |", "|---|---|---|"]
    for dom, n in rows:
        name = AICM_DOMAIN_NAMES.get(dom, dom)
        lines.append(f"| {name} | {dom} | {n} |")
    return "\n".join(lines)


def _pillar_table(entries: list[dict]) -> str:
    counts = Counter(e.get("pillar") for e in entries)
    lines = ["| Pillar | Focus | Skills |", "|---|---|---|"]
    for key, label, focus in PILLAR_META:
        lines.append(f"| **{label}** | {focus} | {counts.get(key, 0)} |")
    unknown = sum(v for k, v in counts.items() if k not in {p[0] for p in PILLAR_META})
    if unknown:
        lines.append(f"| _(unassigned / other)_ | | {unknown} |")
    return "\n".join(lines)


def write_readme(entries: list[dict]) -> None:
    n = len(entries)
    domain_n = len({e["domain"] for e in entries})
    text = f"""# ai · security · skills — reference library v2

An open sample of a structured AI security skill library, aligned to the CSA AI assurance stack: **AICM v1.0.3** (18 control domains), the **AI-CAIQ v1.0.2** self-assessment instrument, and the **AISMM** (5-level Initial→Efficient maturity scale).

→ **[Quickstart in ~10 minutes](quickstart/README.md)**

---

## What this is

Each skill is a `SKILL.md` file: a structured document that tells an AI agent *exactly* how to perform a specific AI security task. An agent loads the skill as context, receives the practitioner's input, and executes the procedure.

This repository contains **{n} AI-native skills** (count derived from `skills/*/SKILL.md` via `scripts/rebuild_index.py`). Skills are grouped under the three pillars defined in [SKILL_SPEC.md](SKILL_SPEC.md) / [PILLARS.md](PILLARS.md), and each skill also maps to exactly one of the {domain_n} AICM control domains present in this sample:

### By pillar

{_pillar_table(entries)}

See [PILLARS.md](PILLARS.md) for the full per-skill lists.

### By AICM domain

{_domain_table(entries)}

Skills are licensed **Apache 2.0**.

---

## What this is NOT

- **Not the full library.** The full working library is substantially larger, with framework crosswalks, the MECE AICM partition, AISMM scoring, and a governance layer. This repository is a representative sample ({n} skills on disk).
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

`index.json` lists all {n} skills with their AICM domain, controls, SSRM role, AISMM category, target level, pillar, and summary — useful for programmatic selection. Regenerate it with `python3 scripts/rebuild_index.py` after adding or editing skills.

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
"""
    README.write_text(text, encoding="utf-8")


def write_pillars(entries: list[dict]) -> None:
    by_pillar: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        by_pillar[e.get("pillar") or "_none"].append(e)

    counts = {k: len(v) for k, v in by_pillar.items()}
    lines = [
        "# The three pillars",
        "",
        "Every skill in this library is grouped under one of three pillars. The `pillar` field in each skill's frontmatter and in `index.json` carries this grouping. Counts and lists below are regenerated from `skills/*/SKILL.md` (`python3 scripts/rebuild_index.py --docs`).",
        "",
        "| Pillar | Focus | Skills |",
        "|---|---|---|",
    ]
    for key, label, focus in PILLAR_META:
        lines.append(f"| **{label}** | {focus} | {counts.get(key, 0)} |")
    lines.append("")

    for key, label, focus in PILLAR_META:
        lines.append(f"## {label}")
        lines.append("")
        lines.append(f"*{focus}.*")
        lines.append("")
        if key == "ai_for_security" and counts.get(key, 0) <= 1:
            lines.append(
                "This pillar was the current authoring gap: using AI itself as a security capability "
                "(AI-assisted detection, triage, and response) is thinly covered by existing standards. "
                "It remains the priority area to build."
            )
            lines.append("")
        for e in sorted(by_pillar.get(key, []), key=lambda x: x["id"]):
            summ = e["summary"].rstrip(".")
            lines.append(f"- **`{e['id']}`** ({e['domain']}) — {summ}.")
        lines.append("")

    other = by_pillar.get("_none", [])
    if other:
        lines.append("## Unassigned pillar")
        lines.append("")
        for e in sorted(other, key=lambda x: x["id"]):
            lines.append(f"- **`{e['id']}`** ({e['domain']}) — {e['summary']}")
        lines.append("")

    PILLARS_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs",
        action="store_true",
        help="Also regenerate README.md and PILLARS.md from the audit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Audit and print counts; do not write files",
    )
    args = parser.parse_args()

    if not SKILLS_DIR.is_dir():
        print(f"✗ skills/ not found at {SKILLS_DIR}", file=sys.stderr)
        return 1

    entries, failures = audit_skills()
    disk_n = len(list(SKILLS_DIR.glob("*/SKILL.md")))

    print(f"Disk SKILL.md files: {disk_n}")
    print(f"Valid index entries: {len(entries)}")
    if failures:
        print(f"Validation failures: {len(failures)}", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)

    if args.dry_run:
        print(_pillar_table(entries))
        print(_domain_table(entries))
        return 1 if failures else 0

    if failures and len(entries) < disk_n:
        # Still write index for valid skills, but fail the run so CI/humans notice.
        write_index(entries)
        if args.docs:
            write_readme(entries)
            write_pillars(entries)
        print(
            f"Wrote index for {len(entries)} valid skills but "
            f"{disk_n - len(entries)} skill(s) failed validation.",
            file=sys.stderr,
        )
        return 1

    write_index(entries)
    print(f"Wrote {INDEX.relative_to(REPO)} ({len(entries)} skills)")
    if args.docs:
        write_readme(entries)
        write_pillars(entries)
        print(f"Wrote {README.relative_to(REPO)} and {PILLARS_MD.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
