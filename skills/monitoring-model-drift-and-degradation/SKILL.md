---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: monitoring-model-drift-and-degradation
name: monitoring-model-drift-and-degradation
version: "1.0"
domain: MDS
aicm_controls:
  - MDS-07
  - LOG-08
ssrm_ownership: MP-Owned
aismm_category: Model Security
aismm_target_level: 4
pillar: security_for_ai
summary: >-
  Use this skill when you need to detect data drift, concept drift, or
  performance degradation in a deployed AI model through continuous
  monitoring, alerting, and automated rollback triggers.
references:
  - Evidently
  - model-monitoring
  - drift-detection
  - Prometheus
  - MLflow
  - observability
---

## When to Use

Use this skill when:
- A deployed model has been in production and you need to detect whether input distribution has shifted.
- Model accuracy KPIs are regressing but no code changes were deployed.
- A compliance requirement mandates continuous monitoring of model behavior post-deployment.
- You are designing the operations layer for a production ML system.

**Do not use** this skill for adversarial robustness testing (see `conducting-adversarial-robustness-testing`); drift monitoring covers natural distribution shift and gradual degradation, not adversarial attacks.

## Inputs

- Reference dataset (the distribution the model was trained/validated on).
- Production inference logs (inputs, outputs, optional ground-truth labels).
- Model performance metrics baseline (accuracy, F1, RMSE, etc.).

## Procedure

### Step 1: Log all inference requests and responses

```python
import json, datetime, hashlib

def log_inference(input_features: dict, prediction: any, model_version: str, log_path: str):
    record = {
        "ts": datetime.datetime.utcnow().isoformat(),
        "model_version": model_version,
        "input_hash": hashlib.sha256(json.dumps(input_features, sort_keys=True).encode()).hexdigest(),
        "input": input_features,
        "prediction": prediction,
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(record) + "\n")
```

### Step 2: Compute data drift with Evidently AI

```bash
pip install evidently
```

```python
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset

reference = pd.read_parquet("reference-dataset.parquet")
production = pd.read_parquet("production-logs-last-7d.parquet")

report = Report(metrics=[DataDriftPreset(), DataQualityPreset()])
report.run(reference_data=reference, current_data=production)
report.save_html("drift-report.html")

# Programmatic access to drift results
result = report.as_dict()
drifted_features = [
    k for k, v in result["metrics"][0]["result"]["drift_by_columns"].items()
    if v["drift_detected"]
]
print(f"Drifted features: {drifted_features}")
```

### Step 3: Monitor model performance metrics

```python
from sklearn.metrics import f1_score
import numpy as np

def compute_rolling_metrics(log_path: str, window_days: int = 7) -> dict:
    records = []
    with open(log_path) as f:
        for line in f:
            r = json.loads(line)
            if "ground_truth" in r:
                records.append(r)
    
    # Filter to window
    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=window_days)).isoformat()
    recent = [r for r in records if r["ts"] >= cutoff]
    
    if not recent:
        return {"error": "no labeled records in window"}
    
    y_true = [r["ground_truth"] for r in recent]
    y_pred = [r["prediction"] for r in recent]
    return {
        "window_days": window_days,
        "n_samples": len(recent),
        "f1": f1_score(y_true, y_pred, average="weighted"),
    }
```

### Step 4: Alert on threshold breaches

```python
# Prometheus metrics export
from prometheus_client import Gauge, start_http_server

MODEL_F1 = Gauge("model_f1_score", "Rolling 7-day F1 score", ["model_version"])
DRIFT_COUNT = Gauge("model_drift_feature_count", "Number of drifted features")

def update_metrics(model_version: str, f1: float, drift_count: int):
    MODEL_F1.labels(model_version=model_version).set(f1)
    DRIFT_COUNT.set(drift_count)

# Alertmanager rule (alert.yaml):
# - alert: ModelF1Degradation
#   expr: model_f1_score < 0.80
#   for: 1h
#   annotations:
#     summary: "Model F1 dropped below 0.80 for {{ $labels.model_version }}"
```

### Step 5: Automate rollback trigger

```python
ROLLBACK_THRESHOLDS = {"f1_min": 0.78, "drift_features_max": 3}

def check_rollback(metrics: dict, drift_count: int) -> bool:
    if metrics.get("f1", 1.0) < ROLLBACK_THRESHOLDS["f1_min"]:
        print("ALERT: F1 below rollback threshold — triggering rollback")
        return True
    if drift_count > ROLLBACK_THRESHOLDS["drift_features_max"]:
        print("ALERT: Too many drifted features — triggering rollback")
        return True
    return False
```

## Outputs

- Evidently drift report HTML with per-feature drift p-values.
- Rolling performance metrics JSON (F1, accuracy, RMSE depending on task).
- Prometheus metrics endpoint consumed by Alertmanager or Grafana.
- Rollback trigger log with reason and timestamp when thresholds are breached.

## Quality Checks

- [ ] All production inference requests are logged with input hash and prediction.
- [ ] Drift detection runs on a schedule (daily or per-1000-predictions) with HTML report stored.
- [ ] Performance metrics are exported to a time-series system and a dashboard exists.
- [ ] Alert rules fire within 1 hour of crossing defined thresholds in test.
- [ ] Rollback procedure is documented and was tested at least once in staging.

**AI-CAIQ evidence:** This skill supports YES response to MDS-07 by producing drift reports, rolling performance metrics, and alerting configurations that demonstrate continuous monitoring of model behavior with automated degradation detection after deployment.
