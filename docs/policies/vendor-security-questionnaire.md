---
> **Provided by AuditCaddie OSS** · [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
> Apache Licensed 2.0 — free to use, customize, and share. Please keep this attribution intact.
---

# Vendor Security Assessment Questionnaire

| | |
|---|---|
| **Issuing Company** | [YOUR COMPANY NAME] |
| **Vendor Name** | [VENDOR NAME] |
| **Assessment Date** | [DATE] |
| **Completed By** | [VENDOR CONTACT, TITLE] |
| **Reviewed By** | [YOUR SECURITY TEAM MEMBER] |
| **Risk Tier** | ☐ Critical  ☐ High  ☐ Standard |

---

## Instructions

Please complete all sections applicable to your service. For each question, provide a Yes/No/Partial answer and a brief explanation. Attach supporting documentation (SOC 2 report, ISO certificate, penetration test summary) where indicated.

**Scoring:** Critical and High tier vendors must achieve a minimum score of 80% to be approved. Standard tier: 60%.

---

## Section 1: Security Certifications and Compliance

| # | Question | Response | Evidence |
|---|----------|----------|---------|
| 1.1 | Do you hold a current SOC 2 Type II certification? | | |
| 1.2 | If yes, which Trust Service Criteria are covered? (Security, Availability, Confidentiality, Privacy, Processing Integrity) | | |
| 1.3 | Is your SOC 2 report within the last 12 months? If older, do you have a bridge letter? | | |
| 1.4 | Do you hold an ISO 27001 certification? What is the scope and expiry date? | | |
| 1.5 | Do you hold any other relevant certifications? (PCI DSS, HIPAA, FedRAMP, CSA STAR) | | |
| 1.6 | Are you GDPR compliant? Do you offer a DPA (Data Processing Agreement)? | | |
| 1.7 | Are you CCPA compliant? How do you handle data subject deletion requests? | | |

**Supporting documents requested:** SOC 2 Type II report (under NDA), ISO 27001 certificate, DPA

---

## Section 2: Data Handling and Protection

| # | Question | Response | Evidence |
|---|----------|----------|---------|
| 2.1 | What categories of data do you collect and process on behalf of customers? | | |
| 2.2 | Where is customer data stored? (Countries / AWS regions) | | |
| 2.3 | Is customer data logically or physically separated from other customers? | | |
| 2.4 | How is customer data encrypted at rest? (Algorithm, key length) | | |
| 2.5 | How is customer data encrypted in transit? (TLS version minimum) | | |
| 2.6 | Do you offer customer-managed encryption keys (BYOK / HYOK)? | | |
| 2.7 | What is your data retention policy for customer data? | | |
| 2.8 | How is customer data deleted upon contract termination? What is the timeline? | | |
| 2.9 | Are backups encrypted? Where are they stored? | | |

---

## Section 3: Access Controls

| # | Question | Response | Evidence |
|---|----------|----------|---------|
| 3.1 | Which of your employees can access customer data? How many? | | |
| 3.2 | What controls govern employee access to customer data? | | |
| 3.3 | Do you require customer consent before accessing customer environments for support? | | |
| 3.4 | Is all employee access to production systems protected by MFA? | | |
| 3.5 | Do you use SSO for internal system access? | | |
| 3.6 | How do you manage privileged/admin access? (PAM, time-limited, session recording) | | |
| 3.7 | How frequently do you review and audit user access to customer data? | | |

---

## Section 4: Subprocessors

| # | Question | Response | Evidence |
|---|----------|----------|---------|
| 4.1 | Do you use subprocessors (third parties) who may access customer data? | | |
| 4.2 | Can you provide your current subprocessor list? | | |
| 4.3 | How do you notify customers of subprocessor changes? | | |
| 4.4 | Do your subprocessors have equivalent security and privacy requirements? | | |

**Supporting documents requested:** Subprocessor list or DPA subprocessor annex

---

## Section 5: Incident Response

| # | Question | Response | Evidence |
|---|----------|----------|---------|
| 5.1 | Do you have a documented Incident Response Plan? | | |
| 5.2 | What is your SLA for notifying customers of security incidents affecting their data? | | |
| 5.3 | What is your escalation contact for reporting a suspected incident? | | |
| 5.4 | Have you experienced any security incidents or data breaches in the past 3 years? | | |
| 5.5 | If yes, briefly describe what happened and the remediation taken. | | |
| 5.6 | Have you had any SOC 2 audit exceptions or qualified opinions? | | |

---

## Section 6: Business Continuity and Availability

| # | Question | Response | Evidence |
|---|----------|----------|---------|
| 6.1 | What is your contractual uptime SLA? | | |
| 6.2 | What was your actual uptime over the last 12 months? (Provide status page link) | | |
| 6.3 | What is your RTO and RPO for major service outages? | | |
| 6.4 | Do you have a documented BCP/DR plan? When was it last tested? | | |
| 6.5 | What happens to customer data if you cease operations? | | |

---

## Section 7: Vulnerability Management

| # | Question | Response | Evidence |
|---|----------|----------|---------|
| 7.1 | Do you conduct annual penetration tests by an independent third party? | | |
| 7.2 | Can you share the executive summary or attestation letter from your most recent pen test? | | |
| 7.3 | What is your SLA for patching critical vulnerabilities? | | |
| 7.4 | Do you have a vulnerability disclosure or bug bounty program? | | |

---

## Section 8: Overall Risk Rating

**Assessor to complete:**

| Domain | Score (0–10) | Weight | Weighted Score |
|--------|-------------|--------|---------------|
| Certifications & Compliance | | 20% | |
| Data Handling & Protection | | 25% | |
| Access Controls | | 20% | |
| Incident Response | | 15% | |
| Business Continuity | | 10% | |
| Vulnerability Management | | 10% | |
| **Total** | | | **/10** |

**Risk Rating:**
- 8.0–10.0: ✅ Approved — Low Risk
- 6.0–7.9: ⚠️ Conditional Approval — document compensating controls
- Below 6.0: ❌ Not Approved — remediation required before approval

**Assessor Notes:**

---

**Approval:**

| | |
|---|---|
| Assessed by | [NAME, DATE] |
| Approved by | [SECURITY LEAD / CISO, DATE] |
| Next review date | [DATE] |

---

> **Provided by AuditCaddie OSS**
> This questionnaire template is provided free of charge under the Apache License 2.0.
> Customize it for your organization, then generate evidence with AuditCaddie.
>
> 🔗 [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
