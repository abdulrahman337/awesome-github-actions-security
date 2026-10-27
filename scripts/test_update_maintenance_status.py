import datetime
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import update_maintenance_status as ums


class SafeCellTests(unittest.TestCase):
    def test_table_and_markdown_syntax_cannot_come_through(self):
        hostile = "v1 | [click](https://evil.test) <img src=x onerror=1> `x` *b* _i_ ~s~"
        cleaned = ums.safe_cell(hostile)
        for ch in "|[]<>`*_~":
            self.assertNotIn(ch, cleaned)

    def test_entities_are_decoded_before_cleaning(self):
        self.assertEqual(ums.safe_cell("v1.2 &lt;beta&gt; &amp; more"), "v1.2 beta & more")

    def test_control_characters_and_newlines_are_removed(self):
        self.assertEqual(ums.safe_cell("a\x1b[31mred\r\nline\x00"), "a31mred line")

    def test_length_is_limited(self):
        self.assertEqual(len(ums.safe_cell("x" * 500)), 30)


class ParsingTests(unittest.TestCase):
    COMMITS = "<feed><updated>2026-10-01T10:00:00Z</updated><entry><updated>2026-09-30T00:00:00Z</updated></entry></feed>"
    RELEASES = ("<feed><entry><updated>2026-10-02T09:00:00Z</updated><title>v2.0.0 | [x](https://evil.test)</title></entry>"
                "<entry><updated>2026-01-01T00:00:00Z</updated><title>v1</title></entry></feed>")

    def test_commit_date(self):
        self.assertEqual(ums.parse_commit_date(self.COMMITS), datetime.date(2026, 10, 1))

    def test_bad_or_missing_dates_are_none(self):
        self.assertIsNone(ums.parse_commit_date("<updated>not-a-date</updated>"))
        self.assertIsNone(ums.parse_commit_date(""))
        self.assertEqual(ums.parse_release("<entry><updated>nope</updated><title>x</title></entry>"), (None, None))

    def test_release_title_is_cleaned(self):
        date, title = ums.parse_release(self.RELEASES)
        self.assertEqual(date, datetime.date(2026, 10, 2))
        self.assertNotIn("|", title)
        self.assertNotIn("](", title)

    def test_nightly_builds_are_summarised(self):
        feed = "<entry><updated>2026-10-02T09:00:00Z</updated><title>Nightly 2026-10-02</title></entry>"
        self.assertEqual(ums.parse_release(feed)[1], "nightly builds")


class RedirectTests(unittest.TestCase):
    def test_redirect_away_from_github_is_refused(self):
        import urllib.error
        handler = ums.GithubOnlyRedirects()
        with self.assertRaises(urllib.error.HTTPError):
            handler.redirect_request(None, None, 302, "Found", {}, "https://evil.test/feed.atom")
        with self.assertRaises(urllib.error.HTTPError):
            handler.redirect_request(None, None, 302, "Found", {}, "http://github.com/x/y/commits.atom")


if __name__ == "__main__":
    unittest.main()
