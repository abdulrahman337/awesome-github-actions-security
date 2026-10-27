#!/usr/bin/env python3
"""Regenerate docs/MAINTENANCE_STATUS.md from GitHub's public commit and release feeds.

Usage:
    python scripts/update_maintenance_status.py

No API token is needed. It reads https://github.com/<owner>/<repo>/commits.atom and
releases.atom for every GitHub project linked in README.md, then rewrites the status page.
Review the generated notes by hand before committing.
"""
import datetime
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_repos import LINK_RE, IGNORED_OWNERS, STATIC_OK, find_repos  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
OUT = ROOT / "docs" / "MAINTENANCE_STATUS.md"

CONFIG = ROOT / "scripts" / "maintenance_config.json"


def load_config():
    """Key tools and hand-written notes live in scripts/maintenance_config.json."""
    if CONFIG.exists():
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        return data.get("key_tools", []), data.get("notes", "")
    return [], ""


MAX_FEED_BYTES = 2_000_000


class GithubOnlyRedirects(urllib.request.HTTPRedirectHandler):
    """Follow redirects only to https://github.com, so a feed can never send the tool elsewhere."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname != "github.com":
            raise urllib.error.HTTPError(newurl, code, "redirect to another host refused", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = urllib.request.build_opener(GithubOnlyRedirects)


def fetch_feed(repo, kind):
    """Return the text of a public Atom feed, or an empty string if it cannot be read."""
    req = urllib.request.Request(f"https://github.com/{repo}/{kind}.atom",
                                 headers={"User-Agent": "awesome-list-maintenance-status"})
    try:
        with OPENER.open(req, timeout=25) as resp:
            return resp.read(MAX_FEED_BYTES).decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError):
        return ""


def safe_cell(text, limit=30):
    """Make text from a remote feed safe for one cell of a Markdown table.

    A release title is chosen by the maintainer of a listed project, so it must not be able to break the
    table, add a link or inject HTML into the page this script writes.
    """
    text = re.sub(r"[\t\r\n\v\f]+", " ", html.unescape(text))
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch == " ")
    text = re.sub(r"[|\\\[\]<>`*_~]", "", text)
    return re.sub(r"\s+", " ", text).strip()[:limit]


def parse_commit_date(feed):
    match = re.search(r"<updated>([^<]*)</updated>", feed)
    if not match:
        return None
    try:
        return datetime.date.fromisoformat(match.group(1)[:10])
    except ValueError:
        return None


def parse_release(feed):
    match = re.search(r"<entry>.*?<updated>([^<]*)</updated>.*?<title>([^<]*)</title>", feed, re.S)
    if not match:
        return None, None
    try:
        date = datetime.date.fromisoformat(match.group(1)[:10])
    except ValueError:
        return None, None
    title = safe_cell(match.group(2))
    if title.lower().startswith("nightly"):
        title = "nightly builds"
    return date, title or "untitled"


def feed_date(repo, kind):
    feed = fetch_feed(repo, kind)
    if kind == "commits":
        return parse_commit_date(feed), None
    return parse_release(feed)


def main():
    key_tools, notes = load_config()
    today = datetime.datetime.now(datetime.timezone.utc).date()
    repos = find_repos(README.read_text(encoding="utf-8"))
    rows, unavailable = [], []
    for r in repos:
        d, _ = feed_date(r, "commits")
        rows.append((r, d, (today - d).days if d else None))
        if d is None:
            unavailable.append(r)
        time.sleep(0.2)
    rows = [x for x in rows if x[1] is not None]
    if unavailable:
        print("No commit feed for: " + ", ".join(unavailable) + " (missing, private or rate limited; left out of the page)",
              file=sys.stderr)
    rows.sort(key=lambda x: x[2])

    def row(r, d, a):
        note = " (reference or dataset)" if r.lower() in STATIC_OK else ""
        return f"| [{r}](https://github.com/{r}) | {d} | {a}{note} |"

    active = [x for x in rows if x[2] <= 183]
    slow = [x for x in rows if 183 < x[2] <= 548]
    quiet = [x for x in rows if x[2] > 548]

    key_rows = []
    lookup = {r.lower(): (d, a) for r, d, a in rows}
    for r in key_tools:
        c = lookup.get(r.lower())
        d, _ = feed_date(r, "commits") if not c else (c[0], None)
        rel_d, rel_t = feed_date(r, "releases")
        name = safe_cell(r.split("/")[1], 60)
        rel = f"{rel_t} ({rel_d})" if rel_t and rel_t != "nightly builds" else (rel_t or "none")
        key_rows.append((d or datetime.date.min, f"| {name} | {d or 'unavailable'} | {rel} |"))
        time.sleep(0.2)
    key_rows.sort(key=lambda x: x[0], reverse=True)

    def table(items):
        return "| Repository | Last commit | Days ago |\n| --- | --- | --- |\n" + "\n".join(row(*x) for x in items)

    doc = f"""# Maintenance Status

A snapshot of how recently each GitHub project in the list was updated, measured on **{today.strftime('%d %B %Y')}**. Use it to judge which tools are still alive before you build a workflow on them. Regenerate it with `python scripts/update_maintenance_status.py`.

## How to read this

- "Last commit" is the most recent commit on the default branch, taken from GitHub's commit feed. "Days ago" counts from the snapshot date.
- A quiet repository is not automatically bad. Datasets, CTF challenges, reference notes and finished standards do not need frequent updates, and they are marked as such. A quiet **tool** is a risk: it may break with new language, compiler, runtime or platform versions.
- Commits are only one signal. Some projects release from other branches, and a low commit count can mean stability. Check releases and open issues before deciding.
- The [repository health script](../scripts/check_repos.py) flags archived and missing repositories automatically. This page is a snapshot and will age.

"""+ (("## Key tools: latest releases\n\n| Tool | Last commit | Latest release |\n| --- | --- | --- |\n" + "\n".join(x[1] for x in key_rows) + "\n\n" + notes + "\n") if key_rows else "") + f"""

## Active: last commit within about 6 months ({len(active)} projects)

{table(active)}

## Slowing: between 6 and 18 months ({len(slow)} projects)

{table(slow)}

## Quiet: more than 18 months ({len(quiet)} projects)

Tools in this group are marked "low recent activity" in the README. Entries marked as reference or dataset are kept on purpose.

{table(quiet)}
"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"Wrote {OUT} ({len(active)} active, {len(slow)} slowing, {len(quiet)} quiet)")


if __name__ == "__main__":
    main()
