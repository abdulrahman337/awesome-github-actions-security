# Awesome GitHub Actions Security [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of tools, research, incident write-ups and official guidance for securing and reviewing GitHub Actions workflows.

CI/CD pipelines run untrusted code, hold powerful credentials and publish software that thousands of projects depend on, which makes them a favorite target. The March 2025 compromise of a popular action exposed secrets from more than 23,000 repositories. This list collects what defenders, maintainers and bug bounty researchers need: scanners, pinning tools, hardening controls, attack research and the incidents that explain why they matter.

Beyond links, this repository ships practical guides:

- [Tool comparison](docs/TOOL_COMPARISON.md) - What zizmor, poutine, actionlint and Scorecard each detect, where they disagree, and how to combine them.
- [Attack patterns](docs/ATTACK_PATTERNS.md) - The common workflow vulnerabilities, how to spot each one, and how to fix it.
- [Hardening checklist](docs/HARDENING_CHECKLIST.md) - Controls to apply to repositories and organizations, in priority order.
- [Incident response playbook](docs/INCIDENT_RESPONSE_PLAYBOOK.md) - What to do in the first hours when an action or workflow you use may be compromised.
- [Incident timeline](docs/INCIDENTS.md) - Major Actions supply chain incidents and what GitHub changed in response.
- [Review workflow](docs/REVIEW_WORKFLOW.md) - How to audit a project's workflows safely, including for bug bounty programs.
- [Quickstart](docs/QUICKSTART.md) - Install and first-run commands for the main tools.
- [Secure workflow example](docs/SECURE_WORKFLOW_EXAMPLE.md) - A hardened workflow template to adapt.
- [Maintenance status](docs/MAINTENANCE_STATUS.md) - Last-activity snapshot of every GitHub project in the list, so you can judge which tools are still alive.

## Contents

