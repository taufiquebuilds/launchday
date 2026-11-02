# Demo GIF, screenshot and social preview

The demo is the proof. It goes in the first screen of the README and becomes the social preview, so it's worth getting right.

## Choose the format

| Project type | Format | Tool |
| --- | --- | --- |
| CLI or TUI | Animated GIF of a real session, 15 to 30 seconds | [VHS](https://github.com/charmbracelet/vhs) |
| Web app or desktop app | Screenshots, or a short MP4/GIF of one flow | Playwright screenshots, or the OS screen recorder |
| Library or API | A before/after code block with real output, or a chart of a benchmark you ran | Code block, or a rendered image |
| Agent skill or prompt | A before/after example of real output | Text in the README |

## CLI and TUI: record with VHS

Install it with `brew install vhs` on macOS or `go install github.com/charmbracelet/vhs@latest`. It needs `ttyd` and `ffmpeg`, which brew installs too.

Copy `templates/demo.tape` into the repo as `docs/demo.tape` and edit it. Keeping the tape in the repo means anyone can re-record the GIF after a change with `vhs docs/demo.tape`, and it's how contributors update the demo.

Script the demo around the proof moment from phase 1:

1. Start with the shortest command that shows value, not the setup.
2. Show one or two interactions (scrolling, sorting, a second command), then quit.
3. Keep it under 30 seconds and the file under about 5 MB. GitHub renders GIFs up to 10 MB, but large ones load slowly.

Things that go wrong, all of them caught in real launches:

- **No colour in the recording.** If the environment has `NO_COLOR` or `FORCE_COLOR=0` set, well-behaved tools print in plain text. Clear them in the hidden setup step: `unset NO_COLOR FORCE_COLOR`.
- **Secrets on screen.** Do setup such as tokens and `PATH` changes between `Hide` and `Show`. Use `$(gh auth token)` and never paste a literal token, even when hidden.
- **Unreadable highlight rows.** A grey selection bar hides grey text. Check the selected row in the frames.
- **Recording real people's data.** Prefer an organisation's public repos or the user's own over an individual's account, especially in promo material.
- **Slow data loads.** If the first screen takes several seconds to fill, either wait inside the tape (`Sleep`) or pick a smaller example account.

Check the result before using it:

```sh
ffprobe -v error -show_entries format=duration -of csv=p=0 docs/demo.gif
for t in 5 12 20; do ffmpeg -v error -y -ss $t -i docs/demo.gif -frames:v 1 /tmp/frame_$t.png; done
```

Then look at the frames.

## Web apps

- Take screenshots at 1280×800 with light content and real-looking data. An empty state is not a demo.
- With Playwright: `npx playwright screenshot --viewport-size=1280,800 http://localhost:3000 docs/screenshot.png`.
- For motion, record one 10 to 20 second flow, then convert it: `ffmpeg -i in.mov -vf "fps=12,scale=1200:-1" -loop 0 docs/demo.gif`.

## Social preview

```sh
sh <skill-dir>/scripts/social_preview.sh docs/demo.gif docs/social-preview.png
```

The script grabs a frame (60% of the way in by default, or pass a time in seconds) and fits it into 1280×640 with padding. It never crops, so nothing gets cut off. Choose a frame where the main thing is visible and readable at thumbnail size.

Uploading is manual: repo **Settings → General → Social preview → Edit → Upload**. There is no API for it. To verify it afterwards:

```sh
gh api graphql -f query='{repository(owner:"OWNER",name:"REPO"){usesCustomOpenGraphImage}}'
```

To keep these images out of published packages, exclude them: `exclude = ["docs/*.gif", "docs/*.png"]` in `Cargo.toml`, the `files` field in `package.json`, or `[tool.setuptools]` exclusions for Python.
