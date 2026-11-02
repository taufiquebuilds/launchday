#!/usr/bin/env python3
"""Score a repository's launch readiness and list what to fix, most important first.

Usage: python3 scripts/audit.py [PATH] [--json]

Checks the local files (README, license, community docs, CI, privacy) and, when
the `gh` CLI is logged in and the repo has a GitHub remote, the GitHub settings
(description, topics, social preview, releases). Standard library only.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

INSTALL_PATTERNS = [
    r"\bnpm (i|install)\b", r"\bnpx\b", r"\bpnpm (add|dlx)\b", r"\byarn (add|dlx)\b",
    r"\bbun (add|x)\b", r"\bpip3? install\b", r"\bpipx install\b", r"\buv (tool )?(add|install)\b",
    r"\buvx\b", r"\bcargo (install|add)\b", r"\bbrew install\b", r"\bgo install\b",
    r"\bgo get\b", r"\bdocker (run|compose)\b", r"curl [^\n|]*\|\s*(ba|z)?sh", r"\bgem install\b",
    r"\bcomposer require\b", r"\bdotnet (add|tool install)\b", r"/plugin (install|marketplace)",
    r"\bskills add\b", r"\bwinget install\b", r"\bscoop install\b", r"\bapt(-get)? install\b",
]
VISUAL_PATTERN = re.compile(
    r"!\[[^\]]*\]\([^)]+\)|<img\s|<video\s|<picture|\.(gif|png|jpe?g|webp|svg|mp4|webm)\b",
    re.IGNORECASE,
)
PLACEHOLDERS = re.compile(
    r"\[INSERT[^\]]*\]|lorem ipsum|\bTODO:? (?:write|add|fill)[^\n]*|\bcoming soon\b",
    re.IGNORECASE,
)
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}"),
    "OpenAI/Anthropic key": re.compile(r"\bsk-(ant-)?[A-Za-z0-9_-]{32,}"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Private key": re.compile(r"-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}"),
}
HYPE = re.compile(
    r"\b(powerful|flexible|extensible|robust|seamless(ly)?|blazing(ly)?|revolutionary|"
    r"game[- ]chang\w*|next[- ]gen\w*|cutting[- ]edge|state[- ]of[- ]the[- ]art|"
    r"modern technologies|built using modern|leverag\w+|synerg\w+)\b", re.I)
BADGE = re.compile(r"shields\.io|badge|/actions/workflows/|codecov\.io|badgen\.net", re.I)
SKIP_DIRS = {".git", "node_modules", "target", "dist", "build", "__pycache__", ".venv", "venv"}
SKIP_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".zip", ".gz", ".lock"}
FREE_MAIL = re.compile(r"@(gmail|googlemail|yahoo|hotmail|outlook|live|icloud|proton(mail)?)\.", re.I)


def run(cmd, cwd):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def find(root, *names):
    for n in names:
        for p in [root / n, root / ".github" / n, root / "docs" / n]:
            if p.is_file():
                return p
    return None


def readme_checks(root):
    """Return list of (id, weight, passed, message)."""
    out = []
    readme = find(root, "README.md", "README.rst", "README", "readme.md")
    if not readme:
        return [("readme", 15, False, "No README. It is the landing page: add one.")]
    text = readme.read_text(errors="replace")
    lines = text.splitlines()
    out.append(("readme", 5, True, f"README found ({readme.name})"))

    # The hook: first real sentence, skipping headings, badges, HTML and blank lines.
    hook = next(
        (
            l.strip()
            for l in lines[:40]
            if l.strip()
            and not l.lstrip().startswith(("#", "[!", "![", "<", "|", "```", "---", ">"))
            and not re.fullmatch(r"\s*(\[!\[.*|\s*)", l)
        ),
        "",
    )
    plain_hook = re.sub(r"[*_`]", "", hook)
    hype = HYPE.findall(plain_hook)
    good_hook = 20 <= len(plain_hook) <= 320 and len(hype) < 2
    if good_hook:
        hook_msg = f"Opening line: \"{plain_hook[:120]}\""
    elif len(hype) >= 2:
        words = ", ".join(sorted({h[0].lower() if isinstance(h, tuple) else h.lower() for h in hype}))
        hook_msg = f"Opening line is vague hype ({words}). Say what it does and for whom, in plain words."
    else:
        hook_msg = "No clear one or two sentence hook near the top. Lead with the pain the project removes."
    out.append(("hook", 15, good_hook, hook_msg))

    first_screen = "\n".join(lines[:45])
    # Badges are images too, but they don't show the project working.
    has_visual = any(not BADGE.search(m.group(0)) and not BADGE.search(line)
                     for line in first_screen.splitlines()
                     for m in VISUAL_PATTERN.finditer(line))
    out.append((
        "visual", 15, has_visual,
        "Image or GIF in the first screen" if has_visual else
        "No screenshot, GIF or video in the first screen. Show it working before explaining it.",
    ))

    early = "\n".join(lines[:90])
    has_install = any(re.search(p, early) for p in INSTALL_PATTERNS)
    out.append((
        "install", 15, has_install,
        "Install command near the top" if has_install else
        "No copy-paste install command in the first 90 lines. Make it one line.",
    ))

    ph = PLACEHOLDERS.search(text)
    out.append((
        "placeholders", 5, not ph,
        "No placeholder text" if not ph else f"Placeholder text left in README: {ph.group(0)!r}",
    ))
    return out


def file_checks(root):
    out = []
    lic = find(root, "LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")
    out.append(("license", 10, bool(lic),
                "License file present" if lic else "No LICENSE. Many people won't use or contribute without one (MIT or Apache-2.0)."))
    contrib = find(root, "CONTRIBUTING.md")
    out.append(("contributing", 4, bool(contrib),
                "CONTRIBUTING.md present" if contrib else "No CONTRIBUTING.md. Say how to run tests and send a PR."))
    coc = find(root, "CODE_OF_CONDUCT.md")
    coc_ok = bool(coc) and not PLACEHOLDERS.search(coc.read_text(errors="replace"))
    out.append(("conduct", 2, coc_ok,
                "Code of conduct present" if coc_ok else
                ("CODE_OF_CONDUCT.md still has a placeholder contact" if coc else "No CODE_OF_CONDUCT.md")))
    wf = list((root / ".github" / "workflows").glob("*.y*ml")) if (root / ".github" / "workflows").is_dir() else []
    out.append(("ci", 6, bool(wf),
                "CI workflow present" if wf else "No CI. A passing badge signals the project works."))
    release = any(re.search(r"tags:|release", p.read_text(errors="replace"), re.I) for p in wf)
    out.append(("release_ci", 4, release,
                "Release workflow present" if release else "No release workflow. Prebuilt binaries or a publish step widen who can install."))
    templates = (root / ".github" / "ISSUE_TEMPLATE").is_dir()
    out.append(("issue_templates", 2, templates,
                "Issue templates present" if templates else "No issue templates. They turn launch-day feedback into usable reports."))
    return out


def privacy_checks(root):
    out = []
    code, email = run(["git", "config", "user.email"], root)
    if code == 0 and email:
        leaky = bool(FREE_MAIL.search(email))
        out.append(("commit_email", 4, not leaky,
                    "Commit email is not a personal address" if not leaky else
                    f"Git is set to commit as a personal email ({email}). It becomes public on push. Set your GitHub noreply address: git config user.email ID+username@users.noreply.github.com"))
    code, files = run(["git", "ls-files"], root)
    paths = files.splitlines() if code == 0 and files else [
        str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()
    ]
    hits = []
    for rel in paths[:5000]:
        p = root / rel
        if SKIP_DIRS.intersection(Path(rel).parts) or p.suffix.lower() in SKIP_SUFFIXES:
            continue
        try:
            if p.stat().st_size > 1_000_000:
                continue
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        for label, pat in SECRET_PATTERNS.items():
            m = pat.search(text)
            # Skip obvious fakes like ghp_aaaa... used in docs and tests.
            if m and len(set(m.group(0)[-20:])) > 4:
                hits.append(f"{label} in {rel}")
    out.append(("secrets", 10, not hits,
                "No secrets found in tracked files" if not hits else "Possible secret: " + "; ".join(hits[:3])))
    return out


def github_checks(root):
    code, _ = run(["gh", "auth", "status"], root)
    if code != 0:
        return [], "gh CLI not logged in: GitHub settings not checked"
    code, raw = run(["gh", "repo", "view", "--json",
                     "nameWithOwner,description,repositoryTopics,homepageUrl,usesCustomOpenGraphImage,latestRelease,isPrivate"], root)
    if code != 0 or not raw:
        return [], "No GitHub repo for this folder yet: GitHub settings not checked"
    info = json.loads(raw)
    topics = info.get("repositoryTopics") or []
    out = [
        ("gh_description", 4, bool(info.get("description")),
         "Repo description set" if info.get("description") else "No repo description. It shows in search and link previews."),
        ("gh_topics", 4, len(topics) >= 5,
         f"{len(topics)} topics" if len(topics) >= 5 else f"Only {len(topics)} topics. Add 5 to 10 so people find it in topic pages."),
        ("gh_social", 6, bool(info.get("usesCustomOpenGraphImage")),
         "Custom social preview set" if info.get("usesCustomOpenGraphImage") else
         "No social preview image. Links on HN, X and Slack show a generic card. Upload one in Settings."),
        ("gh_release", 3, bool(info.get("latestRelease")),
         "Has a release" if info.get("latestRelease") else "No GitHub release yet. Tag v0.1.0 before launch."),
    ]
    if info.get("isPrivate"):
        out.append(("gh_public", 0, False, "Repo is private. Make it public on launch day."))
    return out, f"GitHub: {info.get('nameWithOwner')}"


def main(argv):
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    root = Path(args[0] if args else ".").resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2

    checks = readme_checks(root) + file_checks(root) + privacy_checks(root)
    gh, gh_note = github_checks(root)
    checks += gh
    total = sum(w for _, w, _, _ in checks)
    got = sum(w for _, w, ok, _ in checks if ok)
    score = round(100 * got / total) if total else 0

    if as_json:
        print(json.dumps({
            "path": str(root), "score": score, "github": gh_note,
            "checks": [{"id": i, "weight": w, "passed": ok, "message": m} for i, w, ok, m in checks],
        }, indent=2))
        return 0

    print(f"Launch readiness: {score}/100  ({root.name})")
    print(gh_note)
    fails = sorted([c for c in checks if not c[2]], key=lambda c: -c[1])
    if fails:
        print("\nFix these, most important first:")
        for n, (_, w, _, m) in enumerate(fails, 1):
            print(f"  {n}. [{w:>2} pts] {m}")
    print("\nAlready good:")
    for _, _, ok, m in checks:
        if ok:
            print(f"  - {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
