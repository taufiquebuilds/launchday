#!/usr/bin/env python3
"""Check whether a project name is free on GitHub and the main package registries.

Usage: python3 scripts/name_check.py NAME [NAME ...]

Uses only the Python standard library and public, unauthenticated APIs.
Set GITHUB_TOKEN to raise GitHub's search rate limit (10/min without it).
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "launchday-name-check"
TIMEOUT = 15


def fetch(url, headers=None):
    """Return (status, parsed JSON or None)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, json.loads(resp.read().decode() or "null")
    except urllib.error.HTTPError as e:
        return e.code, None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None, None


def registry(name):
    """Check exact-name packages. Returns list of (registry, taken, detail)."""
    q = urllib.parse.quote(name)
    checks = [
        ("crates.io", f"https://crates.io/api/v1/crates/{q}"),
        ("npm", f"https://registry.npmjs.org/{q}"),
        ("PyPI", f"https://pypi.org/pypi/{q}/json"),
        ("Homebrew", f"https://formulae.brew.sh/api/formula/{q}.json"),
    ]
    out = []
    for label, url in checks:
        status, _ = fetch(url)
        if status == 200:
            out.append((label, True, "taken"))
        elif status == 404:
            out.append((label, False, "free"))
        else:
            out.append((label, None, f"unknown (HTTP {status})"))
    return out


def github(name):
    """Search GitHub repos whose name contains NAME. Returns (count, top repos)."""
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    q = urllib.parse.quote(f"{name} in:name")
    status, data = fetch(
        f"https://api.github.com/search/repositories?q={q}&sort=stars&per_page=5", headers
    )
    if status != 200 or not data:
        return None, []
    top = [
        (r["full_name"], r["stargazers_count"], (r.get("description") or "")[:70])
        for r in data.get("items", [])
    ]
    return data.get("total_count", 0), top


def verdict(regs, gh_count, gh_top):
    """Summarise into a short recommendation."""
    taken = [r for r, t, _ in regs if t]
    big = [r for r in gh_top if r[1] >= 500]
    if taken or big:
        reasons = []
        if taken:
            reasons.append("taken on " + ", ".join(taken))
        if big:
            reasons.append(f"{big[0][0]} has {big[0][1]:,} stars")
        return "AVOID", "; ".join(reasons)
    if gh_count and gh_count > 20:
        return "CROWDED", f"{gh_count} GitHub repos use it; search results will be shared"
    return "GOOD", "free on registries checked and little GitHub overlap"


def main(names):
    if not names:
        print(__doc__.strip())
        return 2
    for name in names:
        regs = registry(name)
        gh_count, gh_top = github(name)
        level, why = verdict(regs, gh_count, gh_top)
        print(f"\n## {name}: {level} ({why})")
        for label, taken, detail in regs:
            mark = "x" if taken else (" " if taken is False else "?")
            print(f"  [{mark}] {label:<10} {detail}")
        if gh_count is None:
            print("  [?] GitHub     search failed (rate limit? set GITHUB_TOKEN)")
        else:
            print(f"  GitHub repos with '{name}' in the name: {gh_count}")
            for full, stars, desc in gh_top:
                print(f"      {stars:>7,}  {full}  {desc}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
