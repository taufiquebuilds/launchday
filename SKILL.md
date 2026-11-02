---
name: launchday
description: Take a code repository from "it works on my machine" to launch-ready on GitHub, then plan the launch. Checks the name for collisions, audits launch readiness, rewrites the README as a landing page, records a demo GIF, makes the social preview, sets up release CI, and writes Hacker News, Reddit and X posts with a posting schedule in the user's time zone. Use this whenever someone wants to launch, ship, publish, open-source, announce or "go viral" with a repo or side project, asks how to get GitHub stars, wants a better README, demo GIF or social preview, or is preparing a Show HN or Reddit post, even if they don't say "launch".
license: MIT
metadata:
  version: 0.1.0
  author: taufiquebuilds
---

# launchday

Most good open-source projects launch badly: a README that explains instead of showing, no demo, no install line, a name that collides with three other tools, and a Show HN posted at 3 AM US time. This skill fixes all of that in one pass, then hands the user a launch plan they can execute in an evening.

You do the preparation. **The user does anything public**: creating the public repo, pushing tags, uploading the social preview, and posting. Publishing is hard to undo and speaks in their name, so you prepare it to the point where it is copy-paste, then stop and hand over.

## How to run it

Work through the phases in order. Each phase ends with something concrete in the repo. Tell the user which phase you are on, so they can follow along.

Scripts live in `scripts/` next to this file. They use only Python's standard library (plus `ffmpeg` for the preview). Run them with the path to this skill's folder, for example `python3 <skill-dir>/scripts/audit.py .`.

| Phase | Output | Script or reference |
| --- | --- | --- |
| 1. Understand | One-paragraph summary you confirm with the user | none |
| 2. Name check | Keep or rename decision | `scripts/name_check.py` |
| 3. Audit | Score and fix list | `scripts/audit.py` |
| 4. README | README rewritten as a landing page | `references/readme.md` |
| 5. Demo | GIF or screenshot plus social preview | `references/demo.md`, `scripts/social_preview.sh` |
| 6. Release | CI and release workflow | `references/release.md` |
| 7. Launch kit | `LAUNCH.md` with posts and schedule | `references/launch-posts.md`, `scripts/launch_time.py` |
| 8. Hand-off | Exact commands for the user to run | none |

If the user asked for only one part ("just fix my README", "write my Show HN"), do that phase. Still run the audit first if it's cheap, because it often reveals the real blocker.

## Phase 1: Understand the project

Read the README, the package manifest (`package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`) and the entry point. Run the project if you can do so safely. Then write one paragraph covering three things:

- **What it does**, in one sentence a non-expert understands.
- **Who has the pain.** Be specific: "maintainers with 10+ repos", not "developers".
- **The proof moment**: the first thing a new user sees that makes them say "oh, nice". The README and demo are built around this.

Confirm it with the user in one short message. A wrong summary here poisons everything downstream. Also ask for anything you cannot find yourself: which GitHub account will host the repo, and their time zone for the launch schedule.

## Phase 2: Name check

```sh
python3 <skill-dir>/scripts/name_check.py <name> [alternative ...]
```

The script checks crates.io, npm, PyPI, Homebrew and GitHub. A shared name splits search results, so people who hear about the project can't find it, and a taken registry name blocks publishing. If the verdict is AVOID or CROWDED, propose 3 to 4 alternatives and check them in the same run. Good names say what the tool does, or evoke it, and are easy to spell after hearing them once.

Renaming is the user's call. If they rename, change every occurrence: manifest, binary name, README, links, CI, config paths and user-agent strings. Use a script that walks the files rather than shell word-splitting, which breaks on paths with spaces. Then rebuild and run the tests.

## Phase 3: Audit

```sh
python3 <skill-dir>/scripts/audit.py <repo-path>
```

You get a score out of 100 and a fix list, sorted by weight. It covers the README hook, a visual and an install line near the top, the license and community files, CI and release workflows, leaked secrets, personal commit emails, and, if `gh` is logged in, the GitHub description, topics, social preview and releases.

Two findings come before anything else, because they cannot be undone after a public push:

- **A secret in a tracked file.** Remove it, and tell the user to rotate it. It is already in git history.
- **A personal commit email** (Gmail and similar). Every public commit shows it. Set the repo's email to the user's GitHub noreply address, `ID+username@users.noreply.github.com`. Get the ID from `gh api user --jq .id`.

