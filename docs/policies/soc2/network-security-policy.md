<!--
  AuditCaddie OSS — Free Policy Template
  Policy:    Network & Communications Security Policy
  Framework: SOC 2 TSC — CC6.6, CC6.7
  Version:   1.0
  License:   Apache 2.0 | auditcaddie.com | github.com/Blodgic/AuditCaddie
-->

---
title: Network & Communications Security Policy
controls: [CC6.6, CC6.7]
framework: soc2
version: "1.0"
review_cycle: Annual
attribution: "Free template provided by AuditCaddie OSS | auditcaddie.com"
---

> **AuditCaddie OSS Free Template** | auditcaddie.com | Apache 2.0

---

# [COMPANY NAME] Network & Communications Security Policy

**Policy Owner:** [CISO / CTO / Head of Engineering]
**Effective Date:** [DATE]
**Last Reviewed:** [DATE]
**Version:** 1.0

---

## 1. Purpose

This policy establishes requirements for network security and secure data transmission at [COMPANY NAME]. It supports SOC 2 TSC CC6.6 (External Threat Protection) and CC6.7 (Information Transmission Security).

## 2. Network Architecture Standards

### 2.1 VPC Design

All production infrastructure is deployed in a dedicated AWS VPC with:
- **Public subnets:** Load balancers and bastion hosts only
- **Private subnets:** Application servers, databases, and internal services
- **No direct internet access** to private subnet resources
- **NAT Gateway** for outbound traffic from private subnets

### 2.2 Security Groups

Security group rules follow least-privilege:
- Ingress rules are restricted to known IP ranges or specific security groups
- No `0.0.0.0/0` ingress rules except on load balancers (ports 443 and 80→443 redirect)
- All direct SSH/RDP access from the internet is prohibited
- Database ports (5432, 3306, 27017, etc.) are never exposed to the internet

### 2.3 Network Monitoring

- **VPC Flow Logs:** Enabled on all VPCs and sent to CloudWatch Logs
- **AWS GuardDuty:** Enabled — monitors for port scanning, unusual network patterns
- **Network ACLs:** Default deny configured as a secondary defense layer

## 3. Encryption in Transit

### 3.1 Public Endpoints

All public-facing endpoints must use HTTPS:
- TLS 1.2 minimum (TLS 1.3 preferred)
- Certificates managed via AWS Certificate Manager (ACM) with automatic renewal
- HTTP to HTTPS redirect enforced at the load balancer
- HSTS header enabled with `max-age=31536000; includeSubDomains`

### 3.2 Internal Service Communication

Service-to-service communication within the VPC uses:
- TLS for any communication leaving the VPC
- [TLS / private certificate authority] for internal microservice communication

### 3.3 Database Connections

- All database connections use SSL/TLS (`sslmode=require` for PostgreSQL; `ssl=true` for others)
- Database endpoints are not accessible from outside the VPC

### 3.4 Email

- Outbound emails use [DKIM, SPF, and DMARC] to prevent spoofing
- Transactional email sent via [SendGrid / AWS SES / Postmark]

## 4. Remote Access

- Developer access to production systems is via [AWS Systems Manager Session Manager / VPN / Bastion host]
- Direct SSH from the internet is disabled on all production instances
- All remote access sessions are logged

## 5. Data Transmission Controls

- Sensitive data is never transmitted via unencrypted channels (no HTTP, FTP, unencrypted SMTP)
- Removable media containing confidential data must be encrypted (see Removable Media Policy)
- File transfers to external parties must use encrypted channels ([SFTP / HTTPS / encrypted email])

---

*This template was provided free of charge by **AuditCaddie OSS**.*
*For AI-assisted policy generation, evidence mapping, and SOC 2 readiness: [auditcaddie.com](https://auditcaddie.com)*
*Template version 1.0 | Apache 2.0 License | github.com/Blodgic/AuditCaddie*
