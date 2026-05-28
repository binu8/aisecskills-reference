---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: configuring-multi-factor-authentication-with-duo
name: configuring-multi-factor-authentication-with-duo
version: "1.0"
subdomain: identity-access-management
summary: >-
  Deploy Cisco Duo multi-factor authentication across enterprise applications, VPN, RDP, and SSH access points. This skill covers Duo integration methods, adaptive authentication policies, device trust
references:
  - iam
  - identity
  - access-control
  - authentication
  - mfa
  - duo
  - multi-factor
---

## When to Use


- When you need to configure multi factor authentication with duo
- When investigating identity-based attacks or reviewing IAM controls and need a structured, step-by-step procedure
- Activates for requests involving: iam, identity, access-control, authentication

## Procedure


### Step 1: Duo Authentication Proxy Setup
1. Deploy Duo Authentication Proxy on Windows/Linux server
2. Configure primary authentication (AD/LDAP or RADIUS)
3. Configure Duo API credentials (Integration Key, Secret Key, API Hostname)
4. Set failmode (safe=deny if Duo unreachable, secure=allow)
5. Test proxy connectivity to Duo cloud and AD

### Step 2: VPN MFA Integration
1. Configure VPN concentrator for RADIUS authentication
2. Point RADIUS to Duo Authentication Proxy
3. Configure Duo proxy with [radius_server_auto] section
4. Test VPN login with Duo Push
5. Deploy to all VPN users with enrollment period

### Step 3: RDP/Windows Logon MFA
1. Install Duo Authentication for Windows Logon on target servers
2. Configure Duo application in Admin Panel
3. Set offline access options (allow N offline logins)
4. Configure bypass for service accounts
5. Test RDP login with Duo MFA

### Step 4: Adaptive Policy Configuration
1. Create user groups (Standard, Privileged, Contractors)
2. Configure per-group authentication policies:
   - Standard: Duo Push allowed, remembered device 7 days
   - Privileged: Verified Push required, no remembered device
   - Contractors: WebAuthn required, no remembered device
3. Configure device health policies:
   - Require encrypted disk
   - Block outdated OS versions
   - Require firewall enabled
4. Set trusted network exceptions for corporate IPs

### Step 5: Phishing-Resistant MFA Deployment
1. Enable Verified Push (requires entering 3-digit code from login screen)
2. Register WebAuthn/FIDO2 security keys for privileged users
3. Disable SMS and phone call for high-risk groups
4. Configure Duo Risk-Based Factor Selection
5. Monitor for MFA fatigue attack patterns

### Step 6: Monitoring and Response
1. Configure Duo Admin Panel alerts
2. Set up authentication log forwarding to SIEM
3. Monitor for: MFA denial patterns, bypass usage, new device enrollments
4. Create incident response playbook for MFA compromise
5. Regular review of bypass and exception policies

## Quality Checks

- [ ] VPN login requires Duo MFA
- [ ] RDP to servers requires Duo MFA
- [ ] SSH access requires Duo MFA
- [ ] Verified Push enabled for privileged users
- [ ] Device health policy blocks non-compliant devices
- [ ] Authentication logs forwarded to SIEM
- [ ] Bypass/emergency access procedures tested
- [ ] MFA fatigue detection alerts configured
