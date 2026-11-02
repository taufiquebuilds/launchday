# Contributing to launchday

Thanks for helping. The most useful contributions are lessons from real launches: a channel that worked, a post format that flopped, a README change that moved the numbers. Open a "Launch tip" issue for those, with links if you can.

## Changing the skill

- `SKILL.md` is the prompt agents read on every use, so every word costs. Keep it short, and put detail in `references/`.
- Explain *why* in instructions, not just *what*. Agents follow reasons better than rules.
- Keep it portable. Claude Code, Codex and Cursor are examples, not the only targets.
- Put deterministic work (lookups, date maths, image processing) in `scripts/`. Use the Python standard library only.

## Before you open a pull request

```sh
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
```

If you change behaviour, add a line to `CHANGELOG.md`. If you bump the version, change it in `SKILL.md` (`metadata.version`), `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json` and the first `CHANGELOG.md` heading. The validator checks that they match.

By contributing, you agree that your contributions are licensed under the MIT License.
