# Review Workflow

How to audit a project's GitHub Actions workflows, for your own repositories or for a bug bounty target. Read [scope and rules](#before-you-start) first, because workflows are code that runs, and careless testing can cause real damage.

## Before you start

- **Check scope.** Confirm the repository is in scope and that CI/CD issues are an accepted class. Programs differ: some treat workflow weaknesses as informational unless you show real impact, and some exclude them.
- **Static review is the default.** Reading workflow files is passive. **Do not open pull requests, issues or comments just to trigger a target's workflows** unless the program explicitly allows it, because that is active testing on their infrastructure.
- **Never use or exfiltrate real secrets.** Demonstrate reachability, not theft.
- **Reproduce in your own fork or repository** with a copy of the workflow and fake secrets.

## 1. Inventory

List every workflow and how it is triggered.

```bash
ls .github/workflows
rg -n "^on:|^  (push|pull_request|pull_request_target|workflow_run|issue_comment|issues|schedule|workflow_dispatch|release)" .github/workflows
```

Also look at composite actions in the repository (`action.yml` files) and reusable workflows called with `uses:`.

## 2. Triage the triggers

| Trigger | Question to ask |
| --- | --- |
| `pull_request_target`, `workflow_run` | Does it check out or execute code from the pull request or the triggering workflow's artifacts? |
| `issue_comment`, `issues` | Is comment or issue text used in a script or passed to another tool? |
| `pull_request` from forks | What can the workflow do with a read-only token and no secrets? Usually little. |
| `workflow_dispatch`, `schedule` | Who can trigger it, and with which inputs? |
| `push`, `release` | Which branches or tags, and who can push to them? |

## 3. Follow untrusted data

For each workflow that can be triggered by someone without write access, trace the attacker-controlled fields: titles, bodies, branch names, commit messages, labels, artifact contents. Check where each ends up: a `run:` script, an `actions/github-script` block, `GITHUB_ENV` or `GITHUB_PATH`, an `env:` that a later script expands, or an input to a third-party action.

See [attack patterns](ATTACK_PATTERNS.md) for the vulnerable and safe forms of each.

## 4. Check privileges

- Which `permissions:` does the workflow or job have? A missing block means the repository default.
- Which secrets can the job read? Are they scoped to an environment?
- Does the job use a self-hosted runner, and is it ephemeral?
- Does checkout persist credentials, and are workspace files uploaded as artifacts?

## 5. Check the supply chain

- Are third-party actions pinned to full commit SHAs?
- Are any actions archived, abandoned or from unknown maintainers?
- Does a reusable workflow or composite action pull in more unpinned dependencies?
- Is Dependabot or Renovate configured for `github-actions`?

## 6. Run the scanners

Scanners find the easy cases quickly. Use them after you read the workflows, not instead of reading.

```bash
zizmor .
actionlint
poutine analyze_local .
```

See the [quickstart](QUICKSTART.md). Treat each result as a lead, and confirm that the trigger is reachable by an attacker and that the impact is real.

## 7. Prove it safely

Build a minimal copy in your own repository:

1. Copy the workflow file and any scripts it calls.
2. Replace real secrets with dummy values, and give the dummy token a recognizable name.
3. Trigger it the way an attacker would, using a pull request from a second account or a fork you control.
4. Show what the attacker controls and what the workflow can reach, for example that the dummy secret value appears in the output or that a write-scoped token is available.

## 8. Rate the impact honestly

Severity depends on what the compromised job can reach: write access to the repository, release or publishing credentials, cloud credentials, or nothing sensitive. A script injection in a job with a read-only token and no secrets is much less serious than one in a release workflow. Say what the token permissions and secrets are, and do not overstate.

## 9. Report

- Link to the exact workflow lines with permalinks that include the commit hash.
- Describe the attacker model: who can trigger it and what they control.
- Include reproduction steps from your own fork and the observed result.
- Suggest the fix, for example moving a value into `env`, narrowing `permissions`, or pinning to a SHA.
- Follow the project's security policy, and give maintainers time to fix before any public discussion.

Write the sections above into your report, with the workflow permalinks, the attacker model, your reproduction and the observed result.
