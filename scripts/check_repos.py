#!/usr/bin/env python3
"""Check the GitHub repositories linked from README.md.

Reports repositories that are archived, missing, renamed/moved, or have not
been pushed to for a long time, so the list can be kept fresh.

Usage:
    python scripts/check_repos.py                # check everything (uses the GitHub API)
    python scripts/check_repos.py --dry-run      # only list the repositories found in the README
    python scripts/check_repos.py --stale-days 365

Set GITHUB_TOKEN to avoid the low unauthenticated API rate limit.
Exit code is 1 if any repository is archived or missing.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

README = Path(__file__).resolve().parent.parent / "README.md"
LINK_RE = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")
IGNORED_OWNERS = {"orgs", "topics", "sponsors", "marketplace", "advisories", "features", "about", "pricing",
                  "security", "settings", "login", "join", "explore", "collections", "apps", "enterprise"}
# Archived repositories that are intentionally kept because they are still useful references.
ARCHIVED_OK = set()
# Datasets, CTFs and reference notes that do not need frequent updates, so no stale warning.
STATIC_OK = {name.lower() for name in """
    cider-security-research/top-10-cicd-security-risks step-security/github-actions-goat
    cider-security-research/cicd-goat
""".split()}


def find_repos(text):
    seen = {}
    for owner, repo in LINK_RE.findall(text):
        if owner.lower() in IGNORED_OWNERS:
            continue
        repo = repo.removesuffix(".git")
        # Names such as "." or "..", or an owner that starts with a hyphen, are never real repositories
        # and must not reach a request path or a command line.
        if repo in (".", "..", "") or owner.startswith("-") or repo.startswith("-"):
            continue
        seen.setdefault(f"{owner}/{repo}".lower(), f"{owner}/{repo}")
    return sorted(seen.values(), key=str.lower)


class ApiOnlyRedirects(urllib.request.HTTPRedirectHandler):
    """Follow redirects only inside api.github.com, so a token can never be sent to another host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname != "api.github.com":
            raise urllib.error.HTTPError(newurl, code, "redirect to another host refused", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = urllib.request.build_opener(ApiOnlyRedirects)


def fetch(full_name, token):
    req = urllib.request.Request(f"https://api.github.com/repos/{full_name}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "awesome-list-repo-check")
    if token:
        # An unredirected header is not copied to the next request if the server redirects.
        req.add_unredirected_header("Authorization", f"Bearer {token}")
    try:
        with OPENER.open(req, timeout=20) as resp:
            return resp.status, json.load(resp)
    except urllib.error.HTTPError as exc:
        return exc.code, {}
    except (urllib.error.URLError, TimeoutError, ValueError):
        return 0, {}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="only list repositories, no API calls")
    parser.add_argument("--stale-days", type=int, default=730, help="warn if no push for this many days")
    args = parser.parse_args()

    repos = find_repos(README.read_text(encoding="utf-8"))
    print(f"Found {len(repos)} GitHub repositories in README.md")
    if args.dry_run:
        for r in repos:
            print(f"  {r}")
        return 0

    token = os.environ.get("GITHUB_TOKEN")
    now = datetime.now(timezone.utc)
    problems, warnings = [], []

    for name in repos:
        status, data = fetch(name, token)
        if status in (403, 429):
            print("Rate limited by the GitHub API. Set GITHUB_TOKEN and retry.", file=sys.stderr)
            return 2
        if status == 404:
            problems.append(f"MISSING   {name}")
        elif status != 200:
            warnings.append(f"UNKNOWN   {name} (HTTP {status})")
        else:
            if data.get("archived"):
                if name.lower() in ARCHIVED_OK:
                    warnings.append(f"ARCHIVED  {name} (kept on purpose)")
                else:
                    problems.append(f"ARCHIVED  {name}")
            if data.get("full_name", name).lower() != name.lower():
                warnings.append(f"MOVED     {name} -> {data['full_name']}")
            pushed = data.get("pushed_at")
            if pushed:
                age = (now - datetime.fromisoformat(pushed.replace("Z", "+00:00"))).days
                if age > args.stale_days and name.lower() not in STATIC_OK:
                    warnings.append(f"STALE     {name} (last push {age} days ago)")
        time.sleep(0.2)

    for line in warnings:
        print(line)
    for line in problems:
        print(line)
    if not problems and not warnings:
        print("All repositories look healthy.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
