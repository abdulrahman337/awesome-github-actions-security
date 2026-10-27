#!/usr/bin/env python3
"""Offline structure and safety checks for the Markdown files in this repository.

Standard library only, no network. It is meant to run on every pull request and before every release.

Usage:
    python scripts/check_readme.py            # errors fail the run, warnings are printed
    python scripts/check_readme.py --strict   # warnings fail the run too

What it checks:
    README.md   every list entry follows "- [Name](https://url) - Description." with a capital letter and a
                final period; no duplicate links (awesome-lint rejects them); the Contents list matches the
                section headings, in order, with working anchors.
    all .md     links use https; no URL shorteners, tracking parameters, credentials in URLs, raw IP
                addresses or local hostnames; no javascript:, data: or file: links; relative links point to
                files and headings that exist.
    all text    no hidden or bidirectional control characters (the "Trojan Source" trick), no byte order mark,
                no control characters, no tabs in Markdown, no trailing spaces, no Windows line endings, and
                a final newline.

Links inside fenced code blocks and inline code are ignored, so examples can show anything.
"""
import argparse
import ipaddress
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import parse_qsl, urlparse

ROOT = Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".txt"}
TEXT_NAMES = {"LICENSE", ".gitignore", ".gitattributes"}
SHORTENERS = {"bit.ly", "t.co", "tinyurl.com", "goo.gl", "ow.ly", "is.gd", "buff.ly", "rebrand.ly", "cutt.ly",
              "shorturl.at", "tiny.cc", "lnkd.in", "t.ly", "rb.gy", "s.id"}
TRACKING = {"fbclid", "gclid", "mc_cid", "mc_eid", "igshid", "ref_src", "referrer", "msclkid", "yclid"}
LOCAL_SUFFIXES = (".local", ".internal", ".lan", ".localhost", ".home.arpa")
HIDDEN = {  # characters that change how text is displayed or hide text from a reviewer
    "\u202a", "\u202b", "\u202c", "\u202d", "\u202e", "\u2066", "\u2067", "\u2068", "\u2069", "\u200e", "\u200f",
    "\u061c", "\u200b", "\u200c", "\u200d", "\u2060", "\ufeff", "\u00ad", "\u180e",
}
NOT_IN_CONTENTS = {"related lists", "contributing", "license"}  # closing sections that are not listed on purpose
ENTRY_RE = re.compile(r"^- \[([^\]]+)\]\((https?://[^)\s]+)\)(.*)$")
LINK_RE = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def slug(heading):
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def blank_code(text):
    """Replace fenced and inline code with spaces, keeping line numbers intact."""
    out, fenced = [], False
    for line in text.split("\n"):
        if FENCE_RE.match(line):
            fenced = not fenced
            out.append("")
        elif fenced:
            out.append("")
        else:
            out.append(re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), line))
    return "\n".join(out)


def headings(text):
    return [(i + 1, m.group(1).strip()) for i, line in enumerate(blank_code(text).split("\n"))
            if (m := re.match(r"^#{1,6}\s+(.*?)\s*#*$", line))]


def normalize_url(url):
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().removeprefix("www.")
    return f"{host}{parsed.path.rstrip('/').removesuffix('.git')}?{parsed.query}"


def check_url(url):
    """Return a list of problems with one absolute URL."""
    problems = []
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme == "http":
        problems.append("uses http, use https")
    elif scheme != "https":
        problems.append(f"scheme {scheme!r} is not allowed")
        return problems
    host = (parsed.hostname or "").lower()
    if parsed.username or parsed.password:
        problems.append("contains credentials")
    if host in SHORTENERS:
        problems.append("is a URL shortener, link to the real page")
    if host == "localhost" or host.endswith(LOCAL_SUFFIXES):
        problems.append("points at a local hostname")
    try:
        ipaddress.ip_address(host)
        problems.append("uses a raw IP address")
    except ValueError:
        pass
    for key, _ in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower().startswith("utm_") or key.lower() in TRACKING:
            problems.append(f"has the tracking parameter {key!r}")
    return problems


def check_entries(text):
    errors, seen = [], {}
    for number, line in enumerate(blank_code(text).split("\n"), 1):
        match = ENTRY_RE.match(text.split("\n")[number - 1]) if line.startswith("- [") else None
        if not match:
            continue
        name, url, rest = match.groups()
        original = text.split("\n")[number - 1]
        if not rest.startswith(" - "):
            errors.append((number, "entry must look like: - [Name](https://url) - Description."))
            continue
        description = rest[3:]
        if not re.match(r"[A-Z]", description):
            errors.append((number, "description must start with a capital letter"))
        if not description.endswith("."):
            errors.append((number, "description must end with a period"))
        if "  " in description or original != original.rstrip():
            errors.append((number, "description has double or trailing spaces"))
        if description.lower().startswith(name.lower()):
            errors.append((number, "description should not start with the name of the entry"))
        if len(description) > 420:
            errors.append((number, f"description is {len(description)} characters, keep entries short"))
        key = normalize_url(url)
        if key in seen:
            errors.append((number, f"duplicate of the entry on line {seen[key]}"))
        seen[key] = number
    return errors


