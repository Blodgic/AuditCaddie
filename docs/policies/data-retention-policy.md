---
> **Provided by AuditCaddie OSS** · [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
> MIT Licensed — free to use, customize, and share. Please keep this footer intact.
---

# Data Retention and Disposal Policy

| | |
|---|---|
| **Company** | [COMPANY NAME] |
| **Version** | 1.0 |
| **Effective Date** | [DATE] |
| **Policy Owner** | [NAME, TITLE] |
| **Approved By** | [CEO / CISO / Legal] |
| **Review Cadence** | Annual |
| **Classification** | Internal |

---

## 1. Purpose

This policy defines how long [COMPANY NAME] retains different categories of data and how data is securely disposed of when it is no longer needed. Retaining data longer than necessary increases privacy risk and regulatory exposure. Retaining data too briefly may violate legal obligations.

## 2. Scope

This policy applies to all data created, collected, stored, or processed by [COMPANY NAME], including:
- Customer data and personal information
- Employee data
- Business records and financial data
- System logs and audit trails
- Security and compliance records

## 3. Data Retention Schedule

### 3.1 Customer Data

| Data Type | Retention Period | Basis |
|-----------|-----------------|-------|
| Customer account information | Duration of relationship + 3 years | Contract / legal |
| Customer usage data and logs | 2 years | Business operations |
| Customer support tickets | 3 years | Business operations |
| Customer payment data | [30 days / per PCI DSS if stored] | PCI DSS |
| Customer PII (GDPR/CCPA) | Duration of relationship; deleted within 30 days of termination request | GDPR/CCPA |
| Customer backups | 30 days rolling | Contract / business |

### 3.2 Employee Data

| Data Type | Retention Period | Basis |
|-----------|-----------------|-------|
| Employment records | 7 years after termination | Employment law |
| Payroll records | 7 years | Tax law |
| Background check results | Duration of employment + 1 year | HR policy |
| Performance reviews | 5 years | HR policy |
| Training completion records | Duration of employment + 3 years | Compliance |
| Terminated employee email | 90 days after termination | Business continuity |

### 3.3 Financial and Business Records

| Data Type | Retention Period | Basis |
|-----------|-----------------|-------|
| Contracts and agreements | 7 years after expiry | Legal |
| Financial statements | 7 years | Tax law |
| Accounts payable/receivable | 7 years | Tax law |
| Audit reports (SOC 2, ISO, etc.) | 7 years | Compliance |
| Insurance policies | 7 years after expiry | Legal |

### 3.4 Security and Compliance Records

| Data Type | Retention Period | Basis |
|-----------|-----------------|-------|
| AWS CloudTrail logs | 7 years | SOC 2 / compliance |
| Application audit logs | 3 years | Compliance |
| VPC flow logs | 1 year | Security operations |
| Security incident reports | 7 years | Legal / compliance |
| Vulnerability scan results | 3 years | SOC 2 / compliance |
| Penetration test reports | 7 years | Compliance |
| Access review records | 3 years | SOC 2 / compliance |
| Change management records | 3 years | SOC 2 / compliance |
| HIPAA records (if applicable) | 6 years from creation or last use | HIPAA |

### 3.5 Technical Logs

| Data Type | Retention Period | Location |
|-----------|-----------------|---------|
| Server/application logs | 90 days (hot) + 1 year (cold archive) | CloudWatch / S3 |
| Database query logs | 90 days | RDS |
| Load balancer access logs | 90 days | S3 |
| Backup snapshots (RDS, EBS) | 30 days rolling | AWS Backup |

## 4. Data Deletion and Disposal

### 4.1 Digital Data

When data reaches end of retention:
- Database records: Logical deletion followed by confirmed purge
- S3 / cloud storage: Permanent deletion using AWS S3 delete API (with verification)
- Backup copies: Explicitly deleted from all backup systems within 30 days of retention expiry

Data subject deletion requests (GDPR Article 17 / CCPA) must be fulfilled within **30 calendar days** of receipt, across all systems including backups.

### 4.2 Physical Media

Physical media containing Confidential data must be disposed of by:
- **HDD / SSD**: DOD 5220.22-M overwrite or physical destruction (shredding)
- **Paper documents**: Cross-cut shredding or certified secure disposal vendor
- **USB / removable media**: Physical destruction

A certificate of destruction must be obtained and retained for 3 years when using a third-party disposal vendor.

### 4.3 Endpoint Devices

Devices being retired, reassigned, or returned must be:
- Wiped using approved tools (NIST 800-88 media sanitization standards)
- Verified clean by IT before reassignment or disposal
- Documented in the device disposition log

## 5. Legal Holds

When [COMPANY NAME] anticipates litigation, regulatory investigation, or audit, a **legal hold** may be placed on data that would otherwise be deleted. Legal holds:
- Are issued by Legal counsel
- Suspend normal retention schedules for the identified data
- Are lifted only by Legal counsel when the matter is resolved

## 6. Compliance with Data Subject Rights

Under GDPR, CCPA, and other privacy regulations, individuals have the right to:
- **Access**: Request a copy of their personal data
- **Deletion**: Request deletion of their personal data (subject to legal exceptions)
- **Portability**: Request their data in a portable format

All requests must be fulfilled within 30 days. Requests are tracked in [TICKETING SYSTEM].

## 7. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [DATE] | [AUTHOR] | Initial version |

---

> **Provided by AuditCaddie OSS**
> This policy template is provided free of charge under the MIT License.
> Customize it for your organization, then generate evidence with AuditCaddie.
>
> 🔗 [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
