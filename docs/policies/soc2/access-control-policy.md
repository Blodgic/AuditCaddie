<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Access Control Policy
  Framework: SOC 2 TSC — CC6.1, CC6.2, CC6.3
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
  Usage:     Replace all [PLACEHOLDERS] with your organization's information.
-->

---
title: Access Control Policy
controls: [CC6.1, CC6.2, CC6.3]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Access Control Policy

**Policy Owner:** [CISO / Head of Engineering / IT Manager]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Next Review:** [DATE + 1 YEAR]
**Version:** 1.0

---

## 1. Purpose

This Access Control Policy establishes the requirements for managing logical access to [COMPANY NAME]'s information systems, cloud infrastructure, and customer data. It supports SOC 2 Trust Services Criteria CC6.1 (Logical Access Security), CC6.2 (User Registration and Access Control), and CC6.3 (Role-Based Access Management).

## 2. Scope

This policy applies to all:
- Employees, contractors, and service accounts with access to [COMPANY NAME] systems
- Cloud infrastructure (AWS, [OTHER CLOUD PROVIDERS])
- Internal systems, development tools, and third-party SaaS applications
- Customer and production data environments

## 3. Access Control Principles

### 3.1 Least Privilege

All users and service accounts are granted only the minimum permissions required to perform their job function. Access rights are reviewed and tightened over time as roles are better understood.

### 3.2 Need to Know

Access to sensitive data and systems is restricted to those with a documented business need. Customer data is never accessed without a legitimate support, engineering, or compliance purpose.

### 3.3 Separation of Duties

Critical functions are divided among multiple individuals to reduce the risk of fraud or error. No single individual should have unchecked end-to-end control over a sensitive process.

## 4. User Access Lifecycle

### 4.1 Access Provisioning (Onboarding)

When a new employee or contractor joins [COMPANY NAME]:
1. [HR / People Operations] initiates the onboarding process
2. The hiring manager submits an access request specifying the required systems and role
3. [IT / Engineering Lead] provisions access based on the approved role profile
4. Access is provisioned before or on the employee's first day
5. Multi-factor authentication (MFA) is enrolled during the first session

All access provisioning is logged in [TICKETING SYSTEM, e.g., Jira / GitHub Issues].

### 4.2 Access Changes (Role Changes / Transfers)

When an employee changes roles or teams:
1. The manager notifies [HR] and [IT] within 2 business days
2. Access not required in the new role is revoked within [5] business days
3. New access required for the new role is provisioned per the normal request process

### 4.3 Access Deprovisioning (Offboarding)

When an employee or contractor leaves [COMPANY NAME]:
1. [HR] triggers the offboarding checklist on or before the last day
2. [IT / Engineering] revokes all access within [24] hours of departure:
   - Disable SSO/IdP account ([Okta / Google Workspace / other])
   - Revoke AWS IAM credentials
   - Revoke GitHub access
   - Disable all SaaS application accounts
   - Rotate any shared credentials known to the departing employee
3. Access revocation is confirmed and logged

## 5. Authentication Requirements

### 5.1 Multi-Factor Authentication (MFA)

MFA is **required** for:
- All cloud console access (AWS, GCP, Azure)
- All SSO-protected applications
- Remote access (VPN, if applicable)
- Code repository access (GitHub/GitLab)
- All privileged accounts

MFA is **strongly recommended** for all other systems.

### 5.2 Password Standards

Passwords must meet the following requirements (aligned to NIST SP 800-63B):
- Minimum length: **14 characters**
- No mandatory complexity rules (length is the primary control)
- No periodic rotation unless compromise is suspected
- Must not match the top 100,000 common passwords
- Must be unique (not reused from other services)

A password manager ([1Password / Bitwarden / other]) is provided to all employees.

### 5.3 Shared and Service Accounts

Shared accounts are prohibited except where technically unavoidable. Where shared accounts exist, they must be:
- Documented in the system inventory
- Protected by MFA where possible
- Reviewed quarterly for continued necessity
- Immediately updated when any authorized user departs

Service accounts must:
- Follow the least-privilege principle
- Use long, randomly generated credentials stored in [secrets manager]
- Never be used for interactive human login

## 6. AWS IAM Standards

### 6.1 IAM User Configuration

- No root account access keys (root keys are permanently deleted)
- Root account MFA is enabled
- IAM users are created only for humans and service accounts with a documented need
- All IAM users with console access have MFA enabled
- AWS IAM Identity Center (SSO) is preferred over individual IAM users

### 6.2 IAM Policies

- Permissions are granted via IAM groups/roles, never directly to individual users
- Wildcard (`*`) actions or resources in policies require documented justification
- Service Control Policies (SCPs) are used to prevent privilege escalation in multi-account setups
- IAM policies are reviewed when roles change

### 6.3 Access Key Rotation

- IAM access keys are rotated at least every **90 days**
- Unused access keys older than 90 days are disabled and deleted
- Automated alerts are configured in [CloudWatch / AWS Config] for keys approaching 90 days

## 7. Access Reviews

Quarterly access reviews are conducted to ensure:
- All users have access appropriate to their current role
- No terminated users retain access
- Privileged accounts are still necessary and appropriately scoped

Access reviews are documented in [TICKETING SYSTEM] and signed off by the relevant system owner. Findings requiring remediation are tracked to closure.

## 8. Privileged Access

### 8.1 Privileged Account Controls

Accounts with administrator or superuser privileges must:
- Be individually assigned (no shared admin accounts)
- Use a separate account from the user's day-to-day account where possible
- Be subject to enhanced logging and monitoring
- Be reviewed monthly for continued necessity

### 8.2 Break-Glass Accounts

Emergency access accounts ("break-glass") must:
- Be documented in the system inventory
- Have credentials stored in [secrets manager / sealed envelope]
- Trigger an automated alert when used
- Be reviewed after each use with a post-incident review

## 9. Remote Access

Remote access to production systems must be through [VPN / bastion host / AWS Systems Manager Session Manager]. Direct SSH/RDP access to production instances from the public internet is prohibited.

## 10. Policy Enforcement and Violations

Violations of this policy are subject to disciplinary action up to and including termination. Violations involving unauthorized access to customer data may also result in civil or criminal liability.

All violations must be reported to [CISO / security@[company].com] immediately.

---

## Appendix A: Access Request Form Template

| Field | Value |
|-------|-------|
| Requestor Name | |
| System / Application | |
| Access Level Requested | |
| Business Justification | |
| Manager Approval | |
| Date Requested | |
| Date Provisioned | |
| Provisioned By | |

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
