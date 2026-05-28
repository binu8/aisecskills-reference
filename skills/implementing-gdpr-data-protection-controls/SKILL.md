---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: implementing-gdpr-data-protection-controls
name: implementing-gdpr-data-protection-controls
version: "1.0"
subdomain: compliance-governance
summary: >-
  The General Data Protection Regulation (EU) 2016/679 (GDPR) is the EU's comprehensive data protection law governing the collection, processing, storage, and transfer of personal data. This skill cover
references:
  - compliance
  - governance
  - gdpr
  - privacy
  - data-protection
  - eu-regulation
---

## When to Use


- When you need to implement gdpr data protection controls
- When meeting regulatory requirements or conducting compliance audits and need a structured, step-by-step procedure
- Activates for requests involving: compliance, governance, gdpr, privacy

## Procedure


### Phase 1: Data Mapping and Assessment (Weeks 1-6)
1. Create comprehensive data inventory:
   - What personal data is collected
   - From whom (data subjects)
   - Why (purposes and lawful bases)
   - Where it's stored (systems, locations, countries)
   - Who has access (internal and external)
   - How long it's retained
   - What security measures protect it
2. Document Records of Processing Activities (ROPA) per Article 30
3. Identify lawful basis for each processing activity
4. Map cross-border data transfers and transfer mechanisms
5. Identify processing activities requiring DPIA

### Phase 2: Gap Analysis and Risk Assessment (Weeks 7-10)
1. Assess current state against GDPR requirements
2. Perform DPIAs for high-risk processing activities
3. Identify security gaps in Article 32 compliance
4. Evaluate data retention compliance
5. Assess data subject rights request handling capabilities

### Phase 3: Technical Controls Implementation (Weeks 11-24)
1. **Encryption**:
   - Data at rest: AES-256 for databases, file systems, backups
   - Data in transit: TLS 1.2+ for all personal data transfers
   - Key management: secure key storage and rotation procedures
2. **Pseudonymization**:
   - Implement tokenization for sensitive identifiers
   - Separate pseudonymization keys from data stores
3. **Access Controls**:
   - Role-based access control (RBAC) for personal data
   - Principle of least privilege
   - MFA for systems processing personal data
   - Regular access reviews
4. **Data Minimization**:
   - Implement data collection limits at application layer
   - Default privacy settings (data protection by default)
   - Automated data retention enforcement
5. **Erasure and Portability**:
   - Build data deletion workflows across all systems
   - Implement data export in machine-readable formats (JSON, CSV)
   - Cascade deletion to backups and archives
6. **Consent Management**:
   - Implement granular consent collection mechanisms
   - Consent withdrawal functionality
   - Consent audit trail and versioning
7. **Breach Detection**:
   - SIEM for personal data access monitoring
   - Data loss prevention (DLP) controls
   - Anomalous access detection

### Phase 4: Organizational Controls (Weeks 11-24)
1. Appoint Data Protection Officer (DPO) if required
2. Develop data protection policies and procedures
3. Create breach notification procedures (72-hour timeline)
4. Establish data subject request (DSR) handling procedures
5. Implement vendor management with Data Processing Agreements (DPAs)
6. Deploy privacy awareness training for all staff
7. Create data protection by design guidance for development teams

### Phase 5: Documentation and Compliance Evidence (Weeks 25-30)
1. Finalize ROPA documentation
2. Document all DPIAs and outcomes
3. Create data protection policies
4. Document technical and organizational measures
5. Establish privacy notice and consent records
6. Create international transfer documentation (SCCs, TIAs)

### Phase 6: Ongoing Compliance (Continuous)
1. Regular DPIA reviews for new processing activities
2. Annual data mapping refresh
3. Periodic security measure testing (Art. 32 requirement)
4. Data subject request tracking and SLA monitoring
5. Breach response readiness testing
6. Training refresh and awareness campaigns
