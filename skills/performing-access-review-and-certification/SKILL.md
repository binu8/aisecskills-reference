---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: performing-access-review-and-certification
name: performing-access-review-and-certification
version: "1.0"
subdomain: identity-access-management
summary: >-
  Conduct systematic access reviews and certifications to ensure users have appropriate access rights aligned with their roles. This skill covers review campaign design, reviewer selection, risk-based p
references:
  - iam
  - identity
  - access-control
  - access-review
  - certification
  - compliance
  - governance
---

## When to Use


- When you need to conduct systematic access reviews and certifications to ensure users have appropriate access rights aligned with their roles.
- When investigating identity-based attacks or reviewing IAM controls and need a structured, step-by-step procedure
- Activates for requests involving: iam, identity, access-control, access-review

## Procedure


### Step 1: Define Review Scope and Schedule
- Identify in-scope applications and systems
- Determine review frequency: quarterly (SOX), semi-annual, annual
- Define campaign timeline: review period, escalation dates, hard close
- Establish escalation chain for non-responsive reviewers

### Step 2: Data Collection and Aggregation
- Extract user-entitlement mappings from each application
- Correlate with HR data (active employees, role, department, manager)
- Identify terminated/transferred users still holding access
- Flag high-risk entitlements (admin, DBA, system, privileged)
- Calculate risk scores based on entitlement sensitivity and user role

### Step 3: Reviewer Assignment
- **Manager Reviews**: Direct manager certifies subordinate access
- **Application Owner Reviews**: App owner certifies all users of their application
- **Hybrid Model**: Manager reviews standard access, app owner reviews privileged
- **Delegate Management**: Allow reviewers to delegate with audit trail

### Step 4: Execute Certification Campaign
- Send notifications to reviewers with clear instructions
- Present entitlements with context (last used date, risk level, role justification)
- Require reviewers to explicitly approve or revoke each item
- Track completion percentage and send reminders
- Escalate to management after deadline

### Step 5: Remediation and Tracking
- Automatically ticket revocations to IT operations
- Set SLA for revocation execution (24-48 hours for high-risk)
- Verify revocation completed (re-check entitlement)
- Exception management for business-justified deviations
- Document all exceptions with expiration dates

### Step 6: Reporting and Evidence
- Generate campaign completion metrics
- Produce per-application compliance reports
- Create audit-ready evidence packages
- Track trends across review cycles
- Feed findings into risk assessment process

## Quality Checks

- [ ] All in-scope applications included in campaign
- [ ] Reviewers assigned for 100% of entitlements
- [ ] Campaign completion rate exceeds 95%
- [ ] Revocations executed within SLA
- [ ] Audit evidence package complete and archived
- [ ] SOD violations identified and documented
- [ ] Exceptions documented with business justification and expiry