Re-run the audit at the end of phase 6. The score going up is the user's progress bar, so show it.

## Phase 4: README as a landing page

Read `references/readme.md` and rewrite the README in that structure. The core idea: a visitor decides in about 10 seconds, using only the first screen. So the first screen must hold the pain, the proof (the GIF) and the install command. The explanation comes after.

Every claim in the README must be true of the code as it is today. Check each feature, flag and number against the source or a real run before you write it. Overclaiming gets caught in the first HN comment, and it costs more trust than the claim gains. Put future work in a Roadmap section, clearly marked.

## Phase 5: Demo and social preview

Read `references/demo.md`. Pick the format from the project type:

- **CLI or TUI:** record a GIF with VHS, using a tape file committed to `docs/demo.tape`, so anyone can re-record it.
- **Web app:** screenshots, or a short screen recording.
- **Library:** a before/after code snippet with real output.

Then make the social preview:

```sh
sh <skill-dir>/scripts/social_preview.sh docs/demo.gif docs/social-preview.png
```

**Look at the frames yourself before moving on.** Extract 2 or 3 frames with `ffmpeg` and view them. Recordings fail quietly: colours disappear because `NO_COLOR` is set in the environment, a token gets typed on screen, text is unreadable on the selected row, or the frame you grabbed shows a loading spinner. Fix and re-record. Looking at the frames is cheap; a broken GIF at the top of the README is not.

## Phase 6: Release and CI

Read `references/release.md` for the project's ecosystem. The goal is install paths for people who don't have the toolchain: prebuilt binaries, or a published package, from a tag push. Make any publish step skip cleanly when its secret isn't set, so the user's first release doesn't show a red failure. Run the project's own lint, format and test commands locally, and make them pass, because CI runs them on the first push.

## Phase 7: Launch kit

```sh
python3 <skill-dir>/scripts/launch_time.py --tz <user's IANA time zone>
```

This picks the next Tuesday, Wednesday or Thursday at 8:30 AM US Eastern and converts the schedule to the user's time zone, following daylight-saving rules. It skips US election weeks, Thanksgiving week, Christmas to New Year and 4 July, and says why. Don't do the conversion in your head: the US/Europe daylight-saving changes shift the offset by an hour twice a year. If you can search the web, also check the chosen week for anything that would dominate tech news (a major Apple, Google or OpenAI event, a big outage) and move a day if needed.

Then read `references/launch-posts.md` and write `LAUNCH.md` in the repo's parent folder, or in `docs/` if the user prefers. It holds the schedule, a pre-launch checklist, the Show HN title and first comment, 2 or 3 Reddit posts for the best-fit subreddits, an X thread, and the day-after plan.

The story in the posts must be real. Use what is actually true about why the project exists or what was learned building it. If you don't know, ask the user for one sentence of their real motivation. Never invent a backstory, user counts or a benchmark.

## Phase 8: Hand-off

Finish with a short message that has:

1. The audit score, before and after.
2. What's now in the repo, as a list of files.
3. The exact commands the user runs to publish, in order: create the public repo, push, wait for CI, tag the release.
4. The manual steps no API can do: uploading the social preview (Settings, then Social preview), pinning the repo, and fixing profile details.
5. The launch day and time in their time zone, and where `LAUNCH.md` is.

After they say they've published, offer to verify. Check that the repo is public, CI is green, the release has assets, the install command works from a clean directory, and the social preview is set (`gh api graphql -f query='{repository(owner:"o",name:"r"){usesCustomOpenGraphImage}}'`).

## What makes a launch work

These are the ideas the phases serve. Use them to make calls the steps don't cover.

- **Show before you tell.** A GIF of the thing working beats three paragraphs about it.
- **One line to try it.** Every extra step before the first "oh, nice" loses people.
- **Be honest and specific.** "Ranks your repos by stars gained this week" beats "AI-powered analytics platform". The HN audience punishes hype and rewards a real story.
- **Timing and replies matter as much as the post.** Post when the audience is awake, and answer every comment in the first 3 hours.
- **Never ask for upvotes or stars.** On HN it gets the post flagged. Elsewhere it reads as spam.
