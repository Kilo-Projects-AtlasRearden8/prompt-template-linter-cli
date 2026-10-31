"""Command-line interface for the prompt template linter."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable

from .lint import lint


def parse_vars(raw: str | None) -> list[str]:
    if not raw:
        return []
    parts: list[str] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if chunk:
            parts.append(chunk)
    return parts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prompt-lint",
        description=(
            "Lint prompt templates locally: undefined {{variables}}, length, "
            "and clarity hints."
        ),
    )
    parser.add_argument("template", help="Path to the prompt template file")
    parser.add_argument(
        "--vars",
        dest="vars",
        default="",
        help="Comma-separated defined variable names",
    )
    parser.add_argument(
        "--vars-file",
        help="File with one variable name per line (comments start with #)",
    )
    parser.add_argument(
        "--min-len",
        type=int,
        default=0,
        help="Minimum template length in characters",
    )
    parser.add_argument(
        "--max-len",
        type=int,
        default=None,
        help="Maximum template length in characters",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output findings as JSON",
    )
    return parser


def read_defined_vars(args: argparse.Namespace) -> list[str]:
    defined: list[str] = list(parse_vars(args.vars))
    if args.vars_file:
        with open(args.vars_file, "r", encoding="utf-8") as handle:
            for line in handle:
                name = line.strip()
                if name and not name.startswith("#"):
                    defined.append(name)
    return defined


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        with open(args.template, "r", encoding="utf-8") as handle:
            template = handle.read()
    except OSError as exc:
        print(f"error: cannot read {args.template}: {exc}", file=sys.stderr)
        return 2

    try:
        defined = read_defined_vars(args)
    except OSError as exc:
        print(f"error: cannot read {args.vars_file}: {exc}", file=sys.stderr)
        return 2

    findings = lint(
        template,
        defined=defined,
        min_len=args.min_len,
        max_len=args.max_len,
    )

    if args.json:
        output = [
            {
                "rule": finding.rule,
                "message": finding.message,
                "line": finding.line,
                "column": finding.column,
                "severity": finding.severity,
            }
            for finding in findings
        ]
        print(json.dumps(output, indent=2))
    else:
        if not findings:
            print(f"{args.template}: clean")
        else:
            for finding in findings:
                print(f"{args.template}:{finding}")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
