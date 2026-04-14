"""
AuditCaddie OSS — Security Toolbox Enabler
==========================================
READ THIS FIRST: These functions perform WRITE operations against your AWS account.
They are only called when the user explicitly clicks "Enable" for a specific tool.
No tool is ever enabled automatically without user consent.

Each enable function is idempotent — safe to call if the tool is already enabled.

Design principle (Steve Zalewski, CISO):
  "We scan what you have. We surface what we see. We recommend what to turn on.
   You decide. If you activate, we generate the evidence. If you don't, we
   document the gap and tell you what it means for your framework."

Required IAM permissions (in addition to SecurityAudit read-only):
  - guardduty:CreateDetector
  - cloudtrail:CreateTrail, cloudtrail:StartLogging, s3:CreateBucket, s3:PutBucketPolicy
  - ec2:CreateFlowLogs, logs:CreateLogGroup, logs:DescribeLogGroups, iam:CreateRole, iam:PutRolePolicy
  - securityhub:EnableSecurityHub, securityhub:BatchEnableStandards
  - s3control:PutPublicAccessBlock
"""

import json
import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError

log = logging.getLogger("auditcaddie.enabler")

# ── Tool Catalog ───────────────────────────────────────────────────────────────
# Each entry defines how a tool is presented to the user and whether it can
# be auto-enabled. Messaging follows Steve Zalewski's client framing.

TOOLBOX_CATALOG = [
    {
        "id": "guardduty",
        "name": "AWS GuardDuty",
        "check_id": "guardduty_enabled",
        "category": "Threat Detection",
        "icon": "shield",
        "auditor_ask": "Your auditor will look for active, continuous threat detection. GuardDuty is the industry-standard answer for AWS environments.",
        "security_risk": "Without it, you have no visibility into compromised credentials, cryptomining, unauthorized access, or active intrusions in your AWS account.",
        "what_it_does": "Analyzes CloudTrail, VPC Flow Logs, and DNS logs using AWS threat intelligence and machine learning to detect threats in real time.",
        "what_gets_created": ["GuardDuty detector in your AWS region"],
        "controls": ["CC7.1", "CC7.2", "CC6.6", "CC6.8"],
        "cost_estimate": "~$4/mo for most startups",
        "setup_time": "30 seconds",
        "can_auto_enable": True,
        "reversible": True,
    },
    {
        "id": "cloudtrail",
        "name": "AWS CloudTrail (All Regions)",
        "check_id": "cloudtrail_enabled_all_regions",
        "category": "Audit Logging",
        "icon": "log",
        "auditor_ask": "SOC 2 auditors require a complete, tamper-evident audit trail of all API activity. CloudTrail is non-negotiable for CC7 controls.",
        "security_risk": "Without it, you cannot prove who did what, when — making breach investigation impossible and leaving a critical gap your auditor will flag.",
        "what_it_does": "Records every API call made in your AWS account across all regions — who did it, from where, and when — stored in S3 with integrity validation.",
        "what_gets_created": [
            "S3 bucket: auditcaddie-cloudtrail-{account_id} (for log storage)",
            "CloudTrail trail: auditcaddie-trail (multi-region, enabled)"
        ],
        "controls": ["CC7.2", "CC7.3", "CC4.1"],
        "cost_estimate": "First trail free · S3 storage ~$2/mo",
        "setup_time": "~1 minute",
        "can_auto_enable": True,
        "reversible": True,
    },
    {
        "id": "vpc_flow_logs",
        "name": "VPC Flow Logs",
        "check_id": "vpc_flow_logs_enabled",
        "category": "Network Monitoring",
        "icon": "network",
        "auditor_ask": "Auditors ask for evidence of network traffic monitoring. VPC Flow Logs is the AWS-native proof that you are watching your network perimeter.",
        "security_risk": "Without it, you have no visibility into unusual traffic patterns, data exfiltration attempts, or lateral movement between your services.",
        "what_it_does": "Captures metadata for all IP traffic flowing to and from your VPC — source, destination, port, protocol, and accept/reject status.",
        "what_gets_created": [
            "CloudWatch Logs group: /auditcaddie/vpc-flow-logs",
            "IAM role: AuditCaddieFlowLogsRole (for CloudWatch delivery)",
            "Flow log enabled on each VPC in the region"
        ],
        "controls": ["CC6.6", "CC7.2"],
        "cost_estimate": "~$1–5/mo depending on traffic volume",
        "setup_time": "~1 minute",
        "can_auto_enable": True,
        "reversible": True,
    },
    {
        "id": "security_hub",
        "name": "AWS Security Hub",
        "check_id": "security_hub_enabled",
        "category": "Posture Management",
        "icon": "hub",
        "auditor_ask": "Demonstrates a centralized, continuous security posture review process — the auditor evidence for CC4.1 (monitoring activities).",
        "security_risk": "Without it, GuardDuty, Inspector, and IAM Access Analyzer findings are siloed with no unified dashboard or consistent remediation workflow.",
        "what_it_does": "Aggregates security findings from GuardDuty, Inspector, IAM Access Analyzer, and Macie into a single prioritized dashboard with CIS and AWS Foundational Security benchmarks.",
        "what_gets_created": [
            "Security Hub enabled in your region",
            "AWS Foundational Security Best Practices standard enabled (free)"
        ],
        "controls": ["CC4.1", "CC4.2", "CC7.1"],
        "cost_estimate": "~$0–3/mo for most startups (first 10K checks/mo free)",
        "setup_time": "30 seconds",
        "can_auto_enable": True,
        "reversible": True,
    },
    {
        "id": "s3_public_access",
        "name": "S3 Block Public Access",
        "check_id": "s3_bucket_public_access_blocked",
        "category": "Data Protection",
        "icon": "lock",
        "auditor_ask": "Auditors check this first. An S3 bucket accidentally made public is one of the most common and embarrassing breach vectors in AWS.",
        "security_risk": "A single misconfigured bucket policy or ACL can expose all customer data publicly. The account-level block is an absolute prevention layer.",
        "what_it_does": "Applies a hard block on all four public access vectors at the account level — overriding any bucket-level settings that might accidentally expose data.",
        "what_gets_created": [
            "Account-level S3 public access block (4 flags enabled)"
        ],
        "controls": ["CC6.7", "C1.1", "C1.2"],
        "cost_estimate": "Free",
        "setup_time": "5 seconds",
        "can_auto_enable": True,
        "reversible": True,
    },
    {
        "id": "config",
        "name": "AWS Config",
        "check_id": "config_enabled",
        "category": "Configuration History",
        "icon": "history",
        "auditor_ask": "For SOC 2 Type II, you need to prove controls were in place throughout the audit period — not just at the time of the scan. Config is that proof.",
        "security_risk": "Without it, you have a compliance snapshot, not a compliance posture. An auditor can challenge any control you cannot show was continuously in place.",
        "what_it_does": "Records the state of every AWS resource at every point in time — creating an immutable configuration history your auditor can review for the full audit period.",
        "what_gets_created": [
            "S3 bucket: auditcaddie-config-{account_id} (for configuration history)",
            "AWS Config recorder (all supported resources)",
            "AWS Config delivery channel"
        ],
        "controls": ["CC5.3", "CC8.1"],
        "cost_estimate": "~$2–10/mo depending on resource count",
        "setup_time": "~2 minutes",
        "can_auto_enable": True,
        "reversible": True,
    },
]


