---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: protecting-model-artifacts-with-key-management
name: protecting-model-artifacts-with-key-management
version: "1.0"
domain: CEK
aicm_controls:
  - CEK-03
  - CEK-08
ssrm_ownership: CSP-Owned
aismm_category: Infrastructure Security & Resilience
aismm_target_level: 3
pillar: security_for_ai
summary: >-
  Use this skill when you need to encrypt AI model artifacts at rest using
  customer-managed keys, implement key rotation, and control access to
  model weights through a key management service.
references:
  - KMS
  - encryption-at-rest
  - AWS-KMS
  - key-rotation
  - model-security
  - HSM
---

## When to Use

Use this skill when:
- Proprietary model weights must be encrypted at rest under customer-managed keys (not provider-managed defaults).
- A compliance requirement (SOC 2, FedRAMP, ISO 27001) mandates CMEK for sensitive AI artifacts.
- You need to revoke access to model artifacts by rotating or disabling the encryption key.
- A data classification policy requires Confidential or Restricted data (including fine-tuned model IP) to use CMEK.

**Do not use** this skill for managing API keys used by AI agents at runtime — see `managing-agent-credential-rotation-and-revocation` for that.

## Inputs

- Model artifact storage location (S3 bucket, Azure Blob, GCS bucket).
- Key management platform (AWS KMS, Azure Key Vault, GCP Cloud KMS, HashiCorp Vault).
- Access policy: which IAM roles/identities may encrypt and decrypt model artifacts.

## Procedure

### Step 1: Create a customer-managed KMS key for model artifacts

```bash
# AWS KMS — create a symmetric CMEK with a restrictive key policy
aws kms create-key \
  --description "CMEK for AI model artifacts — proprietary" \
  --key-usage ENCRYPT_DECRYPT \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "Allow model pipeline to use the key",
        "Effect": "Allow",
        "Principal": {"AWS": "arn:aws:iam::123456789012:role/ml-pipeline"},
        "Action": ["kms:GenerateDataKey", "kms:Decrypt"],
        "Resource": "*"
      },
      {
        "Sid": "Allow key admin",
        "Effect": "Allow",
        "Principal": {"AWS": "arn:aws:iam::123456789012:role/kms-admin"},
        "Action": ["kms:CreateAlias","kms:DescribeKey","kms:ScheduleKeyDeletion","kms:EnableKeyRotation"],
        "Resource": "*"
      }
    ]
  }'
```

### Step 2: Enable automatic annual key rotation

```bash
# Enable automatic rotation (AWS KMS rotates the backing key material annually)
aws kms enable-key-rotation --key-id <KEY_ID>

# Verify rotation is enabled
aws kms get-key-rotation-status --key-id <KEY_ID>
```

### Step 3: Configure S3 bucket for CMEK-encrypted model storage

```bash
# Set default encryption on the model artifact bucket
aws s3api put-bucket-encryption \
  --bucket my-model-artifacts \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789012:key/<KEY_ID>"
      },
      "BucketKeyEnabled": true
    }]
  }'

# Deny uploads without CMEK
aws s3api put-bucket-policy --bucket my-model-artifacts --policy '{
  "Statement": [{
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::my-model-artifacts/*",
    "Condition": {
      "StringNotEquals": {
        "s3:x-amz-server-side-encryption-aws-kms-key-id": "arn:aws:kms:us-east-1:123456789012:key/<KEY_ID>"
      }
    }
  }]
}'
```

### Step 4: Upload and verify model artifact encryption

```python
import boto3

s3 = boto3.client("s3")
KMS_KEY_ID = "arn:aws:kms:us-east-1:123456789012:key/<KEY_ID>"

def upload_model_artifact(local_path: str, bucket: str, key: str):
    s3.upload_file(
        local_path, bucket, key,
        ExtraArgs={
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": KMS_KEY_ID,
        }
    )
    print(f"Uploaded {local_path} → s3://{bucket}/{key} (CMEK)")

def verify_encryption(bucket: str, key: str) -> dict:
    head = s3.head_object(Bucket=bucket, Key=key)
    return {
        "sse": head.get("ServerSideEncryption"),
        "kms_key_id": head.get("SSEKMSKeyId"),
        "encrypted": head.get("ServerSideEncryption") == "aws:kms",
    }
```

### Step 5: Audit key usage and access logs

```bash
# Enable CloudTrail logging for KMS API calls
aws cloudtrail create-trail \
  --name kms-model-artifacts-audit \
  --s3-bucket-name my-audit-logs

# Query for all Decrypt calls on the model key in the last 30 days
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=Decrypt \
  --start-time "$(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%SZ)" \
  | python3 -c "import sys,json; [print(e['CloudTrailEvent']) for e in json.load(sys.stdin)['Events']]"
```

## Outputs

- KMS key resource with restrictive key policy and annual rotation enabled.
- S3 bucket with CMEK default encryption and deny-unencrypted-upload policy.
- Upload function that enforces CMEK on every model artifact write.
- CloudTrail KMS usage audit showing all Encrypt/Decrypt operations.

## Quality Checks

- [ ] CMEK key rotation is enabled and confirmed via `get-key-rotation-status`.
- [ ] S3 bucket rejects any object upload without the designated KMS key.
- [ ] Verification function confirms `ServerSideEncryption: aws:kms` on all model files.
- [ ] KMS key policy restricts Decrypt to the ml-pipeline role only.
- [ ] CloudTrail audit is configured and producing KMS event logs.

**AI-CAIQ evidence:** This skill supports YES response to CEK-03 by producing KMS key configurations with rotation enabled, CMEK-enforced bucket policies, and CloudTrail audit logs demonstrating that AI model artifacts are protected with customer-managed encryption keys under auditable access controls.
