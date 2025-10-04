# ▛//▞▞ ⟦⎊⟧ :: STRATOS.DSL.REFERENCE ⫸

**Domain-Specific Language specification for Codex operation execution.**

---

## Overview

The Stratos DSL is a TOML-based declarative language for defining executable operations with ritual validation. It bridges Telegram, Rust, Ruby, R, and Python.

### Philosophy

- **Declarative** — Define what to do, not how
- **Validated** — Ritual markers enforce authenticity
- **Multi-language** — Use the right tool for each layer
- **Drift-locked** — Structure prevents prompt decay

---

## File Structure

Every op spec has four sections:

```toml
[ritual]   # Authentication and ceremony
[meta]     # Operation metadata
[kernel]   # Execution laws and structure
[[plan]]   # Sequential execution steps
```

---

## [ritual] Section

Defines authentication markers and validation.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ask` | string | Yes | Opening marker (e.g., `///▙`) |
| `boot` | string | Yes | Boot marker (e.g., `⟦⎊⟧` or `[⎊]`) |
| `seal` | string | Yes | Closing marker (e.g., `::∎`) |
| `auth_key` | string | No | SHA256 hash for validation |

### Auth Key

The `auth_key` is computed as:
```
SHA256(ask + boot + seal + secret)
```

**Example:**
```toml
[ritual]
ask = "///▙"
boot = "⟦⎊⟧"
seal = "::∎"
auth_key = "a8c7e3d4f9b2a1c5e8d6f3b9a4c7e2d8f5b3a6c9e4d7f2b8a5c3e6d9f4b7a2c5"
```

### ⟦⎊⟧ vs [⎊]

- **⟦⎊⟧** — Full Unicode ritual marker (preferred)
- **[⎊]** — ASCII-safe fallback

Both work. ⟦⎊⟧ provides additional "load testing" by breaking weak parsers.

### Unsigned Rituals

Omit `auth_key` for unsigned operations:
```toml
[ritual]
ask = "///▙"
boot = "[⎊]"
seal = "::∎"
# No auth_key = unsigned, executes without validation
```

---

## [meta] Section

Operation metadata.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Operation name (e.g., `Video.Edit.Op`) |
| `version` | string | Yes | Version (e.g., `v1.0`) |
| `operator` | string | Yes | Who created it (e.g., `RAVEN`) |
| `tags` | array | No | Tags for categorization |

**Example:**
```toml
[meta]
name = "Data.Analysis.Pipeline"
version = "v2.1"
operator = "ANALYST_BOT"
tags = ["analytics", "pipeline", "daily"]
```

---

## [kernel] Section

Defines execution laws and structure (the "operating system" of the op).

### Fields

All fields are string arrays:

| Field | Purpose |
|-------|---------|
| `purpose` | Why this op exists |
| `rules` | Laws governing execution |
| `identity` | Who/what this op represents |
| `structure` | How steps are organized |
| `motion` | What artifacts are produced |

**Example:**
```toml
[kernel]
purpose = ["process.data", "generate.report", "notify.users"]
rules = ["enforce.auth", "validate.inputs", "log.all.actions"]
identity = ["daily.report", "v2", "analytics.team"]
structure = ["sequential", "validated", "idempotent"]
motion = ["csv.output", "pdf.report", "email.notification"]
```

These are documentation fields that also prime the execution context.

---

## [[plan]] Section

Sequential execution steps. Each step is a separate `[[plan]]` block.

### Step Types

1. **shell** — Execute shell commands
2. **llm** — Call language model
3. **ruby** — Run Ruby script
4. **r** — Run R analysis
5. **validate** — Check conditions
6. **store** — Save to context
7. **recall** — Retrieve from context

---

### shell

Execute shell commands.

**Fields:**
- `id` (string, required) — Step identifier
- `cmd` (string, required) — Command to execute
- `cwd` (string, optional) — Working directory

**Example:**
```toml
[[plan]]
type = "shell"
id = "fetch_data"
cmd = "curl -o data.json https://api.example.com/data"
cwd = "work/"
```

**Multi-command:**
```toml
[[plan]]
type = "shell"
id = "setup"
cmd = "mkdir -p output && cd output && git init"
```

---

