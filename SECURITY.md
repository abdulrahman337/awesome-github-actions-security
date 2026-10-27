# Security Policy

This repository is a curated list plus a few small scripts. It does not run a service, but a list can still hurt people if a link is wrong, and a script can hurt anyone who runs it.

## What to report

- A link that leads to malware, a credential harvester or a look-alike of the real project, or a listed repository that was taken over or renamed to something malicious.
- A bug in a script under `scripts/` that could harm the person who runs it, for example a scope filter that lets an out-of-scope host through, a tool that follows a request to an internal address, or one that leaks a token.
- A problem in a workflow under `.github/workflows`, such as script injection or permissions that are broader than needed.
- Private information, a token or a key that was committed by mistake.

## How to report

Please do not open a public issue for these. Use GitHub's private vulnerability reporting: open the **Security** tab of this repository and choose **Report a vulnerability**. If that button is missing, open an issue titled "Security contact request" that contains no details, and the maintainer will arrange a private channel.

Include what you found, where it is, and how to reproduce it. A proof of concept against your own machine is enough.

## What to expect

The maintainer is a volunteer and answers on a best-effort basis. Confirmed problems are fixed on the `main` branch, and a fix is announced in the commit message or a release note. Only the latest version of `main` is supported.

## Out of scope

Vulnerabilities in the third-party tools that the list links to belong to those projects, so please report them to their maintainers. A listed tool being offensive or dual-use is not a vulnerability in this repository.
