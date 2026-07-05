#!/usr/bin/env python3
"""Validate the reference skill library.

Checks index.json against the SKILL.md files on disk and enforces the v2.1
schema, with a specific gate on the `pillar` field: every skill's pillar (in
both index.json and its SKILL.md frontmatter) must be one of the three allowed
values, and the two must agree.

Stdlib only. Run from the repo root:

    python3 scripts/validate.py

Exit code 0 = all checks pass; 1 = one or more violations.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "index.json"
SKILLS_DIR = REPO / "skills"

SCHEMA_VERSION = "2.1"

# The 18 AICM v1.0.3 control domains (SKILL_SPEC.md).
AICM_DOMAINS = {
    "A&A", "AIS", "BCR", "CCC", "CEK", "DCS", "DSP", "GRC", "HRS",
    "IAM", "IPY", "I&S", "LOG", "MDS", "SEF", "STA", "TVM", "UEM",
}

SSRM_OWNERSHIP = {
    "CSP-Owned", "MP-Owned", "OSP-Owned", "AP-Owned", "AIC-Owned",
    "Shared CSP-MP", "Shared MP-OSP", "Shared OSP-AP", "Shared AP-AIC",
    "Shared Across Supply Chain", "ND",
}

AISMM_CATEGORIES = {
    "Governance", "Organization Management", "IAM", "Security Monitoring",
    "Infrastructure Security & Resilience", "Model Security", "App Security",
    "Data Security", "Risk & Provider Assessment & Management",
    "AI Supported Development & Supply Chain Security",
    "Privacy, Compliance and Audit", "Incident Response",
}

PILLARS = {"security_for_ai", "ai_for_security", "security_from_ai"}

REQUIRED_INDEX_FIELDS = [
    "id", "name", "version", "domain", "aicm_controls",
    "ssrm_ownership", "aismm_category", "aismm_target_level", "summary",
]

REQUIRED_BODY_SECTIONS = ["## When to Use", "## Procedure"]

SUMMARY_MIN_CHARS = 50


def parse_frontmatter_scalars(text: str) -> dict[str, str]:
    """Extract top-level `key: value` scalar fields from a SKILL.md frontmatter
    block. Deliberately minimal (stdlib only): it reads the scalar keys the
    validator cross-checks (id, name, domain, pillar, version). List and
    block-scalar fields are ignored — those are checked via index.json."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    fields: dict[str, str] = {}
    for line in block.splitlines():
        # Only top-level keys (no indentation), skip comments and list items.
        if not line or line[0] in " #-":
            continue
        m = re.match(r"^([A-Za-z0-9_]+):[ \t]*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        # Drop surrounding quotes and skip block-scalar / empty markers.
        if val in (">-", "|", "|-", ">", ""):
            continue
        val = val.strip('"').strip("'")
        fields[key] = val
    return fields


def validate() -> list[str]:
    errors: list[str] = []

    if not INDEX.exists():
        return [f"index.json not found at {INDEX}"]

    data = json.loads(INDEX.read_text())

    if str(data.get("schema_version")) != SCHEMA_VERSION:
        errors.append(
            f"index.json schema_version is {data.get('schema_version')!r}, "
            f"expected {SCHEMA_VERSION}"
        )

    skills = data.get("skills", [])

    if data.get("skill_count") != len(skills):
        errors.append(
            f"skill_count ({data.get('skill_count')}) != number of skills "
            f"in the array ({len(skills)})"
        )

    seen_ids: set[str] = set()
    index_ids: set[str] = set()

    for entry in skills:
        sid = entry.get("id", "<missing id>")
        index_ids.add(sid)

        if sid in seen_ids:
            errors.append(f"{sid}: duplicate id in index.json")
        seen_ids.add(sid)

        for field in REQUIRED_INDEX_FIELDS:
            if field not in entry or entry[field] in (None, "", []):
                errors.append(f"{sid}: missing required field '{field}'")

        domain = entry.get("domain")
        if domain is not None and domain not in AICM_DOMAINS:
            errors.append(f"{sid}: domain '{domain}' is not a valid AICM domain")

        own = entry.get("ssrm_ownership")
        if own is not None and own not in SSRM_OWNERSHIP:
            errors.append(f"{sid}: ssrm_ownership '{own}' is not an allowed value")

        cat = entry.get("aismm_category")
        if cat is not None and cat not in AISMM_CATEGORIES:
            errors.append(f"{sid}: aismm_category '{cat}' is not an allowed value")

        lvl = entry.get("aismm_target_level")
        if lvl is not None and lvl not in (1, 2, 3, 4, 5):
            errors.append(f"{sid}: aismm_target_level '{lvl}' must be 1-5")

        ctrls = entry.get("aicm_controls")
        if not isinstance(ctrls, list) or not ctrls:
            errors.append(f"{sid}: aicm_controls must be a non-empty list")

        summary = entry.get("summary", "")
        if isinstance(summary, str) and len(summary) < SUMMARY_MIN_CHARS:
            errors.append(
                f"{sid}: summary is {len(summary)} chars, "
                f"minimum {SUMMARY_MIN_CHARS}"
            )

        # --- the pillar gate ---
        pillar = entry.get("pillar")
        if pillar is not None and pillar not in PILLARS:
            errors.append(
                f"{sid}: pillar '{pillar}' is not one of "
                f"{sorted(PILLARS)}"
            )

    # Directory <-> index reconciliation + per-file SKILL.md checks.
    if not SKILLS_DIR.exists():
        errors.append(f"skills/ directory not found at {SKILLS_DIR}")
        return errors

    dir_ids = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}

    for missing in sorted(index_ids - dir_ids):
        errors.append(f"{missing}: in index.json but no skills/{missing}/ directory")
    for extra in sorted(dir_ids - index_ids):
        errors.append(f"{extra}: skills/{extra}/ directory but not in index.json")

    index_by_id = {e.get("id"): e for e in skills}

    for sid in sorted(index_ids & dir_ids):
        skill_md = SKILLS_DIR / sid / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"{sid}: skills/{sid}/SKILL.md not found")
            continue

        text = skill_md.read_text()
        fm = parse_frontmatter_scalars(text)
        entry = index_by_id[sid]

        if fm.get("id") != sid:
            errors.append(
                f"{sid}: SKILL.md frontmatter id '{fm.get('id')}' "
                f"!= directory name"
            )

        fm_domain = fm.get("domain")
        if fm_domain is not None and fm_domain != entry.get("domain"):
            errors.append(
                f"{sid}: SKILL.md domain '{fm_domain}' != index.json "
                f"domain '{entry.get('domain')}'"
            )

        # pillar gate: frontmatter and index must agree.
        fm_pillar = fm.get("pillar")
        idx_pillar = entry.get("pillar")
        if fm_pillar is not None and fm_pillar not in PILLARS:
            errors.append(
                f"{sid}: SKILL.md pillar '{fm_pillar}' is not one of "
                f"{sorted(PILLARS)}"
            )
        if fm_pillar != idx_pillar:
            errors.append(
                f"{sid}: SKILL.md pillar '{fm_pillar}' != index.json "
                f"pillar '{idx_pillar}'"
            )

        body = text[text.find("\n---", 3) + 4:] if text.startswith("---") else text
        for section in REQUIRED_BODY_SECTIONS:
            if section not in body:
                errors.append(f"{sid}: SKILL.md missing required section '{section}'")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print(f"✗ validate: {len(errors)} violation(s)\n", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    data = json.loads(INDEX.read_text())
    print(
        f"✓ validate: {data.get('skill_count')} skills, schema v"
        f"{data.get('schema_version')}, pillar gate clean."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
