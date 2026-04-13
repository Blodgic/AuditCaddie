<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Vendor & Third-Party Risk Management Policy
  Framework: SOC 2 TSC — CC9.2, P6.1, P6.4, P6.5
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
-->

---
title: Vendor & Third-Party Risk Management Policy
controls: [CC9.2, P6.1, P6.4, P6.5]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Vendor & Third-Party Risk Management Policy

**Policy Owner:** [CISO / Legal / Head of Operations]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Next Review:** [DATE + 1 YEAR]
**Version:** 1.0

---

## 1. Purpose

This policy governs [COMPANY NAME]'s process for assessing, managing, and monitoring risks associated with third-party vendors and service providers. It supports SOC 2 TSC CC9.2 (Vendor and Partner Risk Management) and Privacy criteria P6.1, P6.4, and P6.5.

## 2. Vendor Classification

| Risk Tier | Definition | Examples | Review Frequency |
|-----------|------------|----------|-----------------|
| **Tier 1 — Critical** | Access to customer PII or production systems | Cloud providers, payment processors, identity providers | Annual |
| **Tier 2 — High** | Significant business dependency, no direct data access | CRM, project management, development tools | Annual |
| **Tier 3 — Standard** | Low dependency, no sensitive data | Office supplies, marketing tools | Every 2 years |

## 3. Vendor Onboarding Process

Before engaging any Tier 1 or Tier 2 vendor, [COMPANY NAME] must complete:

1. **Security Questionnaire:** Vendor completes a security questionnaire (or provides a completed SIG Lite)
2. **SOC 2 Review:** Obtain and review vendor's most recent SOC 2 Type II report (or ISO 27001 certificate)
3. **Privacy Assessment:** For vendors processing personal data, a DPIA is conducted if required
4. **Contract Review:** Legal reviews all contracts for security and privacy requirements
5. **Data Processing Agreement (DPA):** A DPA must be executed before any personal data is shared
6. **Risk Approval:** [CISO / Legal] approves vendor onboarding

## 4. Required Contractual Protections

All vendor contracts for Tier 1 and Tier 2 vendors must include:
- Security incident notification requirement (within 72 hours of discovery)
- Right to audit clause
- Data processing limitations (vendor may not use customer data for secondary purposes)
- Subprocessor change notification requirement
- Secure deletion of data upon termination
- Compliance with applicable data protection laws (GDPR, CCPA, etc.)

## 5. Sub-Processor Management

[COMPANY NAME] maintains a public list of sub-processors who may process customer personal data. The list is available at: [https://[company].com/sub-processors]

Before adding a new sub-processor:
1. Notify customers with [30 days] advance notice per customer DPAs
2. Execute a DPA with the new sub-processor
3. Add the sub-processor to the public list

## 6. Ongoing Vendor Monitoring

Tier 1 vendors are reviewed annually:
- Request updated SOC 2 reports or security attestations
- Review for any security incidents or data breaches reported
- Confirm DPA and security addendum remain current
- Verify vendor's compliance certifications are still valid

## 7. Vendor Inventory

[COMPANY NAME] maintains a Vendor Inventory documenting all Tier 1 and Tier 2 vendors:
- Vendor name and service description
- Risk tier
- Data types accessed (if any)
- DPA status
- Last security review date
- Next review due date

The Vendor Inventory is maintained in [SHARED DRIVE / NOTION / GRC TOOL] and reviewed quarterly.

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
