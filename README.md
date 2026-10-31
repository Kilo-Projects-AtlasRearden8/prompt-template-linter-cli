# prompt-lint

A friendly, local-first command-line tool that lints prompt templates. It checks
for undefined `{{variables}}`, template length, and clarity hints — everything
runs on your machine. No keys, no network, and none of your prompt text ever
leaves your computer.

Built and maintained by **Asdale Dynamics, LLC** (Indiana), beginner-friendly AI
education and practical open-source tools.

## What it does

If you write prompts with `{{variable}}` placeholders, it's easy to forget to
define one, or to write a prompt so short it won't give useful results.
`prompt-lint` reads your template file and reports three kinds of findings:

| Finding | What it means | Severity |
|---------|---------------|----------|
| `undefined-variable` | A `{{variable}}` is used but not listed as defined | error |
| `length` | Template is shorter than `--min-len` or longer than `--max-len` | warn |
| `clarity` | Template is very short, or uses vague words like "stuff" or "things" | hint |

It prints each finding with the file, line, and column so you can fix it quickly.

## Install

You need Python 3.8 or newer.

### From source (recommended)

```bash
git clone <this-repository>
cd prompt-template-linter-cli
python3 -m venv .venv
.venv/bin/pip install -e .
```

### Activate the environment

Each time you open a new terminal:

```bash
.venv/bin/activate
```

Then the `prompt-lint` command is available.

## Usage — step by step

### 1. Create a template file

`my_template.txt`:

```
Write a {{tone}} summary of {{topic}} in {{length}} words.
```

### 2. Define your variables

Tell the linter which variables you actually provide:

```bash
prompt-lint my_template.txt --vars tone,topic
```

### 3. Read the results

```
my_template.txt:error [undefined-variable]:1:43: Undefined variable {{ length }} used in template
my_template.txt:hint [clarity]: Template is very short; consider adding more detail and instructions
```

The linter found that `{{length}}` is used but never defined (an error), and that
the template is quite short (a hint). Fix it, re-run, and aim for a "clean"
result.

### Options

| Option | What it does |
|--------|--------------|
| `my_template.txt` | Path to the template file (required) |
| `--vars tone,topic` | Comma-separated list of variable names you define |
| `--vars-file vars.txt` | File with one variable name per line (`#` starts a comment) |
| `--min-len 50` | Warn if the template is shorter than 50 characters |
| `--max-len 2000` | Warn if the template is longer than 2000 characters |
| `--json` | Print findings as JSON (useful for other tools) |

### Exit codes

- `0` — template is clean, no findings
- `1` — one or more findings found
- `2` — could not read the template or vars file

## Example with length bounds

```bash
prompt-lint my_template.txt --vars tone,topic,length --min-len 20 --max-len 2000
```

## Local-first, by design

`prompt-lint` uses only Python's standard library. It never sends your prompt
over the network, never asks for an API key, and never collects personal data.
Your prompts stay on your machine.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
