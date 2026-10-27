#!/usr/bin/env python3
"""Check every link in the repository's Markdown files.

Run this on your own machine before publishing, because it needs normal internet access.

Usage:
    python scripts/check_links.py                    # check all links
    python scripts/check_links.py --only github.com  # only links on one domain
    python scripts/check_links.py --skip github.com  # everything except one domain
    python scripts/check_links.py --limit 20         # quick test with the first 20 links

Result classes:
    OK        reachable (HTTP 2xx)
    MOVED     reachable but redirected to a different place, update the link
    BLOCKED   the site refused automated requests (403, 429, 999); open it in a browser
    DEAD      404, 410, DNS failure or repeated timeout; fix or remove the entry
    UNSAFE    the address, or a redirect target, is not a public internet address

Safety: a pull request can add any URL to a Markdown file, including one that points at your own
machine or network (localhost, a router, a cloud metadata service such as 169.254.169.254). This tool
refuses to send requests to loopback, private, link-local and other non-public addresses, and it checks
every redirect hop the same way. Only http and https are followed. The check happens at lookup time, so
a hostile DNS server that changes its answer between the check and the connection is not covered; for
untrusted input run the tool in a disposable environment. Use --allow-private only for a local test
server you control.

Exit code is 1 if any link is DEAD or UNSAFE.
"""
import argparse
import ipaddress
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
URL_RE = re.compile(r"https?://[^\s)>\]\"'`]+")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 awesome-link-check")
BLOCKED_CODES = {401, 403, 429, 999}
# Template placeholders that are not real links.
PLACEHOLDER_MARKERS = ("ORG/REPO", "OWNER/REPO", "YOUR_", "/COMMIT/", "path/to/", "example.com")
ALLOW_PRIVATE = False


class UnsafeTarget(urllib.error.URLError):
    """Raised when a URL points at something that is not a public internet host."""


def non_public_reason(host):
    """Return a reason string if `host` resolves to a non-public address, else None.

    Name resolution failures return None so the caller reports them as DNS problems.
    """
    host = host.strip("[]")
    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except (socket.gaierror, UnicodeError):
        return None
    for info in infos:
        address = ipaddress.ip_address(info[4][0].split("%")[0])
        if address.version == 6 and address.ipv4_mapped:
            address = address.ipv4_mapped
        if not address.is_global:
            return f"{host} resolves to {address}, which is not a public address"
    return None


def ensure_public(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise UnsafeTarget(f"scheme {parsed.scheme!r} is not followed")
    if not parsed.hostname:
        raise UnsafeTarget("URL has no host")
    if parsed.username or parsed.password:
        raise UnsafeTarget("URL contains credentials")
    if not ALLOW_PRIVATE:
        reason = non_public_reason(parsed.hostname)
        if reason:
            raise UnsafeTarget(reason)


class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow redirects only to public http(s) addresses."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        ensure_public(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = urllib.request.build_opener(SafeRedirectHandler)


def collect():
    urls = {}
    for path in sorted(ROOT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in URL_RE.findall(text):
            url = match.rstrip(".,;:")
            if any(marker in url for marker in PLACEHOLDER_MARKERS):
                continue
            urls.setdefault(url, path.relative_to(ROOT).as_posix())
    return urls


def normalize(url):
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    return host, parsed.path.rstrip("/")


def fetch(url, method):
    ensure_public(url)
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
    with OPENER.open(req, timeout=20) as resp:
        return resp.status, resp.geturl()


def check(url):
    last_error = ""
    for attempt in range(2):
        for method in ("HEAD", "GET"):
            try:
                status, final = fetch(url, method)
                if normalize(final) != normalize(url):
                    return "MOVED", f"{status} -> {final}"
                return "OK", str(status)
            except UnsafeTarget as exc:
                return "UNSAFE", str(exc.reason)
            except urllib.error.HTTPError as exc:
                if exc.code in BLOCKED_CODES:
                    return "BLOCKED", str(exc.code)
                if exc.code in (404, 410):
                    return "DEAD", str(exc.code)
                last_error = f"HTTP {exc.code}"
            except (urllib.error.URLError, socket.timeout, ConnectionError) as exc:
                reason = getattr(exc, "reason", exc)
                last_error = str(reason)
                if "Name or service not known" in last_error or "getaddrinfo" in last_error:
                    return "DEAD", f"DNS failure ({last_error})"
        time.sleep(1.5)
    return "DEAD", last_error or "no response"


def main():
    global ALLOW_PRIVATE
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", help="only check links on this domain")
    parser.add_argument("--skip", help="skip links on this domain")
    parser.add_argument("--limit", type=int, help="check only the first N links")
    parser.add_argument("--allow-private", action="store_true",
                        help="allow loopback and private addresses (only for a local test server you control)")
    args = parser.parse_args()
    ALLOW_PRIVATE = args.allow_private

    urls = collect()
    items = list(urls.items())
    if args.only:
        items = [(u, f) for u, f in items if args.only in urlparse(u).netloc]
    if args.skip:
        items = [(u, f) for u, f in items if args.skip not in urlparse(u).netloc]
    if args.limit:
        items = items[: args.limit]
    print(f"Checking {len(items)} links...")

    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(lambda item: (item, check(item[0])), items))

    counts = {"OK": 0, "MOVED": 0, "BLOCKED": 0, "DEAD": 0, "UNSAFE": 0}
    for (url, where), (status, detail) in results:
        counts[status] += 1
        if status != "OK":
            print(f"{status:8s} {url}  [{detail}]  (in {where})")
    print("Summary:", ", ".join(f"{k}={v}" for k, v in counts.items()))
    return 1 if counts["DEAD"] or counts["UNSAFE"] else 0


if __name__ == "__main__":
    sys.exit(main())
