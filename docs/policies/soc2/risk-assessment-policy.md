<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Risk Assessment Policy
  Framework: SOC 2 TSC — CC3.1, CC3.2, CC3.3, CC3.4
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
-->

---
title: Risk Assessment Policy
controls: [CC3.1, CC3.2, CC3.3, CC3.4]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Risk Assessment Policy

**Policy Owner:** [CISO / CEO / Head of Compliance]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Next Review:** [DATE + 1 YEAR]
**Version:** 1.0

---

## 1. Purpose

This policy establishes [COMPANY NAME]'s approach to identifying, analyzing, and managing information security risks. It supports SOC 2 TSC CC3.1–CC3.4 (Risk Assessment) and demonstrates that risk management is an ongoing, structured process.

## 2. Risk Assessment Cadence

| Assessment Type | Frequency | Trigger |
|-----------------|-----------|---------|
| **Annual Risk Assessment** | Yearly | Scheduled — [MONTH] each year |
| **Change-Triggered Assessment** | As needed | Significant new technology, major product launch, new data processing |
| **Incident-Triggered Assessment** | After P1/P2 incidents | Following security incidents |
| **Vendor Risk Assessment** | At onboarding and annually | New critical vendor or renewal |

## 3. Risk Assessment Process

### Step 1: Asset Inventory

Identify all information assets relevant to [COMPANY NAME]'s services:
- Cloud infrastructure (AWS accounts, services, regions)
- Customer data (location, classification, volume)
- Application components (services, APIs, databases)
- Third-party integrations and sub-processors
- Employee endpoints and access points

### Step 2: Threat Identification

For each asset, identify applicable threat categories:
- **External Threats:** Unauthorized access, malware, DDoS, phishing, social engineering
- **Internal Threats:** Insider misuse, human error, credential compromise
- **Environmental:** Cloud provider outages, data center failures
- **Fraud:** Financial misstatement, unauthorized transactions, data manipulation
- **Regulatory:** Non-compliance with GDPR, CCPA, SOC 2, [OTHER REGULATIONS]
- **Third-Party:** Vendor breach, supply chain compromise

### Step 3: Vulnerability Assessment

Identify weaknesses that could be exploited by identified threats:
- Technical vulnerabilities (from scan results, pen tests)
- Process gaps (missing controls, inconsistent procedures)
- People gaps (training deficiencies, key person dependencies)

### Step 4: Risk Rating

Each identified risk is rated on a 1–5 scale for:

**Likelihood:** How probable is the risk materializing?
| Score | Level | Description |
|-------|-------|-------------|
| 5 | Certain | Expected to occur within 1 year |
| 4 | Likely | Could occur within 2 years |
| 3 | Possible | Could occur within 5 years |
| 2 | Unlikely | Unlikely but conceivable |
| 1 | Rare | Highly unlikely |

**Impact:** What is the consequence if the risk materializes?
| Score | Level | Description |
|-------|-------|-------------|
| 5 | Critical | Customer data breach, regulatory fine, business-ending |
| 4 | High | Significant data exposure, major service outage, high reputational damage |
| 3 | Medium | Limited data exposure, moderate service disruption |
| 2 | Low | Minor impact, no data exposure, brief disruption |
| 1 | Negligible | Minimal or no impact |

**Risk Score = Likelihood × Impact**

| Score Range | Risk Level | Response |
|-------------|------------|----------|
| 20–25 | Critical | Immediate mitigation required |
| 10–19 | High | Mitigation plan required within 30 days |
| 5–9 | Medium | Mitigation plan within 90 days |
| 1–4 | Low | Accept or monitor |

### Step 5: Risk Treatment

For each risk, select a treatment strategy:
- **Mitigate:** Implement controls to reduce likelihood or impact
- **Transfer:** Purchase insurance or contractually transfer to a vendor
- **Accept:** Formally accept the risk (for low-rated risks with documented rationale)
- **Avoid:** Discontinue the activity creating the risk

### Step 6: Risk Register Maintenance

All identified risks are documented in the Risk Register, which includes:
- Risk ID, description, asset affected
- Likelihood, impact, and risk score
- Risk owner
- Treatment strategy and controls
- Residual risk (after controls)
- Status and due date for open items

The Risk Register is reviewed and updated at least annually or when significant changes occur.

## 4. Fraud Risk Assessment

As part of the annual risk assessment, [COMPANY NAME] specifically evaluates fraud risks:
- Financial misstatement or unauthorized transactions
- Unauthorized access to customer data for personal gain
- Insider threat — data theft or IP theft
- Social engineering attacks targeting employees

Anti-fraud controls are documented in the Risk Register with the treatment strategy and assigned owner.

## 5. Risk Appetite

[COMPANY NAME]'s risk appetite statement:
- **Critical and High risks** are not acceptable and must be mitigated
- **Medium risks** require documented treatment plans with defined timelines
- **Low risks** may be accepted with documented rationale from [CISO / CEO]

Any risk that could result in unauthorized disclosure of customer PII is treated as **High** regardless of the base rating.

## 6. Roles and Responsibilities

| Role | Responsibility |
|------|----------------|
| [CISO / CEO] | Owns the risk assessment process, approves risk register |
| [Engineering Lead] | Identifies and owns technical risks |
| [Legal / Compliance] | Owns regulatory and contractual risks |
| [HR / People Ops] | Owns HR and people-related risks |
| All managers | Participate in risk identification for their area |

## 7. Documentation and Retention

- Risk Register: maintained in [SHARED DRIVE / GRC TOOL / NOTION / CONFLUENCE]
- Risk assessment reports are retained for a minimum of **[3 years]**
- Risk assessment results are shared with [Leadership Team / Board] at least annually

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
