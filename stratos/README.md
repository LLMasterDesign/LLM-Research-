# ▛//▞▞ ⟦⎊⟧ :: STRATOS.ENGINE :: MULTI.LANGUAGE.RUNTIME ⫸

**Domain-specific language execution engine for Codex operations**

---

## What is Stratos?

Stratos is a multi-language execution engine that allows you to define and run operations using a declarative DSL. It integrates:

- **Rust** (engine.stratos) — Core runtime, fast and strict
- **Ruby** (cloud.stratos) — Orchestration and templating
- **R** (r.stratos) — Analysis and document generation
- **Python** (adapters) — Integration with Telegram and other systems

### Key Features

✅ **Ritual Validation** — Uses ⟦⎊⟧ as authentication token  
✅ **Multi-Language** — Choose the right tool for each layer  
✅ **Declarative** — Define what, not how  
✅ **Drift-Locked** — Structure prevents prompt decay  
✅ **Telegram Integration** — Execute from bot commands  

---

## Quick Start

### 1. Build Engine

```bash
cd engine
cargo build --release
```

### 2. Run Example

```bash
./engine/target/release/stratos specs/simple.op.toml
```

### 3. Test All Layers

```bash
# Ruby
./cloud/cloud.stratos.rb list

# R
./r-layer/r.stratos.R

# Python
python adapters/python_adapter.py
```

---

## File Structure

```
stratos/
├── engine/              # Rust runtime (engine.stratos)
│   ├── src/
│   │   ├── lib.rs      # Core library
│   │   └── main.rs     # CLI executable
│   └── Cargo.toml
│
├── cloud/               # Ruby orchestration (cloud.stratos)
│   └── cloud.stratos.rb
│
├── r-layer/             # R analysis (r.stratos)
│   └── r.stratos.R
│
├── adapters/            # Language bridges
│   └── python_adapter.py
│
├── specs/               # Example operation specs
│   ├── example.op.toml
│   └── simple.op.toml
│
├── BUILD.md             # Build instructions
├── STRATOS-DSL.md       # DSL reference
└── README.md            # This file
```

---

## Architecture

```
Telegram User
    ↓
Python Adapter (bot integration)
    ↓
┌──────────────┬──────────────┬──────────────┐
│ engine       │ cloud        │ r-layer      │
│ (Rust)       │ (Ruby)       │ (R)          │
│              │              │              │
│ • Validate   │ • Template   │ • Analyze    │
│ • Execute    │ • Orchestrate│ • Report     │
│ • Strict     │ • Memory     │ • Validate   │
└──────────────┴──────────────┴──────────────┘
    ↓              ↓              ↓
Postgres        Redis         Filesystem
```

---

## Operation Spec Format

Operations are defined in TOML with four sections:

```toml
[ritual]   # Auth and ceremony
[meta]     # Metadata
[kernel]   # Execution laws
[[plan]]   # Steps to execute
```

**Example:**

```toml
[ritual]
ask = "///▙"
boot = "⟦⎊⟧"
seal = "::∎"

[meta]
name = "Hello.World"
version = "v1"
operator = "USER"

[kernel]
purpose = ["test.engine"]
rules = ["execute.safely"]
identity = ["test"]
structure = ["sequential"]
motion = ["stdout"]

[[plan]]
type = "shell"
id = "hello"
cmd = "echo 'Hello from Stratos!'"
```

---

## Security: ⟦⎊⟧ as Auth

The ⟦⎊⟧ marker serves dual purpose:

1. **Visual Ceremony** — Signals ritual operation
2. **Auth Token** — Part of validation hash

### How It Works

- Specs can include an `auth_key` in the `[ritual]` section
- Key is SHA256 of: `ask + boot + seal + secret`
- Engine validates hash before execution
- ⟦⎊⟧ breaks weak parsers (intentional "load testing")
- Only signed specs with valid key execute

### Example

Generate auth key:
```bash
export CODEX_SECRET="my-secret"
echo -n "///▙⟦⎊⟧::∎my-secret" | sha256sum
```

