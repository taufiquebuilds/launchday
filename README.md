<div align="center">

# 🚀 launchday

**Your repo works. Now launch it like it matters.**

[![CI](https://github.com/taufiquebuilds/launchday/actions/workflows/ci.yml/badge.svg)](https://github.com/taufiquebuilds/launchday/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![launchday auditing an unpolished project, checking its name, and scheduling the launch](docs/demo.gif)

</div>

Most good open-source projects launch badly: a README that explains instead of showing, no demo, no one-line install, a name three other tools already use, and a Show HN posted at 3 AM US time. **launchday** is an agent skill that fixes all of it in one pass, then hands you a launch plan you can run in an evening. It works in Claude Code, Codex, Cursor and any agent that supports skills.

```
/plugin marketplace add taufiquebuilds/launchday
/plugin install launchday@launchday
```

Then, in your project: **"launch this repo"**.

## What it does

```
$ python3 scripts/audit.py examples/unlaunched-cli
Launch readiness: 20/100
  1. [15 pts] Opening line is vague hype (built using modern, extensible, flexible, powerful). Say what it does and for whom, in plain words.
  2. [15 pts] No screenshot, GIF or video in the first screen. Show it working before explaining it.
  3. [15 pts] No copy-paste install command in the first 90 lines. Make it one line.
  4. [10 pts] No LICENSE. Many people won't use or contribute without one (MIT or Apache-2.0).
  ...

$ python3 scripts/audit.py ../repoheat     # a repo launched with this process
Launch readiness: 100/100
```

Your agent works through 8 phases and tells you where it is:

| Phase | You get |
| --- | --- |
| 1. **Understand** | A one-paragraph pitch: what it does, who has the pain, and the "oh, nice" moment |
| 2. **Name check** | Collisions on GitHub, crates.io, npm, PyPI and Homebrew, plus alternatives if needed |
| 3. **Audit** | A launch-readiness score out of 100, including leaked secrets and personal commit emails |
| 4. **README** | A rewrite as a landing page: hook, proof, one-line install, with every claim checked against the code |
| 5. **Demo** | A GIF recorded from a script you can re-run (VHS), plus a 1280×640 social preview |
| 6. **Release** | CI plus a tag-to-release workflow for Rust, Node, Python or Go that stays green before you add tokens |
| 7. **Launch kit** | `LAUNCH.md` with a Show HN post, Reddit posts, an X thread, and the schedule in *your* time zone |
| 8. **Hand-off** | The exact commands to publish. You stay in control of anything public. |

## Why it's different from "write me a README"

- **It checks before it writes.** It runs scripts for the things models get wrong: name collisions, time zones and daylight saving, secrets, and cropped previews.
- **It refuses to make things up.** README claims must match the code. Launch posts use your real story, or ask you for it. It never invents a backstory, user numbers or benchmarks.
- **It never publishes for you.** It prepares everything to the point of copy-paste. Creating the public repo, tagging and posting stay your decisions.
- **It's built from a real launch.** Every gotcha in it happened while launching [repoheat](https://github.com/taufiquebuilds/repoheat): a crate name already taken, a GIF recorded without colour because `NO_COLOR` was set, a social preview that cut off the UI, and launch times that were an hour off after US clocks changed.

## Install

**Claude Code:**

```
/plugin marketplace add taufiquebuilds/launchday
/plugin install launchday@launchday
```

**Codex, Cursor, OpenCode and other agents** (via [skills](https://skills.sh)):

```sh
npx skills add taufiquebuilds/launchday --global --agent '*'
```

**Manually:** clone this repo into your agent's skills folder, for example `~/.claude/skills/launchday`.

**Requirements:** Python 3.9 or newer for the scripts. `ffmpeg` for the social preview. [VHS](https://github.com/charmbracelet/vhs) for terminal GIFs, which is optional. `gh` (logged in) adds GitHub-side checks to the audit.

## Use it

Ask your agent in plain words:

- "Launch this repo." (the full 8 phases)
- "Is this ready to post on Hacker News?" (the audit and launch kit)
- "Rewrite my README so people actually try it."
- "Record a demo GIF for this CLI."
- "When should I post my Show HN? I'm in Berlin."

The scripts also work on their own:

```sh
python3 scripts/audit.py .                                  # readiness score + fix list
python3 scripts/name_check.py mytool mytool-cli             # name collisions
python3 scripts/launch_time.py --tz Europe/Berlin           # launch schedule in your zone
sh scripts/social_preview.sh docs/demo.gif docs/social-preview.png
```

## FAQ

**Does it post to Hacker News or Reddit for me?**
No. It writes the posts and the schedule. Posting is yours, because it speaks in your name and can't be taken back.

**Does it work for web apps and libraries, not just CLIs?**
Yes. The demo phase picks the format by project type: a GIF for CLIs and TUIs, screenshots or a short recording for web apps, and a before/after for libraries. The release phase covers Rust, Node, Python and Go.

**Will it guarantee stars?**
No tool can. It removes the reasons good projects get ignored: no proof, no install line, bad timing and a vague pitch. The project still has to be useful.

**What data does it send anywhere?**
`name_check.py` queries the public GitHub, crates.io, npm, PyPI and Homebrew APIs with just the name. `audit.py` reads your repo locally and, if you have `gh` set up, your repo's settings from GitHub. Nothing else.

## Roadmap

- [ ] A recorded before/after of a full agent run
- [ ] Coloured script output
- [ ] Product Hunt and Dev.to post formats
- [ ] Demo recipes for desktop apps and mobile
- [ ] A post-launch check-in: what worked, from star-velocity data

## Contributing

Launch tips from real launches are the most valuable contribution. Open a [launch tip](https://github.com/taufiquebuilds/launchday/issues/new?template=launch_tip.yml) issue with what worked or failed. For code and docs, see [CONTRIBUTING.md](CONTRIBUTING.md). `python3 scripts/validate_package.py` and `python3 -m unittest discover -s tests` must pass.

## License

[MIT](LICENSE)
