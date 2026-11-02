# Release and CI

Goal: anyone can install the project without your toolchain, and a green CI badge shows that it works. Set this up before launch day, because launch-day visitors who can't install leave.

## Principles

- **CI runs what you run locally:** build, test, lint, format check. Run them locally first, so the first push is green. A red badge on launch day is worse than no badge.
- **A tag push makes a release:** `git tag v0.1.0 && git push origin v0.1.0`.
- **Publishing skips cleanly without its secret.** The first release should be all green, even before the user has registry tokens. Use the step-level `env` + `if` pattern below.
- **Pin actions to major versions** (`actions/checkout@v4`) and give release jobs only `contents: write`.

### Skip-without-secret pattern

```yaml
publish:
  runs-on: ubuntu-latest
  needs: build
  env:
    REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}
  steps:
    - if: env.REGISTRY_TOKEN == ''
      run: echo "REGISTRY_TOKEN not set; skipping publish"
    - if: env.REGISTRY_TOKEN != ''
      uses: actions/checkout@v4
    # ...the remaining steps, each with the same `if`
```

Job-level `if` can't read `secrets` directly, which is why the check lives on each step.

## Rust

- **CI:** `cargo check`, `cargo test`, `cargo fmt --all -- --check`, `cargo clippy -- -D warnings`.
- **Release:** a matrix over `x86_64-unknown-linux-gnu`, `x86_64-apple-darwin`, `aarch64-apple-darwin` and `x86_64-pc-windows-msvc`. Build with `cargo build --release --target $T`, archive with `tar czf` (or `7z` on Windows), and upload with `softprops/action-gh-release@v2`.
- **Publish:** `cargo publish`, which reads the `CARGO_REGISTRY_TOKEN` environment variable. Check the crate name on crates.io first: names are first-come and permanent.
- **README install line:** `cargo install --git https://github.com/OWNER/REPO` works before the crate is published.

## Node / TypeScript

- **CI:** `npm ci`, `npm test`, `npm run lint`, `npm run build`, on Node LTS.
- **Release:** on tag, `npm publish --provenance --access public` with `id-token: write` permission and `NODE_AUTH_TOKEN` from an `NPM_TOKEN` secret.
- **For CLIs:** set `"bin"` in `package.json`, so `npx <name>` works. That's the one-line install.
- **Keep the package small:** set the `"files"` field so the demo GIF isn't shipped.

## Python

- **CI:** `pip install -e .[dev]` (or `uv sync`), `pytest`, `ruff check`, `ruff format --check`, across 2 or 3 Python versions.
- **Release:** on tag, `python -m build`, then `pypa/gh-action-pypi-publish@release/v1` using PyPI trusted publishing (`id-token: write`, no token needed once it's configured on pypi.org).
- **CLI install line:** `pipx install <name>` or `uvx <name>`.

## Go

- **CI:** `go vet ./...`, `go test ./...`, `gofmt -l .` (fail if it prints anything).
- **Release:** `goreleaser/goreleaser-action@v6` on tag, with a minimal `.goreleaser.yaml` (builds for linux, darwin and windows on amd64 and arm64).
- **Install line:** `go install github.com/OWNER/REPO@latest`.

## Agent skills and prompt packs

- No build step. CI validates the package: JSON manifests parse, `SKILL.md` frontmatter has `name` and `description`, and any scripts pass their tests.
- Ship manifests for the major agents: `.claude-plugin/plugin.json` and `marketplace.json` (Claude Code), `.cursor-plugin/plugin.json` (Cursor), and `agents/openai.yaml` (Codex and OpenAI-compatible agents). Keep versions identical across them.
- **Install lines:** `/plugin marketplace add OWNER/REPO` for Claude Code, and `npx skills add OWNER/REPO` for everything else.

## After the first release, verify

```sh
gh run list --limit 3
gh release view v0.1.0 --json assets --jq '.assets[].name'
```

Then install from scratch in a temporary directory, exactly as the README says, and run the proof-moment command.
