---
> **Provided by AuditCaddie OSS** · [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
> MIT Licensed — free to use, customize, and share. Please keep this footer intact.
---

# Access Control Policy

| | |
|---|---|
| **Company** | [COMPANY NAME] |
| **Version** | 1.0 |
| **Effective Date** | [DATE] |
| **Policy Owner** | [NAME, TITLE] |
| **Approved By** | [CEO / CTO / CISO] |
| **Review Cadence** | Annual |
| **Classification** | Internal |

---

## 1. Purpose

This policy establishes the principles, requirements, and controls governing logical access to [COMPANY NAME]'s information systems, applications, data, and cloud infrastructure. The objective is to ensure that access to sensitive resources is granted based on the principle of least privilege and that access rights are regularly reviewed and revoked when no longer needed.

## 2. Scope

This policy applies to:

- All employees, contractors, consultants, and third-party vendors of [COMPANY NAME]
- All systems, applications, cloud services, and databases owned or operated by [COMPANY NAME]
- All environments: production, staging, development, and corporate

## 3. Roles and Responsibilities

| Role | Responsibility |
|------|---------------|
| **IT / Security Team** | Administer access control systems, enforce this policy, conduct access reviews |
| **People / HR** | Notify IT of new hires, role changes, and terminations within 24 hours |
| **Managers** | Approve access requests for direct reports; escalate privileged access requests |
| **All Employees** | Use only the access granted to their role; report unauthorized access |
| **Policy Owner** | Maintain this policy; conduct annual reviews |

## 4. Access Provisioning

### 4.1 New User Access

All access requests must be:

1. Submitted via [TICKETING SYSTEM / EMAIL / FORM] by the employee's manager
2. Approved by the appropriate system owner before provisioning
3. Provisioned within [X] business days of approval
4. Documented with the business justification for the access level granted

### 4.2 Least Privilege

Access is granted at the minimum level required for the employee to perform their job function. Administrators must not grant broader permissions than the role requires. Wildcard permissions (e.g., `*` in AWS IAM policies) require Security Team approval.

### 4.3 Privileged Access

Access to production systems, root accounts, and administrative consoles:

- Requires explicit Security Team approval
- Must use Multi-Factor Authentication (MFA) at all times
- Must be reviewed quarterly
- Must be time-limited where technically feasible (e.g., AWS IAM roles with session expiry)

## 5. Authentication Requirements

### 5.1 Multi-Factor Authentication (MFA)

MFA is **required** for:

- All user accounts with access to production systems
- All administrative and privileged accounts
- All VPN and remote access connections
- All cloud console access (AWS, GCP, Azure)
- All SaaS tools containing sensitive company or customer data

MFA is **strongly recommended** for all other company accounts.

### 5.2 Password Requirements

All passwords must meet the following minimum standards:

| Requirement | Standard |
|-------------|----------|
| Minimum length | 14 characters |
| Complexity | Uppercase, lowercase, number, and symbol |
| Reuse | Cannot reuse last 12 passwords |
| Maximum age | 90 days (or use passphrase with MFA — no expiry) |
| Sharing | Never shared between individuals or systems |

Passwords must be stored using an approved password manager: [e.g., 1Password, Bitwarden].

### 5.3 SSH Keys and API Keys

- SSH keys must use ED25519 or RSA 4096-bit minimum
- API keys and access tokens must be rotated at least every 90 days
- Keys must never be embedded in source code, documentation, or configuration files
- Secrets must be stored in an approved secrets manager: [e.g., AWS Secrets Manager, HashiCorp Vault]

## 6. Access Reviews

| Review Type | Frequency | Owner |
|-------------|-----------|-------|
| All user access (production) | Quarterly | Security Team |
| Privileged / admin access | Quarterly | Security Team + Manager |
| Third-party / vendor access | Quarterly | Vendor Manager |
| Full access audit (all systems) | Annual | Policy Owner |

Findings from access reviews must be remediated within:
- **High risk** (inactive accounts with privileged access): 24 hours
- **Medium risk** (excess permissions): 5 business days
- **Low risk** (minor scoping corrections): 30 days

## 7. Access Deprovisioning

### 7.1 Termination (Involuntary)

All access must be revoked **within 2 hours** of termination notification from HR.

### 7.2 Resignation (Voluntary)

All access must be revoked on the **last day of employment**.

### 7.3 Role Change

When an employee changes roles, their prior access must be reviewed and revoked if no longer required. New access is granted per Section 4.1.

### 7.4 Deprovisioning Checklist

HR must notify IT/Security of all departing employees. IT/Security must:

- [ ] Disable the user's SSO/identity provider account
- [ ] Revoke all active IAM credentials (AWS access keys, console access)
- [ ] Remove from all GitHub organizations and teams
- [ ] Revoke VPN certificates and sessions
- [ ] Transfer ownership of files and assets
- [ ] Disable email and forward critical communications
- [ ] Document completion in the HR ticket

## 8. Third-Party and Vendor Access

- Vendor access requires a signed NDA and, where applicable, a Data Processing Agreement (DPA)
- Vendor access must be scoped to the minimum required and reviewed quarterly
- Vendor access must be revoked immediately upon contract termination
- Production access for vendors must use time-limited credentials where possible

## 9. Shared and Service Accounts

- Shared accounts are prohibited except for documented system integrations
- Service accounts must have unique credentials and must not be used for human logins
- Service account credentials must be rotated annually or upon personnel changes

## 10. Exceptions

Exceptions to this policy require written approval from the CISO or CTO. All exceptions must be:

- Documented with business justification
- Time-limited (not to exceed 90 days)
- Reviewed at expiry

## 11. Policy Violations

Violations of this policy may result in disciplinary action up to and including termination of employment or contract. Security incidents resulting from policy violations will be escalated to legal counsel as appropriate.

## 12. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [DATE] | [AUTHOR] | Initial version |

---

> **Provided by AuditCaddie OSS**
> This policy template is provided free of charge under the MIT License.
> Customize it for your organization, then generate evidence with AuditCaddie.
>
> 🔗 [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
