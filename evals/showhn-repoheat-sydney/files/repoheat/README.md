<div align="center">

# 🔥 repoheat

**See which of your GitHub repos are heating up, right in your terminal.**

[![CI](https://github.com/taufiquebuilds/repoheat/actions/workflows/ci.yml/badge.svg)](https://github.com/taufiquebuilds/repoheat/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Built with Ratatui](https://img.shields.io/badge/built%20with-Ratatui-000)](https://ratatui.rs)

![repoheat dashboard showing star velocity and viral scores for the ratatui organization](docs/demo.gif)

</div>

You have a dozen repos. One of them picked up 77 stars this week and you didn't notice, because GitHub only shows you a total. **repoheat** shows stars gained in the last 2 and 7 days for every repo you own, and ranks them by a **viral score** that flags the ones gaining momentum.

```sh
cargo install --git https://github.com/taufiquebuilds/repoheat
export GITHUB_TOKEN=$(gh auth token)
repoheat dashboard --user <your-username>
```

## What you get

- **A live dashboard** of every non-fork repo, sorted by viral score. It refreshes every minute.
- **Star velocity:** stars today plus yesterday (`+2d`), the last 7 days (`+7d`), and a 30-day chart per repo.
- **A viral score from 0 to 100** that shows how each of its points was earned. No black box.
- **One-shot commands** for scripts and quick checks: `pulse` for one repo, `compare` for several side by side.
- **Works on any public repo or org**, not just yours: `repoheat dashboard --user ratatui`.

## Install

**From source** (needs [Rust](https://rustup.rs)):

```sh
cargo install --git https://github.com/taufiquebuilds/repoheat
```

**Prebuilt binaries** for macOS, Linux and Windows will be attached to each [release](https://github.com/taufiquebuilds/repoheat/releases).

### Give it a GitHub token

repoheat reads your token from `GITHUB_TOKEN`, or from the config file that `repoheat init` writes. If you use the GitHub CLI, its token works as is:

```sh
export GITHUB_TOKEN=$(gh auth token)
```

Or [create a token](https://github.com/settings/tokens/new). No scopes are needed for public repos. Traffic numbers (views and clones) only appear for repos you can push to.

## Usage

```sh
repoheat dashboard --user <name>            # interactive dashboard
repoheat dashboard --user <name> --org <org> # include an organization's repos
repoheat dashboard --user <name> --plain     # print a table instead
repoheat pulse owner/repo                    # stats and viral score for one repo
repoheat compare owner/a owner/b owner/c     # side-by-side table
repoheat init                                # save your token to a config file
```

`--plain` is also used automatically when the output isn't a terminal, so `repoheat dashboard --user me > stars.txt` works.

| Key | Action |
| --- | --- |
| `↑` `↓` or `j` `k` | Move |
| `PgUp` `PgDn`, `g` `G` | Jump |
| `s` | Cycle sort: score, stars, +7d, last push |
| `r` | Refresh now |
| `q` or `Esc` | Quit |

## How the viral score works

The score is a transparent heuristic, not a prediction of GitHub Trending (GitHub has never published how Trending works). It adds up four parts:

| Part | Points | What earns them |
| --- | ---: | --- |
| **Momentum** | 40 | Stars in the last 7 days, log-scaled. 500 stars in a week earns the full 40. |
| **Acceleration** | 30 | This week compared with the repo's usual week (the average of the 3 weeks before). A flat week earns 0; 10× the usual week earns 30. |
| **Spike** | 15 | Stars today plus yesterday, log-scaled. 200 stars earns the full 15. |
| **Freshness** | 15 | Pushed in the last 7 days earns 15, in the last 30 days earns 8. |

| Score | Label |
| ---: | --- |
| 0–24 | Quiet |
| 25–49 | Warming up |
| 50–74 | Heating up |
| 75–100 | Trending-ready |

Log scaling means a small repo going from 2 to 80 stars a week can outscore a big repo that gets 80 stars every week. That's on purpose: the score looks for change, not size. The code is in [`src/score.rs`](src/score.rs) if you want to tune it.

## FAQ

**Why doesn't it show who starred my repo?**
Since July 2026, GitHub only shows the list of stargazers to a repo's admins and collaborators. repoheat uses GitHub's [star history endpoint](https://github.blog/changelog/2026-09-04-new-api-endpoint-provides-privacy-safe-star-history-data), which gives daily counts for any public repo without exposing who starred it. That's also why velocity is per day, not per hour.

**Why is loading slow for some accounts?**
GitHub returns repos 100 at a time, at about 2 seconds per page, and forks count toward that. An account with 400 repos took about 12 seconds in testing before the table appeared. Star history then loads in parallel, 6 repos at a time.

**How much of my API rate limit does it use?**
About one request per 100 repos plus one per repo for star history, every refresh. A 30-repo account uses about 31 requests a minute, well within GitHub's 5,000 per hour.

**The colours are missing.**
repoheat follows the [`NO_COLOR`](https://no-color.org) convention. Unset `NO_COLOR` to get colour back.

## Roadmap

- [ ] Local cache so the dashboard opens instantly
- [ ] `compare` inside the dashboard
- [ ] Weekly digest: which repos gained the most
- [ ] Configurable score weights

Ideas and pull requests are welcome. Open an [issue](https://github.com/taufiquebuilds/repoheat/issues) first for anything big.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: `cargo test`, `cargo clippy -- -D warnings` and `cargo fmt --check` must pass. The demo GIF is recorded from [`docs/demo.tape`](docs/demo.tape) with [VHS](https://github.com/charmbracelet/vhs): run `vhs docs/demo.tape`.

## License

[Apache License 2.0](LICENSE)
