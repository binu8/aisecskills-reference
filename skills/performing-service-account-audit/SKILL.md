---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: performing-service-account-audit
name: performing-service-account-audit
version: "1.0"
subdomain: identity-access-management
summary: >-
  Audit service accounts across enterprise infrastructure to identify orphaned, over-privileged, and non-compliant accounts. This skill covers discovery of service accounts in Active Directory, cloud pl
references:
  - iam
  - identity
  - access-control
  - service-accounts
  - audit
  - governance
---

## When to Use


- When you need to audit service accounts across enterprise infrastructure to identify orphaned, over-privileged, and non-compliant accounts.
- When investigating identity-based attacks or reviewing IAM controls and need a structured, step-by-step procedure
- Activates for requests involving: iam, identity, access-control, service-accounts

## Procedure


### Step 1: Discovery - Active Directory
1. Query AD for all service accounts (filter by description, OU, naming convention)
2. Identify accounts with `ServicePrincipalName` set
3. List accounts in privileged groups (Domain Admins, Enterprise Admins)
4. Check for gMSA vs traditional service accounts
5. Identify accounts with `PasswordNeverExpires` flag

### Step 2: Discovery - Cloud Platforms
- **AWS**: List IAM users with access keys, check last used date, identify unused roles
- **Azure**: Enumerate service principals, app registrations, managed identities
- **GCP**: List service accounts, check key age, identify unused permissions

### Step 3: Assessment
- Flag accounts with admin/privileged group membership
- Check password age against rotation policy (90 days max)
- Identify accounts with no login activity in 90+ days
- Verify account ownership against CMDB/asset inventory
- Check for shared credentials (same password hash across accounts)

### Step 4: Risk Classification
- **Critical**: Domain/cloud admin privileges, no password rotation
- **High**: Access to sensitive data, no identified owner
- **Medium**: Standard service permissions, password older than 90 days
- **Low**: Read-only access, managed credentials (gMSA, managed identity)

### Step 5: Remediation
- Disable orphaned accounts after validation with application teams
- Convert traditional service accounts to gMSA where possible
- Rotate credentials older than policy threshold
- Reduce privileges to minimum required
- Assign owners and document dependencies

## Quality Checks

- [ ] Service accounts inventoried across all platforms
- [ ] Each account has assigned owner
- [ ] Privileged service accounts documented with justification
- [ ] Password rotation compliance checked
- [ ] Orphaned accounts flagged for remediation
- [ ] gMSA migration candidates identified
- [ ] Compliance report generated
