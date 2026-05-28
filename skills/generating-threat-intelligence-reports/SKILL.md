---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: generating-threat-intelligence-reports
name: generating-threat-intelligence-reports
version: "1.0.0"
subdomain: threat-intelligence
summary: >-
  Generates structured cyber threat intelligence reports at strategic, operational, and tactical levels tailored to specific audiences including executives, security operations teams, and technical analysts. Use when producing finished intelligence products from raw collection data, creating sector threat briefings, or delivering post-incident intelligence assessments. Activates for requests involving CTI report writing, threat briefings, intelligence products, finished intelligence, or executive security reporting.
references:
  - CTI
  - threat-intelligence
  - intelligence-products
  - TLP
  - PIR
  - report-writing
  - NIST-CSF
---

## When to Use


Use this skill when:
- Producing weekly, monthly, or quarterly threat intelligence summaries for security leadership
- Creating a rapid intelligence assessment in response to a breaking threat (e.g., new zero-day, active ransomware campaign)
- Generating sector-specific threat briefings for executive decision-making on security investments

**Do not use** this skill for raw IOC distribution — use TIP/MISP for automated IOC sharing and reserve report generation for analyzed, finished intelligence.

## Procedure


### Step 1: Determine Report Type and Audience

Select the appropriate intelligence product type:

**Strategic Intelligence Report**: For C-suite, board, risk committee
- Content: Threat landscape trends, adversary intent vs. capability, risk to business objectives
- Format: 1–3 pages, minimal jargon, business impact language, recommended decisions
- Frequency: Monthly/Quarterly

**Operational Intelligence Report**: For CISO, security directors, IR leads
- Content: Active campaigns, adversary TTPs, defensive recommendations, sector peer incidents
- Format: 3–8 pages, moderate technical detail, mitigation priority list
- Frequency: Weekly

**Tactical Intelligence Bulletin**: For SOC analysts, threat hunters, vulnerability management
- Content: Specific IOCs, YARA rules, Sigma detections, CVEs, patching guidance
- Format: Structured tables, code blocks, 1–2 pages
- Frequency: Daily or as-needed

**Flash Report**: Urgent notification for imminent or active threats
- Content: What is happening, immediate risk, what to do right now
- Format: 1 page maximum, distributed within 2 hours of threat identification
- Frequency: As-needed (zero-day, active campaign targeting sector)

### Step 2: Structure Report Using Intelligence Standards

Apply intelligence writing standards from government and professional practice:

**Headline/Key Judgment**: Lead with the most important finding in plain language.
- Bad: "This report examines threat actor TTPs associated with Cl0p ransomware"
- Good: "Cl0p ransomware group is actively exploiting CVE-2024-20353 in Cisco ASA devices to gain initial access; organizations using unpatched ASA appliances face imminent ransomware risk"

**Confidence Qualifiers** (use language from DNI ICD 203):
- High confidence: "assess with high confidence" — strong evidence, few assumptions
- Medium confidence: "assess" — credible sources but analytical assumptions required
- Low confidence: "suggests" — limited sources, significant uncertainty

**Evidence Attribution**: Cite sources using reference numbers [1], [2]; maintain source anonymization in TLP:AMBER/RED products.

### Step 3: Write Report Body

Use structured format:

**Executive Summary** (3–5 bullet points): Key findings, immediate business risk, top recommended action

**Threat Overview**: Who is the adversary? What is their objective? Why does this matter to us?

**Technical Analysis**: TTPs with ATT&CK technique IDs, IOCs, observed campaign behavior

**Impact Assessment**: Potential operational, financial, reputational impact if attack succeeds

**Recommended Actions**: Prioritized, time-bound defensive measures with owner assignment

**Appendices**: Full IOC lists, YARA rules, Sigma detections, raw source references

### Step 4: Apply TLP and Distribution Controls

Select TLP based on source sensitivity and sharing agreements:
- **TLP:RED**: Named recipients only; cannot be shared outside briefing room
- **TLP:AMBER+STRICT**: Organization only; no sharing with subsidiaries or partners
- **TLP:AMBER**: Organization and trusted partners with need-to-know
- **TLP:GREEN**: Community-wide sharing (ISAC members, sector peers)
- **TLP:WHITE/CLEAR**: Public distribution; no restrictions

Include TLP watermark on every page header and footer.

### Step 5: Review and Quality Control

Before dissemination, apply these checks:
- **Accuracy**: Are all facts sourced and cited? No unsubstantiated claims.
- **Clarity**: Can the target audience understand this without additional context?
- **Actionability**: Does every report section drive a decision or action?
- **Classification**: Is TLP correctly applied? No source identification in AMBER/RED products?
- **Timeliness**: Is this intelligence still current? Events older than 48 hours require freshness assessment.
