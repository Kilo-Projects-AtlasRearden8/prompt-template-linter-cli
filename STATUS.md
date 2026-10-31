# STATUS.md

## What was built

`prompt-lint` — a local-first Python CLI for linting prompt templates, built for
Asdale Dynamics, LLC. It is a pure standard-library package (no runtime
dependencies) that reads a prompt template file and reports:

- **undefined-variable** (error): `{{variable}}` references not present in the
  defined variable set (`--vars` or `--vars-file`)
- **length** (warn): template shorter than `--min-len` or longer than
  `--max-len` characters
- **clarity** (hint): very short templates (< 10 words) or vague words like
  "stuff", "things", "maybe"

Processing is 100% local: nothing is sent over the network, and no keys or
personal data are collected.

## Project layout

```
prompt-template-linter-cli/
├── LICENSE               MIT, Copyright (c) 2026 Asdale Dynamics, LLC
├── README.md             usage docs, credits Asdale Dynamics, LLC
├── pyproject.toml        packaging + console script `prompt-lint`
├── src/prompt_linter/    package: __init__, lint (rules), cli (argparse)
├── tests/test_rules.py   19 tests covering all lint rules (pytest/unittest)
├── .venv                 local virtualenv (installed, ignored by git)
├── .gitignore
└── STATUS.md             this file
```

## How to run

```bash
# Create and activate the local environment (one-time)
python3 -m venv .venv
.venv/bin/pip install -e .

# Lint a template
.venv/bin/prompt-lint template.txt --vars tone,topic

# With length bounds and JSON output
.venv/bin/prompt-lint template.txt --vars-file vars.txt --min-len 20 --max-len 2000 --json

# Exit codes: 0 clean, 1 findings found, 2 file/usage error
```

## Verification results

- `pip install -e .` builds and installs successfully.
- `python3 -m pytest -q`: **19 passed**.
- Manual CLI checks passed:
  - undefined `{{variable}}` detected with line/column, exit code 1
  - all variables defined → only non-error hints remain
  - `--vars-file` works (one name per line, `#` comments)
  - `--min-len` / `--max-len` produce length warnings
  - `--json` emits a JSON array of findings
  - missing input file → exit code 2 with error message

## Known gaps

- Length is character-based, not token-based.
- Clarity rules are simple heuristics; they flag, they do not rewrite.
- No config file (all rules via CLI flags only); intentional for simplicity.
- No `.github/workflows` files were added, by design.
- No publishing, no remote repository, no network access used at any point.