### llm

Call language model with prompt.

**Fields:**
- `id` (string, required) — Step identifier
- `prompt` (string, required) — Prompt text
- `model` (string, optional) — Model name (e.g., `gpt-4`)
- `max_tokens` (int, optional) — Token limit

**Example:**
```toml
[[plan]]
type = "llm"
id = "summarize"
prompt = """
///▙
⟦⎊⟧

Summarize the following data in 3 bullet points:
{data from previous step}

::∎
"""
model = "gpt-4"
max_tokens = 200
```

**Note:** Prompts should include ritual markers for consistency.

---

### ruby

Execute Ruby script via cloud.stratos.

**Fields:**
- `id` (string, required) — Step identifier
- `script` (string, required) — Ruby code
- `args` (array, optional) — Command-line arguments

**Example:**
```toml
[[plan]]
type = "ruby"
id = "transform_data"
script = """
require 'json'

data = JSON.parse(File.read('work/data.json'))
transformed = data.map { |item| item['value'] * 2 }
puts JSON.pretty_generate(transformed)
"""
```

**With args:**
```toml
[[plan]]
type = "ruby"
id = "process"
script = """
input_file = ARGV[0]
output_file = ARGV[1]
# process files...
"""
args = ["input.csv", "output.csv"]
```

---

### r

Execute R script for analysis.

**Fields:**
- `id` (string, required) — Step identifier
- `script` (string, required) — R code
- `output` (string, optional) — Output file path

**Example:**
```toml
[[plan]]
type = "r"
id = "statistics"
script = """
data <- read.csv('work/data.csv')
summary_stats <- summary(data)
print(summary_stats)
"""
output = "work/stats.txt"
```

---

### validate

Check conditions and fail if not met.

**Fields:**
- `id` (string, required) — Step identifier
- `check` (string, required) — Validation expression
- `on_fail` (string, optional) — Error message

**Check types:**
- `exists:key` — Check if context key exists
- More validators can be added

**Example:**
```toml
[[plan]]
type = "validate"
id = "check_data"
check = "exists:data_loaded"
on_fail = "Data must be loaded before analysis"
```

---

### store

Store value in execution context.

**Fields:**
- `id` (string, required) — Step identifier
- `key` (string, required) — Context key
- `value` (string, required) — Value to store

**Example:**
```toml
[[plan]]
type = "store"
id = "mark_complete"
key = "analysis_done"
value = "true"
```

---

### recall

Retrieve value from execution context.

**Fields:**
- `id` (string, required) — Step identifier
- `key` (string, required) — Context key

**Example:**
```toml
[[plan]]
type = "recall"
id = "get_status"
key = "analysis_done"
```

---

## Execution Flow

1. **Load** — Parse TOML spec
2. **Validate Ritual** — Check auth_key if present
3. **Display Banner** — Show `ask` and `boot`
4. **Execute Plan** — Run steps sequentially
5. **Collect Outputs** — Store in context
6. **Seal** — Display `seal` marker

---

## Context

The execution context holds:
- **store** — Key-value pairs from `store` steps
- **outputs** — Output from each step (by id)
- **errors** — Any errors encountered

Steps can share data via context.

---

## Multi-Language Integration

### From Python (Telegram Bot)

```python
from python_adapter import StratosEngine

engine = StratosEngine(secret="my-secret")
success, output = engine.execute("myop.toml")
```

### From Ruby (Orchestration)

```ruby
require_relative 'cloud.stratos'

executor = CloudStratos::Executor.new
executor.execute("myop.toml")
```

### From R (Analysis)

```r
source('r.stratos.R')
spec <- load_spec('myop.json')  # Converted from TOML
validate_v8sl_spec(spec)
```

---

## Security: Using ⟦⎊⟧ as Auth

The ⟦⎊⟧ marker serves dual purpose:

1. **Visual Ceremony** — Signals ritual operation
2. **Auth Validation** — Part of hash computation

### Why It Works

- Unicode characters like ⟦⎊⟧ break weak parsers
- Only validated specs with correct auth_key execute
- Unauthorized users can't forge the hash without secret
- "Load testing" — weak systems fail at parse time

### Setup

