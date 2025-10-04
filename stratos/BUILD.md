# ▛//▞▞ ⟦⎊⟧ :: STRATOS.BUILD.GUIDE ⫸

**Build and installation instructions for the stratos multi-language execution engine.**

---

## Prerequisites

### Required

- **Rust** (1.70+) — For engine.stratos
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```

- **Ruby** (2.7+) — For cloud.stratos
  ```bash
  # Most systems have Ruby pre-installed
  ruby --version
  
  # Install toml-rb gem
  gem install toml-rb
  ```

- **R** (4.0+) — For r.stratos layer
  ```bash
  # Ubuntu/Debian
  sudo apt install r-base
  
  # macOS
  brew install r
  
  # Install required packages
  Rscript -e 'install.packages(c("jsonlite", "digest", "knitr"), repos="https://cloud.r-project.org")'
  ```

### Optional

- **Python** (3.8+) — For adapters
  ```bash
  pip install toml
  ```

---

## Build Engine.Stratos (Rust)

```bash
cd stratos/engine

# Build in release mode
cargo build --release

# Binary will be at: target/release/stratos

# Optional: Install globally
cargo install --path .
```

**Verify:**
```bash
./target/release/stratos --help
```

---

## Setup Cloud.Stratos (Ruby)

```bash
cd stratos/cloud

# Make executable
chmod +x cloud.stratos.rb

# Install dependencies
gem install toml-rb json

# Test
./cloud.stratos.rb list
```

---

## Setup R.Stratos (R)

```bash
cd stratos/r-layer

# Make executable
chmod +x r.stratos.R

# Install R packages
Rscript -e 'install.packages(c("jsonlite", "digest", "knitr"), repos="https://cloud.r-project.org")'

# Test
./r.stratos.R
```

---

## Setup Python Adapter

```bash
cd stratos/adapters

# Install dependencies
pip install toml

# Test
python python_adapter.py
```

---

## Test Installation

### 1. Test Simple Spec (No Auth)

```bash
cd stratos

# Execute simple spec
./engine/target/release/stratos specs/simple.op.toml
```

**Expected output:**
```
▛//▞▞ [⎊] :: ENGINE.STRATOS :: LOADING ⫸
...
⫸ run.shell [test] :: echo 'Simple test successful'
Simple test successful
...
::∎
```

### 2. Test With Auth

First, generate auth key:

```bash
export CODEX_SECRET="my-secret-key"

# Compute auth (ask + boot + seal + secret)
echo -n "///▙⟦⎊⟧::∎my-secret-key" | sha256sum
# Copy the hash
```

Edit `specs/example.op.toml` and replace `auth_key` with your hash.

Then execute:

```bash
CODEX_SECRET="my-secret-key" ./engine/target/release/stratos specs/example.op.toml
```

### 3. Test Ruby Layer

```bash
cd cloud
./cloud.stratos.rb store -k test -v "Hello from cloud"
./cloud.stratos.rb recall -k test
./cloud.stratos.rb list
```

### 4. Test R Layer

```bash
cd r-layer

# Convert example spec to JSON first (engine does this)
# For testing, create a simple JSON:
cat > /tmp/test.json << 'EOF'
{
  "ritual": {
    "ask": "///▙",
    "boot": "⟦⎊⟧",
    "seal": "::∎"
  },
  "meta": {
    "name": "Test",
    "version": "v1",
    "operator": "TEST"
  },
  "kernel": {
    "purpose": ["test"]
  },
  "plan": []
}
EOF

./r.stratos.R validate /tmp/test.json
```

---

## Integration with Docker

Add to `docker-compose.yml`:

```yaml
  stratos:
    build: ./stratos/engine
    container_name: codex_stratos
    depends_on:
      - postgres
      - redis
    environment:
      CODEX_SECRET: ${CODEX_SECRET}
      DATABASE_URL: postgres://codex:changeme@postgres:5432/codexdb
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./stratos:/app/stratos
      - ./work:/app/work
    command: ["sleep", "infinity"]  # Keep running for exec
```

Create `stratos/engine/Dockerfile`:

```dockerfile
FROM rust:1.75-slim as builder

WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    ruby \
    r-base \
    python3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/target/release/stratos /usr/local/bin/
COPY ../cloud/cloud.stratos.rb /usr/local/bin/
COPY ../r-layer/r.stratos.R /usr/local/bin/

RUN chmod +x /usr/local/bin/*.rb /usr/local/bin/*.R

WORKDIR /app
CMD ["stratos"]
```

---

## Troubleshooting

### Rust Build Fails

```bash
# Update Rust
rustup update

# Clean and rebuild
cd stratos/engine
cargo clean
cargo build --release
```

### Ruby Missing TOML

```bash
gem install toml-rb
```

### R Packages Missing

```bash
Rscript -e 'install.packages(c("jsonlite", "digest", "knitr"), repos="https://cloud.r-project.org")'
```

### ⟦⎊⟧ Characters Not Displaying

Ensure your terminal supports UTF-8:
```bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

### Auth Validation Fails

Verify your secret matches:
```bash
export CODEX_SECRET="your-secret"
echo -n "///▙⟦⎊⟧::∎your-secret" | sha256sum
```

Compare output with `auth_key` in your spec.

---

## Development Workflow

1. **Edit spec** in `specs/my-op.toml`
2. **Sign it** (if using auth):
   ```ruby
   require_relative '../cloud/cloud.stratos.rb'
   spec = CloudStratos::SpecBuilder.new
   spec.ritual.sign!("your-secret")
   ```
3. **Execute**:
   ```bash
   CODEX_SECRET="your-secret" stratos specs/my-op.toml
   ```
4. **Check outputs** in `work/`

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `CODEX_SECRET` | Auth validation key | `default-secret` |
| `STRATOS_ENGINE` | Path to Rust binary | `auto-detect` |
| `STRATOS_WORK_DIR` | Working directory | `work/` |

---

## Next Steps

- Read: [STRATOS-DSL.md](STRATOS-DSL.md) for DSL reference
- See: [../specs/](../specs/) for more examples
- Integrate: [../bot/stratos_executor.py](../bot/stratos_executor.py) for Telegram

---

**▛//▞▞ ⟦⎊⟧ :: Build complete. Engine ready. Execute with confidence. ⫸**

::∎
