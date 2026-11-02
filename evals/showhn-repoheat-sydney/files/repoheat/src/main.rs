//! repoheat — real-time GitHub analytics in your terminal.
//!
//! Entry point: parses CLI arguments and dispatches to the matching
//! subcommand.

mod cli;
mod config;
mod error;
mod github;
mod score;
mod tui;

use std::cmp::Reverse;
use std::io::IsTerminal;
use std::time::Duration;

use anyhow::{bail, Context, Result};
use chrono::Utc;
use clap::Parser;
use tracing_subscriber::EnvFilter;

use crate::cli::{Cli, Command};
use crate::config::Config;
use crate::github::{GitHubClient, RepoStats};

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env())
        .with_writer(std::io::stderr)
        .init();

    let cli = Cli::parse();

    match cli.command {
        Command::Init => Config::init_interactive().await?,
        Command::Pulse { repo } => run_pulse(&client()?, &repo).await?,
        Command::Compare { repos } => run_compare(&client()?, &repos).await?,
        Command::Dashboard {
            user,
            org,
            refresh,
            plain,
        } => {
            if plain || !std::io::stdout().is_terminal() {
                run_dashboard(&client()?, &user, org.as_deref()).await?;
            } else {
                let target = tui::Target { user, org };
                let refresh = Duration::from_secs(refresh.max(10));
                tui::run(client()?, target, refresh).await?;
            }
        }
    }

    Ok(())
}

/// Build an authenticated client from the loaded config.
fn client() -> Result<GitHubClient> {
    let config = Config::load()?;
    Ok(GitHubClient::new(&config.token)?)
}

/// Split an `owner/repo` slug into its two parts.
fn parse_slug(slug: &str) -> Result<(&str, &str)> {
    match slug.split_once('/') {
        Some((owner, repo)) if !owner.is_empty() && !repo.is_empty() && !repo.contains('/') => {
            Ok((owner, repo))
        }
        _ => bail!("expected `owner/repo`, got `{slug}`"),
    }
}

/// `repoheat pulse owner/repo` — one-shot stats for a single repository.
async fn run_pulse(client: &GitHubClient, slug: &str) -> Result<()> {
    let (owner, repo) = parse_slug(slug)?;
    let stats = client
        .fetch_repo_details(owner, repo)
        .await
        .with_context(|| format!("fetching {slug}"))?;
    let traffic = client.fetch_traffic(owner, repo).await.ok().flatten();
    let now = Utc::now();
    let history = client
        .fetch_star_history(owner, repo, score::HISTORY_WEEKS)
        .await
        .with_context(|| format!("fetching star history for {slug}"))?;

    println!("\n  📦 {}", stats.full_name);
    if let Some(desc) = &stats.description {
        println!("  {desc}");
    }
    println!();
    println!("  ⭐ Stars        {}", fmt_num(stats.stars));
    println!("  🍴 Forks        {}", fmt_num(stats.forks));
    println!("  🐛 Open issues  {}", fmt_num(stats.open_issues));
    println!(
        "  🧑 Language     {}",
        stats.language.as_deref().unwrap_or("—")
    );
    println!("  📅 Created      {}", stats.created_at.format("%Y-%m-%d"));
    println!("  🚀 Last push    {}", stats.pushed_at.format("%Y-%m-%d"));
    if let Some(t) = traffic {
        println!(
            "  👀 Views (14d)  {} ({} unique)",
            fmt_num(t.views),
            fmt_num(t.unique_visitors)
        );
        println!(
            "  📥 Clones (14d) {} ({} unique)",
            fmt_num(t.clones),
            fmt_num(t.unique_cloners)
        );
    }
    println!();
    let v = score::velocity(&history, now.date_naive());
    let s = score::viral_score(&stats, &v, now);
    println!("  📈 Last 2 days  +{}", fmt_num(v.last_2d));
    println!("  📈 Last 7 days  +{}", fmt_num(v.last_7d));
    println!("  🔥 Viral score  {}/100 · {}", s.total, s.label());
    println!(
        "     momentum {}/40 · acceleration {}/30 · spike {}/15 · freshness {}/15",
        s.momentum, s.acceleration, s.spike, s.freshness
    );
    println!();
    Ok(())
}

