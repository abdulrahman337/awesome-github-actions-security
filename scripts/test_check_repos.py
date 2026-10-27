import sys
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_repos as cr


class FindReposTests(unittest.TestCase):
    def test_finds_and_deduplicates(self):
        text = "[a](https://github.com/Foo/Bar) [b](https://github.com/foo/bar.git) [c](https://github.com/baz/qux/tree/main)"
        self.assertEqual(cr.find_repos(text), ["baz/qux", "Foo/Bar"])

    def test_site_paths_and_odd_names_are_ignored(self):
        text = ("https://github.com/orgs/acme/people https://github.com/topics/security https://github.com/sponsors/x "
                "https://github.com/advisories/GHSA-1 https://github.com/owner/.. https://github.com/-evil/repo "
                "https://github.com/owner/-flag https://github.com/owner/.")
        self.assertEqual(cr.find_repos(text), [])


class TokenSafetyTests(unittest.TestCase):
    def test_token_is_not_stored_in_redirectable_headers(self):
        req = urllib.request.Request("https://api.github.com/repos/o/r")
        req.add_unredirected_header("Authorization", "Bearer secret")
        self.assertNotIn("Authorization", req.headers)
        self.assertIn("Authorization", req.unredirected_hdrs)

    def test_redirects_leave_api_github_com_are_refused(self):
        handler = cr.ApiOnlyRedirects()
        for target in ["https://evil.test/x", "http://api.github.com/x", "https://api.github.com.evil.test/x",
                       "https://github.com/x"]:
            with self.assertRaises(urllib.error.HTTPError, msg=target):
                handler.redirect_request(None, None, 301, "Moved", {}, target)


if __name__ == "__main__":
    unittest.main()
