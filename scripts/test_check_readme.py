import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_readme as cr

GOOD = """# Awesome Test

## Contents

- [Tools](#tools)
- [Learning](#learning)

## Tools

- [Alpha](https://github.com/example-org/alpha) - Scans things for problems.
- [Beta](https://example.org/beta) - Explains how the scanner works.

## Learning

- [Gamma](https://example.org/gamma/) - Course material for beginners.

## Contributing

Open a pull request.
"""


def messages(findings):
    return [m for _, m in findings]


class EntryTests(unittest.TestCase):
    def test_good_readme_passes(self):
        self.assertEqual(cr.check_entries(GOOD), [])
        self.assertEqual(cr.check_contents(GOOD), [])

    def bad(self, line):
        return messages(cr.check_entries(GOOD.replace("- [Alpha](https://github.com/example-org/alpha) - Scans things for problems.", line)))

    def test_description_rules(self):
        self.assertTrue(any("capital" in m for m in self.bad("- [Alpha](https://example.org/a) - scans things.")))
        self.assertTrue(any("period" in m for m in self.bad("- [Alpha](https://example.org/a) - Scans things")))
        self.assertTrue(any("name of the entry" in m for m in self.bad("- [Alpha](https://example.org/a) - Alpha scans things.")))
        self.assertTrue(any("double" in m for m in self.bad("- [Alpha](https://example.org/a) - Scans  things.")))
        self.assertTrue(any("must look like" in m for m in self.bad("- [Alpha](https://example.org/a): Scans things.")))

    def test_duplicates_are_found_even_with_cosmetic_differences(self):
        text = GOOD.replace("https://example.org/gamma/", "https://www.example.org/gamma")
        text = text.replace("- [Beta](https://example.org/beta)", "- [Beta](https://example.org/gamma)")
        self.assertTrue(any("duplicate" in m for m in messages(cr.check_entries(text))))

    def test_code_blocks_are_ignored(self):
        text = GOOD + "\n```\n- [Bad](http://x) no description\n```\n"
        self.assertEqual(cr.check_entries(text), [])


class ContentsTests(unittest.TestCase):
    def test_missing_and_misordered_sections(self):
        self.assertTrue(cr.check_contents(GOOD.replace("- [Learning](#learning)\n", "")))
        swapped = GOOD.replace("- [Tools](#tools)\n- [Learning](#learning)", "- [Learning](#learning)\n- [Tools](#tools)")
        self.assertTrue(cr.check_contents(swapped))

    def test_wrong_anchor(self):
        self.assertTrue(any("anchor" in m for m in messages(cr.check_contents(GOOD.replace("(#learning)", "(#learn)")))))

    def test_closing_sections_may_stay_out_of_contents(self):
        self.assertEqual(cr.check_contents(GOOD + "\n## Related Lists\n\n- [Other](https://example.org/o) - Another list.\n"), [])


class UrlTests(unittest.TestCase):
    def test_unsafe_or_noisy_urls(self):
        cases = {
            "http://example.org/x": "http",
            "https://bit.ly/abc": "shortener",
            "https://example.org/x?utm_source=list": "tracking",
            "https://example.org/x?fbclid=1": "tracking",
            "https://user:pw@example.org/": "credentials",
            "https://203.0.113.7/page": "raw IP",
            "https://localhost:8000/": "local",
            "https://printer.local/": "local",
            "javascript:alert(1)": "not allowed",
            "data:text/html,hi": "not allowed",
            "file:///etc/passwd": "not allowed",
            "ftp://example.org/x": "not allowed",
        }
        for url, expected in cases.items():
            self.assertTrue(any(expected in p for p in cr.check_url(url)), url)

    def test_clean_urls_pass(self):
        for url in ["https://example.org/", "https://github.com/owner/repo", "https://example.org/a?page=2"]:
            self.assertEqual(cr.check_url(url), [], url)


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "guide.md").write_text("# Guide\n\n## Setup steps\n", encoding="utf-8")
        (self.root / "README.md").write_text(GOOD, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, text):
        return messages(cr.check_links(text, self.root / "README.md", self.root))

    def test_relative_links(self):
        self.assertEqual(self.check("[g](docs/guide.md#setup-steps)\n"), [])
        self.assertTrue(any("missing file" in m for m in self.check("[g](docs/nope.md)\n")))
        self.assertTrue(any("missing heading" in m for m in self.check("[g](docs/guide.md#nope)\n")))
        self.assertTrue(any("leaves the repository" in m for m in self.check("[g](../outside.md)\n")))
        self.assertTrue(any("missing heading" in m for m in self.check("# A\n\n[x](#nope)\n")))

    def test_readme_cannot_link_the_same_target_twice(self):
        self.assertTrue(any("duplicate link" in m for m in self.check("[a](docs/guide.md)\n[b](docs/guide.md)\n")))

    def test_links_in_code_are_ignored(self):
        self.assertEqual(self.check("```\n[x](http://bad)\n```\nand `[y](javascript:1)`\n"), [])


class CharacterTests(unittest.TestCase):
    def test_hidden_characters(self):
        for ch in ["\u202e", "\u200b", "\ufeff", "\u2066", "\u00ad", "\u061c"]:
            self.assertTrue(cr.check_characters(f"safe{ch}text\n"), hex(ord(ch)))

    def test_control_characters(self):
        self.assertTrue(cr.check_characters("text\x1b[31m\n"))
        self.assertTrue(cr.check_characters("text\x00\n"))

    def test_normal_text_including_other_languages_is_fine(self):
        self.assertEqual(cr.check_characters("Plain text, ünïcode and 日本語 and العربية\n"), [])

    def test_whitespace(self):
        self.assertTrue(cr.check_whitespace("a \nb\n", True))
        self.assertTrue(cr.check_whitespace("a\r\nb\r\n", True))
        self.assertTrue(cr.check_whitespace("a\nb", True))
        self.assertTrue(cr.check_whitespace("a\n\tb\n", True))
        self.assertEqual(cr.check_whitespace("a\n\tb\n", False), [])
        self.assertEqual(cr.check_whitespace("a\nb\n", True), [])


class RepositoryTests(unittest.TestCase):
    def test_this_repository_passes(self):
        problems = cr.run(cr.ROOT)
        self.assertEqual(problems, [], "\n".join(f"{p}:{n}: {m}" for p, n, m in problems))

    def test_run_reports_a_planted_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(GOOD.replace("Scans things for problems.", "scans things.\u202e"), encoding="utf-8")
            found = cr.run(root)
            self.assertTrue(any("capital" in m for _, _, m in found))
            self.assertTrue(any("U+202E" in m for _, _, m in found))


if __name__ == "__main__":
    unittest.main()
