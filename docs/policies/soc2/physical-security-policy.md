<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Physical Security Policy
  Framework: SOC 2 TSC — CC6.4
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
-->

---
title: Physical Security Policy
controls: [CC6.4]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Physical Security Policy

**Policy Owner:** [COO / CISO / Office Manager]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Version:** 1.0

---

## 1. Purpose

This policy establishes physical security requirements to protect [COMPANY NAME]'s facilities, equipment, and information assets from unauthorized physical access. It supports SOC 2 TSC CC6.4 (Physical Access Restrictions).

## 2. Cloud Infrastructure Physical Security

[COMPANY NAME] hosts its production infrastructure on AWS. Physical security controls for data centers are:
- Managed entirely by AWS
- Covered by AWS's SOC 2 Type II certification (available via AWS Artifact)
- Audited by independent third parties annually

**AWS Physical Security Controls (per AWS documentation):**
- Perimeter access controls, 24/7 security staff, CCTV monitoring
- Multi-factor physical access for data center entry
- Environmental controls (fire suppression, cooling, power redundancy)

Customers and employees of [COMPANY NAME] do not have physical access to AWS data centers.

## 3. Office and Workspace Security

### 3.1 Office Access

- Office entrance is secured with [keycard / keypad / other access control]
- Only employees and authorized visitors may enter the office
- Visitor access requires: sign-in log, escort by an employee, visitor badge
- Access is revoked immediately upon employee departure

### 3.2 Clean Desk Policy

Employees must:
- Lock screens when leaving their workstation unattended
- Not leave confidential documents or sensitive information visible on desks when unoccupied
- Store sensitive physical documents in locked drawers or filing cabinets
- Shred confidential documents using cross-cut shredders before disposal

### 3.3 Remote Work

For employees working remotely:
- Work in private environments when handling confidential information
- Use VPN when connecting to company systems from public networks
- Apply screen privacy filters when working in public spaces
- Lock screens when not in use

## 4. Equipment Security

- Company equipment is tagged with [COMPANY NAME] asset tags
- Laptops are covered by full-disk encryption (see Endpoint Protection Policy)
- Loss or theft of company equipment must be reported to [IT / CISO] within [2 hours]
- Visitor devices are not connected to the internal corporate network ([guest WiFi] is available)

## 5. Physical Media

- Physical media (USB drives, external hard drives) containing confidential data must be encrypted
- Removal of physical media from the office must be approved by [Manager]
- Physical media is tracked in the asset inventory
- Physical media is securely disposed of per the Data Retention & Disposal Policy (cross-cut shredding, degaussing, or certified destruction)

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
