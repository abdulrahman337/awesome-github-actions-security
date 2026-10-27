# Attack Patterns

The vulnerabilities that keep showing up in GitHub Actions workflows, how to recognize each one, and how to fix it. Real incidents that used these patterns are in the [incident timeline](INCIDENTS.md).

## 1. Pwn requests: privileged triggers that run untrusted code

`pull_request_target` runs in the context of the **base** repository, with access to secrets and a token that can have write permissions, even when the pull request comes from a fork. If the workflow then checks out and runs the pull request's code, the attacker's code runs with those privileges. `workflow_run` workflows have a similar risk when they trust artifacts or data from a less trusted workflow.

**Spot it:** `on: pull_request_target` (or `workflow_run`) together with `actions/checkout` using `ref: ${{ github.event.pull_request.head.sha }}` or `head.ref`, followed by a build, install or test step.

**Fix:**

- Do not check out or run pull request code in privileged workflows.
- Split the job: an unprivileged `pull_request` workflow builds and tests, and a privileged workflow only consumes its output, treating it as untrusted data.
- Require approval before workflows run for first-time or outside contributors.
- Give the token the minimum permissions.

In the March 2025 chain, Unit 42 traces the first step to a malicious pull request that exploited a `pull_request_target` workflow in a third-party repository.

## 2. Script injection

Expressions like `${{ github.event.issue.title }}` are expanded **before** the shell runs, so attacker-controlled text becomes part of the script.

Attacker-controlled fields include issue and pull request titles and bodies, comment bodies, branch names (`github.head_ref`), commit messages, author names and labels.

```yaml
# Vulnerable: the title is pasted into the script text
- run: |
    echo "Title: ${{ github.event.issue.title }}"

# Safer: pass it through an environment variable and quote it
- env:
    TITLE: ${{ github.event.issue.title }}
  run: |
    echo "Title: $TITLE"
```

The same applies to `actions/github-script`: pass values through `env` or the `context` object instead of interpolating them into the script.

GitHub's [secure use reference](https://docs.github.com/en/actions/reference/security/secure-use) recommends two patterns: use an action written in JavaScript instead of an inline script, or use an intermediate environment variable instead of an inline expression.

**Spot it:** search for `${{` expressions that reference `github.event` or `github.head_ref` inside `run:` and `script:` blocks.

## 3. Mutable action references and tag hijacking

`uses: owner/action@v1` points at a tag, and tags can be moved. An attacker who gets a maintainer's credentials can repoint tags at a malicious commit, so every workflow that references the tag runs the attacker's code on its next run.

**Fix:**

- Pin third-party actions to a **full-length commit SHA** and keep a version comment next to it. A commit SHA cannot be moved, which is why GitHub's hardening guide recommends it. Immutable releases, which publishers can now enable, protect a tag in a similar way, but that is the publisher's choice, so a SHA pin is the one protection you control yourself.
- Keep pins fresh with Dependabot or Renovate.
- Enforce pinning with an organization policy, which GitHub added in August 2025 together with a blocklist.
- Pin the actions that other actions pull in where you can, and review composite actions, because transitive dependencies are not locked today. GitHub's 2026 roadmap plans dependency locking for this.

## 4. Overbroad token permissions and secrets

Older repositories and organizations may give `GITHUB_TOKEN` broad default permissions, and secrets are often available to every job.

**Fix:**

- Set `permissions: {}` at the top of each workflow and give every job only the permissions it needs, usually `contents: read`.
- Avoid `secrets: inherit` for reusable workflows.
- Scope secrets to **environments** with required reviewers.
- Prefer OpenID Connect to cloud providers over long-lived cloud keys.
- Do not give jobs that run third-party code access to secrets they do not need.

## 5. Secrets exposure through logs and runner memory

Actions masks known secrets in logs, but malicious code running in a job can read environment variables and process memory and print the values in a transformed form. The tj-actions payload read secrets from the runner worker process memory and printed them to the workflow logs, which are public for public repositories.

**Fix:**

- Restrict outbound network traffic and monitor it, for example with [Harden-Runner](https://github.com/step-security/harden-runner).
- Keep secrets out of jobs that run third-party actions.
- After a suspected compromise, rotate every secret the affected workflows could access, then review logs and recent runs.

## 6. Credential persistence and artifact leaks

`actions/checkout` stores the workflow token in the repository's git configuration by default. If a later step uploads the workspace, including the `.git` directory, as an artifact, the token can leak to anyone who can download it. Public research on this problem is known as ArtiPACKED.

**Fix:**

- Use `persist-credentials: false` on checkout unless a later step needs git credentials.
- Upload only the specific files you need, never the whole workspace.

## 7. Cache poisoning

Caches can be shared across workflows and branches. A low-privilege workflow that can write to a cache key may plant content that a later privileged workflow, such as a release job, restores and trusts. Public research has demonstrated this against real projects.

**Fix:**

- Do not restore caches in release and publish workflows from keys that untrusted workflows can write.
- Scope cache keys by workflow, branch or trust level.

## 8. Self-hosted runners

A self-hosted runner executes whatever a workflow tells it to. On a public repository, a pull request can trigger code on your machine, and a **persistent** runner keeps state, credentials and processes between jobs.

**Fix:**

- Do not attach self-hosted runners to public repositories.
- Use ephemeral runners that are destroyed after each job, isolate them on the network, and give them no long-lived credentials.

## 9. Environment file injection

Writing untrusted data to `GITHUB_ENV` or `GITHUB_PATH` changes the environment of later steps. Variables such as `PATH` or `LD_PRELOAD` can turn that into code execution.

**Fix:** never write unvalidated input to these files, and validate values against an allowlist.

## 10. Trust in third-party and reusable workflows

Every third-party action and reusable workflow is code you run with your secrets. Archived or unmaintained actions get no fixes, and a maintainer's compromised account becomes your compromise.

**Fix:**

- Review actions before adopting them, prefer actions from maintainers you can verify, and avoid archived ones.
- Reference reusable workflows by SHA too.
- Use the organization allowlist to restrict which actions can run.

## Quick searches

```bash
# Privileged triggers
rg -n "pull_request_target|workflow_run" .github/workflows

# Attacker-controlled values used in expressions
rg -n "\$\{\{ *github\.(event\.(issue|pull_request|comment|review|head_commit)|head_ref)" .github/workflows

# Actions not pinned to a full commit SHA
rg -n "uses: *[^ ]+@" .github/workflows | rg -v "@[0-9a-f]{40}"

# Permissions and secret inheritance
rg -n "permissions:|secrets: inherit" .github/workflows

# Writes to environment files
rg -n "GITHUB_ENV|GITHUB_PATH" .github/workflows
```

These produce leads. Confirm each one by reading the full workflow and checking who can trigger it.
