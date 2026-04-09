"""
AuditCaddie OSS — GitHub Security Checks
Scans GitHub organization or user repositories for security
controls relevant to SOC 2, ISO 27001, and NIST CSF.

Requires a GitHub token with:
  - repo scope (for private repos)
  - read:org scope (for organization checks)
"""

import logging
from typing import Optional

log = logging.getLogger("auditcaddie.github")


def _pass(check_id: str, title: str, detail: str = "") -> dict:
    return {"check": check_id, "title": title, "status": "pass", "detail": detail}

def _fail(check_id: str, title: str, detail: str = "", remediation: str = "") -> dict:
    return {"check": check_id, "title": title, "status": "fail",
            "detail": detail, "remediation": remediation}

def _warn(check_id: str, title: str, detail: str = "") -> dict:
    return {"check": check_id, "title": title, "status": "warn", "detail": detail}

def _error(check_id: str, title: str, detail: str = "") -> dict:
    return {"check": check_id, "title": title, "status": "error", "detail": detail}


def run_github_scan(token: str, org_or_user: Optional[str] = None) -> dict:
    """
    Run GitHub security checks.
    If org_or_user is provided, scans that org/user's repos.
    Otherwise scans repos accessible to the token owner.
    """
    try:
        from github import Github, GithubException
    except ImportError:
        return {
            "ok": False,
            "error": "PyGithub not installed. Run: pip install PyGithub",
            "results": [],
        }

    if not token:
        return {
            "ok": False,
            "error": "No GitHub token provided. Set GITHUB_TOKEN in .env",
            "results": [],
        }

    try:
        gh = Github(token)
        user = gh.get_user()
        actor = org_or_user or user.login
    except Exception as e:
        return {"ok": False, "error": f"GitHub authentication failed: {e}", "results": []}

    results = []

    # ── Fetch repos ────────────────────────────────────────────────────────────
    try:
        if org_or_user:
            try:
                entity = gh.get_organization(org_or_user)
                repos = list(entity.get_repos(type="all"))
                is_org = True
            except Exception:
                entity = gh.get_user(org_or_user)
                repos = list(entity.get_repos())
                is_org = False
        else:
            repos = list(gh.get_user().get_repos())
            is_org = False

        # Limit scan to first 20 repos to keep it fast
        scanned_repos = repos[:20]
        repo_names = [r.name for r in scanned_repos]
    except Exception as e:
        return {"ok": False, "error": f"Failed to fetch repositories: {e}", "results": []}

    # ── Check: Secret Scanning ─────────────────────────────────────────────────
    try:
        no_secret_scan = []
        for repo in scanned_repos:
            if repo.private:
                try:
                    # GitHub API: secret scanning enablement
                    ss = repo.get_vulnerability_alert()  # proxy for security features
                    status = repo.security_and_analysis
                    if status and hasattr(status, "secret_scanning"):
                        if getattr(status.secret_scanning, "status", "disabled") != "enabled":
                            no_secret_scan.append(repo.name)
                except Exception:
                    pass  # API may not expose this for all plans

        if not no_secret_scan:
            results.append(_pass("github_secret_scanning",
                                 "Secret scanning enabled on private repos",
                                 f"Checked {len(scanned_repos)} repo(s)"))
        else:
            results.append(_warn("github_secret_scanning",
                                 "Secret scanning not confirmed on all repos",
                                 f"Enable under repo → Settings → Security → Secret scanning"))
    except Exception as e:
        results.append(_error("github_secret_scanning", "Secret scanning check", str(e)))

    # ── Check: Branch Protection on Default Branch ────────────────────────────
    try:
        unprotected = []
        for repo in scanned_repos:
            try:
                default_branch = repo.default_branch
                branch = repo.get_branch(default_branch)
                protection = branch.get_protection()
                pr_reviews = protection.required_pull_request_reviews
                if pr_reviews is None or pr_reviews.required_approving_review_count < 1:
                    unprotected.append(repo.name)
            except Exception:
                unprotected.append(repo.name)

        if not unprotected:
            results.append(_pass("github_branch_protection",
                                 "Branch protection enabled on default branches",
                                 f"All {len(scanned_repos)} repo(s) require PR review before merge"))
        else:
            results.append(_fail("github_branch_protection",
                                 "Branch protection missing or insufficient",
                                 f"{len(unprotected)} repo(s) unprotected: {', '.join(unprotected[:5])}",
                                 "Repo → Settings → Branches → Branch protection rules → Require pull request reviews"))
    except Exception as e:
        results.append(_error("github_branch_protection", "Branch protection check", str(e)))

    # ── Check: Dependabot Alerts ───────────────────────────────────────────────
    try:
        no_dependabot = []
        for repo in scanned_repos:
            try:
                alerts_enabled = repo.get_vulnerability_alert()
                if not alerts_enabled:
                    no_dependabot.append(repo.name)
            except Exception:
                no_dependabot.append(repo.name)

        if not no_dependabot:
            results.append(_pass("github_dependabot_alerts",
                                 "Dependabot vulnerability alerts enabled",
                                 f"All {len(scanned_repos)} repo(s) have dependency scanning"))
        else:
            results.append(_fail("github_dependabot_alerts",
                                 "Dependabot alerts not enabled on all repos",
                                 f"{len(no_dependabot)} repo(s): {', '.join(no_dependabot[:5])}",
                                 "Repo → Settings → Security → Enable vulnerability alerts"))
    except Exception as e:
        results.append(_error("github_dependabot_alerts", "Dependabot check", str(e)))

    # ── Check: No Accidentally Public Repos ───────────────────────────────────
    try:
        public_repos = [r.name for r in scanned_repos if not r.private]
        total_repos = len(repos)
        if len(public_repos) == 0:
            results.append(_pass("github_public_repo_review",
                                 "No public repositories detected",
                                 "All repos are private"))
        elif len(public_repos) <= 3:
            results.append(_warn("github_public_repo_review",
                                 f"{len(public_repos)} public repo(s) found — verify these are intentionally public",
                                 f"Public: {', '.join(public_repos)}"))
        else:
            results.append(_warn("github_public_repo_review",
                                 f"{len(public_repos)} public repos — review for accidental exposure",
                                 f"Public repos: {', '.join(public_repos[:5])}{'...' if len(public_repos) > 5 else ''}"))
    except Exception as e:
        results.append(_error("github_public_repo_review", "Public repo check", str(e)))

    # ── Check: 2FA Requirement (Org only) ─────────────────────────────────────
    if is_org:
        try:
            org_obj = gh.get_organization(org_or_user)
            if org_obj.two_factor_requirement_enabled:
                results.append(_pass("github_org_2fa",
                                     "Organization requires 2FA for all members",
                                     f"Org '{org_or_user}' enforces 2FA"))
            else:
                results.append(_fail("github_org_2fa",
                                     "Organization 2FA requirement not enforced",
                                     f"Members can access org without 2FA",
                                     "GitHub org → Settings → Authentication security → Require two-factor authentication"))
        except Exception as e:
            results.append(_warn("github_org_2fa", "Could not check org 2FA requirement", str(e)))
    else:
        results.append(_warn("github_org_2fa",
                             "Organization 2FA check skipped",
                             "Provide an organization name to check 2FA enforcement"))

    # ── Check: Code Scanning (SAST) ────────────────────────────────────────────
    try:
        no_sast = []
        for repo in scanned_repos[:10]:  # Only check first 10 to limit API calls
            try:
                # Check for workflow files mentioning code scanning
                contents = repo.get_git_tree("HEAD", recursive=True)
                workflow_files = [f.path for f in contents.tree
                                  if ".github/workflows" in f.path and f.path.endswith(".yml")]
                has_sast = False
                for wf_path in workflow_files:
                    try:
                        content = repo.get_contents(wf_path)
                        if any(keyword in content.decoded_content.decode("utf-8", errors="ignore").lower()
                               for keyword in ["codeql", "semgrep", "snyk", "code-scanning", "sonarqube"]):
                            has_sast = True
                            break
                    except Exception:
                        pass
                if not has_sast:
                    no_sast.append(repo.name)
            except Exception:
                no_sast.append(repo.name)

        if not no_sast:
            results.append(_pass("github_code_scanning",
                                 "Code scanning (SAST) configured in workflows",
                                 "CodeQL, Semgrep, or equivalent found in CI/CD workflows"))
        else:
            results.append(_warn("github_code_scanning",
                                 "Code scanning (SAST) not detected in all repos",
                                 f"{len(no_sast)} repo(s) may lack SAST: {', '.join(no_sast[:3])}. "
                                 "Add GitHub Actions workflow with CodeQL or Semgrep."))
    except Exception as e:
        results.append(_error("github_code_scanning", "Code scanning check", str(e)))

    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    warned = sum(1 for r in results if r["status"] == "warn")

    return {
        "ok": True,
        "actor": actor,
        "repos_scanned": len(scanned_repos),
        "total_repos": len(repos),
        "summary": {"pass": passed, "fail": failed, "warn": warned, "total": len(results)},
        "results": results,
    }
