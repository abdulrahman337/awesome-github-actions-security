# Incident Timeline

Major GitHub Actions supply chain incidents, in order, and what changed afterward. Dates and figures follow the cited sources. Read the primary advisories for exact details, because early reports were often corrected.

## 2024

**December 2024: a malicious pull request exploits `pull_request_target`.** According to Unit 42, an attacker submitted a pull request to the `spotbugs/sonar-findbugs` repository that exploited a workflow using the `pull_request_target` trigger. Credentials obtained this way began the chain that led to the March 2025 compromises.

## 2025

**11 March 2025: `reviewdog/action-setup` compromised** (CVE-2025-30154). The compromised action exposed secrets from workflows that used it.

**Between 10 and 14 March 2025: `tj-actions/changed-files` compromised** (CVE-2025-30066). An attacker pushed malicious code and repointed existing version tags at it. The malicious script read secrets from the runner worker process memory and printed them to the workflow logs, which are public for public repositories. Researchers at StepSecurity detected it on 14 March. GitHub's advisory says the action was used by more than 23,000 repositories and that version 46.0.1 contains the fix. Unit 42 describes how a targeted attack on a Coinbase repository was the first step before the wider impact.

Lessons: tags are mutable, token and secret scope matters, and a compromise in one action can cascade to others that depend on it.

**15 August 2025: GitHub adds SHA pinning enforcement and blocking.** The allowed actions policy can now fail workflows that use actions that are not pinned to a full commit SHA, and administrators can explicitly block specific actions or versions. GitHub also introduced immutable releases, where a release's assets and tag cannot be changed or deleted once marked immutable.

**August to November 2025: further campaigns.** Public write-ups list the Nx "s1ngularity" compromise (August), the second wave of the Shai-Hulud npm worm (November) and the GhostAction campaign as part of the same period. These involve package ecosystems as well as Actions, and they exploit the same mistakes: privileged triggers, over-broad credentials and unpinned dependencies.

## 2026

**March 2026: the trivy-action compromise.** A comparison published by Cycode lists a compromise of the Trivy GitHub Action in March 2026, again involving secrets read from runner process memory. A separate write-up describes an attack against Trivy carried out by an automated bot account. Check Aqua's and GitHub's advisories for authoritative details.

**26 March 2026: GitHub publishes its Actions security roadmap.** It describes workflow-level dependency locking, hardened publishing with immutable releases, policy-driven execution built on rulesets, an Actions data stream and a native egress firewall for hosted runners.

## Patterns across incidents

| Pattern | Seen in |
| --- | --- |
| Privileged trigger running attacker-controlled code | The December 2024 pull request that started the March 2025 chain |
| Stolen maintainer or bot token used to rewrite tags | tj-actions, reviewdog |
| Secrets read from runner memory and printed to logs | tj-actions, trivy-action |
| Unpinned references that pull in the malicious version automatically | Nearly every case |
| Cascade through dependencies between actions | reviewdog into tj-actions |

## Sources

- [GitHub advisory GHSA-mrrh-fwg8-r2c3](https://github.com/advisories/GHSA-mrrh-fwg8-r2c3)
- [Unit 42 analysis](https://unit42.paloaltonetworks.com/github-actions-supply-chain-attack/)
- [Orca hardening guide](https://orca.security/resources/blog/github-actions-hardening/)
- [Cycode analysis](https://cycode.com/blog/github-actions-supply-chain-attack/)
- [15 security pitfalls](https://blog.stephane-robert.info/en/post/github-actions-15-security-pitfalls/)
- [GitHub changelog, August 2025](https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/)
- [GitHub Actions 2026 security roadmap](https://github.blog/news-insights/product-news/whats-coming-to-our-github-actions-2026-security-roadmap/)
