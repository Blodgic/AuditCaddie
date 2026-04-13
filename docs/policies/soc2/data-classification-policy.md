<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Data Classification & Information Handling Policy
  Framework: SOC 2 TSC — C1.1, C1.2, CC6.1
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
-->

---
title: Data Classification & Information Handling Policy
controls: [C1.1, C1.2, CC6.1]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Data Classification & Information Handling Policy

**Policy Owner:** [CISO / Data Protection Officer]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Next Review:** [DATE + 1 YEAR]
**Version:** 1.0

---

## 1. Purpose

This policy defines how [COMPANY NAME] classifies, handles, and protects information assets based on their sensitivity. It supports SOC 2 TSC C1.1 (Confidential Information Identification), C1.2 (Confidential Information Disposal), and CC6.1 (Logical Access Security).

## 2. Data Classification Levels

### Level 1 — Public

**Definition:** Information approved for public release with no restrictions.

**Examples:** Marketing materials, public documentation, press releases, open source code.

**Handling Requirements:**
- No special handling required
- May be posted publicly without approval

---

### Level 2 — Internal

**Definition:** Information intended for internal use only. Not for public disclosure but has low risk if inadvertently disclosed.

**Examples:** Internal procedures, meeting notes, non-sensitive employee communications, anonymized metrics.

**Handling Requirements:**
- Do not share outside [COMPANY NAME] without business justification
- Store on [COMPANY NAME]-approved systems only
- Do not email to personal accounts

---

### Level 3 — Confidential

**Definition:** Sensitive business information whose unauthorized disclosure could harm [COMPANY NAME] or its customers.

**Examples:** Customer data, business strategy, financial projections, source code, API keys, security configurations, employee PII.

**Handling Requirements:**
- Access limited to employees with a documented business need
- Must be encrypted at rest and in transit
- Must not be stored on personal devices or unmanaged cloud storage
- Must not be shared with third parties without an executed NDA or DPA
- Transmission via email requires encryption where technically feasible

---

### Level 4 — Restricted

**Definition:** The most sensitive information. Unauthorized disclosure could have severe consequences including legal liability, regulatory fines, or significant customer harm.

**Examples:** Customer payment card data (PCI scope), health information (HIPAA scope), authentication credentials (passwords, private keys), Social Security Numbers, breach investigation details.

**Handling Requirements:**
- Access strictly controlled and logged
- Encryption required at all times (at rest and in transit)
- Must only be processed in approved, hardened environments
- Must never be sent via email or stored in unsecured locations
- Handling must comply with applicable regulatory requirements (PCI-DSS, HIPAA, GDPR)

## 3. Customer Data

All customer data is classified as **Confidential (Level 3)** at minimum. Customer data that includes PII is treated as **Restricted (Level 4)**.

[COMPANY NAME] employees must not:
- Access customer data without a legitimate support or engineering need
- Copy customer data to personal or unmanaged storage
- Share customer data with third parties without an executed DPA

## 4. Encryption Standards

| Classification | Encryption at Rest | Encryption in Transit |
|----------------|-------------------|-----------------------|
| Public | Optional | Optional |
| Internal | Recommended | Required |
| Confidential | Required | Required |
| Restricted | Required (AES-256 or equivalent) | Required (TLS 1.2+) |

AWS encryption implementations:
- **S3:** Default encryption enabled (SSE-S3 or SSE-KMS)
- **RDS:** Storage encryption enabled at creation
- **KMS:** Customer-managed keys with automatic rotation enabled
- **Secrets:** AWS Secrets Manager or Parameter Store (SecureString)

## 5. Data Labeling

Where feasible, documents and files containing Confidential or Restricted data should be labeled with the appropriate classification level in the document header or metadata.

## 6. Secure Data Disposal

When data is no longer needed:

| Medium | Disposal Method |
|--------|----------------|
| AWS S3 object | S3 Object Delete + Lifecycle Policy |
| RDS data | SQL DELETE + VACUUM or snapshot deletion |
| EC2 instance storage | Instance termination with encrypted volumes |
| Physical media | Secure wipe (DoD 5220.22-M) or physical destruction |
| Paper documents | Cross-cut shredding |

Customer data deletion requests must be processed within [30 days] of request.

## 7. Handling Violations

Employees who mishandle classified data must report the incident to [CISO / security@[company].com] immediately. Mishandling of Confidential or Restricted data is subject to disciplinary action.

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
