# prompt-lint

Local-first CLI to lint prompt templates. Checks for undefined `{{variables}}`,
template length, and clarity hints. Everything runs locally — no keys, no
network, no data leaves your machine.

Built and maintained by **Asdale Dynamics, LLC** (Indiana), beginner-friendly
AI education and practical open-source tools.

## Install

```bash
pip install .
```

Or, for editable installs while developing:

```bash
pip install -e .
```

## Usage

```bash
prompt-lint template.txt
```

### Options

| Option | Meaning |
|--------|---------|
| `template` | Path to the prompt template file to lint (required) |
| `--vars NAME,NAME` | Comma-separated list of defined variable names |
| `--vars-file FILE` | File with one variable name per line (comments start with `#`) |
| `--min-len N` | Warn if template is shorter than N characters |
| `--max-len N` | Warn if template is longer than N characters |
| `--json` | Emit findings as JSON |

### Exit codes

- `0` — template is clean
- `1` — lint findings found
- `2` — file read or usage error

## Example

`template.txt`:

```
Write a {{tone}} summary of {{topic}} in {{length}} words.
```

Defined variables: `tone`, `topic`

```bash
prompt-lint template.txt --vars tone,topic
template.txt:error [undefined-variable]:30:5: Undefined variable {{ length }} used in template
template.txt:hint [clarity]: Template is very short; consider adding more detail and instructions
```

## Rules

- **undefined-variable** — `{{variable}}` references that are not in the defined set (error)
- **length** — template shorter than `--min-len` or longer than `--max-len` (warn)
- **clarity** — very short templates or vague words like "stuff", "things", "maybe" (hint)

All processing is local. No secrets, API keys, or personal data are collected or transmitted.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