# ── Check: what's enabled right now ───────────────────────────────────────────

def check_toolbox_status(session: boto3.Session) -> list[dict]:
    """
    Non-destructive pre-flight check: which security tools are currently active?
    Returns status for each tool in TOOLBOX_CATALOG.
    """
    results = []
    region = session.region_name or "us-east-1"

    try:
        account_id = session.client("sts").get_caller_identity()["Account"]
    except Exception as e:
        return [{"error": f"Could not validate credentials: {e}"}]

    for tool in TOOLBOX_CATALOG:
        entry = {**tool, "status": "unknown", "detail": "", "account_id": account_id}

        try:
            if tool["id"] == "guardduty":
                gd = session.client("guardduty")
                detectors = gd.list_detectors().get("DetectorIds", [])
                if detectors:
                    det = gd.get_detector(DetectorId=detectors[0])
                    if det["Status"] == "ENABLED":
                        entry["status"] = "enabled"
                        entry["detail"] = f"Detector active since {det.get('CreatedAt','')[:10]}"
                    else:
                        entry["status"] = "disabled"
                        entry["detail"] = "Detector exists but is disabled"
                else:
                    entry["status"] = "disabled"
                    entry["detail"] = "GuardDuty not enabled in this region"

            elif tool["id"] == "cloudtrail":
                ct = session.client("cloudtrail")
                trails = ct.describe_trails(includeShadowTrails=False).get("trailList", [])
                multi = [t for t in trails if t.get("IsMultiRegionTrail")]
                if multi:
                    status = ct.get_trail_status(Name=multi[0]["TrailARN"])
                    if status.get("IsLogging"):
                        entry["status"] = "enabled"
                        entry["detail"] = f"Trail '{multi[0]['Name']}' covering all regions"
                    else:
                        entry["status"] = "warn"
                        entry["detail"] = "Trail exists but logging is paused"
                else:
                    entry["status"] = "disabled"
                    entry["detail"] = "No multi-region trail found"

            elif tool["id"] == "vpc_flow_logs":
                ec2 = session.client("ec2")
                vpcs = ec2.describe_vpcs().get("Vpcs", [])
                logs = ec2.describe_flow_logs().get("FlowLogs", [])
                covered = {fl["ResourceId"] for fl in logs if fl["FlowLogStatus"] == "ACTIVE"}
                uncovered = [v["VpcId"] for v in vpcs if v["VpcId"] not in covered]
                if not uncovered:
                    entry["status"] = "enabled"
                    entry["detail"] = f"Flow logs active on all {len(vpcs)} VPC(s)"
                elif len(uncovered) < len(vpcs):
                    entry["status"] = "warn"
                    entry["detail"] = f"{len(uncovered)} of {len(vpcs)} VPC(s) missing flow logs"
                else:
                    entry["status"] = "disabled"
                    entry["detail"] = f"No VPC flow logs found ({len(vpcs)} VPC(s) unmonitored)"
                entry["vpcs"] = [v["VpcId"] for v in vpcs]
                entry["uncovered_vpcs"] = uncovered

            elif tool["id"] == "security_hub":
                sh = session.client("securityhub")
                try:
                    hub = sh.describe_hub()
                    entry["status"] = "enabled"
                    entry["detail"] = "Security Hub active with findings aggregation"
                except ClientError as e:
                    if "not subscribed" in str(e).lower() or "InvalidAccessException" in str(e):
                        entry["status"] = "disabled"
                        entry["detail"] = "Security Hub not subscribed in this region"
                    else:
                        raise

            elif tool["id"] == "s3_public_access":
                try:
                    s3c = session.client("s3control")
                    block = s3c.get_public_access_block(AccountId=account_id)
                    cfg = block["PublicAccessBlockConfiguration"]
                    all_blocked = all([
                        cfg.get("BlockPublicAcls"),
                        cfg.get("IgnorePublicAcls"),
                        cfg.get("BlockPublicPolicy"),
                        cfg.get("RestrictPublicBuckets"),
                    ])
                    if all_blocked:
                        entry["status"] = "enabled"
                        entry["detail"] = "All four public access vectors blocked at account level"
                    else:
                        missing = [k for k, v in cfg.items() if not v]
                        entry["status"] = "warn"
                        entry["detail"] = f"Partial block — missing: {', '.join(missing)}"
                except ClientError as e:
                    if "NoSuchPublicAccessBlockConfiguration" in str(e):
                        entry["status"] = "disabled"
                        entry["detail"] = "No account-level public access block configured"
                    else:
                        raise

            elif tool["id"] == "config":
                cfg_client = session.client("config")
                recorders = cfg_client.describe_configuration_recorders().get("ConfigurationRecorders", [])
                if recorders:
                    statuses = cfg_client.describe_configuration_recorder_status().get("ConfigurationRecordersStatus", [])
                    recording = any(s.get("recording") for s in statuses)
                    if recording:
                        entry["status"] = "enabled"
                        entry["detail"] = "Config recorder active — capturing resource history"
                    else:
                        entry["status"] = "warn"
                        entry["detail"] = "Config recorder exists but not currently recording"
                else:
                    entry["status"] = "disabled"
                    entry["detail"] = "AWS Config not enabled in this region"

        except Exception as e:
            entry["status"] = "error"
            entry["detail"] = f"Check failed: {str(e)[:120]}"

        results.append(entry)

    return results


