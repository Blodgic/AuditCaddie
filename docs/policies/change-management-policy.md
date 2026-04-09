---
> **Provided by AuditCaddie OSS** · [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
> Apache Licensed 2.0 — free to use, customize, and share. Please keep this attribution intact.
---

# Change Management Policy

| | |
|---|---|
| **Company** | [COMPANY NAME] |
| **Version** | 1.0 |
| **Effective Date** | [DATE] |
| **Policy Owner** | [NAME, TITLE] |
| **Approved By** | [CTO / CISO] |
| **Review Cadence** | Annual |
| **Classification** | Internal |

---

## 1. Purpose

This policy defines how [COMPANY NAME] plans, reviews, approves, implements, and validates changes to its production systems, infrastructure, and applications. Controlled change management reduces the risk of unplanned outages, security vulnerabilities, and data loss.

## 2. Scope

This policy applies to all changes to:
- Production cloud infrastructure (AWS, GCP, Azure)
- Production databases and data pipelines
- Application code deployed to production
- Network configuration and security groups
- Authentication systems and identity providers
- Third-party integrations and API configurations

Development and staging environments are exempt but encouraged to follow the same practices.

## 3. Change Types

| Type | Description | Approval Required | Lead Time |
|------|-------------|------------------|-----------|
| **Standard** | Pre-approved, low-risk changes following a documented runbook | Automated / pre-approved | None |
| **Normal** | Planned changes with known risk and documented rollback plan | Peer review + Engineering Lead | 48 hours |
| **Major** | High-risk or large-scope changes affecting multiple systems | Engineering Lead + CTO | 1 week |
| **Emergency** | Urgent changes required to resolve a P1 incident or critical security issue | On-call Lead (post-hoc review within 24h) | Immediate |

## 4. Change Requirements

All Normal and Major changes must include:

- [ ] **Description**: What is changing and why
- [ ] **Risk Assessment**: What could go wrong, and how likely is it
- [ ] **Testing Evidence**: Confirmation the change was tested in staging
- [ ] **Rollback Plan**: Step-by-step instructions to revert the change
- [ ] **Deployment Window**: Scheduled time with low user impact
- [ ] **Success Criteria**: How to verify the change succeeded
- [ ] **Owner**: Who is responsible for implementation and monitoring

## 5. Code Change Process

All changes to application code must follow this process:

1. **Branch**: Create a feature branch from `main` — no direct commits to `main`
2. **Develop**: Write code following secure coding standards
3. **Test**: Write or update tests; all tests must pass
4. **Pull Request**: Open a PR with description of what changed and why
5. **Peer Review**: At least **one** peer review and approval required (two for Major changes)
6. **Security Review**: Security Team review required for changes affecting authentication, authorization, encryption, or external data exposure
7. **Merge**: Merge to `main` only after all approvals
8. **Deploy**: Deploy via CI/CD pipeline — no manual deployments to production
9. **Monitor**: Monitor error rates, latency, and logs for 30 minutes post-deployment

### Branch Protection Requirements

The `main` branch must have the following GitHub branch protection rules configured:
- Require pull request reviews before merging (minimum 1 reviewer)
- Dismiss stale pull request approvals when new commits are pushed
- Require status checks to pass (CI tests, SAST scan)
- Restrict who can push directly to `main`
- No force pushes permitted

## 6. Infrastructure Change Process

All changes to cloud infrastructure must:

1. Be defined as code (Terraform, CloudFormation, CDK) — no manual console changes in production
2. Be reviewed by a peer familiar with the infrastructure
3. Include a `terraform plan` / dry-run output in the PR
4. Be applied via CI/CD pipeline with audit logging
5. Be validated post-apply with automated or manual smoke tests

## 7. Emergency Changes

When an emergency change is required (e.g., active incident response):

1. Verbal approval from on-call Engineering Lead or CTO
2. Change is implemented immediately
3. **Post-hoc documentation** submitted within 24 hours of the change
4. Change reviewed in the next change review meeting

Emergency changes must not be used to bypass normal process for non-emergency work.

## 8. Change Freeze Periods

Changes to production are restricted during:
- [X days before / after major product releases]
- [Holiday periods as defined by leadership]
- [Audit periods — coordinate with Security Team]

Emergency changes are exempt from freeze periods with CTO approval.

## 9. Change Log

All changes must be logged in [TICKETING SYSTEM / CHANGELOG] with:
- Change ID
- Description
- Requester and approver
- Date and time of implementation
- Outcome (success / rollback)

The change log is retained for 3 years and is available to auditors upon request.

## 10. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [DATE] | [AUTHOR] | Initial version |

---

> **Provided by AuditCaddie OSS**
> This policy template is provided free of charge under the Apache License 2.0.
> Customize it for your organization, then generate evidence with AuditCaddie.
>
> 🔗 [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
