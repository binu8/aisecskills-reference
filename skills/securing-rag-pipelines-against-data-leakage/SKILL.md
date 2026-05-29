---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: securing-rag-pipelines-against-data-leakage
name: securing-rag-pipelines-against-data-leakage
version: "1.0"
domain: DSP
aicm_controls:
  - DSP-07
  - DSP-10
ssrm_ownership: AP-Owned
aismm_category: Data Security
aismm_target_level: 4
summary: >-
  Use this skill when you need to audit, harden, or redesign a
  Retrieval-Augmented Generation pipeline to prevent sensitive documents
  from leaking to unauthorized users through LLM responses.
references:
  - RAG
  - vector-database
  - data-leakage
  - langchain
  - llama-index
  - access-control
---

## When to Use

Use this skill when:
- A RAG application retrieves documents from a shared vector store without enforcing per-user access policies.
- You are reviewing an AI product for data-isolation compliance before a security audit.
- An incident suggests an LLM response contained content from documents the requesting user should not access.
- You are designing a new RAG system and need to build data-leakage controls from the start.

**Do not use** this skill as a substitute for a full data-classification review; it focuses on the retrieval and generation boundaries, not upstream data labeling.

## Inputs

- Architecture diagram or codebase for the RAG pipeline (retriever, vector store, prompt assembly, LLM call).
- Document corpus metadata (sensitivity labels, intended audience, ACL definitions).
- Identity context available at query time (user ID, group memberships, tenant ID).

## Procedure

### Step 1: Map retrieval-to-response data flow

Enumerate every point where retrieved content enters the prompt:

```python
# Example: trace LangChain retrieval chain
from langchain.callbacks import StdOutCallbackHandler

chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    callbacks=[StdOutCallbackHandler()]  # log all retrieved docs + final prompt
)
```

Document each hop: vector query → retrieved chunks → prompt template → LLM response → output parser.

### Step 2: Enforce metadata-filtered retrieval

Attach ACL metadata to every document at index time and push filters into every retrieval call:

```python
# Pinecone example — index with access metadata
index.upsert(vectors=[
    {"id": doc_id, "values": embedding,
     "metadata": {"sensitivity": "confidential", "allowed_groups": ["finance"]}}
])

# Retrieve only docs the user's groups can access
query_filter = {"allowed_groups": {"$in": user_groups}}
results = index.query(vector=query_embedding, filter=query_filter, top_k=5)
```

For Weaviate, use `where` filters; for Qdrant, use `must` conditions in `Filter`.

### Step 3: Apply prompt-level content stripping

Before assembling the final prompt, scan retrieved chunks against the user's clearance level:

```python
def strip_unauthorized_chunks(chunks, user_clearance: int) -> list:
    safe = []
    for chunk in chunks:
        level = SENSITIVITY_MAP.get(chunk.metadata.get("sensitivity", "public"), 0)
        if level <= user_clearance:
            safe.append(chunk)
        else:
            logger.warning("Blocked chunk id=%s sensitivity=%s", chunk.id, chunk.metadata["sensitivity"])
    return safe
```

Log every blocked chunk with user identity for audit trail.

### Step 4: Validate LLM output for residual leakage

Run the generated response through a post-generation scanner before returning it:

```python
import re

PATTERNS = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "cc": re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b"),
    "internal_hostname": re.compile(r"\b[a-z]+-prod-[a-z0-9]+\.internal\b"),
}

def scan_output(text: str) -> list[str]:
    findings = []
    for label, pattern in PATTERNS.items():
        if pattern.search(text):
            findings.append(label)
    return findings

findings = scan_output(llm_response)
if findings:
    raise DataLeakageError(f"Response contains potential sensitive data: {findings}")
```

### Step 5: Implement tenant isolation at the vector store level

For multi-tenant deployments, enforce namespace or collection separation:

```python
# Pinecone: one namespace per tenant
vectorstore = Pinecone(index=index, namespace=f"tenant-{tenant_id}")

# Weaviate: class-per-tenant with tenant isolation enabled
client.schema.create_class({
    "class": f"Docs_{tenant_id}",
    "multiTenancyConfig": {"enabled": True}
})
```

### Step 6: Write retrieval security tests

```python
def test_cross_tenant_isolation():
    # Index a doc under tenant_a, query as tenant_b — expect zero results
    index_doc(tenant="tenant_a", content="SECRET: acquisition target is AcmeCorp")
    results = retrieve(query="acquisition target", tenant="tenant_b")
    assert len(results) == 0, "Cross-tenant leakage detected"
```

Add this test to CI so regressions fail the build.

## Outputs

- A retrieval security test suite with cross-user and cross-tenant isolation cases.
- Updated pipeline code with metadata filters, content strippers, and output scanners.
- An audit log schema capturing: user ID, query, retrieved doc IDs, blocked chunk IDs, response hash.
- A findings report mapping each leakage vector to the corrective control applied.

## Quality Checks

- [ ] Every retrieval call passes an ACL filter — no unfiltered `as_retriever()` calls remain.
- [ ] Blocked-chunk events are written to a durable audit log with user identity and timestamp.
- [ ] Output scanner tests cover SSN, PII, internal hostnames, and secret tokens.
- [ ] Cross-tenant isolation test passes in CI with zero results returned across tenants.
- [ ] Sensitivity labels are present on ≥95% of indexed documents (verified via metadata audit query).

**AI-CAIQ evidence:** This skill supports YES response to DSP-07 by producing an audit log of every retrieval decision, metadata filter configurations, and a test suite demonstrating that unauthorized documents are not returned to unpermitted users.
