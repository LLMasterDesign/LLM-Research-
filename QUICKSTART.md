# Quick Start Guide

## Setup (1 minute)

```bash
# Install dependencies
pip install -r requirements.txt
```

## Put Your Obsidian Notes Here

Copy your Obsidian markdown files to the `notes/` directory:

```bash
# Example: Copy your existing vault
cp -r /path/to/your/obsidian/vault/* notes/

# Or create some test notes
mkdir -p notes
echo -e "---\ntitle: My First Note\ntags: [example]\n---\n\n# My First Note\n\nThis is a [[link]] to another note." > notes/first-note.md
```

## Run Your First Scan

```bash
# Quick scan to see what needs fixing
make scan

# Or use the tool directly
python obsidian-tools/organizer.py notes/ --action scan
```

## Common Tasks

### 1. Clean Up Your Vault

```bash
# See what's wrong
make scan

# Find duplicates
make duplicates

# Find orphaned files
make orphans

# Find broken links
make broken-links
```

### 2. Lint Your Files

```bash
# Basic linting
make lint

# Strict mode (more warnings)
make lint-strict
```

### 3. Organize Files

```bash
# Preview organization by tags (safe, no changes)
make organize

# Actually organize (moves files!)
make organize-execute
```

### 4. Add Frontmatter

```bash
# Adds standardized frontmatter to all files
make add-frontmatter
```

### 5. Chunk Large Files

```bash
# Preview chunks
python obsidian-tools/chunker.py notes/large-file.md

# Save chunks to files
python obsidian-tools/chunker.py notes/large-file.md --save --output ./chunks
```

## Recommended First Steps

1. **Backup your vault first!** (Copy to safe location)
2. Run `make scan` to see current state
3. Fix broken links manually or create missing notes
4. Run `make add-frontmatter` to standardize metadata
5. Run `make lint` regularly to maintain quality

## Tips

- All organize commands default to **dry-run** mode (safe preview)
- Use `--execute` flag when you're ready to make actual changes
- Start with small subsets to test before running on entire vault
- Keep your vault in git for version control

## Need Help?

See the main [README.md](README.md) for detailed documentation.
