"""Integration tests for the prompt-lint CLI."""

from __future__ import annotations

import io
import os
import tempfile
import unittest

from prompt_linter.cli import main


def _write_template(content: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(content)
    return path


class TestCliIntegration(unittest.TestCase):
    def _run(self, *args):
        return main(list(args))

    def test_clean_template_exits_zero(self):
        path = _write_template(
            "Write a detailed summary of the quarterly sales report in plain English."
        )
        try:
            code = self._run(path)
            self.assertEqual(code, 0)
        finally:
            os.remove(path)

    def test_undefined_variable_exits_one(self):
        path = _write_template("Hello {{name}}")
        try:
            code = self._run(path)
            self.assertEqual(code, 1)
        finally:
            os.remove(path)

    def test_defined_variable_suppresses_error(self):
        path = _write_template(
            "Hello {{name}}, here is a detailed summary of your recent results."
        )
        try:
            code = self._run(path, "--vars", "name")
            self.assertEqual(code, 0)
        finally:
            os.remove(path)

    def test_missing_file_exits_two(self):
        code = self._run("/tmp/kilo/does-not-exist-12345.txt")
        self.assertEqual(code, 2)

    def test_min_len_warns(self):
        path = _write_template("Hi")
        try:
            code = self._run(path, "--min-len", "50")
            self.assertEqual(code, 1)
        finally:
            os.remove(path)

    def test_json_output(self):
        path = _write_template("{{missing}}")
        try:
            captured = io.StringIO()
            # main prints to sys.stdout; replace it temporarily.
            import sys

            old_stdout = sys.stdout
            sys.stdout = captured
            try:
                code = self._run(path, "--json")
            finally:
                sys.stdout = old_stdout
            self.assertEqual(code, 1)
            out = captured.getvalue()
            self.assertIn("undefined-variable", out)
            self.assertIn("missing", out)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