def check_contents(text):
    errors = []
    found = headings(text)
    titles = [(n, t) for n, t in found if t.lower() != "contents"]
    lines = text.split("\n")
    start = next((n for n, t in found if t.lower() == "contents"), None)
    if start is None:
        return [(1, "README has no '## Contents' section")]
    listed = []
    for i in range(start, len(lines)):
        if lines[i].startswith("## ") and i + 1 != start:
            break
        m = re.match(r"^- \[([^\]]+)\]\(#([^)]+)\)\s*$", lines[i])
        if m:
            listed.append((i + 1, m.group(1), m.group(2)))
    sections = [t for n, t in titles if n > start and re.match(r"^##\s", lines[n - 1])
                and t.lower() not in NOT_IN_CONTENTS]
    if [t for _, t, _ in listed] != sections:
        errors.append((start, "Contents does not match the ## headings, in order "
                              f"(listed {len(listed)}, headings {len(sections)})"))
    for number, title, anchor in listed:
        if anchor != slug(title):
            errors.append((number, f"anchor #{anchor} does not match the title {title!r}"))
    return errors


def check_links(text, path, root):
    errors = []
    heads = {slug(t) for _, t in headings(text)}
    seen = {}
    for number, line in enumerate(blank_code(text).split("\n"), 1):
        for target in LINK_RE.findall(line):
            if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                for problem in check_url(target):
                    errors.append((number, f"link {target} {problem}"))
            elif not target.startswith("#") or len(target) > 1:
                file_part, _, anchor = target.partition("#")
                if file_part:
                    destination = (path.parent / file_part).resolve()
                    try:
                        destination.relative_to(root.resolve())
                    except ValueError:
                        errors.append((number, f"relative link {target} leaves the repository"))
                        continue
                    if not destination.exists():
                        errors.append((number, f"relative link {target} points to a missing file"))
                        continue
                    if anchor and destination.suffix == ".md":
                        other = {slug(t) for _, t in headings(destination.read_text(encoding="utf-8"))}
                        if anchor not in other:
                            errors.append((number, f"link {target} points to a missing heading"))
                elif anchor not in heads:
                    errors.append((number, f"link #{anchor} points to a missing heading"))
            if path.name == "README.md" and not target.startswith("#"):
                if target in seen:
                    errors.append((number, f"duplicate link {target} (first on line {seen[target]}); "
                                           "awesome-lint rejects links that appear twice"))
                seen.setdefault(target, number)
    return errors


def check_characters(text):
    errors = []
    for number, line in enumerate(text.split("\n"), 1):
        for ch in line:
            if ch in HIDDEN:
                errors.append((number, f"hidden or direction-changing character U+{ord(ch):04X}"))
            elif ch != "\t" and ch != "\r" and unicodedata.category(ch) in ("Cc", "Co", "Cn"):
                errors.append((number, f"control or unassigned character U+{ord(ch):04X}"))
    return errors


def check_whitespace(text, is_markdown):
    errors = []
    if "\r" in text:
        errors.append((1, "Windows line endings, use LF"))
    if text and not text.endswith("\n"):
        errors.append((text.count("\n") + 1, "missing final newline"))
    for number, line in enumerate(text.split("\n"), 1):
        if line != line.rstrip(" \t\r"):
            errors.append((number, "trailing whitespace"))
        if is_markdown and "\t" in line:
            errors.append((number, "tab character in Markdown"))
    return errors


def text_files(root):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts or "node_modules" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES:
            yield path


def run(root):
    problems = []
    for path in text_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append((rel, 1, "file is not valid UTF-8"))
            continue
        found = check_characters(text) + check_whitespace(text, path.suffix == ".md")
        if path.suffix == ".md":
            found += check_links(text, path, root)
            if path.name == "README.md" and path.parent == root:
                found += check_entries(text) + check_contents(text)
        problems += [(rel, n, msg) for n, msg in found]
    return sorted(problems)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(ROOT), help="repository folder to check (default: this repository)")
    args = parser.parse_args()
    problems = run(Path(args.root))
    for rel, number, message in problems:
        print(f"ERROR {rel}:{number}: {message}")
    print(f"{len(problems)} problem(s) found" if problems else "All checks passed")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