Add to spec:
```toml
[ritual]
ask = "///▙"
boot = "⟦⎊⟧"
seal = "::∎"
auth_key = "a8c7e3d4f9b2a1c5e8d6f3b9a4c7e2d8f5b3a6c9e4d7f2b8a5c3e6d9f4b7a2c5"
```

Execute:
```bash
CODEX_SECRET="my-secret" stratos myop.toml
```

---

## Step Types

| Type | Purpose | Language |
|------|---------|----------|
| `shell` | Execute commands | System |
| `llm` | Call language model | API |
| `ruby` | Run Ruby script | Ruby |
| `r` | Run R analysis | R |
| `validate` | Check conditions | Engine |
| `store` | Save to context | Engine |
| `recall` | Retrieve from context | Engine |

---

## Integration Examples

### From Telegram Bot

```python
from stratos_executor import get_executor

executor = get_executor()
result = await executor.shell_op("ls -la", operator="USER")
print(result['output'])
```

### From Ruby

```ruby
require_relative 'cloud/cloud.stratos'

spec = CloudStratos::SpecBuilder.new
  .meta(name: "Test", version: "v1", operator: "RUBY")
  .shell(id: "test", cmd: "echo 'test'")
  .sign("my-secret")
  .save("test.toml")

executor = CloudStratos::Executor.new
executor.execute("test.toml")
```

### From Python

```python
from python_adapter import StratosEngine

engine = StratosEngine(secret="my-secret")
success, output = engine.execute("myop.toml")
```

---

## Layer Responsibilities

### Engine.Stratos (Rust)
- **Core execution** — Run specs with strict validation
- **Auth validation** — Verify ritual markers
- **Context management** — Store/recall between steps
- **Error handling** — Safe failure and recovery

### Cloud.Stratos (Ruby)
- **Spec templating** — Build ops programmatically
- **Memory layer** — Inter-layer data storage (TTL, JSON)
- **Orchestration** — Coordinate multi-step workflows
- **Rapid iteration** — Fast prototyping

### R.Stratos (R)
- **Analysis** — Statistical computation
- **Reporting** — Generate markdown/PDF with tables
- **Validation** — V8SL spec validation
- **Data QA** — Quality checks and summaries

### Python Adapter
- **Bot integration** — Telegram command bridge
- **Quick ops** — Simple operation builders
- **Memory access** — Cloud.stratos memory interface
- **Report generation** — Trigger R layer

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `CODEX_SECRET` | Auth validation key | `default-secret` |
| `STRATOS_ENGINE` | Path to Rust binary | auto-detect |
| `STRATOS_WORK_DIR` | Working directory | `work/` |

---

## Documentation

- **[BUILD.md](BUILD.md)** — Build and installation
- **[STRATOS-DSL.md](STRATOS-DSL.md)** — Complete DSL reference
- **[specs/](specs/)** — Example operation specs

---

## Use Cases

### 1. Automated Workflows
Define repeatable operations that run on schedule or trigger.

### 2. Data Pipelines
ETL operations with validation and reporting.

### 3. Bot Commands
Execute complex multi-step operations from Telegram.

### 4. CI/CD Integration
Run validated build/deploy operations.

### 5. Analysis Automation
Scheduled data analysis with R + reporting.

---

## Roadmap

- [ ] WebAssembly compilation for browser execution
- [ ] GraphQL API for remote execution
- [ ] Visual spec builder (web UI)
- [ ] More step types (http, database, etc.)
- [ ] Parallel execution support
- [ ] Conditional branching
- [ ] Loop constructs

---

## Contributing

Stratos uses drift-lock principles:

1. Preserve ritual structure
2. Maintain auth validation
3. Keep TOML as spec format
4. Document all changes

---

## License

Part of the Codex Memory system. Use for personal and educational purposes.

---

**▛//▞▞ ⟦⎊⟧ :: Multi-language execution. Ritual validation. Drift-locked stability. ⫸**

::∎
