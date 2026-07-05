# The three pillars

Every skill in this library is grouped under one of three pillars. The `pillar` field in each skill's frontmatter and in `index.json` carries this grouping.

| Pillar | Focus | Skills |
|---|---|---|
| **Security for AI** | Protecting AI systems throughout their lifecycle | 35 |
| **AI for Security** | Deploying AI as a security capability | 0 |
| **Security from AI** | Managing AI-specific risks and harms | 20 |

## Security for AI

*Protecting AI systems throughout their lifecycle.*

- **`applying-zero-trust-to-ai-workloads`** (I&S) — Use this skill when you need to apply zero-trust principles to AI workload networking — ensuring no implicit trust between AI services, agents, and data stores, with continuous verification at every layer.
- **`assessing-jailbreak-resistance-pre-deployment`** (TVM) — Use this skill when you need to quantitatively score a deployed or pre-production LLM system's resistance to jailbreak attempts before go-live, producing a pass/fail safety gate result.
- **`assessing-third-party-model-and-provider-risk`** (STA) — Use this skill when you need to evaluate the security, privacy, and compliance risks of adopting a third-party AI model provider, API service, or pre-trained model before onboarding.
- **`building-an-ai-risk-register`** (GRC) — Use this skill when you need to create or maintain a structured AI risk register that captures, scores, and tracks mitigations for identified risks across an organization's AI portfolio.
- **`capturing-agent-action-and-delegation-telemetry`** (LOG) — Use this skill when you need to instrument an AI agent system to capture every tool call, sub-agent delegation, and state transition as structured telemetry for security investigation and compliance purposes.
- **`completing-the-ai-caiq-self-assessment`** (A&A) — Use this skill when you need to complete the CSA AI Consensus Assessments Initiative Questionnaire (AI-CAIQ) for your organization, producing a shareable, verifiable self-attestation of AI security controls.
- **`conducting-adversarial-robustness-testing`** (MDS) — Use this skill when you need to systematically measure how an AI model responds to adversarial inputs — perturbations, out-of-distribution samples, and evasion attacks — before production deployment.
- **`conducting-an-aicm-control-assessment`** (A&A) — Use this skill when you need to conduct a structured assessment of your organization's AI controls against the CSA AICM control framework, producing a scored maturity profile and gap remediation plan.
- **`defending-against-prompt-injection`** (AIS) — Use this skill when you need to harden an LLM application against prompt injection attacks, where adversarial content in user inputs or retrieved documents attempts to override system instructions or exfiltrate data.
- **`deploying-llm-output-guardrails`** (AIS) — Use this skill when you need to intercept, classify, and block or rewrite unsafe, off-topic, or policy-violating LLM outputs before they reach end users, using layered guardrail controls.
- **`designing-ai-service-failover-and-resilience`** (BCR) — Use this skill when you need to design failover and resilience patterns for AI services — including LLM API fallback, model endpoint redundancy, and graceful degradation under provider outages.
- **`detecting-prompt-injection-and-jailbreak-attempts`** (LOG) — Use this skill when you need to monitor LLM application logs for prompt injection and jailbreak attempts in real time, alert on patterns, and feed detections into a SIEM for incident response.
- **`enabling-model-and-data-portability-and-export`** (IPY) — Use this skill when you need to implement model and training data export capabilities so that an organization can migrate away from a provider, exercise data portability rights, or fulfill GDPR data export obligations.
- **`establishing-ai-acceptable-use-and-developer-training`** (HRS) — Use this skill when you need to create an AI acceptable use policy, security training curriculum, and attestation process for developers and staff who build or use AI systems.
- **`generating-an-ai-bill-of-materials`** (STA) — Use this skill when you need to produce a machine-readable AI Bill of Materials that inventories all models, datasets, libraries, and supply chain dependencies for an AI system deployment.
- **`hardening-agent-orchestration-against-drift`** (AIS) — Use this skill when you need to prevent an AI agent orchestration system from drifting outside its intended scope through goal hijacking, runaway loops, or unauthorized sub-agent delegation.
- **`implementing-on-behalf-of-delegation-and-consent`** (IAM) — Use this skill when an AI agent must act on behalf of a human user, requiring explicit OAuth delegation flows, consent capture, and auditable on-behalf-of token chains to prevent privilege escalation.
- **`implementing-permission-aware-retrieval-for-rag`** (DSP) — Use this skill when building or auditing a RAG system that must enforce fine-grained document-level permissions, ensuring each user retrieves only documents their identity and role permit them to see.
- **`implementing-prompt-and-response-logging`** (LOG) — Use this skill when you need to implement structured, tamper-resistant logging of LLM prompts and responses to support security monitoring, incident investigation, and compliance audits.
- **`isolating-ai-training-clusters`** (DCS) — Use this skill when you need to network-isolate an AI training cluster to prevent training data and model weights from being accessible outside the training environment, and to limit the blast radius of a compromise.
- **`managing-agent-credential-rotation-and-revocation`** (IAM) — Use this skill when you need to rotate API keys or secrets used by AI agents on a schedule, or immediately revoke credentials when an agent is compromised, decommissioned, or behaves anomalously.
- **`mapping-controls-to-iso-42001`** (GRC) — Use this skill when you need to map your organization's existing security and AI controls to ISO/IEC 42001 requirements and produce a gap analysis and compliance coverage report.
- **`monitoring-model-drift-and-degradation`** (MDS) — Use this skill when you need to detect data drift, concept drift, or performance degradation in a deployed AI model through continuous monitoring, alerting, and automated rollback triggers.
- **`protecting-model-artifacts-with-key-management`** (CEK) — Use this skill when you need to encrypt AI model artifacts at rest using customer-managed keys, implement key rotation, and control access to model weights through a key management service.
- **`provisioning-non-human-identities-for-ai-agents`** (IAM) — Use this skill when you need to create, scope, and govern dedicated non-human identities for AI agents — service accounts, workload identities, or machine credentials — separate from human user accounts.
- **`red-teaming-llm-applications`** (TVM) — Use this skill when you need to conduct a structured red-team assessment of an LLM application, systematically probing for jailbreaks, data extraction, harmful output, and safety bypass vulnerabilities.
- **`scanning-ai-bom-for-vulnerable-components`** (TVM) — Use this skill when you need to generate an AI Bill of Materials and scan it for known CVEs, malicious packages, and supply chain risks in ML frameworks, model dependencies, and data pipeline libraries.
- **`scanning-training-and-grounding-data-for-pii`** (DSP) — Use this skill when you need to detect, classify, and remediate personally identifiable information in datasets before they are used to train, fine-tune, or ground an AI model.
- **`scoping-mcp-tool-authorization-least-privilege`** (IAM) — Use this skill when you need to apply least-privilege principles to MCP tool grants, ensuring each AI agent can invoke only the specific tools and parameter ranges required for its assigned task.
- **`securing-mcp-server-and-tool-boundaries`** (AIS) — Use this skill when you need to harden a Model Context Protocol server and its exposed tools against unauthorized invocation, privilege escalation, and data exfiltration through agent-initiated tool calls.
- **`securing-rag-pipelines-against-data-leakage`** (DSP) — Use this skill when you need to audit, harden, or redesign a Retrieval-Augmented Generation pipeline to prevent sensitive documents from leaking to unauthorized users through LLM responses.
- **`validating-training-data-provenance-and-lineage`** (DSP) — Use this skill when you need to establish or verify the chain of custody for a training dataset — confirming source, transformation history, and licensing before a model is trained or released.
- **`verifying-model-integrity-and-provenance-signing`** (MDS) — Use this skill when you need to cryptographically verify that a model artifact has not been tampered with since it was produced, and to sign new model artifacts so downstream consumers can establish provenance.
- **`verifying-open-model-supply-chain-integrity`** (STA) — Use this skill when you need to verify that an open-weight model downloaded from a public registry has not been tampered with, backdoored, or substituted before it is deployed in your environment.
- **`versioning-models-and-system-prompts-with-rollback`** (CCC) — Use this skill when you need to implement version control and rollback capability for AI model artifacts and system prompts, so that a bad deployment can be reverted within minutes without manual intervention.

