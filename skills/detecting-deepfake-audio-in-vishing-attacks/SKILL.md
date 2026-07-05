---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: detecting-deepfake-audio-in-vishing-attacks
name: detecting-deepfake-audio-in-vishing-attacks
version: "1.0"
domain: TVM
aicm_controls:
  - TVM-03
  - SEF-05
ssrm_ownership: AIC-Owned
aismm_category: Incident Response
aismm_target_level: 3
pillar: security_from_ai
atlas_techniques:
  - AML.T0088
  - AML.T0043
summary: >-
  Use this skill when you need to determine whether a recorded phone call
  contains AI-generated (deepfake) speech — for example a suspected vishing
  call that cloned an executive's voice to authorize a wire transfer — by
  extracting spectral features and classifying the audio, then producing a
  forensic report.
references:
  - deepfake-detection
  - audio-forensics
  - MFCC
  - vishing
  - voice-cloning
  - spectral-analysis
---

## When to Use

Use this skill when:
- A suspected vishing call used an AI-cloned voice to authorize a payment or action, and you need forensic proof.
- Incident response must decide whether a recorded call contains synthetic speech.
- Fraud or legal investigation requires evidence that audio was AI-generated.
- A red-team exercise uses voice cloning and the blue team needs a detection capability.

**Do not use** this skill for text-based phishing (email/SMS) — use email header analysis or URL detonation instead; and do not treat a single score as proof, always pair it with out-of-band verification of the purported speaker.

## Inputs

- Audio samples in WAV, MP3, or FLAC (mono or stereo, any sample rate); minimum ~3 seconds for reliable statistics.
- Python 3.9+ with `librosa`, `numpy`, `scikit-learn`, `scipy`; FFmpeg installed for format conversion.
- Optional: a reference corpus of known-genuine voice samples for the targeted individual (improves accuracy).

## Procedure

### Step 1: Preprocess the audio

```python
import librosa, numpy as np

y, sr = librosa.load("suspect_call.wav", sr=16000, mono=True)
y_trimmed, _ = librosa.effects.trim(y, top_db=25)
y_norm = y_trimmed / np.max(np.abs(y_trimmed))
```

### Step 2: Extract spectral features

```python
mfccs = librosa.feature.mfcc(y=y_norm, sr=sr, n_mfcc=20)
mfcc_delta = librosa.feature.delta(mfccs)
spectral_contrast = librosa.feature.spectral_contrast(y=y_norm, sr=sr)
spectral_centroid = librosa.feature.spectral_centroid(y=y_norm, sr=sr)
zcr = librosa.feature.zero_crossing_rate(y_norm)
```

Deepfake indicators: reduced spectral contrast in the 4–8 kHz range (vocoders compress high-frequency detail), abnormally consistent spectral centroid over time, low zero-crossing-rate variance, and missing formant transitions at consonant-vowel boundaries.

### Step 3: Build a feature vector and classify

```python
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

def build_feature_vector(y, sr):
    features = []
    for coeff in librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20):
        features += [np.mean(coeff), np.std(coeff), np.min(coeff), np.max(coeff)]
    for band in librosa.feature.spectral_contrast(y=y, sr=sr):
        features += [np.mean(band), np.std(band)]
    return np.array(features)
```

Use an ensemble (Random Forest for robustness, Gradient Boosting for accuracy) with a voting rule to reduce false positives.

### Step 4: Temporal artifact analysis

```python
f0, _, _ = librosa.pyin(y_norm, fmin=50, fmax=500, sr=sr)
f0_clean = f0[~np.isnan(f0)]
pitch_jitter = np.mean(np.abs(np.diff(f0_clean))) if len(f0_clean) > 1 else 0
```

Genuine speech shows natural pitch jitter and shimmer; synthetic speech from neural vocoders typically shows reduced jitter.

### Step 5: Spectrogram inspection and forensic report

Generate mel-spectrograms for manual review (look for energy cutoffs above the vocoder ceiling and periodic banding), then compile a report with the verdict, confidence, per-feature anomalies against a genuine baseline, and a chain-of-custody note.

## Outputs

- A per-sample verdict (`likely deepfake` / `likely genuine`) with an ensemble confidence score.
- A feature-anomaly table comparing the suspect sample to a genuine baseline (MFCC variance, spectral contrast, pitch jitter, ZCR).
- A forensic report with spectrogram evidence and a chain-of-custody statement suitable for legal or compliance follow-up.

## Quality Checks

- [ ] A known-synthetic sample is classified `likely deepfake`; a known-genuine sample is classified `likely genuine`.
- [ ] Samples under 3 seconds are rejected or flagged as low-confidence rather than scored silently.
- [ ] Phone-codec degradation (G.711, AMR) is recorded as a caveat in the report, not ignored.
- [ ] Every verdict is paired with an out-of-band verification recommendation.
- [ ] Original audio is preserved with chain-of-custody documentation.

**AI-CAIQ evidence:** This skill supports a YES response to TVM-03 by producing forensic detection findings and a documented analysis procedure for AI-generated synthetic-media threats reaching the organization.
