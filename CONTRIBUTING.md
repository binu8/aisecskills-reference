# Contributing

Contributions are welcome — new skills, corrections to existing ones, and improvements to the schema documentation.

## Proposing a new skill

1. Fork this repository.
2. Create a directory under `skills/` named with a kebab-case identifier (e.g. `skills/detecting-dns-tunneling/`).
3. Add a `SKILL.md` following the schema in [SKILL_SPEC.md](SKILL_SPEC.md).
4. Open a pull request with a short description of what the skill covers and why it belongs in this library.

### What makes a good skill

- **Specific.** One task, not a category. "Triage a brute-force alert in Splunk" is a skill; "SIEM operations" is not.
- **Executable.** The Procedure section should be runnable without ambiguity. Include commands, queries, or templates where the technique has a canonical form.
- **Honest scope.** The When to Use section should include an explicit "Do not use for…" clause.
- **Tool-aware but not tool-locked.** Name the tool where the procedure is tool-specific; note alternatives where they exist.

### What doesn't belong

- Marketing copy or vendor promotion
- Procedures that require proprietary data or closed systems with no open-source equivalent
- Duplicate coverage of an existing skill without a meaningful differentiation

## Licence terms

By submitting a contribution you agree to license it under Apache 2.0, consistent with the rest of this repository.

## Schema

All skills must pass schema validation. The required fields are: `id`, `name`, `version`, `subdomain`, `summary`. The required body section is `## Procedure`. See [SKILL_SPEC.md](SKILL_SPEC.md) for the full specification.
