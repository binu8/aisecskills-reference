---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: isolating-ai-training-clusters
name: isolating-ai-training-clusters
version: "1.0"
domain: DCS
aicm_controls:
  - DCS-07
  - I&S-04
ssrm_ownership: CSP-Owned
aismm_category: Infrastructure Security & Resilience
aismm_target_level: 3
summary: >-
  Use this skill when you need to network-isolate an AI training cluster
  to prevent training data and model weights from being accessible outside
  the training environment, and to limit the blast radius of a compromise.
references:
  - network-isolation
  - VPC
  - Kubernetes-NetworkPolicy
  - training-security
  - GPU-cluster
  - egress-control
---

## When to Use

Use this skill when:
- A new GPU training cluster is being provisioned and requires network segmentation before training begins.
- A security review found that training workers have unrestricted internet egress or access to production networks.
- A data classification policy requires that Confidential training data be processed only in isolated environments.
- An audit requires evidence of network controls around the training infrastructure.

**Do not use** this skill for inference cluster security — training clusters have unique data sensitivity and should be treated separately.

## Inputs

- Cloud provider and training infrastructure type (AWS EC2 + EFA, GKE, Azure AKS, on-prem GPU cluster).
- Training data sensitivity classification.
- Required egress: package registries, experiment tracking, artifact stores.

## Procedure

### Step 1: Deploy training cluster in a dedicated VPC with no public subnets

```bash
# Terraform: isolated training VPC (AWS)
cat > training-vpc.tf << 'EOF'
resource "aws_vpc" "training" {
  cidr_block           = "10.20.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "ai-training-isolated", Environment = "training" }
}

resource "aws_subnet" "training_private" {
  vpc_id            = aws_vpc.training.id
  cidr_block        = "10.20.1.0/24"
  map_public_ip_on_launch = false  # No public IPs
  tags = { Name = "training-private-a" }
}

# No internet gateway — training instances cannot reach the internet directly
# Use VPC endpoints for S3, ECR, Secrets Manager
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.training.id
  service_name = "com.amazonaws.us-east-1.s3"
  route_table_ids = [aws_route_table.training.id]
}
EOF
terraform apply -auto-approve
```

### Step 2: Restrict security groups to training-only communication

```bash
# Allow only: inter-node GPU communication (EFA), experiment tracker, artifact store
aws ec2 create-security-group \
  --group-name training-cluster-sg \
  --description "AI training cluster — isolated" \
  --vpc-id vpc-XXXXX

# Allow intra-cluster traffic only
aws ec2 authorize-security-group-ingress \
  --group-id sg-XXXXX \
  --protocol all \
  --source-group sg-XXXXX  # self-reference: nodes talk to each other only

# Allow egress to S3 VPC endpoint and ECR VPC endpoint only (no 0.0.0.0/0)
aws ec2 authorize-security-group-egress \
  --group-id sg-XXXXX \
  --protocol tcp --port 443 \
  --cidr 10.20.0.0/16  # VPC endpoint range only
```

### Step 3: Apply Kubernetes NetworkPolicy for training jobs (GKE/AKS)

```yaml
# training-network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: training-job-isolation
  namespace: training
spec:
  podSelector:
    matchLabels:
      role: training-worker
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              role: training-worker  # inter-worker only
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: artifact-store   # MLflow / model registry
      ports:
        - port: 5000
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system      # DNS
      ports:
        - port: 53
          protocol: UDP
    # Block all other egress — no internet, no production namespaces
```

```bash
kubectl apply -f training-network-policy.yaml
```

### Step 4: Mount training data read-only and validate no write egress

```yaml
# Kubernetes pod spec excerpt
volumes:
  - name: training-data
    persistentVolumeClaim:
      claimName: training-data-pvc
      readOnly: true  # training workers cannot modify the source data
containers:
  - name: trainer
    securityContext:
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      allowPrivilegeEscalation: false
```

### Step 5: Validate isolation with network probes

```bash
# Run a probe pod in the training namespace — it should NOT be able to reach production services
kubectl run isolation-probe --image=curlimages/curl:latest -n training --rm -it \
  --restart=Never -- curl -m 5 http://prod-database.production.svc.cluster.local
# Expected: connection timeout or refused

kubectl run isolation-probe --image=curlimages/curl:latest -n training --rm -it \
  --restart=Never -- curl -m 5 https://example.com
# Expected: connection refused (egress blocked)
```

## Outputs

- Terraform VPC configuration with private-only subnets and S3/ECR VPC endpoints.
- Security group rules restricting egress to VPC endpoints only.
- Kubernetes NetworkPolicy YAML blocking cross-namespace and internet egress.
- Isolation probe test results confirming production services are unreachable from training namespace.

## Quality Checks

- [ ] Training instances have no public IP addresses.
- [ ] Security group denies all 0.0.0.0/0 egress (verified via `describe-security-group-rules`).
- [ ] NetworkPolicy probe test confirms production namespace is unreachable.
- [ ] Training data volume is mounted read-only.
- [ ] VPC Flow Logs are enabled and egress traffic to non-VPC-endpoint destinations is zero.

**AI-CAIQ evidence:** This skill supports YES response to DCS-07 by producing network isolation configurations (VPC, security groups, NetworkPolicy), VPC endpoint configurations for required services, and probe test results demonstrating that AI training clusters are isolated from internet access and production environments.
