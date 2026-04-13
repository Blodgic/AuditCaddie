<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Data Retention & Secure Disposal Policy
  Framework: SOC 2 TSC — P4.1, P4.2, P4.3, C1.2
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
-->

---
title: Data Retention & Secure Disposal Policy
controls: [P4.1, P4.2, P4.3, C1.2]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Data Retention & Secure Disposal Policy

**Policy Owner:** [CISO / Legal / Data Protection Officer]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Next Review:** [DATE + 1 YEAR]
**Version:** 1.0

---

## 1. Purpose

This policy defines how long [COMPANY NAME] retains different categories of data and how data is securely disposed of at the end of its retention period. It supports SOC 2 TSC P4.1–P4.3 and C1.2, and applicable privacy regulations (GDPR, CCPA).

## 2. Data Retention Schedule

### 2.1 Customer Data

| Data Category | Retention Period | Legal Basis | Disposal Method |
|---------------|-----------------|-------------|----------------|
| Customer account data | Duration of customer relationship + [2 years] | Contract | Secure deletion |
| Customer transaction records | [7 years] | Tax/legal requirements | Secure deletion |
| Customer support communications | [3 years] | Legitimate interest | Secure deletion |
| Customer PII (name, email, etc.) | Duration of relationship + [30 days after deletion request] | Contract / Consent | Secure deletion |
| Usage logs and analytics | [1 year] | Legitimate interest | Anonymization or deletion |

### 2.2 Employee and HR Data

| Data Category | Retention Period | Legal Basis |
|---------------|-----------------|-------------|
| Active employee records | Duration of employment + [7 years] | Legal / HR compliance |
| Payroll records | [7 years] | Tax requirements |
| Background check results | [5 years] | Compliance |
| Performance reviews | [3 years after departure] | Legitimate interest |

### 2.3 Security and Audit Logs

| Log Type | Retention Period |
|----------|-----------------|
| AWS CloudTrail | [1 year] |
| Application access logs | [1 year] |
| Security incident records | [3 years] |
| Vulnerability scan results | [2 years] |
| Penetration test reports | [3 years] |
| SOC 2 audit evidence | [5 years] |

### 2.4 Business Records

| Record Type | Retention Period |
|-------------|-----------------|
| Contracts and agreements | [7 years after expiration] |
| Financial records | [7 years] |
| Board minutes | Permanent |
| Insurance policies | [7 years after expiration] |

## 3. Automated Retention Controls

Where possible, retention is enforced automatically:

**AWS S3:**
- Lifecycle policies move data to Glacier after [90 days] and delete after the applicable retention period
- Versioning enabled with [30-day] version expiration

**Databases:**
- Automated purge jobs run [weekly / monthly] to delete records past their retention date
- Purge jobs are logged and results reviewed by [DATA OWNER]

**Application logs:**
- Log retention configured in [CloudWatch Logs] — [1 year] retention policy applied to all log groups

## 4. Customer Data Deletion Requests

When a customer requests deletion of their data (right to erasure under GDPR, or CCPA deletion request):

1. Request received via [privacy@[company].com] or in-product deletion request
2. Identity verified by [SUPPORT / LEGAL]
3. Deletion performed within **30 days** of verified request
4. Confirmation sent to customer
5. Request and confirmation logged

**Exceptions:** Data required to be retained for legal, regulatory, or contractual obligations may be retained beyond the customer's deletion request. The customer is notified of the specific legal basis.

## 5. Secure Disposal Standards

### 5.1 Digital Data

| Storage Type | Disposal Method |
|--------------|----------------|
| AWS S3 | S3 Object Delete API; versioned objects fully deleted; lifecycle policies applied |
| RDS / Database | SQL DELETE statements followed by VACUUM; for full database retirement, final snapshot then instance deletion with no final snapshot bypass |
| EBS Volumes | AWS encrypts EBS by default; deletion of encrypted volume renders data irrecoverable |
| Secrets Manager / Parameter Store | Secret deletion with [7-day] recovery window, then permanent deletion |
| Email and Documents | Permanent deletion from [Google Workspace / Microsoft 365] trash |

### 5.2 Physical Media

Physical storage devices are disposed of by:
- **In-house:** Degaussing and physical destruction for HDDs; physical destruction for SSDs and USB drives
- **Third-party:** Certified data destruction vendor with certificate of destruction provided

### 5.3 End-of-Life Devices

When employee devices are decommissioned:
1. Device is wiped using [Apple Remote Wipe / MDM factory reset / DBAN]
2. Wipe is verified and documented
3. Device is recycled through [certified e-waste vendor]

## 6. Retention Review

The Data Retention Schedule is reviewed annually to:
- Update retention periods based on regulatory changes
- Verify automated deletion mechanisms are functioning
- Confirm all data categories are accounted for

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
