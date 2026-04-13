<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Incident Response Policy
  Framework: SOC 2 TSC — CC7.3, CC7.4, CC7.5, P6.3, P6.6
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
-->

---
title: Incident Response Policy
controls: [CC7.3, CC7.4, CC7.5, P6.3, P6.6]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Incident Response Policy

**Policy Owner:** [CISO / Head of Engineering]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Next Review:** [DATE + 1 YEAR]
**Version:** 1.0

---

## 1. Purpose

This policy establishes [COMPANY NAME]'s approach to detecting, responding to, and recovering from security incidents. It supports SOC 2 TSC CC7.3 (Security Event Evaluation), CC7.4 (Incident Response Program), CC7.5 (Security Incident Recovery), and privacy criteria P6.3 and P6.6 (breach notification).

## 2. Scope

This policy applies to all security events affecting [COMPANY NAME]'s systems, infrastructure, customer data, and employees. It includes:
- Unauthorized access to systems or data
- Malware infections or ransomware
- Data breaches or suspected exposure of customer PII
- Denial of service attacks
- Insider threats or policy violations
- Physical security incidents affecting data

## 3. Incident Classification

### Severity Levels

| Severity | Description | Examples | Response SLA |
|----------|-------------|----------|--------------|
| **P1 — Critical** | Active breach or significant data exposure | Confirmed data exfiltration, ransomware, production system compromise | Immediate (< 1 hour) |
| **P2 — High** | Potential breach or significant vulnerability | Suspected unauthorized access, AWS credential compromise, GuardDuty high finding | < 4 hours |
| **P3 — Medium** | Security event requiring investigation | Failed brute force, anomalous access patterns, phishing attempt | < 24 hours |
| **P4 — Low** | Minor security event or policy violation | Accidental access to wrong data, policy violation, low-severity GuardDuty finding | < 72 hours |

## 4. Incident Response Team

### 4.1 Roles and Responsibilities

| Role | Responsibility |
|------|----------------|
| **Incident Commander** | [CISO / Engineering Lead] — overall coordination and decision-making |
| **Technical Lead** | [Senior Engineer] — technical investigation and containment |
| **Communications Lead** | [CEO / Legal] — internal and external communications |
| **Privacy Officer** | [Legal / DPO] — breach notification and regulatory requirements |

### 4.2 Contact Information

- **Security Incident Hotline:** [security@[company].com]
- **On-Call Escalation:** [PagerDuty / phone number]
- **Legal Counsel:** [LEGAL CONTACT]

## 5. Incident Response Phases

### Phase 1: Detection and Identification

**Sources of incident detection:**
- AWS GuardDuty findings (automated alerting via SNS/PagerDuty)
- CloudWatch alarms (unauthorized API calls, root account usage)
- Endpoint detection and response (EDR) alerts
- Employee reports to [security@[company].com]
- Customer reports or third-party notifications

**Identification steps:**
1. Acknowledge the alert within the response SLA for the detected severity
2. Confirm the event is a real incident (not a false positive)
3. Assign an Incident Commander and open an incident ticket in [TICKETING SYSTEM]
4. Create a dedicated incident channel in [Slack / Teams]: `#incident-[date]-[brief-description]`

### Phase 2: Containment

**Immediate containment actions (within P1/P2 SLA):**
- Isolate affected systems (revoke IAM credentials, stop EC2 instances, block network access)
- Preserve evidence: take memory dumps and forensic snapshots before remediation
- Revoke compromised credentials immediately
- Enable enhanced logging on affected systems

**Containment decisions are made by the Incident Commander** and documented in the incident ticket.

### Phase 3: Eradication

1. Identify the root cause of the incident
2. Remove malware, backdoors, or unauthorized access points
3. Patch or remediate the vulnerability that allowed the incident
4. Verify eradication before proceeding to recovery

### Phase 4: Recovery

1. Restore affected systems from clean backups or rebuild from infrastructure-as-code
2. Verify system integrity before returning to production
3. Monitor systems closely for [48-72] hours after recovery
4. Document all recovery steps taken

### Phase 5: Post-Incident Review

A post-incident review is required for all P1 and P2 incidents within **5 business days** of incident closure. The review must document:
- Timeline of events
- Root cause analysis
- What worked well in the response
- Identified gaps or improvement areas
- Action items with owners and due dates

Post-incident review reports are retained for [3 years] and shared with the [Security Committee / Leadership].

## 6. Privacy Breach Assessment

### 6.1 Breach Determination

When an incident involves personal data, the Privacy Officer must assess:
- What personal data was affected?
- How many individuals are affected?
- What is the risk to affected individuals?
- Does the incident qualify as a "breach" under applicable regulations?

### 6.2 Regulatory Notification Timelines

| Regulation | Notification Requirement |
|------------|--------------------------|
| **GDPR** | Supervisory authority: within 72 hours of discovery. Individuals: without undue delay if high risk. |
| **CCPA** | Affected California residents: without unreasonable delay |
| **[STATE BREACH LAW]** | [APPLICABLE TIMELINE] |
| **Contractual** | Per customer DPAs and agreements |

### 6.3 Customer Notification

Customers affected by a breach will be notified via [email / in-app notification] with:
- A description of what occurred
- What data was affected
- Steps [COMPANY NAME] is taking
- Recommended actions for affected customers
- A point of contact for questions

## 7. Evidence Preservation

All incident-related evidence must be preserved and must not be modified or destroyed during an active investigation. Evidence includes:
- CloudTrail logs
- VPC flow logs
- EC2/container logs
- AWS Config snapshots
- GuardDuty findings
- Application logs

Evidence retention: minimum **1 year** for all incidents; minimum **3 years** for P1/P2 incidents.

## 8. Communication Guidelines

### Internal Communications

Incident details are shared on a need-to-know basis. The incident channel and ticket are the authoritative sources. Avoid communicating incident details via unsecured channels (e.g., personal email, public Slack).

### External Communications

All external communications about incidents (to customers, regulators, media, or the public) must be reviewed and approved by [LEGAL / CEO] before sending. No employee should make unauthorized public statements about a security incident.

## 9. Testing the Incident Response Plan

[COMPANY NAME] conducts at least **one tabletop exercise per year** to test this plan. Results are documented and used to improve the plan. The exercise scenarios should include:
- Ransomware/data exfiltration scenario
- Insider threat scenario
- Third-party/supply chain compromise

---

## Appendix A: Incident Response Checklist

**P1 Immediate Actions (first 60 minutes):**
- [ ] Alert acknowledged and Incident Commander assigned
- [ ] Incident channel opened
- [ ] Affected systems identified and isolated
- [ ] Credentials revoked
- [ ] Evidence preserved (snapshots, logs)
- [ ] Leadership notified
- [ ] Privacy Officer engaged if personal data affected
- [ ] Legal notified if breach likely

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
