<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Business Continuity & Disaster Recovery Policy
  Framework: SOC 2 TSC — CC9.1, A1.1, A1.2, A1.3
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
-->

---
title: Business Continuity & Disaster Recovery Policy
controls: [CC9.1, A1.1, A1.2, A1.3]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Business Continuity & Disaster Recovery Policy

**Policy Owner:** [CTO / Head of Engineering / CEO]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Next Review:** [DATE + 1 YEAR]
**Version:** 1.0

---

## 1. Purpose

This policy establishes [COMPANY NAME]'s approach to maintaining service availability, protecting critical data, and recovering from disruptions. It supports SOC 2 TSC CC9.1 (Business Disruption Risk Mitigation), A1.1 (Capacity Management), A1.2 (Environmental and Recovery Infrastructure), and A1.3 (Recovery Plan Testing).

## 2. Business Impact Analysis

### 2.1 Critical Systems

| System | Description | Max Tolerable Downtime |
|--------|-------------|----------------------|
| [PRIMARY PRODUCTION APPLICATION] | Customer-facing service | [4 hours] |
| [DATABASE / DATA STORE] | Customer data storage | [2 hours] |
| [AUTHENTICATION SERVICE] | User login and access | [2 hours] |
| [API GATEWAY] | API access layer | [4 hours] |
| [CI/CD PIPELINE] | Engineering deployments | [24 hours] |

### 2.2 Recovery Objectives

| System Tier | Recovery Time Objective (RTO) | Recovery Point Objective (RPO) |
|-------------|-------------------------------|-------------------------------|
| **Tier 1 — Critical** | [2 hours] | [15 minutes] |
| **Tier 2 — Important** | [8 hours] | [1 hour] |
| **Tier 3 — Standard** | [24 hours] | [24 hours] |

## 3. Backup Configuration

### 3.1 Database Backups

- **RDS Automated Backups:** Enabled with [7-day / 30-day] retention
- **Backup window:** [Daily, e.g., 02:00–03:00 UTC]
- **Point-in-Time Recovery:** Enabled (supports recovery to any point within the retention period)
- **Cross-region backup:** [Enabled / Disabled] — backups replicated to [SECONDARY REGION]
- **Manual snapshots:** Taken before all major deployments

### 3.2 Object Storage Backups

- **S3 Versioning:** Enabled on all buckets containing customer or critical data
- **S3 Lifecycle Policies:** Versions older than [90 days] transitioned to Glacier; deleted after [1 year]
- **S3 Replication:** [Cross-region replication enabled to [DR REGION] for critical buckets]

### 3.3 Code and Configuration

- **Source Code:** Stored in [GitHub] with full history. Repositories are [backed up via GitHub's built-in redundancy / archived to S3 monthly]
- **Infrastructure as Code:** All infrastructure is defined in [Terraform / CDK] and stored in source control
- **Secrets:** Stored in [AWS Secrets Manager / Parameter Store] — not in code

### 3.4 AWS Backup

AWS Backup is configured to provide centralized backup management for:
- RDS instances
- EBS volumes (if used)
- DynamoDB tables (if used)
- EFS file systems (if used)

Backup plans are reviewed annually and after significant infrastructure changes.

## 4. Capacity Management

[COMPANY NAME] monitors and manages capacity to meet availability commitments:

### 4.1 Auto-Scaling

Production workloads use auto-scaling to handle demand spikes:
- **EC2/ECS/EKS:** Auto Scaling Groups or ECS Service Auto Scaling configured
- **RDS:** Storage auto-scaling enabled; read replicas for read-heavy workloads
- **CloudFront/ALB:** CDN and load balancer distribute traffic globally

### 4.2 Capacity Monitoring

CloudWatch dashboards monitor:
- CPU utilization (alarm at [80%])
- Memory utilization (alarm at [80%])
- Database connections (alarm at [80% of max_connections])
- Storage utilization (alarm at [80%])
- Request error rates (alarm at [5%])

### 4.3 Capacity Planning

Capacity reviews are conducted [quarterly] to:
- Review actual usage vs. allocated capacity
- Project growth based on customer acquisition forecasts
- Pre-provision capacity for known demand events

## 5. Availability Monitoring

[COMPANY NAME] uses the following uptime monitoring:
- **External monitoring:** [UptimeRobot / Pingdom / Datadog] — monitors public endpoints every [1 minute]
- **Internal monitoring:** CloudWatch alarms on key health metrics
- **Status page:** [status.[company].com] — updated during incidents
- **On-call rotation:** [PagerDuty / OpsGenie] with [X]-minute response SLA for P1 alerts

### 5.1 SLA Targets

| Metric | Target |
|--------|--------|
| Monthly Uptime | [99.9%] |
| P1 Incident Acknowledgment | [15 minutes] |
| P1 Incident Resolution | [4 hours] |

## 6. Disaster Recovery Procedures

### 6.1 Activation Criteria

The DR Plan is activated when:
- A production outage cannot be resolved within [2 hours]
- An AWS region is unavailable
- A catastrophic data loss event occurs
- A security incident requires taking production offline

**Authorization:** DR activation requires approval from [CTO / CEO].

### 6.2 DR Runbook

**Step 1 — Assess and Declare**
- Assess impact and confirm DR activation is needed
- Notify leadership team
- Open DR incident channel: `#incident-dr-[date]`

**Step 2 — Activate DR Environment**
- [For multi-region setups: Route 53 failover DNS automatically redirects traffic to [DR REGION]]
- [For single-region setups: Launch recovery environment using IaC in [DR REGION]]
- Confirm recovery environment health checks pass

**Step 3 — Restore Data**
- Restore from most recent RDS snapshot within RPO
- Verify data integrity
- Run smoke tests on critical workflows

**Step 4 — Communicate**
- Update status page
- Notify affected customers if applicable
- Provide estimated recovery timeline

**Step 5 — Monitor and Stabilize**
- Monitor DR environment closely for [4 hours]
- Confirm all critical functions operational

**Step 6 — Plan Return to Primary** (if applicable)
- Restore primary environment
- Sync any data written to DR environment
- Failback with maintenance window communication

## 7. DR Testing

### 7.1 Testing Schedule

| Test Type | Frequency | Description |
|-----------|-----------|-------------|
| **Backup Restoration Test** | Quarterly | Restore a database snapshot to a test environment and verify data integrity |
| **DR Tabletop Exercise** | Annually | Walk through the DR runbook with the engineering team |
| **Full DR Failover Test** | [Annually / Biannually] | Perform an actual failover to the DR environment |

### 7.2 Test Documentation

All DR tests must be documented with:
- Date and participants
- Scenario tested
- Steps followed
- Actual RTO and RPO achieved
- Issues identified and remediation actions
- Sign-off from [CTO / Engineering Lead]

Test records are retained for a minimum of **[3 years]**.

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
