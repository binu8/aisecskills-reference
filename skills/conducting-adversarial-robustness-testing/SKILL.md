---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: conducting-adversarial-robustness-testing
name: conducting-adversarial-robustness-testing
version: "1.0"
domain: MDS
aicm_controls:
  - MDS-05
ssrm_ownership: MP-Owned
aismm_category: Model Security
aismm_target_level: 4
pillar: security_for_ai
summary: >-
  Use this skill when you need to systematically measure how an AI model
  responds to adversarial inputs — perturbations, out-of-distribution samples,
  and evasion attacks — before production deployment.
references:
  - ART
  - adversarial-examples
  - robustness
  - Foolbox
  - TextAttack
  - model-evaluation
---

## When to Use

Use this skill when:
- You are releasing a model that will process untrusted input (public API, chatbot, autonomous agent).
- A red-team engagement requires quantified robustness metrics.
- You need to satisfy an AI risk assessment that asks for evidence of adversarial testing.
- A model update changes the underlying architecture or fine-tuning data and must be re-validated.

**Do not use** this skill as a substitute for prompt-injection testing of LLM applications (see `defending-against-prompt-injection`); this skill focuses on model-level robustness, not application-level guard bypasses.

## Inputs

- Model artifact or API endpoint.
- Evaluation dataset (labeled test samples).
- Threat model specifying the adversary type: white-box, black-box, transfer attack.

## Procedure

### Step 1: Establish a clean-accuracy baseline

```python
from datasets import load_dataset
from transformers import pipeline

clf = pipeline("text-classification", model="./my-model")
dataset = load_dataset("glue", "sst2", split="validation")

correct = sum(
    1 for ex in dataset
    if clf(ex["sentence"])[0]["label"].lower() == ("positive" if ex["label"] == 1 else "negative")
)
baseline_accuracy = correct / len(dataset)
print(f"Clean accuracy: {baseline_accuracy:.3%}")
```

### Step 2: Run TextAttack adversarial attacks (NLP models)

```bash
pip install textattack
```

```python
import textattack
from textattack.attack_recipes import TextFoolerJin2019, BERTAttackLi2020
from textattack.models.wrappers import HuggingFaceModelWrapper
from textattack.datasets import HuggingFaceDataset

model_wrapper = HuggingFaceModelWrapper(model, tokenizer)
dataset = HuggingFaceDataset("glue", "sst2", split="validation[:200]")

attack = TextFoolerJin2019.build(model_wrapper)
results = attack.attack_dataset(dataset, indices=range(200))

n_success = sum(1 for r in results if r.__class__.__name__ == "SuccessfulAttackResult")
print(f"Attack success rate: {n_success/200:.2%}  (target: <20%)")
```

### Step 3: Run image-based attacks for vision models (ART)

```python
from art.attacks.evasion import ProjectedGradientDescentNumpy
from art.estimators.classification import PyTorchClassifier
import numpy as np

classifier = PyTorchClassifier(model=model, loss=criterion, optimizer=optimizer,
                                input_shape=(3, 224, 224), nb_classes=10)
attack = ProjectedGradientDescentNumpy(estimator=classifier, eps=0.03, eps_step=0.007, max_iter=40)

x_adv = attack.generate(x=x_test[:100])
adv_preds = np.argmax(classifier.predict(x_adv), axis=1)
rob_accuracy = np.mean(adv_preds == y_test[:100])
print(f"Robust accuracy (PGD-40): {rob_accuracy:.3%}")
```

### Step 4: Test out-of-distribution (OOD) robustness

```python
# Measure confidence calibration on OOD samples
def ood_max_softmax_score(model, ood_loader) -> list[float]:
    import torch, torch.nn.functional as F
    scores = []
    with torch.no_grad():
        for x, _ in ood_loader:
            logits = model(x)
            scores.extend(F.softmax(logits, dim=-1).max(dim=1).values.tolist())
    return scores

# A well-calibrated model should return low max-softmax scores on OOD data
ood_scores = ood_max_softmax_score(model, ood_loader)
print(f"Mean OOD confidence: {sum(ood_scores)/len(ood_scores):.3f}  (target: <0.5)")
```

### Step 5: Compile robustness report

```python
import json, datetime

report = {
    "model": "./my-model",
    "eval_date": datetime.datetime.utcnow().isoformat(),
    "clean_accuracy": baseline_accuracy,
    "textfooler_attack_success_rate": n_success / 200,
    "pgd40_robust_accuracy": rob_accuracy,
    "ood_mean_confidence": sum(ood_scores) / len(ood_scores),
    "pass": (n_success / 200 < 0.20) and (rob_accuracy > 0.50),
}
with open("robustness-report.json", "w") as f:
    json.dump(report, f, indent=2)
```

## Outputs

- `robustness-report.json` with clean accuracy, attack success rates, and robust accuracy metrics.
- Adversarial example samples (perturbed inputs that caused model failure).
- Pass/fail determination against defined thresholds.

## Quality Checks

- [ ] Baseline clean-accuracy is established before any adversarial perturbations.
- [ ] At least two distinct attack types are run (e.g., word-substitution + character-level for NLP).
- [ ] Attack success rate is below the organization's accepted threshold (commonly <20%).
- [ ] OOD confidence scores are recorded and below a calibration threshold.
- [ ] Report is stored with the model version and referenced in the model card.

**AI-CAIQ evidence:** This skill supports YES response to MDS-05 by producing a quantified robustness report with clean accuracy, adversarial attack success rates, and pass/fail determinations that demonstrate systematic adversarial testing was conducted prior to deployment.
