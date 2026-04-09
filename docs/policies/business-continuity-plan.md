---
> **Provided by AuditCaddie OSS** · [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
> Apache Licensed 2.0 — free to use, customize, and share. Please keep this attribution intact.
---

# Business Continuity and Disaster Recovery Plan

| | |
|---|---|
| **Company** | [COMPANY NAME] |
| **Version** | 1.0 |
| **Effective Date** | [DATE] |
| **Policy Owner** | [NAME, TITLE] |
| **Approved By** | [CEO / CTO] |
| **Review Cadence** | Annual + after each declared disaster |
| **Classification** | Internal — Restricted |

---

## 1. Purpose

This Business Continuity and Disaster Recovery (BCP/DR) Plan ensures [COMPANY NAME] can continue critical operations and restore systems to normal following a disruptive event. This plan covers natural disasters, infrastructure failures, cyber attacks, and other events that threaten operational continuity.

## 2. Recovery Objectives

| System | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) |
|--------|------------------------------|-------------------------------|
| Production application | [4 hours] | [1 hour] |
| Production database | [4 hours] | [1 hour] |
| Customer authentication | [2 hours] | [30 minutes] |
| Corporate email / Slack | [8 hours] | [24 hours] |
| Development environment | [24 hours] | [24 hours] |
| Internal tools | [24 hours] | [24 hours] |

*RTO: Maximum time to restore service. RPO: Maximum data loss acceptable.*

## 3. Backup Architecture

### 3.1 Database Backups (RDS)
- **Automated backups**: Enabled, 7-day retention, daily snapshots
- **Manual snapshots**: Taken before major changes, retained 30 days
- **Cross-region replication**: [Yes/No — enabled to us-west-2 for DR]
- **Backup verification**: Quarterly restore test to isolated environment

### 3.2 Application Data (S3)
- **Versioning**: Enabled on all buckets containing customer data
- **Cross-region replication**: Critical buckets replicated to [SECONDARY REGION]
- **Object lock**: Enabled on audit log buckets (compliance requirement)

### 3.3 Infrastructure as Code
- All infrastructure is defined in Terraform / CloudFormation stored in GitHub
- Infrastructure can be redeployed from scratch in a new region using IaC
- IaC repository is backed up and mirrored to [SECONDARY SCM / S3]

## 4. Disaster Scenarios and Response

### Scenario A: Single-Region AWS Outage

1. Activate incident response — notify BCP team
2. Assess estimated AWS restoration time from AWS Health Dashboard
3. If ETA > RTO: initiate failover to secondary region [REGION]
4. DNS failover via Route 53 health checks (automated if configured)
5. Verify data integrity from cross-region replica
6. Communicate status to customers via status page

### Scenario B: Database Corruption / Accidental Deletion

1. Stop write traffic to the affected database
2. Identify the last known-good restore point from RDS automated backups
3. Restore database to isolated instance for validation
4. Validate data integrity
5. Promote restored instance or restore from snapshot to original
6. Resume traffic; monitor for anomalies

### Scenario C: Ransomware / Destructive Cyber Attack

1. Immediately isolate all affected systems from network
2. Activate Incident Response Plan — engage forensics if needed
3. Do **not** restore from backups until compromise scope is confirmed
4. Deploy infrastructure from IaC to clean AWS account or new VPC
5. Restore databases from backups made **before** the compromise date
6. Rotate all credentials before restoring internet access
7. Notify customers, regulators per breach notification requirements

### Scenario D: Critical SaaS Tool Outage (Slack, GitHub, etc.)

1. Activate backup communication channel: [EMAIL / ALTERNATIVE TOOL]
2. Identify critical workflows affected
3. Implement manual workarounds as defined in runbooks
4. Monitor vendor status page and communicate ETA to team
5. Document impact for post-incident review

## 5. BCP Team Roles

| Role | Responsibility | Primary | Backup |
|------|---------------|---------|--------|
| BCP Coordinator | Declares disaster, activates plan, external comms | [NAME] | [NAME] |
| Infrastructure Lead | AWS failover, DNS, network | [NAME] | [NAME] |
| Data Recovery Lead | Database restore, data validation | [NAME] | [NAME] |
| Communications Lead | Customer and stakeholder communication | [NAME] | [NAME] |
| Legal/Compliance | Regulatory notification if data affected | [NAME] | [NAME] |

**Emergency contact list**: [LINK TO SECURE DOCUMENT]

## 6. Testing Schedule

| Test Type | Frequency | Last Tested | Next Test |
|-----------|-----------|-------------|-----------|
| Backup restore test (DB) | Quarterly | [DATE] | [DATE] |
| Tabletop exercise | Annual | [DATE] | [DATE] |
| Full DR failover test | Annual | [DATE] | [DATE] |
| BCP plan review | Annual | [DATE] | [DATE] |

Test results are documented and used to improve this plan.

## 7. Communication Templates

### Customer Status Update (Outage in Progress)
> We are currently experiencing [ISSUE DESCRIPTION] affecting [AFFECTED FEATURES]. Our team is actively working on a resolution. We will provide an update by [TIME]. We apologize for the impact to your work.

### Customer Resolution Notice
> The issue affecting [FEATURES] has been resolved as of [TIME]. Services have been restored to normal operation. We will publish a post-incident report within 48 hours. We apologize for the disruption.

## 8. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [DATE] | [AUTHOR] | Initial version |

---

> **Provided by AuditCaddie OSS**
> This policy template is provided free of charge under the Apache License 2.0.
> Customize it for your organization, then generate evidence with AuditCaddie.
>
> 🔗 [github.com/Blodgic/AuditCaddie](https://github.com/Blodgic/AuditCaddie) · [auditcaddie.com](https://auditcaddie.com)