/// `repoheat compare a/b c/d ...` — side-by-side table.
async fn run_compare(client: &GitHubClient, slugs: &[String]) -> Result<()> {
    let mut rows = Vec::with_capacity(slugs.len());
    for slug in slugs {
        let (owner, repo) = parse_slug(slug)?;
        let stats = client
            .fetch_repo_details(owner, repo)
            .await
            .with_context(|| format!("fetching {slug}"))?;
        rows.push(stats);
    }
    rows.sort_by_key(|r| Reverse(r.stars));
    print_table(&rows);
    Ok(())
}

/// `repoheat dashboard --user X [--org Y]` — table of every repo.
async fn run_dashboard(client: &GitHubClient, user: &str, org: Option<&str>) -> Result<()> {
    let mut repos = client
        .fetch_user_repos(user)
        .await
        .with_context(|| format!("fetching repos for {user}"))?;
    if let Some(org) = org {
        repos.extend(
            client
                .fetch_org_repos(org)
                .await
                .with_context(|| format!("fetching repos for {org}"))?,
        );
    }
    repos.retain(|r| !r.is_fork && !r.is_archived);
    repos.sort_by_key(|r| Reverse(r.stars));

    if repos.is_empty() {
        println!("No public, non-fork repos found for {user}.");
        return Ok(());
    }

    print_table(&repos);
    let total_stars: u64 = repos.iter().map(|r| r.stars).sum();
    let total_forks: u64 = repos.iter().map(|r| r.forks).sum();
    println!(
        "\n  {} repos · ⭐ {} stars · 🍴 {} forks\n",
        repos.len(),
        fmt_num(total_stars),
        fmt_num(total_forks)
    );
    Ok(())
}

/// Print repositories as an aligned table.
fn print_table(repos: &[RepoStats]) {
    let name_w = repos
        .iter()
        .map(|r| r.full_name.chars().count())
        .max()
        .unwrap_or(4)
        .clamp(4, 48);

    println!();
    println!(
        "  {:<name_w$}  {:>8}  {:>7}  {:>7}  {:<12}  {:<10}",
        "REPO", "STARS", "FORKS", "ISSUES", "LANGUAGE", "LAST PUSH"
    );
    println!("  {}", "─".repeat(name_w + 54));
    for r in repos {
        println!(
            "  {:<name_w$}  {:>8}  {:>7}  {:>7}  {:<12}  {:<10}",
            truncate(&r.full_name, name_w),
            fmt_num(r.stars),
            fmt_num(r.forks),
            fmt_num(r.open_issues),
            truncate(r.language.as_deref().unwrap_or("—"), 12),
            r.pushed_at.format("%Y-%m-%d"),
        );
    }
}

/// Format a number with thousands separators (`12345` → `12,345`).
fn fmt_num(n: u64) -> String {
    let s = n.to_string();
    let mut out = String::with_capacity(s.len() + s.len() / 3);
    for (i, c) in s.chars().enumerate() {
        if i > 0 && (s.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(c);
    }
    out
}

/// Truncate a string to `max` characters, adding `…` when cut.
fn truncate(s: &str, max: usize) -> String {
    if s.chars().count() <= max {
        s.to_string()
    } else {
        let cut: String = s.chars().take(max.saturating_sub(1)).collect();
        format!("{cut}…")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn formats_numbers() {
        assert_eq!(fmt_num(0), "0");
        assert_eq!(fmt_num(999), "999");
        assert_eq!(fmt_num(1000), "1,000");
        assert_eq!(fmt_num(1234567), "1,234,567");
    }

    #[test]
    fn parses_slugs() {
        assert_eq!(parse_slug("tokio-rs/tokio").unwrap(), ("tokio-rs", "tokio"));
        assert!(parse_slug("nope").is_err());
        assert!(parse_slug("/repo").is_err());
        assert!(parse_slug("a/b/c").is_err());
    }

    #[test]
    fn truncates() {
        assert_eq!(truncate("short", 10), "short");
        assert_eq!(truncate("abcdefghij", 5), "abcd…");
    }
}
