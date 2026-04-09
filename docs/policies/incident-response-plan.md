---
> **Provided by AuditCaddie OSS** · [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
> Apache Licensed 2.0 — free to use, customize, and share. Please keep this attribution intact.
---

# Incident Response Plan

| | |
|---|---|
| **Company** | [COMPANY NAME] |
| **Version** | 1.0 |
| **Effective Date** | [DATE] |
| **Policy Owner** | [NAME, TITLE] |
| **Approved By** | [CEO / CTO / CISO] |
| **Review Cadence** | Annual + after each declared incident |
| **Classification** | Internal — Restricted |

---

## 1. Purpose

This Incident Response Plan (IRP) defines the procedures [COMPANY NAME] follows to detect, contain, eradicate, and recover from security incidents. The goal is to minimize damage, reduce recovery time, and preserve evidence for post-incident analysis and regulatory compliance.

## 2. Scope

This plan applies to all security incidents affecting [COMPANY NAME]'s:
- Cloud infrastructure (AWS, GCP, Azure)
- Corporate systems, SaaS tools, and endpoints
- Customer data, employee data, or proprietary information

## 3. Incident Response Team

| Role | Name | Contact |
|------|------|---------|
| **Incident Commander** | [NAME] | [EMAIL / PHONE] |
| **Security Lead** | [NAME] | [EMAIL / PHONE] |
| **Engineering Lead** | [NAME] | [EMAIL / PHONE] |
| **Legal / Compliance** | [NAME / FIRM] | [EMAIL / PHONE] |
| **Communications Lead** | [NAME] | [EMAIL / PHONE] |
| **Executive Sponsor** | [CEO / CTO] | [EMAIL / PHONE] |

**24/7 Emergency Contact:** [PHONE / SLACK CHANNEL]

## 4. Incident Classification

| Severity | Description | Examples | Response SLA |
|----------|-------------|----------|-------------|
| **P1 — Critical** | Active breach, data exfiltration, ransomware, production down | Attacker in prod, customer data exposed, ransomware deployed | Immediate — 15 min |
| **P2 — High** | Suspected breach, significant vulnerability exploited, service degraded | Unauthorized access detected, critical CVE actively exploited | 1 hour |
| **P3 — Medium** | Policy violation, anomalous activity, minor service impact | Phishing email clicked but no compromise, failed brute-force | 4 hours |
| **P4 — Low** | Precursor event, informational alert, no confirmed impact | Port scan detected, failed login from unknown IP | 24 hours |

## 5. Incident Response Phases

### Phase 1: Detection and Reporting

**Sources of detection:**
- AWS GuardDuty / Security Hub alerts
- CloudWatch alarms
- Employee report via [SLACK CHANNEL / EMAIL]
- Customer report
- External security researcher
- Third-party monitoring service

**Any employee** who suspects a security incident must immediately:
1. Report to [SECURITY EMAIL] or [SLACK CHANNEL]
2. Do **not** attempt to investigate or remediate independently
3. Do **not** discuss the incident externally or on personal devices
4. Preserve any evidence (screenshots, logs, emails)

### Phase 2: Triage and Classification

The Security Lead triages the report within the SLA for the estimated severity and:
- Confirms whether an incident has occurred
- Assigns an initial severity classification (P1–P4)
- Activates the Incident Response Team if P1 or P2
- Opens a dedicated incident channel: `#incident-YYYY-MM-DD-[short-name]`
- Creates an incident ticket in [TICKETING SYSTEM]

### Phase 3: Containment

**Short-term containment** (immediate — stop the bleeding):
- Isolate affected systems from the network
- Revoke compromised credentials immediately
- Block attacker IP addresses / disable exposed endpoints
- Preserve system snapshots and logs before changes

**Long-term containment** (stabilize for investigation):
- Deploy patches or configuration changes to prevent re-entry
- Increase monitoring on adjacent systems
- Notify affected customers if appropriate (legal decision)

### Phase 4: Eradication

- Identify and remove all attacker artifacts (malware, backdoors, rogue accounts)
- Patch or remediate the root cause vulnerability
- Rotate all credentials that may have been exposed
- Confirm attacker no longer has access

### Phase 5: Recovery

- Restore systems from verified clean backups
- Validate system integrity before returning to production
- Monitor for signs of re-compromise for 72 hours minimum
- Gradually restore full service capability

### Phase 6: Post-Incident Review

A blameless post-incident review must occur within **5 business days** of containment. The review produces:

- **Incident Timeline**: What happened, when, and how it was detected
- **Root Cause Analysis**: The technical and process failures that enabled the incident
- **Impact Assessment**: Data exposed, systems affected, customer impact
- **Lessons Learned**: What worked, what didn't
- **Action Items**: Specific remediation tasks with owners and due dates

The review report is retained for 7 years.

## 6. Communication Guidelines

### Internal Communication
- All incident communication happens in the dedicated `#incident-*` Slack channel
- The Incident Commander provides updates every 30 minutes during active P1/P2 incidents
- Executive updates every 2 hours or on material status changes

### External Communication (customers, press, regulators)
- **No external communication** without approval from Legal and the Executive Sponsor
- The Communications Lead drafts all external notifications
- Customer notifications are approved by Legal before sending

### Regulatory Notification Requirements

| Regulation | Notification Requirement |
|------------|--------------------------|
| **GDPR** | Supervisory authority within 72 hours of discovery; individuals if high risk |
| **HIPAA** | Individuals within 60 days; HHS annually; media if 500+ affected in a state |
| **CCPA** | Affected individuals in "expedient time" |
| **SOC 2** | Notify auditor if incident affects controls in audit period |

## 7. Evidence Preservation

The following must be preserved immediately upon incident declaration:

- [ ] AWS CloudTrail logs for the incident time window (download to S3 with retention lock)
- [ ] GuardDuty and Security Hub findings
- [ ] VPC flow logs
- [ ] Application logs from affected systems
- [ ] Screenshots of dashboards at time of detection
- [ ] All communications related to the incident

Evidence must **not** be modified. If systems must be wiped for containment, take forensic snapshots first.

## 8. Incident Playbooks

### Playbook A: Phishing / Credential Compromise

1. Identify the affected account(s) from email headers or IdP logs
2. Immediately revoke all sessions and reset credentials
3. Enable MFA if not already active
4. Check for mail rules, forwarding, or OAuth grants created by attacker
5. Review what data the account had access to
6. Notify affected user; provide phishing awareness training
7. Determine if customer data was accessed

### Playbook B: Ransomware

1. **Immediately isolate** all affected systems from the network — disconnect from internet
2. Do not pay ransom without legal counsel
3. Notify law enforcement: FBI IC3 (ic3.gov)
4. Identify blast radius from backups and CMDB
5. Restore from last verified clean backup
6. Conduct full credential rotation before restoring internet access
7. Engage forensics firm if extent of compromise is unknown

### Playbook C: Data Breach / Unauthorized Data Access

1. Identify what data was accessed and by whom
2. Determine the exposure window (first access → containment)
3. Preserve all access logs before any changes
4. Legal determines notification obligations
5. Prepare breach notification letters
6. Notify regulatory bodies per Section 6 timelines
7. Offer credit monitoring if personal data exposed

### Playbook D: Unauthorized AWS Access

1. Immediately revoke the compromised IAM key or role
2. Check CloudTrail for all API calls made with compromised credentials (extend window by 30 days)
3. Review for: new IAM users, privilege escalation, S3 data downloads, EC2 launches, new Lambda functions
4. Rotate all potentially exposed secrets
5. Check AWS Cost Explorer for unexpected spend (crypto mining indicator)

## 9. Testing and Training

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Tabletop exercise (discussion-based) | Annually | Security Lead |
| Live drill (simulated incident) | Annually | Security Lead |
| Playbook review and update | After each incident + annually | Incident Commander |
| New hire incident response training | At onboarding | HR + Security |

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
