# Tool Comparison

Which workflow scanner to use, and why you should usually run more than one. The evidence comes from a systematic academic study and from how real projects use these tools. Tools change quickly, so treat the details as a snapshot and rerun a comparison on your own workflows.

## What the research found

A study from Université de Montréal, [Unpacking Security Scanners for GitHub Actions Workflows](https://arxiv.org/abs/2601.14455), compared several scanners on the same set of real workflows (596 workflows in its results). Its main findings:

- **Scanners do not look for the same weaknesses.** zizmor was the only scanner that covered all ten weakness categories in the study, using 23 rules. poutine covered seven with 13 rules and emphasized supply chain risks such as untrusted checkouts and known vulnerabilities from the OSV database. actionlint covered five and concentrated on structural validation, with 28 of its 36 rules targeting that.
- **Scanners disagree on the same weakness.** For unpinned dependencies, the number of findings on the same workflows ranged from zero for poutine, which flags only transitive unpinned references inside composite actions, to 509 for zizmor, which exempts official GitHub-maintained actions, up to roughly 2,250 to 2,500 for pinning tools and OpenSSF Scorecard. Scorecard also checks non-action dependencies such as Python package versions.
- **Some weaknesses are reported by only one tool.** Scorecard alone reported one weakness category on most of the workflows, poutine alone reported known vulnerable components, and actionlint alone reported certain structural problems.
- **Recommendation of the authors.** They identified poutine as the most balanced single tool because of its precision, its unique detection of vulnerable components and its sub-second runtime, while warning that zizmor's broader rules produce more low-confidence findings.

## The tools side by side

| | [zizmor](https://github.com/zizmorcore/zizmor) | [poutine](https://github.com/boostsecurityio/poutine) | [actionlint](https://github.com/rhysd/actionlint) | [OpenSSF Scorecard](https://github.com/ossf/scorecard) |
| --- | --- | --- | --- | --- |
| Platforms | GitHub Actions only | GitHub Actions, GitLab CI, Azure DevOps and Tekton | GitHub Actions | Repository-level checks on GitHub projects |
| Focus | Broadest coverage of workflow security weaknesses | Supply chain weaknesses and known vulnerable components | Syntax, types, expressions and shell script checks | Overall project security posture |
| Strength | Wide rule set, can propose automatic fixes | Precise, fast, multi-platform, supports custom Rego rules | Catches real errors before a workflow runs | Quick posture score across many repositories |
| Watch out for | More low-confidence findings to triage | Narrower scope than zizmor | Can flag newer valid keys or permissions as errors when its schema lags | Counts differ from workflow-level scanners |

## Suppressing false positives

Each tool has its own mechanism, so write a short justification next to every suppression. Check each tool's documentation for the current syntax.

| Tool | How |
| --- | --- |
| zizmor | An inline comment of the form `# zizmor: ignore[rule-name]` with a reason |
| poutine | A `.poutine.yml` file that can ignore by rule, path, job and more, or an inline `# poutine:ignore rule` comment |
| actionlint | The `-ignore` flag with a pattern for messages to skip |

## Evidence from the field

GitHub's own `gh-aw` repository runs zizmor, poutine and actionlint on its compiled workflows every day, and the automated reports it files show the pattern clearly. In one day's report, actionlint accounted for 1,497 of 1,910 findings and was described as overwhelmingly false positives against generated files, because actionlint does not model the project's compiler extensions, while zizmor and poutine produced about a hundred between them. In other reports actionlint flagged a permission scope it had not yet learned and an unknown key that GitHub Actions itself ignores. This is a special case, because those workflows are generated, but it shows how a tool whose schema lags can bury real findings in noise.

Take-away: run the tools together, but triage by tool, and do not let one noisy tool hide the others.

## A sensible setup

1. **In CI on every pull request:** run zizmor and poutine, and upload results as SARIF so they appear in the repository's Security tab. Add actionlint for syntax and shell checks.
2. **Triage disagreements by hand.** A finding reported by two independent tools deserves attention first. A finding reported by one tool needs a read of the workflow.
3. **Fix pinning findings with a pinning tool** such as [pinact](https://github.com/suzuki-shunsuke/pinact), then keep pins fresh with Dependabot or Renovate. See the [hardening checklist](HARDENING_CHECKLIST.md).
4. **Use Scorecard for posture** across an organization, to find which repositories to look at first.
5. **Review suppressions** regularly, because a suppression that was right last year may hide a real problem today.
6. **Remember what scanners miss.** They cannot judge who can trigger a workflow in practice, how much a token can do, or whether a secret is too broadly shared. Read the [attack patterns](ATTACK_PATTERNS.md) and review by hand.
