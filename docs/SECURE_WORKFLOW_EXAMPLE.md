# Secure Workflow Example

A hardened template to adapt. Every action is pinned to a full commit SHA with the version in a comment, and the workflow passes `actionlint` and `zizmor` in their strictest mode. The SHAs were checked against the release tags on 25 October 2026 and picked from releases that were at least two weeks old, so look for newer releases before you copy them, and verify each SHA yourself.

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

# Start with no permissions. Give each job only what it needs.
permissions: {}

# Cancel superseded runs on pull requests, but never a run on the main branch.
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  test:
    name: Build and test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: read
    steps:
      # Pinned to a full SHA, with the human-readable version in a comment.
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false   # keep the token out of the workspace

      # Optional: watch and restrict outbound traffic. Start in audit mode,
      # review the observed endpoints, then switch to block mode.
      - uses: step-security/harden-runner@ccd8616d44fd3846e67624a50d5aad6d37bf2d25 # v2.22.1
        with:
          egress-policy: audit

      - name: Build
        run: make build

      - name: Test
        run: make test

      # Untrusted values go through env, never directly into the script.
      - name: Print branch name safely
        env:
          BRANCH: ${{ github.head_ref }}
        run: echo "Branch is $BRANCH"
```

Notes:

- This workflow uses `pull_request`, not `pull_request_target`, so fork pull requests run with a read-only token and without secrets.
- It has **no secrets**. Jobs that need deploy credentials belong in a separate workflow that runs only on trusted events, uses an [environment](HARDENING_CHECKLIST.md) with required reviewers, and authenticates to the cloud with OpenID Connect where possible.
- For release workflows, add only the extra permissions you need, for example `id-token: write` for OIDC or attestations, and keep the trigger narrow, such as protected tags.
- Pin or review every other action you add. See the [hardening checklist](HARDENING_CHECKLIST.md) and [attack patterns](ATTACK_PATTERNS.md).