## AI for Security

*Deploying AI as a security capability.*

_No skills yet. This pillar is the current authoring gap: using AI itself as a security capability (AI-assisted detection, triage, and response) is thinly covered by existing standards and is the next area to build._

## Security from AI

*Managing AI-specific risks and harms.*

- **`bounding-agent-autonomy-and-tool-scopes-least-privilege`** (IAM) — Use this skill when an AI agent can invoke state-changing tools and you need to bound its blast radius with least-privilege tool scopes, rate limits, and budgets enforced by a fail-closed broker.
- **`building-an-ai-incident-response-playbook`** (SEF) — Use this skill when you need to create or update an incident response playbook that covers AI-specific incident types — model compromise, prompt injection attacks, data leakage through LLM outputs, and agent credential theft.
- **`classifying-ai-systems-under-eu-ai-act`** (GRC) — Use this skill when you need to classify an AI system under the EU AI Act risk tiers — unacceptable, high-risk, limited, or minimal — and determine the resulting compliance obligations.
- **`detect-mcp-adversarial-input-corpus`** (AIS) — Use this skill when you need runtime detection of adversarial prompts / jailbreak attempts matching a curated fingerprint catalog, running the vendored detector over OCSF-normalized MCP activity to emit detection findings.
- **`detect-mcp-model-artifact-tampering`** (MDS) — Use this skill when you need runtime detection of ML supply-chain compromise where an MCP server swaps a model artifact (weights, adapter, tokenizer) mid-session, running the vendored detector over OCSF-normalized MCP activity to emit detection findings.
- **`detect-mcp-model-token-flood`** (MDS) — Use this skill when you need runtime detection of unbounded prompt-token consumption against a model endpoint over MCP (OWASP LLM10), running the vendored detector over OCSF-normalized MCP activity to emit detection findings.
- **`detect-mcp-plugin-supply-chain`** (STA) — Use this skill when you need runtime detection of MCP plugin/tool whose inputSchema references a hostname outside an allowlist (supply-chain risk), running the vendored detector over OCSF-normalized MCP activity to emit detection findings.
- **`detect-mcp-shadow-tool-injection`** (AIS) — Use this skill when you need runtime detection of MCP tool poisoning where a tool's description or inputSchema is mutated mid-session away from a server-registered baseline, running the vendored detector over OCSF-normalized MCP activity to emit detection findings.
- **`detect-mcp-tool-drift`** (AIS) — Use this skill when you need runtime detection of MCP tool-poisoning / rug-pull where a tool's schema changes within a session after the agent has already trusted it, running the vendored detector over OCSF-normalized MCP activity to emit detection findings.
- **`detect-mcp-unbounded-tool-output`** (AIS) — Use this skill when you need runtime detection of unbounded tool-output consumption (OWASP LLM10) where a tool systematically breaches output ceilings, running the vendored detector over OCSF-normalized MCP activity to emit detection findings.
- **`detect-prompt-injection-mcp-proxy`** (AIS) — Use this skill when you need runtime detection of prompt-injection and instruction-smuggling language embedded in MCP tool descriptions, running the vendored detector over OCSF-normalized MCP activity to emit detection findings.
- **`detect-system-prompt-extraction`** (AIS) — Use this skill when you need runtime detection of MCP tool-call responses that leak system-prompt or hidden-instruction material, running the vendored detector over OCSF-normalized MCP activity to emit detection findings.
- **`detect-tool-output-exfiltration-instructions`** (DSP) — Use this skill when you need runtime detection of MCP tool-call responses instructing the agent to exfiltrate conversation history, prompts, files, or secrets, running the vendored detector over OCSF-normalized MCP activity to emit detection findings.
- **`detecting-cascading-and-feedback-loop-agent-behavior`** (LOG) — Use this skill when agents can chain actions or read from and write to a shared source, and you need to detect cascades and feedback loops behind a circuit-breaker.
- **`detecting-deepfake-audio-in-vishing-attacks`** (TVM) — Use this skill when you need to determine whether a recorded phone call contains AI-generated deepfake speech, extracting spectral features to classify the audio and produce a forensic report.
- **`evaluating-model-safety-bias-and-harm`** (MDS) — Use this skill when you need to systematically evaluate an AI model for safety failures, demographic bias, and harmful output potential before releasing it to production or a broader audience.
- **`governing-ai-coding-assistant-endpoints`** (UEM) — Use this skill when you need to govern which AI coding assistant endpoints developers may connect to from managed devices, preventing data leakage to unapproved external AI services through IDE plugins and CLI tools.
- **`implementing-content-safety-output-filtering`** (AIS) — Use this skill when a generative AI application exposes free-form output to end users and you need to filter that output through a content-safety classifier before it reaches them.
- **`implementing-kill-switch-and-rollback-for-autonomous-agents`** (SEF) — Use this skill when an autonomous AI agent holds state-changing permissions in production and you need an emergency kill switch and per-action rollback the SOC can invoke within seconds.
- **`investigating-compromised-ai-agent-credentials`** (SEF) — Use this skill when you suspect or have confirmed that credentials used by an AI agent have been stolen or misused, and need to contain the incident, reconstruct the timeline, and restore secure operations.

