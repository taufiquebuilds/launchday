#!/usr/bin/env python3
"""Check that the skill package is consistent before a release.

Usage: python3 scripts/validate_package.py

Checks: manifests parse, versions match everywhere, the manifest description
matches the first sentence of the SKILL.md description, every file SKILL.md
points to exists, and SKILL.md stays short enough to read on every use.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_WORDS = 3000
errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    data, current = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^\S[^:]*:", line):
            key, _, val = line.partition(":")
            current = key.strip()
            data[current] = val.strip()
        elif current and line.strip():
            k, _, v = line.strip().partition(":")
            data[f"{current}.{k.strip()}"] = v.strip()
    return data


skill = (ROOT / "SKILL.md").read_text()
fm = frontmatter(skill)
check(fm.get("name") == "launchday", "SKILL.md frontmatter name must be 'launchday'")
check(bool(fm.get("description")), "SKILL.md frontmatter needs a description")
version = fm.get("metadata.version")
check(bool(version), "SKILL.md needs metadata.version")
first_sentence = re.split(r"(?<=\.)\s", fm.get("description", ""), maxsplit=1)[0]

manifests = {}
for rel in [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".cursor-plugin/plugin.json"]:
    try:
        manifests[rel] = json.loads((ROOT / rel).read_text())
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"{rel}: {e}")

for rel in [".claude-plugin/plugin.json", ".cursor-plugin/plugin.json"]:
    m = manifests.get(rel, {})
    check(m.get("version") == version, f"{rel} version {m.get('version')} != SKILL.md {version}")
    check(m.get("description") == first_sentence, f"{rel} description must equal the first sentence of the SKILL.md description")
mkt = manifests.get(".claude-plugin/marketplace.json", {})
for p in mkt.get("plugins", []):
    check(p.get("description") == first_sentence, "marketplace.json plugin description must match too")

changelog = (ROOT / "CHANGELOG.md").read_text()
heading = re.search(r"^## \[?v?([\d.]+)", changelog, re.M)
check(bool(heading) and heading.group(1) == version, f"First CHANGELOG.md heading must be version {version}")

for ref in sorted(set(re.findall(r"`((?:references|scripts|templates)/[\w./-]+)`", skill))):
    check((ROOT / ref).exists(), f"SKILL.md points to {ref}, which does not exist")

words = len(re.findall(r"\S+", skill))
check(words <= MAX_WORDS, f"SKILL.md has {words} words; keep it under {MAX_WORDS}")

if errors:
    print("Package check failed:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print(f"Package OK: version {version}, SKILL.md {words} words")