- [Workflow Scanners and Linters](#workflow-scanners-and-linters)
- [Pinning and Dependency Management](#pinning-and-dependency-management)
- [Runtime Hardening and Monitoring](#runtime-hardening-and-monitoring)
- [Secrets and Credentials](#secrets-and-credentials)
- [Provenance, Signing and Policy](#provenance-signing-and-policy)
- [Local Testing](#local-testing)
- [Attack Research and Training](#attack-research-and-training)
- [Official Guidance and Roadmap](#official-guidance-and-roadmap)
- [Incidents and Case Studies](#incidents-and-case-studies)

## Workflow Scanners and Linters

- [zizmor](https://github.com/zizmorcore/zizmor) - Static analysis for GitHub Actions workflows that finds injection, permission and pinning problems.
- [poutine](https://github.com/boostsecurityio/poutine) - Security scanner for build pipelines that detects misconfigurations in GitHub Actions and other pipeline formats.
- [actionlint](https://github.com/rhysd/actionlint) - Static checker for workflow files that catches syntax and type errors and flags untrusted inputs used in scripts.
- [Octoscan](https://github.com/synacktiv/octoscan) - Static vulnerability scanner for GitHub Actions workflows, from Synacktiv.
- [Raven](https://github.com/CycodeLabs/raven) - Graph-based analyzer that stores workflows in Neo4j to find vulnerabilities across many repositories; low recent activity.
- [Semgrep Rules](https://github.com/semgrep/semgrep-rules) - Community rules that include GitHub Actions checks such as shell injection.
- [CodeQL](https://github.com/github/codeql) - Semantic analysis engine whose supported languages include GitHub Actions workflows.
- [OpenSSF Scorecard](https://github.com/ossf/scorecard) - Automated checks that include token permissions, pinned dependencies and dangerous workflow patterns.
- [zizmor-action](https://github.com/zizmorcore/zizmor-action) - Action that runs zizmor from a workflow; the maintainers say it is ready for public use but still in early development.
- [Scorecard Action](https://github.com/ossf/scorecard-action) - Official GitHub Action that runs OpenSSF Scorecard checks on a repository and can publish the results.

## Pinning and Dependency Management

- [pinact](https://github.com/suzuki-shunsuke/pinact) - Pins actions and reusable workflows to full commit SHAs and keeps version comments up to date.
- [ratchet](https://github.com/sethvargo/ratchet) - Pins and updates actions and container references across several CI systems.
- [frizbee](https://github.com/stacklok/frizbee) - Pins actions and container image references to checksums, from Stacklok.
- [pin-github-action](https://github.com/mheap/pin-github-action) - Command line tool that pins action versions to commit SHAs and works in pre-commit hooks.
- [Dependabot Core](https://github.com/dependabot/dependabot-core) - Engine behind Dependabot, which can update pinned actions when set up for the github-actions ecosystem.
- [Renovate](https://github.com/renovatebot/renovate) - Automated dependency updater that supports GitHub Actions and digest pinning.
- [Dependency Review Action](https://github.com/actions/dependency-review-action) - Fails pull requests that introduce vulnerable dependencies.

## Runtime Hardening and Monitoring

- [Harden-Runner](https://github.com/step-security/harden-runner) - Runtime security agent that monitors and restricts network and file activity on runners.
- [Actions Permissions](https://github.com/GitHubSecurityLab/actions-permissions) - GitHub Security Lab tool that helps find least-privilege GITHUB_TOKEN permissions for workflows.
- [StepSecurity Secure Repo](https://github.com/step-security/secure-repo) - Applies security best practices to workflows, such as pinning and token permissions.

## Secrets and Credentials

- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Finds secrets in repositories and other sources, and can verify whether they are live; keep verification off unless you are allowed to test credentials.
- [Gitleaks](https://github.com/gitleaks/gitleaks) - Scans repositories and history for hardcoded secrets using configurable rules.

## Provenance, Signing and Policy

- [attest-build-provenance](https://github.com/actions/attest-build-provenance) - Official action for signed build provenance attestations; since version 4 it is a thin wrapper, and new workflows should use actions/attest.
- [SLSA GitHub Generator](https://github.com/slsa-framework/slsa-github-generator) - Generators that produce SLSA provenance for builds on GitHub-hosted runners; no longer actively maintained, and its maintainers suggest GitHub artifact attestations instead.
- [Cosign](https://github.com/sigstore/cosign) - Signs and verifies container images and other artifacts.
- [Allstar](https://github.com/ossf/allstar) - GitHub app that continuously enforces security policies on repositories, such as branch protection.
- [SLSA](https://slsa.dev) - Framework of supply chain security levels and requirements for build provenance.
- [attest](https://github.com/actions/attest) - Official action that generates attestations for workflow artifacts, and the base that the provenance and SBOM actions now wrap.
- [Gitsign](https://github.com/sigstore/gitsign) - Keyless Git commit signing with Sigstore, tied to your GitHub or OIDC identity.

## Local Testing

- [act](https://github.com/nektos/act) - Runs workflows locally in containers, a safe way to experiment without touching a real repository.

## Attack Research and Training

- [Gato-X](https://github.com/AdnaneKhan/gato-x) - Enumeration and vulnerability-finding tool for GitHub Actions pipelines, for use only within authorized scope.
- [GitHub Actions Goat](https://github.com/step-security/github-actions-goat) - Intentionally vulnerable repository for learning about Actions attacks and runtime hardening.
- [Top 10 CI/CD Security Risks](https://github.com/cider-security-research/top-10-cicd-security-risks) - Write-up of the ten most critical CI/CD risks, with examples and mitigations.
- [Preventing Pwn Requests](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/) - GitHub Security Lab article on the dangerous pull_request_target pattern.
- [CI/CD Security Cheat Sheet](https://github.com/OWASP/CheatSheetSeries) - OWASP Cheat Sheet Series, which includes a CI/CD security cheat sheet among many others.
- [Unpacking Security Scanners for GitHub Actions](https://arxiv.org/abs/2601.14455) - Comparative study from Université de Montréal showing that workflow scanners cover different weaknesses and disagree on the same workflows.
- [gha-hazmat](https://github.com/woodruffw/gha-hazmat) - Collection of insecure and exploitable workflows and action definitions, each isolated, with Actions disabled so nothing runs.
- [CI/CD Goat](https://github.com/cider-security-research/cicd-goat) - Deliberately vulnerable CI/CD environment with capture-the-flag challenges, from Cider Security; low recent activity.
- [Trajan](https://github.com/praetorian-inc/trajan) - Praetorian scanner for CI/CD pipeline weaknesses on GitHub, GitLab and Azure DevOps that also automates attacks, so use it only inside authorized scope.

## Official Guidance and Roadmap

- [Security Hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions) - GitHub's guide, which states that pinning to a full-length commit SHA is the only way to use an action as an immutable release.
- [Actions 2026 Security Roadmap](https://github.blog/news-insights/product-news/whats-coming-to-our-github-actions-2026-security-roadmap/) - GitHub plan for workflow dependency locking, immutable releases, policy controls and an egress firewall for hosted runners.
- [SHA Pinning Enforcement and Blocking](https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/) - Changelog describing the policy that blocks specific actions and fails workflows that are not SHA pinned.
- [Securely Using pull_request_target](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) - GitHub guide for deciding whether a workflow needs that privileged event and how to use it safely.
- [Secure Use Reference](https://docs.github.com/en/actions/reference/security/secure-use) - GitHub reference of good practices, including patterns that mitigate script injection.

## Incidents and Case Studies

- [tj-actions Advisory](https://github.com/advisories/GHSA-mrrh-fwg8-r2c3) - GitHub advisory for the tj-actions/changed-files compromise, which affected more than 23,000 repositories.
- [Unit 42 Analysis](https://unit42.paloaltonetworks.com/github-actions-supply-chain-attack/) - Timeline of how a targeted attack on Coinbase expanded into the tj-actions and reviewdog incidents.
- [Orca Hardening Guide](https://orca.security/resources/blog/github-actions-hardening/) - Walkthrough of the tj-actions chain in five steps, with matching hardening measures.
- [Cycode Analysis](https://cycode.com/blog/github-actions-supply-chain-attack/) - Comparison of documented Actions attacks that share the same pattern.
- [15 Security Pitfalls](https://blog.stephane-robert.info/en/post/github-actions-15-security-pitfalls/) - Checklist of common mistakes mapped to real 2025 and 2026 campaigns.
- [The Case for GitHub Actions Security](https://securitylabs.datadoghq.com/articles/case-for-github-actions-security/) - Datadog Security Labs article on pwn requests, script injection and compromised credentials after recent attacks.

## Related Lists

- [Static Analysis](https://github.com/analysis-tools-dev/static-analysis) - Curated list of static analysis tools, linters and code quality checkers for many languages.

## Contributing

Contributions are welcome. Please read the [contribution guidelines](CONTRIBUTING.md) first.
