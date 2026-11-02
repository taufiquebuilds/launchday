"""Tests for the helper scripts. Run with: python3 -m unittest discover tests"""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


launch_time = load("launch_time")
audit = load("audit")
name_check = load("name_check")


class LaunchTimeTests(unittest.TestCase):
    def test_picks_tuesday_to_thursday_only(self):
        slots = list(launch_time.next_slots(date(2026, 10, 5), 6))  # a quiet Monday
        self.assertEqual([s.weekday() for s in slots], [1, 2, 3, 1, 2, 3])

    def test_never_picks_the_same_day(self):
        first = next(launch_time.next_slots(date(2026, 10, 6), 1))  # a Tuesday
        self.assertEqual(first.date(), date(2026, 10, 7))

    def test_skips_us_election_week(self):
        skipped = []
        first = next(launch_time.next_slots(date(2026, 11, 2), 1, skipped))
        self.assertEqual(first.date(), date(2026, 11, 10))
        self.assertEqual([d for d, _ in skipped], [date(2026, 11, 3), date(2026, 11, 4), date(2026, 11, 5)])

    def test_no_election_skip_in_odd_years(self):
        first = next(launch_time.next_slots(date(2027, 11, 1), 1))
        self.assertEqual(first.date(), date(2027, 11, 2))

    def test_skips_thanksgiving_and_christmas(self):
        self.assertIsNotNone(launch_time.conflict(date(2026, 11, 24)))  # Thanksgiving is 26 Nov
        self.assertIsNotNone(launch_time.conflict(date(2026, 12, 29)))
        self.assertIsNone(launch_time.conflict(date(2026, 12, 15)))

    def test_follows_us_daylight_saving(self):
        kolkata = ZoneInfo("Asia/Kolkata")
        before = next(launch_time.next_slots(date(2026, 10, 26), 1))  # EDT
        after = next(launch_time.next_slots(date(2026, 11, 9), 1))  # EST
        self.assertEqual(before.astimezone(kolkata).strftime("%H:%M"), "18:00")
        self.assertEqual(after.astimezone(kolkata).strftime("%H:%M"), "19:00")


class AuditTests(unittest.TestCase):
    def make_repo(self, files):
        tmp = Path(tempfile.mkdtemp())
        for rel, text in files.items():
            p = tmp / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        return tmp

    def score(self, checks):
        return {c[0]: c[2] for c in checks}

    def test_good_readme_passes_core_checks(self):
        repo = self.make_repo({
            "README.md": "# tool\n\nSee which repos gain stars this week, in your terminal.\n\n"
                         "![demo](docs/demo.gif)\n\n```sh\ncargo install tool\n```\n",
        })
        got = self.score(audit.readme_checks(repo))
        self.assertTrue(got["hook"] and got["visual"] and got["install"] and got["placeholders"])

    def test_hype_opening_fails_the_hook(self):
        repo = self.make_repo({"README.md": "# t\n\nA powerful, flexible and extensible framework for data.\n"})
        self.assertFalse(self.score(audit.readme_checks(repo))["hook"])

    def test_bare_readme_fails_core_checks(self):
        repo = self.make_repo({"README.md": "# tool\n\nTODO: write docs\n"})
        got = self.score(audit.readme_checks(repo))
        self.assertFalse(got["visual"])
        self.assertFalse(got["install"])
        self.assertFalse(got["placeholders"])

    def test_usage_placeholder_is_not_flagged(self):
        repo = self.make_repo({"README.md": "# t\n\nDoes a useful thing for people.\n\n"
                                            "```sh\nnpx t --user <your-username>\n```\n"})
        self.assertTrue(self.score(audit.readme_checks(repo))["placeholders"])

    def test_badges_do_not_count_as_a_visual(self):
        repo = self.make_repo({"README.md": "# t\n\n[![CI](https://github.com/o/t/actions/workflows/ci.yml/badge.svg)](x)\n"
                                            "[![License](https://img.shields.io/badge/license-MIT-blue.svg)](x)\n"})
        self.assertFalse(self.score(audit.readme_checks(repo))["visual"])

    def test_fake_tokens_and_build_folders_are_ignored(self):
        repo = self.make_repo({"docs.md": 'export GITHUB_TOKEN=ghp_' + "a" * 36 + "\n",
                               "__pycache__/x.pyc": "ghp_" + "Zx9Qw2Er7Ty4Ui1Op3As5Df8Gh6Jk0Lz2Xc"})
        self.assertTrue(self.score(audit.privacy_checks(repo))["secrets"])

    def test_finds_secret_and_personal_email(self):
        repo = self.make_repo({"cfg.py": 'k = "ghp_' + "Zx9Qw2Er7Ty4Ui1Op3As5Df8Gh6Jk0Lz2Xc" + '"\n'})
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "me@gmail.com"], cwd=repo, check=True)
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        got = self.score(audit.privacy_checks(repo))
        self.assertFalse(got["secrets"])
        self.assertFalse(got["commit_email"])

    def test_placeholder_contact_in_code_of_conduct(self):
        repo = self.make_repo({"CODE_OF_CONDUCT.md": "Report to [INSERT CONTACT METHOD]."})
        self.assertFalse(self.score(audit.file_checks(repo))["conduct"])


class NameCheckTests(unittest.TestCase):
    def test_taken_registry_means_avoid(self):
        level, _ = name_check.verdict([("crates.io", True, "taken")], 3, [])
        self.assertEqual(level, "AVOID")

    def test_big_github_repo_means_avoid(self):
        level, _ = name_check.verdict([("npm", False, "free")], 2, [("o/x", 5000, "")])
        self.assertEqual(level, "AVOID")

    def test_many_small_repos_means_crowded(self):
        level, _ = name_check.verdict([("npm", False, "free")], 300, [("o/x", 20, "")])
        self.assertEqual(level, "CROWDED")

    def test_free_name_is_good(self):
        level, _ = name_check.verdict([("npm", False, "free")], 3, [("o/x", 4, "")])
        self.assertEqual(level, "GOOD")


class PackageTests(unittest.TestCase):
    def test_package_validates(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_package.py")],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
