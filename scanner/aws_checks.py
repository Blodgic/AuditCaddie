"""
AuditCaddie OSS — AWS Security Checks
Runs read-only API calls against your AWS account to evaluate
security controls against compliance frameworks.

All checks require only read permissions (no writes, no changes).
Recommended IAM policy: SecurityAudit (AWS managed) or the
minimal policy documented at github.com/Blodgic/AuditCaddie.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

log = logging.getLogger("auditcaddie.aws")

# ── Result helpers ─────────────────────────────────────────────────────────────

def _pass(check_id: str, title: str, detail: str = "") -> dict:
    return {"check": check_id, "title": title, "status": "pass", "detail": detail}

def _fail(check_id: str, title: str, detail: str = "", remediation: str = "") -> dict:
    return {"check": check_id, "title": title, "status": "fail",
            "detail": detail, "remediation": remediation}

def _warn(check_id: str, title: str, detail: str = "") -> dict:
    return {"check": check_id, "title": title, "status": "warn", "detail": detail}

def _error(check_id: str, title: str, detail: str = "") -> dict:
    return {"check": check_id, "title": title, "status": "error", "detail": detail}


# ── IAM Checks ─────────────────────────────────────────────────────────────────

def check_iam_mfa_all_users(iam) -> dict:
    cid = "iam_mfa_all_users"
    title = "MFA enabled for all IAM users"
    try:
        users = iam.list_users()["Users"]
        no_mfa = []
        for user in users:
            devices = iam.list_mfa_devices(UserName=user["UserName"])["MFADevices"]
            if not devices:
                # Check if user has console access (password)
                try:
                    iam.get_login_profile(UserName=user["UserName"])
                    no_mfa.append(user["UserName"])
                except ClientError as e:
                    if e.response["Error"]["Code"] != "NoSuchEntity":
                        no_mfa.append(user["UserName"])

        if not no_mfa:
            return _pass(cid, title, f"All {len(users)} users have MFA or no console access")
        return _fail(cid, title,
                     f"{len(no_mfa)} user(s) without MFA: {', '.join(no_mfa[:5])}",
                     "IAM → Users → Security credentials → Assign MFA device")
    except Exception as e:
        return _error(cid, title, str(e))


def check_iam_password_policy(iam) -> dict:
    cid = "iam_password_policy_strength"
    title = "IAM password policy meets security standards"
    try:
        policy = iam.get_account_password_policy()["PasswordPolicy"]
        issues = []
        if policy.get("MinimumPasswordLength", 0) < 14:
            issues.append(f"minimum length {policy.get('MinimumPasswordLength')} (need 14+)")
        if not policy.get("RequireUppercaseCharacters"):
            issues.append("uppercase not required")
        if not policy.get("RequireLowercaseCharacters"):
            issues.append("lowercase not required")
        if not policy.get("RequireNumbers"):
            issues.append("numbers not required")
        if not policy.get("RequireSymbols"):
            issues.append("symbols not required")

        if not issues:
            return _pass(cid, title, "Password policy meets NIST 800-63B standards")
        return _fail(cid, title, f"Policy gaps: {'; '.join(issues)}",
                     "IAM → Account settings → Password policy")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            return _fail(cid, title, "No password policy set",
                         "IAM → Account settings → Set password policy (min 14 chars)")
        return _error(cid, title, str(e))


def check_iam_no_root_access_keys(iam) -> dict:
    cid = "iam_no_root_access_keys"
    title = "No root account access keys"
    try:
        summary = iam.get_account_summary()["SummaryMap"]
        count = summary.get("AccountAccessKeysPresent", 0)
        if count == 0:
            return _pass(cid, title, "Root account has no active access keys")
        return _fail(cid, title, f"{count} root access key(s) detected",
                     "IAM → Security credentials (root) → Access keys → Delete all root keys")
    except Exception as e:
        return _error(cid, title, str(e))


def check_iam_access_key_rotation(iam) -> dict:
    cid = "iam_access_key_rotation_90days"
    title = "IAM access keys rotated within 90 days"
    try:
        users = iam.list_users()["Users"]
        stale = []
        now = datetime.now(timezone.utc)
        for user in users:
            keys = iam.list_access_keys(UserName=user["UserName"])["AccessKeyMetadata"]
            for key in keys:
                if key["Status"] == "Active":
                    age_days = (now - key["CreateDate"]).days
                    if age_days > 90:
                        stale.append(f"{user['UserName']} ({age_days}d)")
        if not stale:
            return _pass(cid, title, "All active access keys are within 90-day rotation window")
        return _fail(cid, title, f"{len(stale)} stale key(s): {', '.join(stale[:3])}",
                     "IAM → Users → Security credentials → Create new key, disable old key")
    except Exception as e:
        return _error(cid, title, str(e))


# ── S3 Checks ──────────────────────────────────────────────────────────────────

def check_s3_encryption(s3) -> dict:
    cid = "s3_bucket_encryption_at_rest"
    title = "All S3 buckets have default encryption enabled"
    try:
        buckets = s3.list_buckets()["Buckets"]
        unencrypted = []
        for bucket in buckets:
            try:
                s3.get_bucket_encryption(Bucket=bucket["Name"])
            except ClientError as e:
                if e.response["Error"]["Code"] == "ServerSideEncryptionConfigurationNotFoundError":
                    unencrypted.append(bucket["Name"])
        if not unencrypted:
            return _pass(cid, title, f"All {len(buckets)} buckets have default encryption")
        return _fail(cid, title, f"{len(unencrypted)} unencrypted bucket(s): {', '.join(unencrypted[:3])}",
                     "S3 → select bucket → Properties → Default encryption → Enable SSE-S3 or SSE-KMS")
    except Exception as e:
        return _error(cid, title, str(e))


def check_s3_public_access_blocked(s3) -> dict:
    cid = "s3_bucket_public_access_blocked"
    title = "S3 account-level public access block enabled"
    try:
        config = s3.get_public_access_block(AccountId=boto3.client("sts").get_caller_identity()["Account"])
        block = config["PublicAccessBlockConfiguration"]
        all_blocked = all([
            block.get("BlockPublicAcls"),
            block.get("IgnorePublicAcls"),
            block.get("BlockPublicPolicy"),
            block.get("RestrictPublicBuckets"),
        ])
        if all_blocked:
            return _pass(cid, title, "Account-level S3 public access block is fully enabled")
        missing = [k for k, v in block.items() if not v]
        return _fail(cid, title, f"Missing: {', '.join(missing)}",
                     "S3 → Block Public Access settings for this account → Block all public access")
    except Exception as e:
        return _error(cid, title, str(e))


def check_s3_versioning(s3) -> dict:
    cid = "s3_bucket_versioning_enabled"
    title = "S3 versioning enabled on critical buckets"
    try:
        buckets = s3.list_buckets()["Buckets"]
        no_versioning = []
        for bucket in buckets:
            v = s3.get_bucket_versioning(Bucket=bucket["Name"])
            if v.get("Status") != "Enabled":
                no_versioning.append(bucket["Name"])
        if not no_versioning:
            return _pass(cid, title, f"All {len(buckets)} buckets have versioning enabled")
        return _warn(cid, title,
                     f"{len(no_versioning)} bucket(s) without versioning — enable on buckets storing critical data")
    except Exception as e:
        return _error(cid, title, str(e))


# ── CloudTrail Checks ──────────────────────────────────────────────────────────

def check_cloudtrail_all_regions(ct) -> dict:
    cid = "cloudtrail_enabled_all_regions"
    title = "CloudTrail enabled across all regions"
    try:
        trails = ct.describe_trails(includeShadowTrails=False)["trailList"]
        multi_region = [t for t in trails if t.get("IsMultiRegionTrail")]
        if multi_region:
            # Verify at least one is logging
            for trail in multi_region:
                status = ct.get_trail_status(Name=trail["TrailARN"])
                if status.get("IsLogging"):
                    return _pass(cid, title,
                                 f"Trail '{trail['Name']}' covers all regions and is actively logging")
            return _warn(cid, title, "Multi-region trail exists but logging is not active")
        return _fail(cid, title, "No multi-region CloudTrail found",
                     "CloudTrail → Create trail → Apply to all regions → Create")
    except Exception as e:
        return _error(cid, title, str(e))


# ── CloudWatch Checks ──────────────────────────────────────────────────────────

def check_cloudwatch_alarms(cw) -> dict:
    cid = "cloudwatch_alarms_configured"
    title = "CloudWatch alarms configured for security events"
    try:
        alarms = cw.describe_alarms()["MetricAlarms"]
        if alarms:
            return _pass(cid, title, f"{len(alarms)} CloudWatch alarm(s) configured")
        return _warn(cid, title, "No CloudWatch alarms found — configure alerts for root usage and unauthorized API calls",)
    except Exception as e:
        return _error(cid, title, str(e))


# ── GuardDuty Checks ───────────────────────────────────────────────────────────

def check_guardduty_enabled(session) -> dict:
    cid = "guardduty_enabled"
    title = "GuardDuty threat detection enabled"
    try:
        gd = session.client("guardduty")
        detectors = gd.list_detectors()["DetectorIds"]
        if detectors:
            det = gd.get_detector(DetectorId=detectors[0])
            if det["Status"] == "ENABLED":
                return _pass(cid, title, f"GuardDuty detector {detectors[0][:8]}... is active")
        return _fail(cid, title, "GuardDuty not enabled in this region",
                     "GuardDuty → Get started → Enable GuardDuty (~$4/mo for most startups)")
    except Exception as e:
        return _error(cid, title, str(e))


# ── RDS Checks ─────────────────────────────────────────────────────────────────

def check_rds_encryption(rds) -> dict:
    cid = "rds_encryption_enabled"
    title = "RDS instances have storage encryption enabled"
    try:
        instances = rds.describe_db_instances()["DBInstances"]
        if not instances:
            return _pass(cid, title, "No RDS instances found")
        unencrypted = [db["DBInstanceIdentifier"] for db in instances
                       if not db.get("StorageEncrypted")]
        if not unencrypted:
            return _pass(cid, title, f"All {len(instances)} RDS instance(s) encrypted at rest")
        return _fail(cid, title, f"Unencrypted: {', '.join(unencrypted)}",
                     "RDS encryption must be enabled at creation. Create encrypted snapshot and restore to new instance.")
    except Exception as e:
        return _error(cid, title, str(e))


def check_rds_backups(rds) -> dict:
    cid = "rds_automated_backups_enabled"
    title = "RDS automated backups enabled (7+ day retention)"
    try:
        instances = rds.describe_db_instances()["DBInstances"]
        if not instances:
            return _pass(cid, title, "No RDS instances found")
        issues = []
        for db in instances:
            retention = db.get("BackupRetentionPeriod", 0)
            if retention < 7:
                issues.append(f"{db['DBInstanceIdentifier']} ({retention}d)")
        if not issues:
            return _pass(cid, title, f"All {len(instances)} RDS instance(s) have 7+ day backup retention")
        return _fail(cid, title, f"Insufficient backup retention: {', '.join(issues)}",
                     "RDS → select instance → Modify → Backup retention period → 7 days minimum")
    except Exception as e:
        return _error(cid, title, str(e))


# ── VPC Checks ─────────────────────────────────────────────────────────────────

def check_vpc_flow_logs(ec2) -> dict:
    cid = "vpc_flow_logs_enabled"
    title = "VPC flow logs enabled"
    try:
        vpcs = ec2.describe_vpcs()["Vpcs"]
        logs = ec2.describe_flow_logs()["FlowLogs"]
        covered_vpcs = {fl["ResourceId"] for fl in logs if fl["FlowLogStatus"] == "ACTIVE"}
        uncovered = [v["VpcId"] for v in vpcs if v["VpcId"] not in covered_vpcs]
        if not uncovered:
            return _pass(cid, title, f"Flow logs enabled on all {len(vpcs)} VPC(s)")
        return _fail(cid, title, f"{len(uncovered)} VPC(s) without flow logs: {', '.join(uncovered[:3])}",
                     "VPC → Your VPCs → select VPC → Flow logs → Create flow log → CloudWatch Logs")
    except Exception as e:
        return _error(cid, title, str(e))


# ── KMS Checks ─────────────────────────────────────────────────────────────────

def check_kms_key_rotation(kms) -> dict:
    cid = "kms_key_rotation_enabled"
    title = "KMS customer-managed keys have rotation enabled"
    try:
        paginator = kms.get_paginator("list_keys")
        keys = [k for page in paginator.paginate() for k in page["Keys"]]
        cmks_no_rotation = []
        for key in keys:
            try:
                meta = kms.describe_key(KeyId=key["KeyId"])["KeyMetadata"]
                if meta["KeyManager"] == "CUSTOMER" and meta["KeyState"] == "Enabled":
                    rotation = kms.get_key_rotation_status(KeyId=key["KeyId"])
                    if not rotation.get("KeyRotationEnabled"):
                        cmks_no_rotation.append(key["KeyId"][:8] + "...")
            except ClientError:
                continue
        if not cmks_no_rotation:
            return _pass(cid, title, "All customer-managed KMS keys have rotation enabled")
        return _fail(cid, title, f"{len(cmks_no_rotation)} key(s) without rotation: {', '.join(cmks_no_rotation[:3])}",
                     "KMS → Customer managed keys → select key → Key rotation → Enable")
    except Exception as e:
        return _error(cid, title, str(e))


# ── ACM Checks ─────────────────────────────────────────────────────────────────

def check_acm_certificates(acm) -> dict:
    cid = "acm_certificates_valid"
    title = "ACM certificates valid and not expiring soon"
    try:
        certs = acm.list_certificates(CertificateStatuses=["ISSUED"])["CertificateSummaryList"]
        if not certs:
            return _warn(cid, title, "No ACM certificates found — ensure TLS is configured for all public endpoints")
        now = datetime.now(timezone.utc)
        expiring = []
        for cert in certs:
            detail = acm.describe_certificate(CertificateArn=cert["CertificateArn"])["Certificate"]
            if detail.get("NotAfter"):
                days_left = (detail["NotAfter"] - now).days
                if days_left < 30:
                    domain = detail.get("DomainName", "unknown")
                    expiring.append(f"{domain} ({days_left}d)")
        if not expiring:
            return _pass(cid, title, f"All {len(certs)} ACM certificate(s) are valid with 30+ days remaining")
        return _fail(cid, title, f"Expiring soon: {', '.join(expiring)}",
                     "ACM → select certificate → Renew (or enable auto-renewal)")
    except Exception as e:
        return _error(cid, title, str(e))


# ── Security Hub / Config ──────────────────────────────────────────────────────

def check_security_hub(session) -> dict:
    cid = "security_hub_enabled"
    title = "AWS Security Hub enabled"
    try:
        sh = session.client("securityhub")
        hub = sh.describe_hub()
        return _pass(cid, title, f"Security Hub enabled: {hub.get('HubArn', '')[:40]}...")
    except ClientError as e:
        if "not subscribed" in str(e).lower() or "InvalidAccessException" in str(e):
            return _warn(cid, title, "Security Hub not enabled — aggregates findings from GuardDuty, Inspector, IAM Access Analyzer")
        return _error(cid, title, str(e))


def check_config_enabled(session) -> dict:
    cid = "config_enabled"
    title = "AWS Config enabled for resource inventory"
    try:
        cfg = session.client("config")
        recorders = cfg.describe_configuration_recorders()["ConfigurationRecorders"]
        if not recorders:
            return _warn(cid, title, "AWS Config not enabled — provides continuous resource inventory and compliance history")
        statuses = cfg.describe_configuration_recorder_status()["ConfigurationRecordersStatus"]
        recording = any(s.get("recording") for s in statuses)
        if recording:
            return _pass(cid, title, "AWS Config is enabled and actively recording")
        return _warn(cid, title, "AWS Config recorder exists but is not currently recording")
    except Exception as e:
        return _error(cid, title, str(e))


# ── Main scan runner ───────────────────────────────────────────────────────────

CHECK_REGISTRY = {
    "iam_mfa_all_users":            lambda s: check_iam_mfa_all_users(s.client("iam")),
    "iam_password_policy_strength": lambda s: check_iam_password_policy(s.client("iam")),
    "iam_no_root_access_keys":      lambda s: check_iam_no_root_access_keys(s.client("iam")),
    "iam_access_key_rotation_90days": lambda s: check_iam_access_key_rotation(s.client("iam")),
    "s3_bucket_encryption_at_rest": lambda s: check_s3_encryption(s.client("s3")),
    "s3_bucket_public_access_blocked": lambda s: check_s3_public_access_blocked(s.client("s3")),
    "s3_bucket_versioning_enabled": lambda s: check_s3_versioning(s.client("s3")),
    "cloudtrail_enabled_all_regions": lambda s: check_cloudtrail_all_regions(s.client("cloudtrail")),
    "cloudwatch_alarms_configured": lambda s: check_cloudwatch_alarms(s.client("cloudwatch")),
    "guardduty_enabled":            lambda s: check_guardduty_enabled(s),
    "rds_encryption_enabled":       lambda s: check_rds_encryption(s.client("rds")),
    "rds_automated_backups_enabled": lambda s: check_rds_backups(s.client("rds")),
    "vpc_flow_logs_enabled":        lambda s: check_vpc_flow_logs(s.client("ec2")),
    "kms_key_rotation_enabled":     lambda s: check_kms_key_rotation(s.client("kms")),
    "acm_certificates_valid":       lambda s: check_acm_certificates(s.client("acm")),
    "security_hub_enabled":         lambda s: check_security_hub(s),
    "config_enabled":               lambda s: check_config_enabled(s),
}


def run_aws_scan(
    checks: list[str],
    aws_access_key: Optional[str] = None,
    aws_secret_key: Optional[str] = None,
    aws_region: str = "us-east-1",
) -> dict:
    """
    Run the requested AWS checks.
    Credentials: pass explicitly or rely on boto3 credential chain
    (env vars, ~/.aws/credentials, EC2 instance role, etc.)
    """
    try:
        kwargs: dict = {"region_name": aws_region}
        if aws_access_key and aws_secret_key:
            kwargs["aws_access_key_id"] = aws_access_key
            kwargs["aws_secret_access_key"] = aws_secret_key

        session = boto3.Session(**kwargs)
        # Validate credentials early
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        account_id = identity["Account"]
        account_arn = identity["Arn"]
    except NoCredentialsError:
        return {
            "ok": False,
            "error": "No AWS credentials found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env, or configure an IAM role.",
            "results": [],
        }
    except ClientError as e:
        return {"ok": False, "error": str(e), "results": []}

    results = []
    for check_id in checks:
        fn = CHECK_REGISTRY.get(check_id)
        if fn is None:
            results.append(_warn(check_id, check_id, "Check not implemented in this version"))
            continue
        try:
            results.append(fn(session))
        except Exception as e:
            results.append(_error(check_id, check_id, f"Unexpected error: {e}"))

    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    warned = sum(1 for r in results if r["status"] == "warn")

    return {
        "ok": True,
        "account_id": account_id,
        "account_arn": account_arn,
        "region": aws_region,
        "summary": {"pass": passed, "fail": failed, "warn": warned, "total": len(results)},
        "results": results,
    }
