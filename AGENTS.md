# Guide for agents working on this repo

launchday is an agent skill. `SKILL.md` is the prompt; `references/` holds detail it loads on demand; `scripts/` holds standard-library Python and POSIX sh helpers.

- Keep `SKILL.md` under 3,000 words. `scripts/validate_package.py` enforces it.
- The manifest descriptions must equal the first sentence of the `SKILL.md` description. Versions must match in `SKILL.md`, both `plugin.json` files and the first `CHANGELOG.md` heading.
- Run `python3 scripts/validate_package.py` and `python3 -m unittest discover -s tests` before committing.
- The skill must never publish, push or post on the user's behalf, and never invent claims. Keep those rules intact in any edit.
