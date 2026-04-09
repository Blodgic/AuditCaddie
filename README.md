<div align="center">

# AuditCaddie OSS

**Self-hosted compliance scanning for AWS + GitHub**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://github.com/Blodgic/AuditCaddie/pkgs/container/auditcaddie)

[**Get Started**](#quick-start) · [**Templates**](templates/) · [**Enterprise**](https://auditcaddie.com/pricing) · [**Docs**](https://github.com/Blodgic/AuditCaddie/wiki)

</div>

---

AuditCaddie OSS is the free, self-hosted compliance engine that scans your AWS account and GitHub repositories, maps findings to compliance frameworks, and uses AI to generate the policy documents your auditor is asking for.

**10 minutes from zero to audit-ready evidence.**

## What it does

| Module | What it checks |
|--------|---------------|
| **AWS Scanner** | IAM (MFA, password policy, root keys, key rotation), S3 (encryption, public access), CloudTrail, CloudWatch alarms, GuardDuty, RDS (encryption, backups), VPC flow logs, KMS rotation, ACM certificates, Security Hub, AWS Config |
| **GitHub Scanner** | Branch protection, secret scanning, Dependabot alerts, public repo review, 2FA enforcement, code scanning (SAST) |
| **AI Policy Generator** | GPT-4o or Claude Sonnet generates audit-ready policy documents from your scan findings. You bring the key. |
| **Compliance Report** | Printable HTML report with readiness score, pass/fail by control, and remediation guidance |

## Compliance Frameworks Included

| Template | Framework | Controls |
|----------|-----------|----------|
| `soc2-startup` | SOC 2 Type I | 10 controls |
| `nist-csf-smb` | NIST CSF 2.0 | 12 controls |
| `iso27001-saas` | ISO 27001:2022 | 14 controls |
| `hipaa-healthtech` | HIPAA Security Rule | 13 controls |
| `vendor-assessment` | Third-Party Vendor | 15 domains |

## Quick Start

### One-line install (Mac/Linux + Docker)

```bash
curl -sSL https://raw.githubusercontent.com/Blodgic/AuditCaddie/main/install.sh | bash
```

The installer prompts for your API keys, downloads everything, and opens your browser at `http://localhost:8080`.

---

### Manual setup (Docker)

**1. Clone and configure**

```bash
git clone https://github.com/Blodgic/AuditCaddie.git
cd AuditCaddie
cp .env.example .env
# Edit .env with your keys
```

**2. Start**

```bash
docker compose up -d
```

Open **http://localhost:8080**

---

### Local Python (no Docker)

```bash
git clone https://github.com/Blodgic/AuditCaddie.git
cd AuditCaddie
pip install -r requirements.txt
cp .env.example .env   # edit with your keys
python app.py
```

---

### Deploy to a cloud VPC

Copy your `.env` to the server and run:

```bash
docker compose up -d
```

Then access via the server's IP or domain. Optionally set `AUDITCADDIE_PASSWORD` in `.env` to require a login.

## Configuration

Edit `.env` with your keys:

```env
# AI (required — at least one)
OPENAI_API_KEY=sk-...          # gpt-4o
ANTHROPIC_API_KEY=sk-ant-...   # claude-sonnet-4-5

# AWS (optional — for AWS scanning)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1

# GitHub (optional — for GitHub scanning)
GITHUB_TOKEN=ghp_...
GITHUB_ORG=your-org            # optional, leave blank for personal repos
```

### AWS Permission Requirements

Minimum read-only IAM policy: attach **SecurityAudit** (AWS managed) to the user or role.

For least-privilege, the scanner only calls these read-only APIs:
`iam:List*`, `iam:Get*`, `s3:GetBucket*`, `s3:ListBuckets`, `cloudtrail:Describe*`, `cloudtrail:GetTrail*`, `cloudwatch:DescribeAlarms`, `guardduty:List*`, `guardduty:Get*`, `rds:Describe*`, `ec2:Describe*`, `kms:List*`, `kms:Describe*`, `kms:GetKey*`, `acm:List*`, `acm:Describe*`, `securityhub:Describe*`, `config:Describe*`, `sts:GetCallerIdentity`

## OSS vs Enterprise

| Feature | OSS (free) | Enterprise |
|---------|-----------|------------|
| AWS scanning (17 checks) | ✅ | ✅ |
| GitHub scanning (6 checks) | ✅ | ✅ |
| AI policy generation (BYOK) | ✅ | ✅ |
| 5 compliance frameworks | ✅ | ✅ |
| Compliance reports (HTML) | ✅ | ✅ |
| Self-hosted / single user | ✅ | ✅ |
| Custom compliance frameworks | ❌ | ✅ |
| Team collaboration & roles | ❌ | ✅ |
| SSO / SAML (Okta, Azure AD) | ❌ | ✅ |
| Fieldguide integration | ❌ | ✅ |
| Auditor portal | ❌ | ✅ |
| White-label trust center | ❌ | ✅ |
| CI/CD API access | ❌ | ✅ |
| Priority support & SLA | ❌ | ✅ |

**[Upgrade to Enterprise →](https://auditcaddie.com/pricing)**

## Architecture

```
AuditCaddie OSS
├── app.py                   FastAPI backend (single file)
├── scanner/
│   ├── aws_checks.py        17 read-only AWS security checks
│   └── github_checks.py     6 GitHub security checks
├── ai_generator.py          OpenAI + Anthropic policy generation
├── static/index.html        Single-page frontend (vanilla JS)
├── templates/               YAML compliance templates
└── data/                    SQLite DB + scan results (your data, local)
```

**Stack:** Python 3.12 · FastAPI · boto3 · PyGithub · SQLite · Vanilla JS  
**No Node.js. No database server. No message queue. No build step.**

## Updating

```bash
cd ~/auditcaddie
docker compose pull
docker compose up -d
```

Your data in `./data/` is preserved across updates.

## Community

- **Issues & features:** [github.com/Blodgic/AuditCaddie/issues](https://github.com/Blodgic/AuditCaddie/issues)
- **Commercial product:** [auditcaddie.com](https://auditcaddie.com)
- **Policy templates** — free to use, customize, and share under Apache 2.0. Keep the attribution header.

## License

**Apache License 2.0** — free to use, self-host, modify, and redistribute. See [LICENSE](LICENSE).

Apache 2.0 is a permissive open source license that also includes:
- An **express patent grant** from all contributors (meaningful protection for security and AI tooling)
- A **trademark clause** — "AuditCaddie" and "BLODGIC" are protected marks; this license does not grant their use

**This repository contains the Community Edition only.** See [LICENSE](LICENSE) for the full scope of what is and is not included.

Enterprise features (multi-tenancy, SSO, Fieldguide integration, auditor portal, advanced evidence workflows, and more) are available under a commercial license at [auditcaddie.com/pricing](https://auditcaddie.com/pricing).

---

<div align="center">
<strong>AuditCaddie</strong> · <a href="https://auditcaddie.com">auditcaddie.com</a> · Built with ❤️ for the GRC community
</div>
