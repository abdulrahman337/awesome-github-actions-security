# Contribution Guidelines

Thanks for helping make this list better. Please keep it focused on **securing and reviewing GitHub Actions workflows and CI/CD pipelines**.

## What belongs here

- Scanners, linters, pinning tools and runtime hardening tools for GitHub Actions and similar pipelines.
- Research, incident analyses, official guidance and training material about CI/CD attacks and defenses.
- Attestation, signing and policy tools that make pipelines verifiable.

## What does not belong here

- General DevOps or CI tooling with no security angle.
- Offensive tooling meant to attack repositories without authorization.
- Abandoned or archived projects. If a repository has had no activity for a long time and has no maintained alternative, open an issue instead.
- Marketing pages, affiliate links and paid courses presented as free resources.
- Duplicates of items already in the list.

## How to add an item

1. Search the list first to make sure it is not already there.
2. Add your item to the **most fitting section**, in this format:

   ```markdown
   - [Name](https://link) - Short description that starts with a capital letter and ends with a period.
   ```

3. Keep the description factual: what it does, not how great it is. Do not start it with the item's name.
4. Use one pull request per addition and a title like `Add Name`.
5. Make sure the link works and points to the canonical project page.

## Supply chain and safety rules

A list is only useful if people can trust its links and its code. These rules are checked automatically where possible.

- **Check the owner.** Open the project's own documentation and confirm that the repository owner and name match it. Look-alike forks, typosquats and recently transferred repositories are a real attack on lists like this one.
- **Link to the canonical page over HTTPS.** No URL shorteners, no tracking parameters such as `utm_source`, no affiliate links and no credentials in a URL.
- **No install one-liners that pipe the internet into a shell.** If a guide needs an install step, show a pinned version and a way to verify it.
- **No secrets, no real targets in examples.** Use `example.com` and the documentation address ranges `192.0.2.0/24`, `198.51.100.0/24` and `203.0.113.0/24`.
- **Nothing built to harm people.** No malware, stealers or tools whose main purpose is abuse. Dual-use tools are fine when they have a legitimate use and the entry says to use them only with authorization.
- **Scripts:** standard library only, no `shell=True`, treat every input as hostile, fail closed, and add a test for each new behavior.
- **Workflows:** follow the advice in the GitHub Actions lists. Pin every action to a full commit SHA with the version in a comment, give each job the least permissions it needs, do not check out untrusted code with `pull_request_target`, and pass untrusted values through environment variables instead of putting them in `run:`.

## Checking your changes

Run these before opening a pull request. The first two also run automatically on every pull request.

```bash
python scripts/check_readme.py                                 # entry format, Contents, links, hidden characters
python -m unittest discover -s scripts -p "test_*.py"          # unit tests for the scripts
npx --yes awesome-lint@2.3.0                                   # list formatting rules
python scripts/check_repos.py --dry-run                        # lists all GitHub repositories found in the README
python scripts/check_links.py                                  # checks every link (needs normal internet access)
python scripts/update_maintenance_status.py                    # refreshes docs/MAINTENANCE_STATUS.md
```

A weekly workflow also checks links and flags archived or moved repositories, so the list stays healthy over time. Security problems go through the process in [SECURITY.md](SECURITY.md), not through public issues.
