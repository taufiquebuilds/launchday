# README as a landing page

A visitor gives a README about 10 seconds. In that time they need three answers: what is this, does it work, and how do I try it. Everything below the first screen is for people who are already interested.

## Structure

Use this order. Skip a section if it has nothing true to say.

1. **Name and one-line value.** Under 15 words, plain language: what it does for whom. "See which of your GitHub repos are heating up, right in your terminal."
2. **Badges.** One line at most: CI, license, latest release. Badges that would show zero (downloads, stars) hurt more than they help on day one.
3. **The visual.** A GIF, screenshot or before/after, near the top. Give it real alt text describing what it shows.
4. **The hook paragraph.** 2 or 3 sentences: the pain, then what this does about it. Start from the user's situation, not from the technology.
5. **Quick start.** At most 3 commands, copy-paste ready, ending with the command that shows the proof moment.
6. **Features.** 3 to 6 bullets. Each starts with a bold outcome and is something a user can verify.
7. **Install.** All the ways: package manager, prebuilt binaries, from source. Include any token or configuration step here, with the least-privilege option.
8. **Usage.** Commands, flags and keys as a table or a short code block. Copy them from the real `--help` output.
9. **How it works.** Only if there is something non-obvious, like a scoring formula, an algorithm or an architecture choice. Transparency is a feature, and HN readers read this section.
10. **FAQ.** The 3 to 5 questions you'd expect in the first comments: limits, privacy, performance, "why not X".
11. **Roadmap.** Unbuilt ideas, as an unchecked list, clearly separate from the features.
12. **Contributing and license.** Two short sections linking the files.

## Writing rules

- **Lead with the pain, not the stack.** "Written in Rust" is a detail; "opens in 50 ms" is a reason.
- **Use numbers you measured.** "Loads 400 repos in about 12 seconds" beats "blazing fast". If you didn't measure it, don't say it.
- **Use the reader's words.** Say "stars this week", not "temporal engagement velocity".
- **Keep paragraphs short.** Use 1 to 3 sentences each, and put lists in bullets.
- **Make code blocks runnable.** No `$` prompts, no `...`, and use placeholders like `<your-username>` only when unavoidable.
- **Verify every claim against the code.** For each feature bullet, find where it's implemented. For each flag, check `--help`. For each number, have a run or test that produced it. Remove or move to the roadmap anything you can't back up.
- **Avoid hype words:** revolutionary, blazing, seamless, game-changing, next-generation, AI-powered (unless AI is the point), simply, just.

## Before and after

**Before** (explains, buries the proof):

> # mytool
> mytool is a powerful, flexible, extensible framework for analyzing repository metrics, built with modern technologies.
> ## Installation
> Clone the repo and run `make install`. You will need Rust 1.75...

**After** (shows, then lets you try):

> # 🔥 mytool
> **See which of your repos are gaining stars this week.**
>
> ![mytool dashboard ranking repos by stars gained](docs/demo.gif)
>
> GitHub shows total stars. It doesn't tell you which repo picked up 80 this week. mytool does, for every repo you own.
>
> ```sh
> cargo install mytool
> mytool dashboard --user <your-username>
> ```

## GitHub settings that go with the README

These live in the repo settings, not in the README, and the audit checks them:

- **Description:** the one-line value, under 120 characters.
- **Topics:** 5 to 10. Mix the language (`rust`), the form (`cli`, `tui`), the domain (`github-analytics`) and the community (`ratatui`, `developer-tools`).
- **Website:** docs or a demo, if one exists.
- **Social preview:** the 1280×640 image from phase 5.
