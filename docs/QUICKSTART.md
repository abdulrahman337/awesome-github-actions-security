# Quickstart

Install and first-run commands for the main tools. Tools change quickly, so check each project's README for current instructions and options (`--help`).

## Install safely

Tools you install run with your permissions, so treat installation as a security decision.

- **Pin a version.** The commands below use releases that were at least two weeks old on 25 October 2026. Check each project's releases page for newer ones, and wait a couple of weeks after a new release before you adopt it.
- **Check the name.** Look-alike packages exist on PyPI, npm and the Go module ecosystem. Copy the install command from the project's own README and compare the owner with the repository linked in the list.
- **Isolate what handles untrusted input.** Use a virtual environment, `pipx`, a container or a virtual machine for tools that read files or traffic you did not create.
- **Do not pipe the internet into a shell.** Download, verify, then run. Do not run an analysis tool as root unless its documentation says it must.

## Scan workflows

```bash
# zizmor: static analysis of workflow files
pipx install zizmor==1.30.1   # or: cargo install --locked zizmor --version 1.30.1, or brew install zizmor
zizmor .                    # scans .github/workflows and local actions

# actionlint: syntax, types and some injection checks
brew install actionlint     # or download a release binary
actionlint

# poutine: pipeline misconfiguration scanner
poutine analyze_local .
poutine analyze_repo OWNER/REPO    # a remote repository, needs a GitHub token
```

Run these on code you own or are allowed to analyze.

## Pin actions to commit SHAs

```bash
# pinact: pin actions and reusable workflows
pinact run

# ratchet: pin a workflow file
ratchet pin .github/workflows/ci.yml

# frizbee: pin actions in a directory
frizbee actions .github/workflows
```

Review the diff after pinning, and keep the version comment next to each SHA so Dependabot or Renovate can update it. Add the ecosystem to `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Find the right token permissions

Set `permissions:` explicitly, starting from read-only, then add only what a job needs:

```yaml
permissions:
  contents: read
```

The [Actions Permissions](https://github.com/GitHubSecurityLab/actions-permissions) tool can monitor which permissions a workflow actually uses, to help you tighten them.

## Run workflows locally

```bash
act -l              # list jobs
act pull_request    # run workflows for an event, in containers
```

Use dummy secrets with `act`, and treat unknown workflows as untrusted code.

## Scan for secrets

```bash
gitleaks git .
trufflehog git file://. --no-verification
```

`--no-verification` stops TruffleHog from authenticating with the credentials it finds. Do not turn verification on for code you do not own unless the program explicitly allows testing credentials.

## Scan the whole project's posture

```bash
scorecard --repo=github.com/OWNER/REPO
```

Scorecard checks include token permissions, pinned dependencies and dangerous workflow patterns. It needs a GitHub token in `GITHUB_AUTH_TOKEN`.

## Quick searches

See [attack patterns](ATTACK_PATTERNS.md#quick-searches) for ripgrep commands that find privileged triggers, untrusted expressions and unpinned actions.
