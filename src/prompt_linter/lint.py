"""Lint rules for prompt templates.

All processing is local. No data is sent anywhere.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

VARIABLE_RE = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")

# Heuristic clarity hints. Beginner-friendly, never medical advice.
VAGUE_WORDS = (
    "stuff",
    "things",
    "something",
    "anything",
    "maybe",
    "perhaps",
    "some",
    "a few",
    "several",
)

SHORT_TEMPLATE_WORDS = 10


@dataclass(frozen=True)
class Finding:
    rule: str
    message: str
    line: int | None = None
    column: int | None = None
    severity: str = "hint"

    def __str__(self) -> str:
        location = ""
        if self.line is not None:
            location = f":{self.line}"
            if self.column is not None:
                location += f":{self.column}"
        return f"{self.severity} [{self.rule}]{location}: {self.message}"


def find_variables(template: str) -> list[str]:
    """Return variable names referenced in {{variable}} syntax, in order of appearance."""
    return [match.group(1) for match in VARIABLE_RE.finditer(template)]


def undefined_variables(template: str, defined: Iterable[str]) -> list[Finding]:
    """Find {{variables}} used in the template that are not defined."""
    defined_set = set(defined)
    findings: list[Finding] = []
    for match in VARIABLE_RE.finditer(template):
        name = match.group(1)
        if name not in defined_set:
            line = template.count("\n", 0, match.start()) + 1
            column = match.start() - template.rfind("\n", 0, match.start())
            findings.append(
                Finding(
                    rule="undefined-variable",
                    message=f"Undefined variable {{ {name} }} used in template",
                    line=line,
                    column=column,
                    severity="error",
                )
            )
    return findings


def length_check(
    template: str, min_len: int = 0, max_len: int | None = None
) -> list[Finding]:
    """Check template length (character count) against bounds."""
    findings: list[Finding] = []
    length = len(template)
    if min_len and length < min_len:
        findings.append(
            Finding(
                rule="length",
                message=(
                    f"Template is too short: {length} characters (minimum {min_len})"
                ),
                severity="warn",
            )
        )
    if max_len is not None and length > max_len:
        findings.append(
            Finding(
                rule="length",
                message=(
                    f"Template is too long: {length} characters (maximum {max_len})"
                ),
                severity="warn",
            )
        )
    return findings


def clarity_hints(template: str) -> list[Finding]:
    """Heuristic hints to make prompts clearer for beginners."""
    findings: list[Finding] = []
    words = template.split()
    if len(words) < SHORT_TEMPLATE_WORDS:
        findings.append(
            Finding(
                rule="clarity",
                message=(
                    "Template is very short; consider adding more detail and instructions"
                ),
                severity="hint",
            )
        )
    lowered = template.lower()
    for word in VAGUE_WORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", lowered):
            findings.append(
                Finding(
                    rule="clarity",
                    message=f"Vague word '{word}' detected; try being more specific",
                    severity="hint",
                )
            )
    return findings


def lint(
    template: str,
    defined: Iterable[str] = (),
    min_len: int = 0,
    max_len: int | None = None,
) -> list[Finding]:
    """Run all lint rules on a template."""
    findings: list[Finding] = []
    findings.extend(undefined_variables(template, defined))
    findings.extend(length_check(template, min_len, max_len))
    findings.extend(clarity_hints(template))
    return findings
