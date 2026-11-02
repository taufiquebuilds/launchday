//! Star velocity and the "viral potential" score.
//!
//! The score is a transparent heuristic, not a prediction of GitHub's
//! (unpublished) trending algorithm. It rewards recent star momentum,
//! acceleration over the repo's own baseline, a fresh two-day spike, and
//! recent pushes. Every component is exposed so users can see why a repo
//! scored the way it did.

use std::collections::HashMap;

use chrono::{DateTime, Duration, NaiveDate, Utc};

use crate::github::{RepoStats, StarWeek};

/// Number of days of daily star counts kept for sparklines.
pub const WINDOW_DAYS: usize = 30;

/// Weeks of history needed to cover [`WINDOW_DAYS`] plus a partial week.
pub const HISTORY_WEEKS: u32 = (WINDOW_DAYS as u32).div_ceil(7) + 1;

/// Star counts over recent time windows.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Velocity {
    /// Stars received today and yesterday (UTC).
    pub last_2d: u64,
    /// Stars received in the last 7 days, including today.
    pub last_7d: u64,
    /// Average weekly stars over days 8 to 28 (the repo's own baseline).
    pub baseline_weekly: f64,
    /// Stars per day for the last [`WINDOW_DAYS`] days, oldest first.
    pub daily: Vec<u64>,
}

/// Compute star velocity from weekly star history.
///
/// `today` is the current UTC date; days after it are ignored.
pub fn velocity(weeks: &[StarWeek], today: NaiveDate) -> Velocity {
    let mut by_day: HashMap<NaiveDate, u64> = HashMap::new();
    for week in weeks {
        for (offset, count) in week.days.iter().enumerate() {
            *by_day
                .entry(week.week_start + Duration::days(offset as i64))
                .or_default() += count;
        }
    }

    let stars_on = |days_ago: usize| {
        by_day
            .get(&(today - Duration::days(days_ago as i64)))
            .copied()
            .unwrap_or(0)
    };

    let daily: Vec<u64> = (0..WINDOW_DAYS).rev().map(stars_on).collect();
    let baseline_total: u64 = (7..28).map(stars_on).sum();

    Velocity {
        last_2d: (0..2).map(stars_on).sum(),
        last_7d: (0..7).map(stars_on).sum(),
        baseline_weekly: baseline_total as f64 / 3.0,
        daily,
    }
}

/// Viral potential score with its components.
#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct Score {
    /// Total, 0 to 100.
    pub total: u8,
    /// Stars in the last 7 days, log-scaled (max 40).
    pub momentum: u8,
    /// Last 7 days vs. the repo's own baseline (max 30).
    pub acceleration: u8,
    /// Stars today and yesterday, log-scaled (max 15).
    pub spike: u8,
    /// How recently the repo was pushed (max 15).
    pub freshness: u8,
}

impl Score {
    /// Short human label for the score band.
    pub fn label(&self) -> &'static str {
        match self.total {
            0..=24 => "Quiet",
            25..=49 => "Warming up",
            50..=74 => "Heating up",
            _ => "Trending-ready",
        }
    }
}

/// Stars per week at which momentum maxes out.
const MOMENTUM_CAP: f64 = 500.0;
/// Stars over two days at which the spike component maxes out.
const SPIKE_CAP: f64 = 200.0;
/// Week-over-baseline ratio at which acceleration maxes out.
const ACCEL_CAP: f64 = 10.0;

/// Compute the viral potential score for a repository.
pub fn viral_score(stats: &RepoStats, v: &Velocity, now: DateTime<Utc>) -> Score {
    let log_scaled = |x: f64, cap: f64, max: f64| -> u8 {
        ((x.ln_1p() / cap.ln_1p()).min(1.0) * max).round() as u8
    };

    let momentum = log_scaled(v.last_7d as f64, MOMENTUM_CAP, 40.0);
    let spike = log_scaled(v.last_2d as f64, SPIKE_CAP, 15.0);

    let acceleration = if v.last_7d == 0 {
        0
    } else {
        // Only growth above the baseline counts: a flat week scores 0.
        let ratio = v.last_7d as f64 / v.baseline_weekly.max(1.0);
        log_scaled((ratio - 1.0).max(0.0), ACCEL_CAP - 1.0, 30.0)
    };

    let since_push = now - stats.pushed_at;
    let freshness = if since_push <= Duration::days(7) {
        15
    } else if since_push <= Duration::days(30) {
        8
    } else {
        0
    };

    Score {
        total: momentum + acceleration + spike + freshness,
        momentum,
        acceleration,
        spike,
        freshness,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn stats(now: DateTime<Utc>, pushed_days_ago: i64) -> RepoStats {
        RepoStats {
            name: "r".into(),
            full_name: "o/r".into(),
            description: None,
            stars: 0,
            forks: 0,
            open_issues: 0,
            watchers: 0,
            language: None,
            created_at: now,
            updated_at: now,
            pushed_at: now - Duration::days(pushed_days_ago),
            is_fork: false,
            is_archived: false,
            topics: vec![],
            default_branch: "main".into(),
            size_kb: 0,
        }
    }

    fn date(y: i32, m: u32, d: u32) -> NaiveDate {
        NaiveDate::from_ymd_opt(y, m, d).unwrap()
    }

    #[test]
    fn velocity_buckets_by_day() {
        // Today is Monday 2026-11-02; weeks start on Sundays.
        let today = date(2026, 11, 2);
        let weeks = vec![
            StarWeek {
                week_start: date(2026, 11, 1),
                days: vec![2, 3, 9, 0, 0, 0, 0], // Wednesday is in the future
            },
            StarWeek {
                week_start: date(2026, 10, 25),
                days: vec![1, 0, 0, 0, 0, 0, 4], // Sunday is 8 days ago
            },
            StarWeek {
                week_start: date(2026, 10, 18),
                days: vec![0, 0, 0, 0, 0, 0, 6],
            },
        ];
        let v = velocity(&weeks, today);
        assert_eq!(v.last_2d, 5);
        assert_eq!(v.last_7d, 9);
        assert!((v.baseline_weekly - 7.0 / 3.0).abs() < 1e-9);
        assert_eq!(v.daily.len(), WINDOW_DAYS);
        assert_eq!(v.daily[WINDOW_DAYS - 1], 3);
        assert_eq!(v.daily[WINDOW_DAYS - 2], 2);
        assert_eq!(v.daily.iter().sum::<u64>(), 16);
    }

    #[test]
    fn history_covers_window() {
        assert!(HISTORY_WEEKS as usize * 7 >= WINDOW_DAYS + 6);
    }

    #[test]
    fn dead_repo_scores_zero() {
        let now = Utc::now();
        let s = viral_score(&stats(now, 365), &Velocity::default(), now);
        assert_eq!(s.total, 0);
        assert_eq!(s.label(), "Quiet");
    }

    #[test]
    fn spiking_repo_scores_high() {
        let now = Utc::now();
        let v = Velocity {
            last_2d: 300,
            last_7d: 600,
            baseline_weekly: 5.0,
            daily: vec![],
        };
        let s = viral_score(&stats(now, 0), &v, now);
        assert_eq!(s.total, 100);
        assert_eq!(s.label(), "Trending-ready");
    }

    #[test]
    fn steady_repo_gets_little_acceleration() {
        let now = Utc::now();
        let v = Velocity {
            last_2d: 6,
            last_7d: 20,
            baseline_weekly: 20.0,
            daily: vec![],
        };
        let s = viral_score(&stats(now, 3), &v, now);
        assert_eq!(s.acceleration, 0);
        assert!(s.total < 50, "got {}", s.total);
    }
}
