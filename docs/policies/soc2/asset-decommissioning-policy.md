<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Asset Decommissioning & Disposal Policy
  Framework: SOC 2 TSC — CC6.5, P4.3, C1.2
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
-->

---
title: Asset Decommissioning & Disposal Policy
controls: [CC6.5, P4.3, C1.2]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Asset Decommissioning & Disposal Policy

**Policy Owner:** [CISO / CTO / IT Manager]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Version:** 1.0

---

## 1. Purpose

This policy establishes procedures for the secure decommissioning and disposal of logical and physical assets to prevent unauthorized recovery of sensitive data. It supports SOC 2 TSC CC6.5, P4.3, and C1.2.

## 2. Cloud Asset Decommissioning

### 2.1 EC2 Instances

Before terminating an EC2 instance:
1. Confirm no customer data remains on instance storage (ephemeral storage)
2. Take a final snapshot if needed for audit purposes
3. Terminate instance — AWS securely wipes underlying storage
4. Remove associated security groups, Elastic IPs, and DNS entries
5. Document the decommission in the asset inventory

### 2.2 RDS Databases / Data Stores

Before deleting a database:
1. Confirm data has been migrated or is no longer needed
2. Obtain approval from [Data Owner / Engineering Lead]
3. For customer data: verify customer data deletion has been completed
4. Take a final encrypted snapshot if required for compliance
5. Delete the database instance — specify no final snapshot if data is no longer needed
6. Snapshots are retained per the data retention schedule, then deleted
7. Document the decommission

### 2.3 S3 Buckets

Before deleting an S3 bucket:
1. Confirm all objects are expired or transferred to another location
2. Verify no customer PII remains (or that deletion has been completed per retention policy)
3. Empty and delete the bucket
4. Update bucket policies and access references

### 2.4 IAM Credentials and Service Accounts

When a service is decommissioned:
1. Revoke all associated IAM credentials and access keys immediately
2. Delete associated IAM users, roles, and policies
3. Remove from SSO/IdP if applicable
4. Update any secrets or certificates that referenced the decommissioned service

## 3. Physical Device Decommissioning

### 3.1 Employee Devices (Laptops, Phones)

When an employee departs or a device is retired:
1. Remove MDM enrollment and apply remote wipe
2. Verify wipe completion
3. Remove from asset inventory
4. Recycle through [certified e-waste vendor with certificate of destruction]

### 3.2 Storage Media

| Media Type | Disposal Method |
|------------|----------------|
| SSD | Cryptographic erasure (AES) + physical destruction by certified vendor |
| HDD | Degaussing + physical destruction by certified vendor |
| USB drives | Physical destruction |
| Mobile devices | Factory reset + Remote MDM wipe |
| Paper documents | Cross-cut shredding |

All physical destruction must be performed by or witnessed by [IT / CISO] and documented with a certificate of destruction.

## 4. Decommissioning Log

All decommissioned assets are logged in the Asset Inventory with:
- Asset type and identifier
- Date of decommission
- Disposal method used
- Approver
- Certificate of destruction reference (for physical media)

The decommissioning log is retained for [3 years].

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