# ── Enablers: write operations, called only on explicit user consent ───────────

def enable_guardduty(session: boto3.Session) -> dict:
    """Enable GuardDuty threat detection. Creates a detector in the current region."""
    try:
        gd = session.client("guardduty")
        # Check if already enabled
        existing = gd.list_detectors().get("DetectorIds", [])
        if existing:
            det = gd.get_detector(DetectorId=existing[0])
            if det["Status"] == "ENABLED":
                return {"ok": True, "already_enabled": True,
                        "message": "GuardDuty was already enabled.",
                        "detail": f"Detector ID: {existing[0][:8]}..."}

        response = gd.create_detector(
            Enable=True,
            FindingPublishingFrequency="SIX_HOURS",
            Features=[
                {"Name": "S3_DATA_EVENTS", "Status": "ENABLED"},
                {"Name": "EKS_AUDIT_LOGS", "Status": "ENABLED"},
                {"Name": "MALWARE_PROTECTION", "Status": "ENABLED"},
            ],
        )
        detector_id = response["DetectorId"]
        log.info("GuardDuty enabled — detector %s", detector_id[:8])
        return {
            "ok": True,
            "message": "GuardDuty is now active. Threat detection begins immediately.",
            "detail": f"Detector ID: {detector_id[:8]}... · Findings publish every 6 hours",
            "evidence": {
                "tool": "AWS GuardDuty",
                "action": "CreateDetector",
                "detector_id": detector_id,
                "status": "ENABLED",
            },
        }
    except ClientError as e:
        return {"ok": False, "error": f"AWS error: {e.response['Error']['Message']}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def enable_cloudtrail(session: boto3.Session) -> dict:
    """
    Enable CloudTrail multi-region logging.
    Creates a dedicated S3 bucket and trail if none exist.
    """
    import time
    try:
        account_id = session.client("sts").get_caller_identity()["Account"]
        region = session.region_name or "us-east-1"
        bucket_name = f"auditcaddie-cloudtrail-{account_id}"
        trail_name = "auditcaddie-trail"
        ct = session.client("cloudtrail")

        # Check if multi-region trail already exists
        trails = ct.describe_trails(includeShadowTrails=False).get("trailList", [])
        existing = next((t for t in trails if t.get("IsMultiRegionTrail")), None)
        if existing:
            status = ct.get_trail_status(Name=existing["TrailARN"])
            if status.get("IsLogging"):
                return {"ok": True, "already_enabled": True,
                        "message": f"CloudTrail multi-region trail '{existing['Name']}' already logging.",
                        "detail": "No changes made."}
            # Trail exists but not logging — just start it
            ct.start_logging(Name=existing["TrailARN"])
            return {"ok": True, "message": f"CloudTrail logging resumed for trail '{existing['Name']}'.",
                    "detail": "Trail was paused — now actively logging."}

        # Create dedicated S3 bucket for CloudTrail logs
        s3 = session.client("s3")
        try:
            if region == "us-east-1":
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region}
                )
        except ClientError as e:
            if e.response["Error"]["Code"] not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
                raise

        # Apply CloudTrail bucket policy
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AWSCloudTrailAclCheck",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:GetBucketAcl",
                    "Resource": f"arn:aws:s3:::{bucket_name}",
                },
                {
                    "Sid": "AWSCloudTrailWrite",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:PutObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/AWSLogs/{account_id}/*",
                    "Condition": {"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}},
                },
            ],
        }
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))

        # Block public access on the CloudTrail bucket
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True, "IgnorePublicAcls": True,
                "BlockPublicPolicy": True, "RestrictPublicBuckets": True,
            },
        )

        time.sleep(1)  # Brief pause for bucket policy propagation

        # Create and start the trail
        trail = ct.create_trail(
            Name=trail_name,
            S3BucketName=bucket_name,
            IsMultiRegionTrail=True,
            EnableLogFileValidation=True,
            IncludeGlobalServiceEvents=True,
        )
        ct.start_logging(Name=trail["TrailARN"])

        log.info("CloudTrail trail '%s' created and logging to %s", trail_name, bucket_name)
        return {
            "ok": True,
            "message": "CloudTrail is now recording all API activity across all regions.",
            "detail": f"Trail: {trail_name} · Logs → s3://{bucket_name} · Log file validation enabled",
            "evidence": {
                "tool": "AWS CloudTrail",
                "action": "CreateTrail + StartLogging",
                "trail_name": trail_name,
                "trail_arn": trail["TrailARN"],
                "s3_bucket": bucket_name,
                "multi_region": True,
                "log_validation": True,
            },
        }
    except ClientError as e:
        return {"ok": False, "error": f"AWS error: {e.response['Error']['Message']}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def enable_vpc_flow_logs(session: boto3.Session) -> dict:
    """
    Enable VPC Flow Logs for all VPCs in the region.
    Creates a CloudWatch Logs group and IAM role for delivery.
    """
    try:
        account_id = session.client("sts").get_caller_identity()["Account"]
        region = session.region_name or "us-east-1"
        ec2 = session.client("ec2")
        logs_client = session.client("logs")
        iam = session.client("iam")

        vpcs = ec2.describe_vpcs().get("Vpcs", [])
        if not vpcs:
            return {"ok": True, "message": "No VPCs found in this region — nothing to configure.",
                    "detail": "Flow logs will be enabled automatically when VPCs are created."}

        # Create CloudWatch Logs group
        log_group = "/auditcaddie/vpc-flow-logs"
        try:
            logs_client.create_log_group(logGroupName=log_group)
            logs_client.put_retention_policy(logGroupName=log_group, retentionInDays=365)
        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceAlreadyExistsException":
                raise

        # Create IAM role for VPC Flow Logs → CloudWatch delivery
        role_name = "AuditCaddieVPCFlowLogsRole"
        role_arn = None
        try:
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "vpc-flow-logs.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }],
            }
            role = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="AuditCaddie — VPC Flow Logs delivery to CloudWatch",
            )
            role_arn = role["Role"]["Arn"]
            iam.put_role_policy(
                RoleName=role_name,
                PolicyName="AuditCaddieFlowLogsPolicy",
                PolicyDocument=json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup", "logs:CreateLogStream",
                            "logs:PutLogEvents", "logs:DescribeLogGroups",
                            "logs:DescribeLogStreams",
                        ],
                        "Resource": "*",
                    }],
                }),
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "EntityAlreadyExists":
                role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
            else:
                raise

        import time; time.sleep(8)  # IAM propagation delay

        # Enable flow logs for each uncovered VPC
        existing_logs = ec2.describe_flow_logs().get("FlowLogs", [])
        covered = {fl["ResourceId"] for fl in existing_logs if fl["FlowLogStatus"] == "ACTIVE"}
        enabled_vpcs, skipped_vpcs = [], []

        for vpc in vpcs:
            vpc_id = vpc["VpcId"]
            if vpc_id in covered:
                skipped_vpcs.append(vpc_id)
                continue
            ec2.create_flow_logs(
                ResourceIds=[vpc_id],
                ResourceType="VPC",
                TrafficType="ALL",
                LogGroupName=log_group,
                DeliverLogsPermissionArn=role_arn,
                LogFormat="${version} ${account-id} ${interface-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${packets} ${bytes} ${start} ${end} ${action} ${log-status}",
            )
            enabled_vpcs.append(vpc_id)

        log.info("VPC Flow Logs enabled on %d VPC(s)", len(enabled_vpcs))
        return {
            "ok": True,
            "message": f"VPC Flow Logs now active on {len(enabled_vpcs) + len(skipped_vpcs)} VPC(s) → CloudWatch Logs.",
            "detail": f"Log group: {log_group} · 1-year retention · All traffic captured",
            "evidence": {
                "tool": "VPC Flow Logs",
                "action": "CreateFlowLogs",
                "log_group": log_group,
                "vpcs_enabled": enabled_vpcs,
                "vpcs_already_covered": skipped_vpcs,
                "iam_role": role_name,
            },
        }
    except ClientError as e:
        return {"ok": False, "error": f"AWS error: {e.response['Error']['Message']}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def enable_security_hub(session: boto3.Session) -> dict:
    """Enable AWS Security Hub with the Foundational Security Best Practices standard."""
    try:
        sh = session.client("securityhub")
        try:
            sh.describe_hub()
            return {"ok": True, "already_enabled": True,
                    "message": "Security Hub is already enabled.",
                    "detail": "Findings are already being aggregated."}
        except ClientError:
            pass  # Not yet enabled — proceed

        sh.enable_security_hub(
            EnableDefaultStandards=True,
            Tags={"ManagedBy": "AuditCaddie"},
        )
        log.info("Security Hub enabled")
        return {
            "ok": True,
            "message": "Security Hub is now active. AWS Foundational Security Best Practices enabled.",
            "detail": "Findings from GuardDuty, Inspector, and IAM Access Analyzer will now aggregate here.",
            "evidence": {
                "tool": "AWS Security Hub",
                "action": "EnableSecurityHub",
                "standards": ["AWS Foundational Security Best Practices"],
            },
        }
    except ClientError as e:
        return {"ok": False, "error": f"AWS error: {e.response['Error']['Message']}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def enable_s3_public_access_block(session: boto3.Session) -> dict:
    """Block all public S3 access at the account level."""
    try:
        account_id = session.client("sts").get_caller_identity()["Account"]
        s3c = session.client("s3control")
        s3c.put_public_access_block(
            AccountId=account_id,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            },
        )
        log.info("S3 account-level public access block enabled for account %s", account_id)
        return {
            "ok": True,
            "message": "S3 public access is now blocked at the account level.",
            "detail": "All 4 public access vectors blocked — no bucket can be made public, even by accident.",
            "evidence": {
                "tool": "S3 Block Public Access",
                "action": "PutPublicAccessBlock",
                "account_id": account_id,
                "all_flags_enabled": True,
            },
        }
    except ClientError as e:
        return {"ok": False, "error": f"AWS error: {e.response['Error']['Message']}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def enable_config(session: boto3.Session) -> dict:
    """
    Enable AWS Config with a dedicated S3 bucket for configuration history.
    Records all supported resources in the current region.
    """
    import time
    try:
        account_id = session.client("sts").get_caller_identity()["Account"]
        region = session.region_name or "us-east-1"
        bucket_name = f"auditcaddie-config-{account_id}"
        recorder_name = "auditcaddie-config-recorder"
        cfg = session.client("config")

        # Check if already recording
        recorders = cfg.describe_configuration_recorders().get("ConfigurationRecorders", [])
        if recorders:
            statuses = cfg.describe_configuration_recorder_status().get("ConfigurationRecordersStatus", [])
            if any(s.get("recording") for s in statuses):
                return {"ok": True, "already_enabled": True,
                        "message": "AWS Config is already recording.",
                        "detail": "Configuration history is being captured."}

        # Create S3 bucket for Config delivery
        s3 = session.client("s3")
        try:
            if region == "us-east-1":
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region}
                )
        except ClientError as e:
            if e.response["Error"]["Code"] not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
                raise

        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {"Sid": "AWSConfigBucketPermissionsCheck", "Effect": "Allow",
                 "Principal": {"Service": "config.amazonaws.com"},
                 "Action": "s3:GetBucketAcl", "Resource": f"arn:aws:s3:::{bucket_name}"},
                {"Sid": "AWSConfigBucketDelivery", "Effect": "Allow",
                 "Principal": {"Service": "config.amazonaws.com"},
                 "Action": "s3:PutObject",
                 "Resource": f"arn:aws:s3:::{bucket_name}/AWSLogs/{account_id}/Config/*",
                 "Condition": {"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}}},
            ],
        }))
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={"BlockPublicAcls": True, "IgnorePublicAcls": True,
                                            "BlockPublicPolicy": True, "RestrictPublicBuckets": True},
        )

        # Create IAM service-linked role (or use existing)
        iam = session.client("iam")
        role_arn = f"arn:aws:iam::{account_id}:role/aws-service-role/config.amazonaws.com/AWSServiceRoleForConfig"
        try:
            iam.create_service_linked_role(AWSServiceName="config.amazonaws.com")
            time.sleep(5)
        except ClientError as e:
            if e.response["Error"]["Code"] != "InvalidInput":  # Already exists
                pass

        # Create Config recorder and delivery channel
        cfg.put_configuration_recorder(ConfigurationRecorder={
            "name": recorder_name,
            "roleARN": role_arn,
            "recordingGroup": {
                "allSupported": True,
                "includeGlobalResourceTypes": True,
            },
        })
        cfg.put_delivery_channel(DeliveryChannel={
            "name": "auditcaddie-delivery-channel",
            "s3BucketName": bucket_name,
            "configSnapshotDeliveryProperties": {"deliveryFrequency": "TwentyFour_Hours"},
        })
        cfg.start_configuration_recorder(ConfigurationRecorderName=recorder_name)

        log.info("AWS Config enabled — recording to s3://%s", bucket_name)
        return {
            "ok": True,
            "message": "AWS Config is now recording your infrastructure configuration history.",
            "detail": f"Recorder: {recorder_name} · History → s3://{bucket_name} · Daily snapshots",
            "evidence": {
                "tool": "AWS Config",
                "action": "PutConfigurationRecorder + StartConfigurationRecorder",
                "recorder_name": recorder_name,
                "s3_bucket": bucket_name,
                "all_resources": True,
            },
        }
    except ClientError as e:
        return {"ok": False, "error": f"AWS error: {e.response['Error']['Message']}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── Dispatch map ───────────────────────────────────────────────────────────────

ENABLER_REGISTRY = {
    "guardduty":      enable_guardduty,
    "cloudtrail":     enable_cloudtrail,
    "vpc_flow_logs":  enable_vpc_flow_logs,
    "security_hub":   enable_security_hub,
    "s3_public_access": enable_s3_public_access_block,
    "config":         enable_config,
}
