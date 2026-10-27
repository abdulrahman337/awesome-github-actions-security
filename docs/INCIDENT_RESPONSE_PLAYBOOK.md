# Incident Response Playbook

What to do when a GitHub Actions action or workflow you use may have been compromised, as happened with `tj-actions/changed-files` in March 2025. It is general guidance, so adapt it to your organization's incident process and plan.

**Priorities, in order:** stop the exposure, rotate secrets, find out what ran, then clean up and learn. Rotate first and investigate second, because a leaked secret stays dangerous while you investigate.

## 1. Triage (first 15 minutes)

Answer three questions: which of our workflows use the affected action, when did they run, and which secrets could they reach?

```bash
# Find workflows that reference the action across an organization
gh search code "tj-actions/changed-files" --owner YOUR_ORG --extension yml
gh search code "tj-actions/changed-files" --owner YOUR_ORG --extension yaml

# Code search is not exhaustive (forks are not searched by default), so also check local checkouts
rg -n "uses: *tj-actions/changed-files" .github

# List recent runs of a repository
gh run list --repo OWNER/REPO --limit 100 --json databaseId,workflowName,createdAt,conclusion,event
```

Record the exposure window from the advisory, and add margin on both sides. Treat every run inside it as potentially affected. Public repositories publish their logs, so if the malicious code printed secrets there, anyone could read them.

| Situation | Treat as |
| --- | --- |
| Public repository, ran in the window, workflow had secrets | Leaked: rotate now |
| Private repository, ran in the window, workflow had secrets | Possibly exfiltrated over the network: rotate now |
| Ran in the window, no secrets, read-only token | Low risk, but check the token and artifacts |
| Did not run in the window | Not affected by this incident, but remove the action anyway |

## 2. Contain

```bash
gh workflow disable "WORKFLOW NAME" --repo OWNER/REPO    # stop a workflow from running
```

- Remove or replace the affected action, or pin it to a commit from **before** the compromise window that you have reviewed yourself.
- Add the action or version to the organization's blocklist so no other repository can run it. GitHub added this blocking and SHA pinning enforcement to the allowed actions policy in August 2025.
- Pause release and deployment pipelines that used the action until you have checked what they published.

## 3. Rotate secrets

List what the affected workflows could access, then rotate it all.

```bash
gh secret list --repo OWNER/REPO
gh secret list --org YOUR_ORG
gh secret list --repo OWNER/REPO --env ENVIRONMENT
```

| Secret type | Action |
| --- | --- |
| Personal access tokens and fine-grained tokens | Revoke and reissue with the smallest scope |
| Cloud access keys | Rotate, then invalidate sessions issued with the old keys |
| OpenID Connect roles | Review trust policies for who can assume the role, and shorten session lifetimes |
| Package registry and publishing tokens | Rotate, then check recent publishes |
| Deploy keys, SSH keys, signing keys | Replace, and revoke the old public keys |
| Third-party service API keys | Rotate in each service |
| The `GITHUB_TOKEN` | Short-lived and expires after the job, so no rotation needed, but check what it could do |

Rotate secrets from a clean machine, and change the workflow before you add new secrets, so the new values are not exposed to the same problem.

## 4. Investigate

- **Read the logs** of runs inside the window: `gh run view RUN_ID --repo OWNER/REPO --log`. Look for large encoded blobs, unexpected network calls and steps you do not recognize.
- **Check what the workflows produced:** commits, tags, releases, packages and container images created during the window. Compare them with known-good builds.
- **Look for persistence:** new deploy keys, webhooks, installed GitHub Apps, new collaborators or changed branch rules and workflow files.
- **Check downstream systems** for use of leaked credentials: cloud audit logs, registry logs and service access logs, filtered by the time of the runs.
- **Use the audit log** of your organization if your plan provides one, to review changes to settings, secrets and access.

## 5. Recover

- Rebuild and republish artifacts that were built during the window from a clean, pinned pipeline.
- Yank or revoke compromised releases and packages, and publish corrected ones.
- Restore workflow files from a reviewed commit, and require review for every change under `.github/workflows/`.
- Re-enable pipelines gradually, with the hardening below in place.

## 6. Communicate

- Tell internal stakeholders what was exposed and what you rotated.
- If you publish software, tell downstream users which versions were affected and what to do, and publish a security advisory.
- If you are an open source maintainer, record the timeline publicly once it is safe.

## 7. Learn and harden

Run a short review that answers: how did the action reach production, why were secrets available to that job, and what would have stopped it? Then apply the matching controls from the [hardening checklist](HARDENING_CHECKLIST.md):

- Pin third-party actions to full commit SHAs and enforce that with the organization policy.
- Give every workflow minimal `permissions:` and keep secrets out of jobs that run third-party code.
- Restrict and monitor outbound traffic from runners.
- Prefer short-lived OpenID Connect credentials over stored keys.
- Scan your workflows in CI with the tools in the [tool comparison](TOOL_COMPARISON.md).

## Incident notes template

```markdown
# Incident: [short name]

- Detected: [date and time, by whom]
- Affected component: [action and version range, exposure window]
- Repositories and workflows affected: [list]
- Secrets potentially exposed: [list] — rotated at [time]
- Evidence reviewed: [logs, audit log, downstream logs]
- Impact found: [none / describe]
- Actions taken: [contain, rotate, rebuild, communicate]
- Root cause and fixes: [what, owner, due date]
```
