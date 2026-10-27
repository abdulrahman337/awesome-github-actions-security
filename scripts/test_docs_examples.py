import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHA_PIN = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}(\s+#.*)?$")


def yaml_blocks(path):
    return re.findall(r"```ya?ml\n(.*?)```", path.read_text(encoding="utf-8"), re.S)


def uses_lines(text):
    return [m.group(1).strip() for m in re.finditer(r"^\s*-?\s*uses:\s*(.+)$", text, re.M)]


class SecureExampleTests(unittest.TestCase):
    """The example people are told to copy must itself follow the advice in this list."""

    def example(self):
        blocks = yaml_blocks(ROOT / "docs" / "SECURE_WORKFLOW_EXAMPLE.md")
        self.assertEqual(len(blocks), 1)
        return blocks[0]

    def test_every_action_is_pinned_to_a_full_commit_sha_with_a_version_comment(self):
        lines = uses_lines(self.example())
        self.assertTrue(lines)
        for line in lines:
            self.assertRegex(line, SHA_PIN, line)
            self.assertIn("# v", line, line)

    def test_no_dangerous_trigger_and_least_privilege(self):
        text = self.example()
        self.assertNotIn("pull_request_target", re.sub(r"#.*", "", text))
        self.assertRegex(text, r"(?m)^permissions:\s*\{\}")
        self.assertRegex(text, r"(?m)^    permissions:\n      contents: read")
        self.assertIn("persist-credentials: false", text)
        self.assertRegex(text, r"timeout-minutes:\s*\d+")

    def test_untrusted_values_never_appear_inside_run_scripts(self):
        text = self.example()
        for match in re.finditer(r"run:\s*(\|[^\n]*\n(?:\s+.*\n?)+|.*)", text):
            self.assertNotRegex(match.group(1), r"\$\{\{\s*github\.(event|head_ref)", match.group(1))

    def test_plain_scalars_do_not_contain_a_colon_and_space(self):
        # "run: echo \"Branch: $X\"" is invalid YAML because a plain scalar cannot contain ": ".
        for line in self.example().splitlines():
            m = re.match(r"^\s*(?:-\s+)?[\w-]+:\s+([^\"'|>#\s{[].*)$", line)
            if m:
                self.assertNotIn(": ", re.sub(r"\s+#.*$", "", m.group(1)), line)


class VulnerableExamplesTests(unittest.TestCase):
    def test_every_yaml_snippet_in_the_docs_is_valid_after_a_basic_check(self):
        for path in sorted((ROOT / "docs").glob("*.md")):
            for block in yaml_blocks(path):
                for line in block.splitlines():
                    m = re.match(r"^\s*(?:-\s+)?[\w-]+:\s+([^\"'|>#\s{[].*)$", line)
                    if m:
                        value = re.sub(r"\s+#.*$", "", m.group(1))
                        self.assertNotIn(": ", value, f"{path.name}: {line}")


if __name__ == "__main__":
    unittest.main()
