---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: implementing-content-safety-output-filtering
name: implementing-content-safety-output-filtering
version: "1.0"
domain: AIS
aicm_controls:
  - AIS-08
  - MDS-07
ssrm_ownership: AP-Owned
aismm_category: App Security
aismm_target_level: 4
pillar: security_from_ai
nist_ai_rmf:
  - MEASURE-2.6
  - MEASURE-2.7
summary: >-
  Use this skill when a generative AI application exposes free-form output to
  end users and you need to filter that output through a content-safety
  classifier before it reaches them — blocking hate, harassment, sexual,
  violence, self-harm, or illegal content per a published policy, with the
  same policy enforced regardless of which model produced the output.
references:
  - content-safety
  - output-filter
  - llama-guard
  - nist-ai-rmf
  - eu-ai-act
---

## When to Use

Use this skill when:
- A generative app sends free-form text, image, or video to end users (chat, summarization, content generation).
- The organization has a content policy and needs demonstrable enforcement on model outputs.
- AICM AIS/MDS controls require output-safety evidence, or EU AI Act Article 5 prohibitions apply.

**Do not use** this skill as the only safety layer — combine it with input-side guardrails (`defending-against-prompt-injection`), pre-deployment eval gates, and runtime drift monitoring; and do not deploy it on internal-only scratchpads with no end-user exposure.

## Inputs

- A hosting plane that can interpose between the model and the response (proxy, gateway, or middleware).
- A published content policy mapping each category (hate, harassment, sexual, violence, self-harm, illegal, child-exposure, PII-leak) to allow / warn / block thresholds.
- At least one classifier: an open-weights model (e.g. Llama Guard) or a managed service (e.g. Azure AI Content Safety, Google Model Armor).
- A logging sink (SIEM) so blocked outputs are auditable.

## Procedure

### Step 1: Author the policy

Tabulate each output category with its allowed contexts, warn threshold, and hard-block threshold. Keep the table version-controlled and reviewed by policy and legal.

### Step 2: Wire the classifier onto the response path

Place the classifier as an interceptor between the model and the user. Score every output before it is relayed.

### Step 3: Apply the policy decision tree

- Score at or above the block threshold → return the policy refusal template; do **not** relay the model's raw output.
- Score in the warn band → relay the output with a content advisory and log the score.
- Score below the warn band → relay the output; sample a fraction for audit logs.

### Step 4: Emit telemetry

Every classification event → SIEM with `{userId_hash, model, category, score, decision, requestId}`. Build dashboards aggregated by category and by model so a single model regressing is visible.

### Step 5: Fail closed on classifier outage

If the classifier is unavailable, fall back to a stricter policy (return the refusal template) rather than relaying unscored output.

### Step 6: Recalibrate quarterly

Measure the false-positive rate per category against a held-out set and adjust thresholds with policy and legal in the loop.

## Outputs

- A version-controlled content policy with per-category allow/warn/block thresholds.
- A response-path interceptor that scores and gates every model output.
- A SIEM stream of classification events plus per-category and per-model dashboards.
- A quarterly calibration report with per-category false-positive and false-negative rates.

## Quality Checks

- [ ] A prompt that elicits a known-unsafe output is blocked end-to-end (response is the refusal template; a log event lands in the SIEM).
- [ ] A benign output passes through unmodified.
- [ ] A simulated classifier outage triggers fail-closed within a bounded time (stricter policy active).
- [ ] Every relayed output above the warn band carries a content advisory and a logged score.
- [ ] A quarterly calibration report exists with per-category FP/FN rates.

**AI-CAIQ evidence:** This skill supports a YES response to AIS-08 by producing a published output-safety policy, an interceptor that enforces it on every response, and audit logs demonstrating that unsafe model outputs are blocked before reaching users.
