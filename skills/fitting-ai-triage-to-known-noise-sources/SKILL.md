---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: fitting-ai-triage-to-known-noise-sources
name: fitting-ai-triage-to-known-noise-sources
version: "1.0"
domain: LOG
aicm_controls:
  - LOG-05
  - GRC-04
ssrm_ownership: AP-Owned
aismm_category: Security Monitoring
aismm_target_level: 4
pillar: ai_for_security
summary: >-
  Use this skill when an AI-assisted alert triage system is flagging too
  many known-benign patterns as incidents, and you need to fit its decision
  policy to your organization's specific noise sources — vulnerability
  scanners, backup service accounts, VPN egress ranges, approved tooling —
  without suppressing genuine true positives.
references:
  - SOC
  - alert triage
  - false-positive suppression
  - SIEM
---

## When to Use

- Use this skill when an AI-assisted triage layer (or a human analyst using an LLM copilot) has an unacceptably high false-positive escalation rate.
- Use this skill when you can name the recurring benign sources responsible for the noise (a vulnerability scanner's IP range, a backup job's service accounts, a VPN concentrator's egress range, an approved IT tool's file hash, a change-ticket system's reference format).
- **Do not use** this skill to suppress alert classes you cannot name and justify. Suppression rules must be traceable to a specific, documented noise source — never a blanket "alerts of this type are usually fine."

## Inputs

- A sample of recent alerts with analyst-confirmed labels (true positive / false positive), ideally 20+ per alert type.
- A list of the org's known noise sources: CIDR ranges (scanners, VPN egress), account naming conventions (service accounts), approved tool signatures (file hashes), and any reference-number conventions (change tickets) that legitimately explain an alert.

## Procedure

1. **Group the false positives by cause.** For each alert type with a high FP rate, cluster the false positives by *why* a human analyst dismissed them. Most SOC noise collapses into a small number of named causes (5-10, not hundreds).
2. **Name each cause as a checkable predicate.** Write each cause as something a program (or an LLM given the right context) can check: "source IP is in 10.50.0.0/24" (the scanner range), "account matches `^svc-backup-\d+$`" (the backup naming pattern), "file hash equals the approved tool's known hash." Vague causes ("looks automated") do not become predicates — go back to step 1 and split further.
3. **Encode the predicates as the AI's decision policy.** Whether the triage system is a rule engine or an LLM prompt, supply these predicates as explicit context: "Suppress an alert only if it matches one of these named conditions; otherwise escalate." An LLM given this context can apply it to variations it hasn't seen (a new backup account matching the same naming pattern), which is the whole point of fitting over hardcoding a literal list.
4. **Validate on a held-out set before trusting it.** Split your labelled sample: fit the predicates using one part, then measure the false-positive suppression rate and the true-positive catch rate on alerts the fitting process never saw. The true-positive catch rate must stay at (or very near) 100% — a suppression policy that starts dropping real attacks is a regression, not an improvement, no matter how much it cuts noise.
5. **Re-measure after each policy change.** Every time a new noise source is added to the predicate list, re-run the held-out validation. Predicate lists drift; validation catches when a "known noise source" predicate has grown broad enough to start swallowing genuine incidents.

## Outputs

- A named, documented list of suppression predicates (the fitted decision policy), each traceable to a specific noise source.
- A before/after measurement: false-positive rate and true-positive catch rate on both the fitting sample and a held-out sample.

## Quality Checks

- [ ] Every suppression predicate is traceable to a specific, named noise source (not a vague pattern).
- [ ] True-positive catch rate on the held-out sample is at or near 100% — suppression never traded away a real detection.
- [ ] The false-positive rate measurably dropped from baseline (no context awareness) to fitted (predicates applied), on both the fitting sample and the held-out sample.
- [ ] The policy is re-validated whenever a new suppression predicate is added.

AI-CAIQ evidence: a completed fitting + held-out validation cycle is evidence for LOG-05 (alert/event correlation tuning) in an AI-CAIQ self-assessment.
