#!/usr/bin/env python3
"""Pick the next good launch slot and print the posting schedule in your time zone.

Usage: python3 scripts/launch_time.py [--tz Asia/Kolkata] [--after 2026-11-02] [--count 3]

Hacker News and r/programming traffic peaks on US weekday mornings, so the
default slot is Tuesday to Thursday, 8:30 AM US Eastern. US Eastern switches
between EST and EDT, so times are computed with real time-zone rules instead
of a fixed offset. Days when big news or holidays drown out small launches
(US election days, Thanksgiving week, the Christmas to New Year stretch,
4 July) are skipped, and the skipped days are listed with the reason.
"""

import argparse
import sys
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

EASTERN = ZoneInfo("America/New_York")
LAUNCH_DAYS = {1: "Tuesday", 2: "Wednesday", 3: "Thursday"}  # Monday is 0
HN_TIME = time(8, 30)

# (minutes after the HN post, channel)
SCHEDULE = [
    (0, "Hacker News (Show HN)"),
    (30, "Reddit: the best-fit subreddit"),
    (60, "Reddit: second and third subreddits"),
    (90, "X / Bluesky / LinkedIn thread"),
]


def nth_weekday(year, month, weekday, n):
    """The n-th given weekday (Monday=0) of a month."""
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (n - 1))


def conflict(day):
    """Return why `day` is a bad launch day, or None."""
    election = nth_weekday(day.year, 11, 0, 1) + timedelta(days=1)  # Tuesday after first Monday
    if day.year % 2 == 0 and election <= day <= election + timedelta(days=2):
        return "US election week: results news crowds everything out"
    thanksgiving = nth_weekday(day.year, 11, 3, 4)
    if thanksgiving - timedelta(days=3) <= day <= thanksgiving + timedelta(days=1):
        return "US Thanksgiving week: much of the audience is away"
    if (day.month == 12 and day.day >= 22) or (day.month == 1 and day.day <= 2):
        return "Christmas to New Year: much of the audience is away"
    if day.month == 7 and day.day in (3, 4, 5):
        return "US Independence Day"
    return None


def local_zone(name):
    if name:
        return ZoneInfo(name)
    return datetime.now().astimezone().tzinfo


def next_slots(after, count, skipped=None):
    """Yield the next `count` good launch days strictly after `after`.

    Days skipped for a conflict are appended to `skipped` as (date, reason).
    """
    day = after + timedelta(days=1)
    found = 0
    while found < count:
        if day.weekday() in LAUNCH_DAYS:
            why = conflict(day)
            if why:
                if skipped is not None:
                    skipped.append((day, why))
            else:
                yield datetime.combine(day, HN_TIME, tzinfo=EASTERN)
                found += 1
        day += timedelta(days=1)


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--tz", help="IANA time zone for your local times, e.g. Asia/Kolkata")
    p.add_argument("--after", help="Pick slots after this date (YYYY-MM-DD). Default: today")
    p.add_argument("--count", type=int, default=3, help="How many candidate days to list")
    args = p.parse_args(argv)

    try:
        tz = local_zone(args.tz)
    except ZoneInfoNotFoundError:
        print(f"Unknown time zone: {args.tz}", file=sys.stderr)
        return 2
    after = date.fromisoformat(args.after) if args.after else datetime.now(EASTERN).date()

    skipped = []
    slots = list(next_slots(after, args.count, skipped))
    first = slots[0]
    for day, why in skipped:
        if day < first.date():
            print(f"Skipped {LAUNCH_DAYS[day.weekday()]} {day:%d %b}: {why}")
    print(f"Recommended launch: {LAUNCH_DAYS[first.weekday()]} {first:%d %b %Y}")
    if slots[1:]:
        print("Backups: " + ", ".join(f"{LAUNCH_DAYS[s.weekday()]} {s:%d %b}" for s in slots[1:]))
    print()
    print(f"{'Post':<38} {'US Eastern':<14} Your time ({tz})")
    for minutes, channel in SCHEDULE:
        t = first + timedelta(minutes=minutes)
        local = t.astimezone(tz)
        day_note = "" if local.date() == t.date() else f" ({local:%a})"
        eastern = t.strftime("%I:%M %p %Z")
        print(f"{channel:<38} {eastern:<14} {local:%I:%M %p}{day_note}")
    end = (first + timedelta(hours=3)).astimezone(tz)
    print(f"\nStay online to reply to comments until about {end:%I:%M %p} your time.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
