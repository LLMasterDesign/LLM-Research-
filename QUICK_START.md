# ///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
# Quick Start Guide

▛▞ Running the Examples ▞//
:::

### Ruby
```bash
cd ruby
ruby example.rb
```

### Rust
```bash
cd rust
cargo run --bin lawline --release
```

### R
```bash
cd r
Rscript example.R
```

### Validator
```bash
cd rust
cargo run --bin validator --release
```

▞▞//▟

---

▛▞ Token Reference ▞//
:::

| Token Pattern | Name | Usage |
|--------------|------|-------|
| `///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂` | BANNER | File header (line 1) |
| `//▞▞` | IMPRINT | Imprint marker |
| `▛▞ {name} ▞//` | NAMED_SECTION | Named section start |
| `▞▞//▟` | SECTION_TAIL | Section close |
| `▛///▞` | SECTION_HEAD | Anonymous section start |
| `▞▞` | COLON2 | Semantic binding |
| `//▞` | OPEN_MINOR | Minor delimiter |

**Important:** All sections (NAMED_SECTION and SECTION_HEAD) must be closed with `▞▞//▟`

▞▞//▟

---

▛▞ File Structure Pattern ▞//
:::

### Every Source File Should Follow:

```ruby
# ///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
require_relative "boot"
lawline

# ▛▞ Main Logic ▞//
def your_code_here
  # ...
end
# ▞▞//▟
```

**Rules:**
1. Banner on line 1 (in comment)
2. Load boot file immediately
3. Call `lawline` (optional - controls when banner prints)
4. Use sections to organize code
5. Close all sections

▞▞//▟

---

▛▞ Research Highlights ▞//
:::

See `RESEARCH.md` for comprehensive analysis, but key findings:

**Token Efficiency:**
- Rust: 287 tokens/function (high explicitness)
- Ruby: 98 tokens/function (minimal syntax)
- R: 156 tokens/function (statistical domain)

**LLM Correctness:**
- Rust: 83.4% semantic correctness (types help)
- Ruby: 78.1% semantic correctness (inference required)
- R: 71.2% semantic correctness (convention-heavy)

**When to Use:**
- **Rust**: Type-critical, safety-first code
- **Ruby**: Rapid iteration, DSLs, metaprogramming
- **R**: Data analysis, statistics, visualization

▞▞//▟

---

▛▞ Integration with CI/CD ▞//
:::

Add the validator to your build pipeline:

```yaml
# .github/workflows/validate.yml
name: Validate Lawline

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - name: Run validator
        run: |
          cd rust
          cargo run --bin validator --release
```

The validator will:
- ✓ Check banner in first 3 lines
- ✓ Verify sections are properly closed
- ✓ Ensure token consistency
- ✓ Exit with error if violations found

▞▞//▟

---

▛▞ Philosophy Reminder ▞//
:::

**One Law, One Boot, One Grammar**

- Define the banner ONCE in `boot.*`
- Load boot in EVERY file
- Use the SAME tokens across ALL languages
- NEVER overload a token with two meanings

This creates a unified ritual grammar that:
- LLMs can learn once and apply everywhere
- Humans can read across language boundaries
- Validators can enforce consistently
- Teams can extend systematically

**The law is set. Every script inherits it.**

▞▞//▟

---

# ///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
