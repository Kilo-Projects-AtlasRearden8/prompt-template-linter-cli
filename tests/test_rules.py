"""Tests for the prompt-lint lint rules."""

from __future__ import annotations

import unittest

from prompt_linter.lint import (
    clarity_hints,
    find_variables,
    lint,
    length_check,
    undefined_variables,
)


class TestFindVariables(unittest.TestCase):
    def test_finds_variables_in_order(self):
        template = "Hi {{name}}, your {{item}} is ready."
        self.assertEqual(find_variables(template), ["name", "item"])

    def test_handles_whitespace_inside_braces(self):
        template = "{{  name  }} and {{item}}"
        self.assertEqual(find_variables(template), ["name", "item"])

    def test_ignores_invalid_variable_names(self):
        template = "{{123bad}} {{-dash}} {{ok_name}}"
        self.assertEqual(find_variables(template), ["ok_name"])

    def test_no_variables(self):
        self.assertEqual(find_variables("plain text here"), [])


class TestUndefinedVariables(unittest.TestCase):
    def test_reports_undefined(self):
        findings = undefined_variables("Hi {{name}}", ["user"])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule, "undefined-variable")
        self.assertEqual(findings[0].severity, "error")
        self.assertIn("name", findings[0].message)

    def test_no_findings_when_all_defined(self):
        findings = undefined_variables("{{a}} {{b}}", ["a", "b"])
        self.assertEqual(findings, [])

    def test_duplicates_reported_each_time(self):
        findings = undefined_variables("{{x}} and {{x}}", [])
        self.assertEqual(len(findings), 2)

    def test_records_line_and_column(self):
        template = "line one\n{{missing}}\n"
        findings = undefined_variables(template, [])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 2)


class TestLengthCheck(unittest.TestCase):
    def test_too_short(self):
        findings = length_check("short", min_len=10)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule, "length")
        self.assertEqual(findings[0].severity, "warn")

    def test_too_long(self):
        findings = length_check("x" * 100, max_len=10)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "warn")

    def test_within_bounds(self):
        findings = length_check("exactly five", min_len=1, max_len=100)
        self.assertEqual(findings, [])

    def test_no_bounds_means_no_findings(self):
        self.assertEqual(length_check("anything at all"), [])


class TestClarityHints(unittest.TestCase):
    def test_short_template(self):
        findings = clarity_hints("Hi there.")
        self.assertTrue(any(f.rule == "clarity" for f in findings))

    def test_long_enough_template(self):
        findings = clarity_hints(
            "Please write a clear and detailed summary of the meeting notes provided above."
        )
        short = [f for f in findings if "very short" in f.message]
        self.assertEqual(short, [])

    def test_vague_words(self):
        findings = clarity_hints("Do some stuff with things.")
        messages = " ".join(f.message for f in findings)
        self.assertIn("stuff", messages)
        self.assertIn("things", messages)

    def test_no_hints_for_good_template(self):
        findings = clarity_hints(
            "Write a detailed summary of the quarterly sales report in plain English."
        )
        self.assertEqual(findings, [])


class TestLint(unittest.TestCase):
    def test_runs_all_rules(self):
        template = "{{missing}}"
        findings = lint(template, defined=[])
        self.assertTrue(any(f.rule == "undefined-variable" for f in findings))
        self.assertTrue(any(f.rule == "clarity" for f in findings))

    def test_clean_template(self):
        template = (
            "Write a detailed summary of the quarterly sales report in plain English."
        )
        findings = lint(template, defined=[])
        self.assertEqual(findings, [])

    def test_defined_variables_suppress_errors(self):
        findings = lint("Hello {{name}}", defined=["name"])
        self.assertFalse(any(f.rule == "undefined-variable" for f in findings))


if __name__ == "__main__":
    unittest.main()
