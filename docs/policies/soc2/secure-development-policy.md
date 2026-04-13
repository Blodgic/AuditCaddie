<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Secure Software Development Policy
  Framework: SOC 2 TSC — CC8.1, CC5.1, CC5.2, CC5.3
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
-->

---
title: Secure Software Development Policy
controls: [CC8.1, CC5.1, CC5.2, CC5.3]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Secure Software Development Policy

**Policy Owner:** [CTO / Head of Engineering]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Next Review:** [DATE + 1 YEAR]
**Version:** 1.0

---

## 1. Purpose

This policy establishes secure software development practices for [COMPANY NAME] to ensure that security is embedded throughout the software development lifecycle (SDLC). It supports SOC 2 TSC CC8.1 (Change Management) and CC5.1–CC5.3 (Control Activities).

## 2. Secure Development Principles

All software development at [COMPANY NAME] follows these principles:
- **Security by design:** Security requirements are defined at the start of development
- **Least privilege:** Code and services are granted only the permissions they need
- **Defense in depth:** Multiple layers of security controls protect systems
- **Fail securely:** System failures default to a secure state
- **Minimize attack surface:** Unnecessary features, endpoints, and permissions are removed

## 3. SDLC Security Requirements

### 3.1 Requirements Phase

- Security requirements are captured alongside functional requirements
- Data flows are documented with classification level for all new features handling PII or sensitive data
- Threat modeling is performed for major new features or architectural changes

### 3.2 Development Phase

**Prohibited in Code:**
- Hardcoded credentials, API keys, passwords, or private keys
- Direct inclusion of unvalidated user input in SQL queries (use parameterized queries)
- Use of deprecated or known-vulnerable cryptographic algorithms (MD5, SHA-1, DES)
- Logging of PII or sensitive data at DEBUG/INFO level
- Disabling of TLS certificate verification

**Required Practices:**
- Secrets managed via [AWS Secrets Manager / Parameter Store / Vault] — never in code or environment files committed to git
- Input validation on all user-supplied data
- Output encoding to prevent XSS
- Authentication and authorization checks on all protected endpoints
- OWASP Top 10 vulnerabilities actively avoided in code reviews

### 3.3 Code Review Phase

All code merged to the main branch must pass peer review:
- At least **[1] approving reviewer** required for standard changes
- At least **[2] approving reviewers** required for security-sensitive changes (auth, encryption, data handling)
- Reviewers must check for security vulnerabilities in addition to functional correctness
- Automated SAST scan must pass: [CodeQL / Semgrep / Snyk Code]

### 3.4 Testing Phase

| Test Type | Tool | Requirement |
|-----------|------|-------------|
| Unit tests | [Jest / pytest / etc.] | Required for new functions |
| Integration tests | — | Required for API endpoints |
| SAST | [CodeQL / Semgrep] | Required — must pass before merge |
| Dependency scanning | [Dependabot / Snyk] | Continuous — critical vulns block merge |
| DAST | [OWASP ZAP] | [Quarterly against staging] |

### 3.5 Deployment Phase

- Deployments to production follow the Change Management Policy
- Infrastructure is managed as code ([Terraform / CDK]) — no manual console changes
- Production and staging environments are separated
- Secrets are injected at runtime from [Secrets Manager] — never baked into container images
- Container images are scanned before deployment ([ECR Enhanced Scanning])

## 4. Third-Party Dependencies

[COMPANY NAME] manages open-source and third-party dependencies:
- All new dependencies must be reviewed for security issues before adoption
- Dependabot (or equivalent) monitors for known vulnerabilities in dependencies
- Critical and High CVEs in dependencies are remediated within the vulnerability SLA
- A software bill of materials (SBOM) is [maintained / generated on release]

## 5. Secrets Management

- All secrets (API keys, database passwords, credentials) are stored in [AWS Secrets Manager / Parameter Store]
- No secrets in source code, Dockerfiles, or CI/CD configuration files
- Secrets are rotated [automatically / every 90 days]
- Access to production secrets is logged and audited
- git-secrets or equivalent is installed on developer machines to prevent accidental commit of secrets

## 6. Environment Separation

| Environment | Access | Data |
|-------------|--------|------|
| **Development** | All engineers | Synthetic/anonymized data only |
| **Staging** | All engineers | Anonymized copy of production schema; no real PII |
| **Production** | Restricted to [list] via [SSM / bastion] | Real customer data |

No engineer has direct database access to production except via documented break-glass procedure.

## 7. Security Training for Developers

All engineers receive:
- Secure coding training upon joining
- Annual refresher (OWASP Top 10 review)
- Access to [security training platform, e.g., Secure Code Warrior]

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
