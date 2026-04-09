---
> **Provided by AuditCaddie OSS** · [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
> MIT Licensed — free to use, customize, and share.
---

# AuditCaddie OSS — Free Policy Library

**7 production-ready compliance policy templates. Customize, sign, and submit to your auditor.**

All documents are MIT licensed — free to use, share, and modify. Keep the footer attribution intact to help grow the open source GRC community.

---

## Policy Templates

| Document | Frameworks | Description |
|----------|-----------|-------------|
| [Access Control Policy](policies/access-control-policy.md) | SOC 2 CC6, ISO 27001 A.5.15, NIST PR.AA | User provisioning, MFA, password standards, access reviews, deprovisioning |
| [Information Security Policy](policies/information-security-policy.md) | SOC 2, ISO 27001, NIST | Top-level security policy, data classification, employee responsibilities |
| [Incident Response Plan](policies/incident-response-plan.md) | SOC 2 CC7, ISO 27001 A.5.24, HIPAA §164.308(a)(6) | 6-phase IR process, playbooks for phishing/ransomware/breach/AWS, breach notification |
| [Vulnerability Management Policy](policies/vulnerability-management-policy.md) | SOC 2 CC7.1, ISO 27001 A.8.8, NIST ID.RA | Scanning, patching SLAs, pen test schedule, risk acceptance |
| [Change Management Policy](policies/change-management-policy.md) | SOC 2 CC8.1, ISO 27001 A.8.32 | PR review process, branch protection, IaC requirements, emergency changes |
| [Data Retention and Disposal Policy](policies/data-retention-policy.md) | SOC 2 P6, ISO 27001 A.8.10, HIPAA, GDPR | Retention schedules by data type, deletion procedures, legal holds |
| [Business Continuity Plan](policies/business-continuity-plan.md) | SOC 2 A1, ISO 27001 A.5.29, NIST RC | RTO/RPO targets, backup architecture, DR scenarios, runbooks |
| [Acceptable Use Policy](policies/acceptable-use-policy.md) | SOC 2, ISO 27001 A.6.2 | Permitted and prohibited use of company systems, devices, and data |
| [Vendor Security Questionnaire](policies/vendor-security-questionnaire.md) | SOC 2 CC9, ISO 27001 A.5.19 | Scored assessment for third-party vendor due diligence |

---

## How to Use These Templates

1. **Download** the policy markdown file
2. **Find and replace** all `[PLACEHOLDER]` fields with your company's specifics
3. **Review** with your legal counsel for jurisdiction-specific requirements
4. **Sign and date** the document (digital signature or wet signature)
5. **Run AuditCaddie** to generate supporting technical evidence
6. **Submit** to your auditor with the AuditCaddie evidence package

### Pro tip: Use AuditCaddie AI to customize faster

In AuditCaddie OSS, go to **Policies → Generate Policy Document**, paste a description of your company and the policy you need, and the AI will generate a customized version in seconds using GPT-4o or Claude Sonnet.

---

## Compliance Framework Mapping

| Policy | SOC 2 | ISO 27001 | NIST CSF | HIPAA |
|--------|-------|-----------|----------|-------|
| Access Control | CC6.1, CC6.2, CC6.3 | A.5.15, A.8.5 | PR.AA-1 | §164.308(a)(3), §164.312(a) |
| Information Security | CC1.2, CC2.1 | A.5.1 | GV.OC-1 | §164.308(a)(1) |
| Incident Response | CC7.3, CC7.4, CC7.5 | A.5.24, A.5.26 | RS.MA-1, DE.CM-1 | §164.308(a)(6) |
| Vulnerability Mgmt | CC7.1, CC7.2 | A.8.8, A.8.7 | ID.RA-1, DE.CM-1 | §164.308(a)(1) |
| Change Management | CC8.1 | A.8.32 | PR.IP-1 | §164.308(a)(1) |
| Data Retention | P6.1, P6.4 | A.8.10 | PR.DS-3 | §164.310(d)(2), §164.316(b)(2) |
| Business Continuity | A1.1, A1.2 | A.5.29, A.5.30 | RC.RP-1, RC.BC-1 | §164.308(a)(7) |
| Acceptable Use | CC6.2 | A.6.2, A.8.19 | PR.AT-1 | §164.308(a)(5) |
| Vendor Assessment | CC9.2 | A.5.19, A.5.21 | ID.SC-1 | §164.308(b)(1) |

---

## Need More?

- **Frameworks**: See the [templates/](../templates/) directory for YAML compliance templates (SOC 2, NIST CSF, ISO 27001, HIPAA, Vendor Assessment)
- **Custom policies**: Use AuditCaddie's AI policy generator for custom documents not listed here
- **Enterprise**: [auditcaddie.com/pricing](https://auditcaddie.com/pricing) — team sharing, Fieldguide integration, auditor portal

---

> **AuditCaddie OSS** — Free compliance infrastructure for everyone.
> [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
