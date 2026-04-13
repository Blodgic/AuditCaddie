<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Internal Audit & Control Evaluation Policy
  Framework: SOC 2 TSC — CC4.1, CC4.2
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
-->

---
title: Internal Audit & Control Evaluation Policy
controls: [CC4.1, CC4.2]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Internal Audit & Control Evaluation Policy

**Policy Owner:** [CISO / Head of Compliance / CEO]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Version:** 1.0

---

## 1. Purpose

This policy establishes [COMPANY NAME]'s approach to evaluating the design and effectiveness of internal controls and communicating deficiencies to responsible parties. It supports SOC 2 TSC CC4.1 (Evaluation of Internal Controls) and CC4.2 (Communication of Control Deficiencies).

## 2. Control Evaluation Activities

### 2.1 Annual Security Review

[COMPANY NAME] conducts an annual internal security review covering:
- Review of all security policies for currency and applicability
- Review of access rights and privileged account holders
- Review of vendor risk assessments and certifications
- Review of open security findings and remediation status
- AWS security posture assessment using [AWS Security Hub / AuditCaddie / Prowler]
- Review of security training completion records

**Owner:** [CISO]
**Timing:** [Month] each year
**Output:** Internal Security Review Report

### 2.2 Quarterly Controls Reviews

Quarterly reviews are conducted for:
- Access control review (active user accounts and permissions)
- Vulnerability scan result review (open items aging)
- Patch compliance review
- Incident and security event summary

**Owner:** [Engineering Lead / CISO]
**Output:** Quarterly Controls Summary (documented in [TICKETING SYSTEM / Notion / Confluence])

### 2.3 External Assessments

| Assessment | Frequency | Scope |
|------------|-----------|-------|
| SOC 2 Type I / II Audit | [Annual] | Full TSC scope per engagement |
| Penetration Testing | [Annual] | External attack surface + selected internal scope |
| Vulnerability Assessment | [Quarterly] | AWS infrastructure and applications |

External assessment reports are reviewed within [5 business days] of receipt and findings are entered into the remediation tracking system.

## 3. Control Deficiency Management

### 3.1 Deficiency Classification

| Level | Description | Example |
|-------|-------------|---------|
| **Material Weakness** | A significant deficiency that could materially affect the reliability of financial reporting or security | Root access keys in use, no MFA on production systems |
| **Significant Deficiency** | A deficiency that is less severe than a material weakness but still warrants attention | Access reviews overdue >90 days, scan not run in 6 months |
| **Control Gap** | A missing or inadequate control that does not yet rise to a significant deficiency | Policy not reviewed in 18 months, missing documentation |

### 3.2 Deficiency Tracking

All identified deficiencies are entered into [TICKETING SYSTEM / GRC TOOL] with:
- Deficiency description and classification
- Control(s) affected
- Root cause
- Assigned owner
- Due date for remediation
- Status

### 3.3 Deficiency Communication

Deficiencies are communicated:
- **Material Weaknesses:** Immediate notification to [CEO / Board]; remediation plan within [30 days]
- **Significant Deficiencies:** Reported to [CISO / Engineering Lead] within [5 business days]; remediation plan within [60 days]
- **Control Gaps:** Reported at next quarterly controls review; remediation within [90 days]

All deficiency communications are documented and retained.

## 4. Continuous Monitoring

In addition to periodic reviews, [COMPANY NAME] monitors controls continuously via:
- AWS Security Hub findings (automated alerts)
- GuardDuty threat detection (automated alerts)
- AWS Config rules (automated compliance checks)
- AuditCaddie automated scans

Automated findings are reviewed [daily / on-alert] and fed into the deficiency management process above.

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
