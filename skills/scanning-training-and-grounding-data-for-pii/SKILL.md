---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: scanning-training-and-grounding-data-for-pii
name: scanning-training-and-grounding-data-for-pii
version: "1.0"
domain: DSP
aicm_controls:
  - DSP-10
  - DSP-13
ssrm_ownership: Shared AP-AIC
aismm_category: Data Security
aismm_target_level: 3
pillar: security_for_ai
summary: >-
  Use this skill when you need to detect, classify, and remediate personally
  identifiable information in datasets before they are used to train,
  fine-tune, or ground an AI model.
references:
  - PII
  - Presidio
  - GDPR
  - CCPA
  - data-masking
  - spaCy
---

## When to Use

Use this skill when:
- A training corpus or RAG document store was assembled from raw web scrapes, customer data, or support tickets that may contain PII.
- A privacy review or GDPR/CCPA compliance requirement demands evidence that personal data was removed before model training.
- An AI model's outputs suggest it memorized names, email addresses, or financial data from training data.
- You are building a data-preparation pipeline and need automated PII gating before data reaches the model.

**Do not use** this skill as the sole privacy control — it does not replace consent management, data retention policies, or legal basis review.

## Inputs

- Dataset files (JSONL, CSV, plain text, Parquet) or an object-store URI.
- A list of PII categories to target (e.g., SSN, email, credit card, health identifiers).
- Desired remediation strategy: redact, replace with synthetic, or quarantine.

## Procedure

### Step 1: Install and configure Microsoft Presidio

```bash
pip install presidio-analyzer presidio-anonymizer
python -m spacy download en_core_web_lg
```

### Step 2: Define recognizers and scan a document

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def scan_text(text: str) -> list[dict]:
    results = analyzer.analyze(
        text=text,
        entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN",
                  "CREDIT_CARD", "US_BANK_NUMBER", "IP_ADDRESS", "LOCATION"],
        language="en",
    )
    return [{"type": r.entity_type, "score": r.score, "start": r.start, "end": r.end} for r in results]

def anonymize_text(text: str, strategy: str = "replace") -> str:
    results = analyzer.analyze(text=text, language="en")
    if strategy == "redact":
        ops = {r.entity_type: OperatorConfig("redact") for r in results}
    else:
        ops = {r.entity_type: OperatorConfig("replace", {"new_value": f"<{r.entity_type}>"}) for r in results}
    return anonymizer.anonymize(text=text, analyzer_results=results, operators=ops).text
```

### Step 3: Batch scan a JSONL training file

```python
import json, csv

def scan_jsonl(input_path: str, text_field: str, output_report: str):
    findings = []
    with open(input_path) as f:
        for line_no, line in enumerate(f, 1):
            record = json.loads(line)
            text = record.get(text_field, "")
            hits = scan_text(text)
            for hit in hits:
                if hit["score"] >= 0.7:
                    findings.append({"line": line_no, **hit})
    with open(output_report, "w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=["line", "type", "score", "start", "end"])
        writer.writeheader()
        writer.writerows(findings)
    print(f"Scanned {line_no} records; {len(findings)} PII hits written to {output_report}")
```

### Step 4: Remediate — produce a clean dataset

```python
def clean_jsonl(input_path: str, output_path: str, text_field: str):
    with open(input_path) as fin, open(output_path, "w") as fout:
        for line in fin:
            record = json.loads(line)
            record[text_field] = anonymize_text(record[text_field], strategy="replace")
            fout.write(json.dumps(record) + "\n")
```

### Step 5: Validate residual PII rate

After remediation, re-scan and assert the residual rate is below your threshold:

```python
def assert_pii_rate(report_path: str, total_records: int, threshold: float = 0.001):
    with open(report_path) as f:
        count = sum(1 for _ in csv.DictReader(f))
    rate = count / total_records
    assert rate <= threshold, f"Residual PII rate {rate:.4%} exceeds threshold {threshold:.4%}"
    print(f"PII rate: {rate:.4%} — PASS")
```

### Step 6: Record compliance evidence

```bash
sha256sum cleaned-training-data.jsonl > cleaned-training-data.sha256
cat > pii-scan-evidence.json <<EOF
{
  "scan_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "input_file": "training-data.jsonl",
  "output_file": "cleaned-training-data.jsonl",
  "tool": "presidio 2.x",
  "pii_hits_before": $(wc -l < pii-report.csv),
  "residual_rate_threshold": 0.001,
  "pass": true
}
EOF
```

## Outputs

- PII scan report (CSV) with line number, entity type, confidence score, and character offsets.
- Cleaned dataset file with PII replaced or redacted.
- SHA-256 checksum of the cleaned file.
- `pii-scan-evidence.json` recording scan tool, date, hit counts, and pass/fail status.

## Quality Checks

- [ ] Scan covers all targeted PII entity types at confidence threshold ≥ 0.7.
- [ ] Cleaned dataset SHA-256 matches the recorded checksum.
- [ ] Residual PII rate after remediation is below the accepted threshold (e.g., 0.1%).
- [ ] Scan evidence JSON is stored with the dataset version and referenced in the lineage manifest.
- [ ] At least one synthetic PII injection test confirms the scanner detects known entities.

**AI-CAIQ evidence:** This skill supports YES response to DSP-10 by producing a PII scan report, a cleaned dataset, and a signed evidence JSON artifact that demonstrates personal data was detected and remediated before the data was used in model training or grounding.
