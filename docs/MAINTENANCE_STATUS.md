# Maintenance Status

A snapshot of how recently each GitHub project in the list was updated, measured on **25 October 2026**. Use it to judge which tools are still alive before you build a workflow on them. Regenerate it with `python scripts/update_maintenance_status.py`.

## How to read this

- "Last commit" is the most recent commit on the default branch, taken from GitHub's commit feed. "Days ago" counts from the snapshot date.
- A quiet repository is not automatically bad. Datasets, CTF challenges, reference notes and finished standards do not need frequent updates, and they are marked as such. A quiet **tool** is a risk: it may break with new language, compiler, runtime or platform versions.
- Commits are only one signal. Some projects release from other branches, and a low commit count can mean stability. Check releases and open issues before deciding.
- The [repository health script](../scripts/check_repos.py) flags archived and missing repositories automatically. This page is a snapshot and will age.

## Key tools: latest releases

| Tool | Last commit | Latest release |
| --- | --- | --- |
| zizmor | 2026-10-25 | v1.32.0-rc1 (2026-10-23) |
| pinact | 2026-10-25 | v5.0.2 (2026-10-25) |
| scorecard | 2026-10-24 | v5.6.0 (2026-10-12) |
| poutine | 2026-10-21 | v1.1.6 (2026-05-22) |
| harden-runner | 2026-10-19 | v2.22.2 (2026-10-19) |
| act | 2026-06-01 | v0.2.89 (2026-06-01) |
| actionlint | 2026-04-19 | v1.7.12 (2026-03-31) |




## Active: last commit within about 6 months (30 projects)

| Repository | Last commit | Days ago |
| --- | --- | --- |
| [dependabot/dependabot-core](https://github.com/dependabot/dependabot-core) | 2026-10-25 | 0 |
| [OWASP/CheatSheetSeries](https://github.com/OWASP/CheatSheetSeries) | 2026-10-25 | 0 |
| [renovatebot/renovate](https://github.com/renovatebot/renovate) | 2026-10-25 | 0 |
| [suzuki-shunsuke/pinact](https://github.com/suzuki-shunsuke/pinact) | 2026-10-25 | 0 |
| [zizmorcore/zizmor](https://github.com/zizmorcore/zizmor) | 2026-10-25 | 0 |
| [ossf/scorecard](https://github.com/ossf/scorecard) | 2026-10-24 | 1 |
| [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) | 2026-10-24 | 1 |
| [zizmorcore/zizmor-action](https://github.com/zizmorcore/zizmor-action) | 2026-10-24 | 1 |
| [github/codeql](https://github.com/github/codeql) | 2026-10-23 | 2 |
| [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) | 2026-10-23 | 2 |
| [synacktiv/octoscan](https://github.com/synacktiv/octoscan) | 2026-10-23 | 2 |
| [sigstore/cosign](https://github.com/sigstore/cosign) | 2026-10-22 | 3 |
| [analysis-tools-dev/static-analysis](https://github.com/analysis-tools-dev/static-analysis) | 2026-10-21 | 4 |
| [boostsecurityio/poutine](https://github.com/boostsecurityio/poutine) | 2026-10-21 | 4 |
| [semgrep/semgrep-rules](https://github.com/semgrep/semgrep-rules) | 2026-10-21 | 4 |
| [sigstore/gitsign](https://github.com/sigstore/gitsign) | 2026-10-20 | 5 |
| [step-security/harden-runner](https://github.com/step-security/harden-runner) | 2026-10-19 | 6 |
| [praetorian-inc/trajan](https://github.com/praetorian-inc/trajan) | 2026-10-18 | 7 |
| [actions/dependency-review-action](https://github.com/actions/dependency-review-action) | 2026-10-16 | 9 |
| [actions/attest](https://github.com/actions/attest) | 2026-10-15 | 10 |
| [ossf/scorecard-action](https://github.com/ossf/scorecard-action) | 2026-10-14 | 11 |
| [stacklok/frizbee](https://github.com/stacklok/frizbee) | 2026-10-13 | 12 |
| [AdnaneKhan/gato-x](https://github.com/AdnaneKhan/gato-x) | 2026-10-02 | 23 |
| [ossf/allstar](https://github.com/ossf/allstar) | 2026-09-19 | 36 |
| [step-security/secure-repo](https://github.com/step-security/secure-repo) | 2026-09-10 | 45 |
| [actions/attest-build-provenance](https://github.com/actions/attest-build-provenance) | 2026-08-21 | 65 |
| [mheap/pin-github-action](https://github.com/mheap/pin-github-action) | 2026-08-13 | 73 |
| [slsa-framework/slsa-github-generator](https://github.com/slsa-framework/slsa-github-generator) | 2026-08-07 | 79 |
| [sethvargo/ratchet](https://github.com/sethvargo/ratchet) | 2026-07-18 | 99 |
| [nektos/act](https://github.com/nektos/act) | 2026-06-01 | 146 |

## Slowing: between 6 and 18 months (3 projects)

| Repository | Last commit | Days ago |
| --- | --- | --- |
| [rhysd/actionlint](https://github.com/rhysd/actionlint) | 2026-04-19 | 189 |
| [woodruffw/gha-hazmat](https://github.com/woodruffw/gha-hazmat) | 2026-04-19 | 189 |
| [GitHubSecurityLab/actions-permissions](https://github.com/GitHubSecurityLab/actions-permissions) | 2026-01-31 | 267 |

## Quiet: more than 18 months (4 projects)

Tools in this group are marked "low recent activity" in the README. Entries marked as reference or dataset are kept on purpose.

| Repository | Last commit | Days ago |
| --- | --- | --- |
| [step-security/github-actions-goat](https://github.com/step-security/github-actions-goat) | 2025-03-14 | 590 (reference or dataset) |
| [CycodeLabs/raven](https://github.com/CycodeLabs/raven) | 2025-02-24 | 608 |
| [cider-security-research/cicd-goat](https://github.com/cider-security-research/cicd-goat) | 2024-07-11 | 836 (reference or dataset) |
| [cider-security-research/top-10-cicd-security-risks](https://github.com/cider-security-research/top-10-cicd-security-risks) | 2023-01-18 | 1376 (reference or dataset) |