1. Choose a strong secret: `export CODEX_SECRET="your-secret-here"`
2. Compute auth for your spec:
   ```bash
   echo -n "///▙⟦⎊⟧::∎your-secret-here" | sha256sum
   ```
3. Add `auth_key` to spec
4. Distribute spec (auth_key visible but can't be forged)
5. Execute with secret in environment

---

## Best Practices

### 1. Sign Production Specs

Always use `auth_key` for production:
```ruby
spec.sign!("production-secret")
```

### 2. Use Descriptive IDs

```toml
[[plan]]
id = "fetch_user_data"  # Good
id = "step1"            # Bad
```

### 3. Validate Early

Add validation steps after data loading:
```toml
[[plan]]
type = "shell"
id = "load"
cmd = "curl -o data.json https://api/data"

[[plan]]
type = "validate"
id = "check_loaded"
check = "exists:data_loaded"
```

### 4. Document with Kernel

Use kernel fields to explain intent:
```toml
[kernel]
purpose = ["exactly what this op does"]
rules = ["constraints and requirements"]
```

### 5. Wrap LLM Prompts in Ritual

```toml
[[plan]]
type = "llm"
prompt = """
///▙
⟦⎊⟧

Your prompt here...

::∎
"""
```

---

## Examples

### Simple Shell Pipeline

```toml
[ritual]
ask = "///▙"
boot = "[⎊]"
seal = "::∎"

[meta]
name = "Backup.Database"
version = "v1"
operator = "CRON"

[kernel]
purpose = ["backup.postgres"]
rules = ["compress", "timestamp"]
identity = ["backup.job"]
structure = ["sequential"]
motion = ["backup.sql.gz"]

[[plan]]
type = "shell"
id = "dump"
cmd = "pg_dump codexdb > backup.sql"

[[plan]]
type = "shell"
id = "compress"
cmd = "gzip backup.sql"

[[plan]]
type = "shell"
id = "move"
cmd = "mv backup.sql.gz /backups/$(date +%Y%m%d).sql.gz"
```

### Data Analysis Pipeline

```toml
[ritual]
ask = "///▙"
boot = "⟦⎊⟧"
seal = "::∎"
auth_key = "abc123..."

[meta]
name = "Daily.Analysis"
version = "v2.0"
operator = "ANALYTICS_BOT"
tags = ["daily", "report", "automated"]

[kernel]
purpose = ["analyze.daily.metrics", "generate.report"]
rules = ["validate.data", "email.on.complete"]
identity = ["daily.report", "v2"]
structure = ["validated", "sequential"]
motion = ["csv.data", "pdf.report"]

[[plan]]
type = "shell"
id = "fetch"
cmd = "psql -c 'COPY (SELECT * FROM metrics WHERE date = CURRENT_DATE) TO STDOUT WITH CSV HEADER' > daily.csv"

[[plan]]
type = "validate"
id = "check_data"
check = "exists:fetch"

[[plan]]
type = "r"
id = "analyze"
script = """
data <- read.csv('daily.csv')
summary <- summary(data)
write.csv(summary, 'summary.csv')
"""
output = "summary.csv"

[[plan]]
type = "ruby"
id = "report"
script = """
require 'csv'
data = CSV.read('summary.csv')
puts "Report generated with #{data.size} rows"
"""

[[plan]]
type = "store"
id = "complete"
key = "report_done"
value = "true"
```

---

## Appendix: Auth Key Generation

### Bash

```bash
SECRET="my-secret"
echo -n "///▙⟦⎊⟧::∎$SECRET" | sha256sum | cut -d' ' -f1
```

### Ruby

```ruby
require 'digest'
secret = "my-secret"
Digest::SHA256.hexdigest("///▙⟦⎊⟧::∎#{secret}")
```

### Python

```python
import hashlib
secret = "my-secret"
hashlib.sha256(f"///▙⟦⎊⟧::∎{secret}".encode()).hexdigest()
```

### R

```r
library(digest)
secret <- "my-secret"
digest(paste0("///▙⟦⎊⟧::∎", secret), algo = "sha256", serialize = FALSE)
```

---

**▛//▞▞ ⟦⎊⟧ :: DSL complete. Execute with precision. Seal with confidence. ⫸**

::∎
