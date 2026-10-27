# Hardening Checklist

Controls for repositories and organizations, roughly in order of impact. Tick them off one by one. Each control links to the tool or setting that implements it.

## Repository level

| Control | Why it matters | How |
| --- | --- | --- |
| Pin third-party actions to full commit SHAs | Tags can be moved to malicious commits | [pinact](https://github.com/suzuki-shunsuke/pinact), [ratchet](https://github.com/sethvargo/ratchet) or [frizbee](https://github.com/stacklok/frizbee) |
| Keep pins updated automatically | Pinned versions go stale and miss fixes | Dependabot or Renovate for the `github-actions` ecosystem |
| Wait before adopting a brand new release | A compromised release is often found within days | Dependabot `cooldown`, or Renovate `minimumReleaseAge`, set to about two weeks |
| Set minimal `permissions:` on every workflow | Limits what a compromised step can do | `permissions: {}` at the top of the file, then only what each job needs inside the job |
| Avoid `pull_request_target` with untrusted checkout | Prevents privileged execution of attacker code | Split into unprivileged build and privileged follow-up |
| Never put untrusted expressions inside scripts | Prevents script injection | Pass values through `env` and quote them |
| Use `persist-credentials: false` on checkout | Keeps the token out of the workspace and artifacts | Set it on every `actions/checkout` step |
| Protect workflow files | Changes to workflows change what runs with secrets | CODEOWNERS on `.github/workflows/` and required reviews |
| Use environments with required reviewers for deploy secrets | Keeps production secrets away from ordinary jobs | Repository settings, Environments |
| Prefer OIDC over long-lived cloud credentials | Short-lived tokens limit damage when leaked | Configure your cloud provider's trust for GitHub's OIDC |
| Scan workflows in CI | Catches regressions automatically | [zizmor](https://github.com/zizmorcore/zizmor), [actionlint](https://github.com/rhysd/actionlint), [poutine](https://github.com/boostsecurityio/poutine) |
| Review dependency changes in pull requests | Stops vulnerable dependencies entering | [Dependency Review Action](https://github.com/actions/dependency-review-action) |
| Scan for secrets | Finds leaked credentials early | [Gitleaks](https://github.com/gitleaks/gitleaks), [TruffleHog](https://github.com/trufflesecurity/trufflehog) |
| Do not run install scripts you do not need | Package install hooks are a common route for supply chain malware | `npm ci --ignore-scripts` or `NPM_CONFIG_IGNORE_SCRIPTS=true`, and pin the exact version of any tool you run with `npx` |

## Runner level

| Control | Why it matters | How |
| --- | --- | --- |
| Monitor and restrict outbound traffic | Stops exfiltration of secrets from compromised steps | [Harden-Runner](https://github.com/step-security/harden-runner) in audit mode first, then block mode |
| Use ephemeral runners | No state or credentials survive between jobs | Self-hosted runner ephemeral mode, or hosted runners |
| Do not use self-hosted runners on public repositories | Pull requests could run code on your infrastructure | Use GitHub-hosted runners for public projects |
| Isolate runner networks | Limits lateral movement | Network segmentation, no access to internal services |

## Organization level

| Control | Why it matters | How |
| --- | --- | --- |
| Enforce SHA pinning in the allowed actions policy | Makes unpinned actions fail | Organization Actions settings, SHA pinning enforcement |
| Block known-bad actions and versions | Stops reuse of compromised actions quickly | The blocklist in the allowed actions policy |
| Restrict which actions may run | Reduces the third-party attack surface | Allow only your own actions, GitHub's, and an explicit list |
| Default token permissions to read-only | Safe defaults for new repositories | Organization Actions settings, workflow permissions |
| Require approval for workflows from outside contributors | Stops drive-by pull requests running workflows | Repository and organization Actions settings |
| Continuously enforce repository policies | Catches drift | [Allstar](https://github.com/ossf/allstar) |
| Measure posture | Finds weak spots across many repositories | [OpenSSF Scorecard](https://github.com/ossf/scorecard) |

## Releases and provenance

| Control | Why it matters | How |
| --- | --- | --- |
| Generate build provenance attestations | Lets consumers verify what built an artifact | [attest](https://github.com/actions/attest) (the base that [attest-build-provenance](https://github.com/actions/attest-build-provenance) now wraps). The older [SLSA GitHub Generator](https://github.com/slsa-framework/slsa-github-generator) is no longer actively maintained |
| Sign artifacts and images | Detects tampering after the build | [Cosign](https://github.com/sigstore/cosign) |
| Use immutable releases where available | A published release cannot be altered | GitHub's immutable releases feature, see the [roadmap](https://github.blog/news-insights/product-news/whats-coming-to-our-github-actions-2026-security-roadmap/) |
| Publish from a protected, minimal workflow | Fewer inputs means fewer ways in | Separate release workflow with approvals and no untrusted triggers |

## If you may have been compromised

1. Identify which workflows used the affected action or ran the suspicious code, and when.
2. **Rotate every secret** those runs could access, starting with tokens that have write access.
3. Review recent workflow runs, logs and outbound network activity, and check for unexpected commits, tags or releases.
4. Check whether logs exposed secrets in a public repository, and delete or restrict them if you can.
5. Pin to known-good SHAs, block the bad action in your policy, and tell your downstream users if you publish software.

## What GitHub is adding

GitHub's March 2026 roadmap describes workflow-level dependency locking with a `dependencies:` section, policy-driven execution controls built on rulesets, an Actions data stream for observability and a native egress firewall for GitHub-hosted runners. These are plans, so verify what has shipped before relying on them. Until then, pinning, minimal permissions and runtime monitoring are the controls you can apply today.
