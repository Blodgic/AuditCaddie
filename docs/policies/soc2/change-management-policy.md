<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Change Management Policy
  Framework: SOC 2 TSC — CC5.1, CC5.2, CC5.3, CC8.1, CC3.4
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
-->

---
title: Change Management Policy
controls: [CC5.1, CC5.2, CC5.3, CC8.1, CC3.4]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Change Management Policy

**Policy Owner:** [CTO / Head of Engineering]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Next Review:** [DATE + 1 YEAR]
**Version:** 1.0

---

## 1. Purpose

This policy governs the authorization, development, testing, approval, and implementation of changes to [COMPANY NAME]'s infrastructure, software, and operational procedures. It supports SOC 2 TSC CC8.1 (Change Management), CC5.1–CC5.3 (Control Activities), and CC3.4 (Assessment of Impactful Changes).

## 2. Scope

This policy applies to all changes to:
- Production software and application code
- Cloud infrastructure (AWS, [other])
- Database schemas and data migrations
- Third-party integrations and API configurations
- Security configurations and access control settings
- Operational procedures and runbooks

## 3. Change Types and Approval Requirements

### 3.1 Standard Changes

**Definition:** Pre-approved, low-risk, routine changes following a documented procedure.

**Examples:** Dependency updates with no breaking changes, routine configuration parameter updates, content updates.

**Process:** Can be executed by any authorized engineer following the standard deployment procedure. Must be logged.

### 3.2 Normal Changes

**Definition:** Planned changes requiring assessment, testing, and approval before implementation.

**Examples:** New features, infrastructure changes, schema migrations, access control modifications, new third-party integrations.

**Process:**
1. Engineer opens a pull request (PR) or change request in [GITHUB / TICKETING SYSTEM]
2. PR description includes: what changed, why, risk assessment, test plan, rollback plan
3. Peer code review by at least **[1 / 2] approved reviewers**
4. Automated tests pass in CI/CD pipeline
5. Change is merged to staging for QA testing
6. Engineering Lead / [APPROVER] approves promotion to production
7. Change is deployed to production during [designated change window or standard deployment hours]
8. Post-deployment monitoring for [30 minutes / specified period]

### 3.3 Emergency Changes

**Definition:** Urgent changes required to restore service, remediate a security vulnerability, or prevent significant business impact.

**Examples:** Critical security patches, production outage fixes, active incident remediation.

**Process:**
1. Incident Commander or on-call engineer authorizes the emergency change
2. Minimal testing is performed given the time constraint
3. Change is implemented with at least one peer present (pair-programming/review)
4. Full documentation of the change is completed **within 24 hours** of implementation
5. Post-implementation review is conducted within [5] business days

## 4. Code Review Requirements

### 4.1 Branch Protection Rules

The following branch protection rules are enforced on the `main` / `production` branch:
- **Require pull request reviews before merging:** Minimum [1] approving review
- **Dismiss stale reviews:** Enabled — new commits require re-approval
- **Require status checks to pass:** All CI/CD checks must pass
- **Require signed commits:** [Enabled / Recommended]
- **Restrict who can push to matching branches:** Only [AUTHORIZED GROUP]
- **Require linear history:** [Enabled / Optional]

### 4.2 Code Review Standards

Reviewers must check for:
- Correctness and business logic
- Security vulnerabilities (injection, auth flaws, insecure defaults)
- Sensitive data handling (no hardcoded secrets, no PII in logs)
- Test coverage for new functionality
- Rollback capability

## 5. Testing Requirements

All normal and emergency changes must include a test plan that covers:
- **Unit tests:** All new functions/methods
- **Integration tests:** Interactions with external systems/APIs
- **Regression tests:** Ensure existing functionality is not broken
- **Security testing:** SAST scan for code changes (via [Snyk / CodeQL / Semgrep])

Test results must be documented and pass before production deployment.

## 6. Infrastructure-as-Code

All cloud infrastructure changes must be managed through infrastructure-as-code (IaC):
- **Tool:** [Terraform / AWS CDK / CloudFormation]
- Changes to IaC must follow the same PR and review process as application code
- Drift between IaC definitions and actual infrastructure must be investigated and remediated
- Direct console changes to production infrastructure are prohibited except during emergencies (and must be codified afterward)

## 7. Deployment Process

### 7.1 Deployment Windows

Standard deployments occur during: [BUSINESS HOURS / MON–THU 10AM–4PM [TIMEZONE]]. Deployments are avoided during:
- Major customer events or peak usage periods
- Fridays (unless critical)
- Holidays

### 7.2 Rollback Plan

Every change must have a documented rollback procedure. For software changes, rollback is typically achieved by:
- Reverting the deployment to the previous release
- Re-applying database migration rollback scripts
- Restoring from the last known good backup (for data changes)

## 8. Change Log and Audit Trail

All changes are logged in [GITHUB / JIRA / CHANGE LOG SYSTEM] with:
- Change description and ticket number
- Author and approver(s)
- Date and time of deployment
- Test results
- Rollback procedure
- Post-deployment monitoring results

Change records are retained for a minimum of **[2 years]**.

## 9. Segregation of Duties

To maintain separation between development and production:
- Developers do not have direct push access to the `main` branch
- The same engineer who wrote a critical change should not be the sole approver (unless team size requires an exception, which must be documented)
- Infrastructure provisioning in production requires approval from an authorized operations lead

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
