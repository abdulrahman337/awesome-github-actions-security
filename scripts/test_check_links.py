import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_links as cl


class SafetyTests(unittest.TestCase):
    def setUp(self):
        cl.ALLOW_PRIVATE = False

    def test_non_public_addresses_are_refused(self):
        for host in ["127.0.0.1", "localhost", "10.1.2.3", "192.168.0.1", "172.16.5.4", "169.254.169.254",
                     "100.64.0.1", "0.0.0.0", "[::1]", "::ffff:127.0.0.1", "fe80::1", "fc00::1"]:
            self.assertIsNotNone(cl.non_public_reason(host), host)
            with self.assertRaises(cl.UnsafeTarget):
                cl.ensure_public(f"http://{host}/" if ":" not in host or host.startswith("[") else f"http://[{host}]/")

    def test_public_literals_pass_the_lookup_check(self):
        for host in ["8.8.8.8", "1.1.1.1", "2606:4700:4700::1111"]:
            self.assertIsNone(cl.non_public_reason(host), host)

    def test_only_http_and_https_are_followed(self):
        for url in ["file:///etc/passwd", "ftp://example.org/x", "gopher://example.org/", "data:text/plain,hi"]:
            with self.assertRaises(cl.UnsafeTarget):
                cl.ensure_public(url)

    def test_credentials_in_url_are_refused(self):
        with self.assertRaises(cl.UnsafeTarget):
            cl.ensure_public("https://user:pass@8.8.8.8/")

    def test_redirect_to_a_private_address_is_refused(self):
        handler = cl.SafeRedirectHandler()
        request = mock.Mock(full_url="https://8.8.8.8/")
        with self.assertRaises(cl.UnsafeTarget):
            handler.redirect_request(request, None, 302, "Found", {}, "http://169.254.169.254/latest/meta-data/")

    def test_unsafe_link_is_reported_and_not_requested(self):
        with mock.patch.object(cl.OPENER, "open", side_effect=AssertionError("must not connect")):
            status, detail = cl.check("http://127.0.0.1:8080/admin")
        self.assertEqual(status, "UNSAFE")
        self.assertIn("not a public address", detail)

    def test_allow_private_is_an_explicit_opt_in(self):
        cl.ALLOW_PRIVATE = True
        try:
            cl.ensure_public("http://127.0.0.1:8000/")
        finally:
            cl.ALLOW_PRIVATE = False

    def test_dns_failure_is_not_unsafe(self):
        self.assertIsNone(cl.non_public_reason("this-host-does-not-exist.invalid"))


if __name__ == "__main__":
    unittest.main()
