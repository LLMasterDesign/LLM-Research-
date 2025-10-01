# Obsidian Vault Management Tools

A comprehensive suite of Python tools to lint, organize, and chunk your Obsidian markdown files.

## 🚀 Features

- **Markdown Linter** - Validate markdown files for Obsidian best practices
- **File Chunker** - Split large files into manageable chunks for processing
- **Vault Organizer** - Clean up, find duplicates, broken links, and organize by tags

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Make tools executable (optional)
chmod +x obsidian-tools/*.py
```

## 🛠️ Tools

### 1. Markdown Linter

Checks your markdown files for common issues:
- Missing or invalid frontmatter
- Broken wiki-style links `[[link]]`
- Malformed markdown links
- Header structure issues
- Trailing whitespace
- Tag formatting

**Usage:**

```bash
# Lint a single file
python obsidian-tools/markdown_linter.py path/to/file.md

# Lint entire vault
python obsidian-tools/markdown_linter.py /path/to/vault

# Strict mode (more warnings)
python obsidian-tools/markdown_linter.py --strict /path/to/vault
```

**Example Output:**
```
Linting 45 file(s)...

notes/My Note.md
┏━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Line ┃ Type     ┃ Message                          ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ warning  │ No frontmatter found             │
│ 15   │ warning  │ Wiki link may be malformed       │
│ 23   │ info     │ Trailing whitespace              │
└──────┴──────────┴───────────────────────────────────┘
```

### 2. File Chunker

Intelligently splits large markdown files into smaller chunks while preserving context.

**Features:**
- Chunk by headers (preserves document structure)
- Chunk by paragraphs (for unstructured content)
- Preserves frontmatter metadata
- Estimates token counts
- Adds navigation breadcrumbs

**Usage:**

```bash
# Analyze without saving
python obsidian-tools/chunker.py /path/to/large-file.md

# Save chunks to files
python obsidian-tools/chunker.py /path/to/large-file.md --save

# Custom chunk size and output directory
python obsidian-tools/chunker.py /path/to/vault \
  --max-chars 2000 \
  --output ./chunks \
  --save

# Force paragraph-based chunking
python obsidian-tools/chunker.py file.md --method paragraphs --save
```

**Example Output:**
```
Processing 3 file(s)...

Large Document.md
  Original size: 45230 bytes
  Chunks created: 8
  ✓ Large Document_chunk_001_of_008.md (3950 chars, ~987 tokens)
  ✓ Large Document_chunk_002_of_008.md (4100 chars, ~1025 tokens)
  ...
```

### 3. Vault Organizer

Analyzes and organizes your Obsidian vault.

**Features:**
- Find duplicate files
- Identify orphaned notes (no incoming links)
- Detect broken wiki links
- Organize files by tags
- Add/update frontmatter
- Dry-run mode (safe preview)

**Usage:**

```bash
# Scan vault for issues
python obsidian-tools/organizer.py /path/to/vault --action scan

# Find duplicates
python obsidian-tools/organizer.py /path/to/vault --action duplicates

# Find orphaned files
python obsidian-tools/organizer.py /path/to/vault --action orphans

# Find broken links
python obsidian-tools/organizer.py /path/to/vault --action broken-links

# Organize files by tags (dry run)
python obsidian-tools/organizer.py /path/to/vault --action organize-tags

# Actually move files (execute mode)
python obsidian-tools/organizer.py /path/to/vault --action organize-tags --execute

# Add frontmatter to all files
python obsidian-tools/organizer.py /path/to/vault --action add-frontmatter --execute
```

**Example Output:**
```
Obsidian Vault Organizer
Vault: /Users/me/Documents/Obsidian
Mode: DRY RUN

Scanning vault...

Found 3 duplicate file names:
  • Meeting Notes.md
    - work/Meeting Notes.md
    - archive/Meeting Notes.md

Found 12 orphaned files (no incoming links)
  • Random Thought.md
  • Old Draft.md
  ...

Found 5 broken links in 3 files
  • projects/Project A.md
    - [[Non-existent Note]]
    - [[Deleted File]]

Files by tags:
┏━━━━━━━━━━━━━┳━━━━━━━┓
┃ Tag         ┃ Count ┃
┡━━━━━━━━━━━━━╇━━━━━━━┩
│ work        │    45 │
│ personal    │    32 │
│ untagged    │    18 │
└─────────────┴───────┘
```

## 📁 Directory Structure

```
/workspace
├── obsidian-tools/          # Tool scripts
│   ├── markdown_linter.py   # Linter
│   ├── chunker.py           # Chunker
│   └── organizer.py         # Organizer
├── notes/                   # Your Obsidian notes go here
├── templates/               # Template files
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🎯 Workflow Recommendations

### Initial Cleanup
1. **Scan your vault** to identify issues:
   ```bash
   python obsidian-tools/organizer.py notes/ --action scan
   ```

2. **Fix broken links** manually or create missing notes

3. **Add frontmatter** to standardize metadata:
   ```bash
   python obsidian-tools/organizer.py notes/ --action add-frontmatter --execute
   ```

4. **Organize by tags** if desired:
   ```bash
   python obsidian-tools/organizer.py notes/ --action organize-tags --execute
   ```

### Regular Maintenance
1. **Lint before committing** changes:
   ```bash
   python obsidian-tools/markdown_linter.py notes/
   ```

2. **Review orphans** periodically:
   ```bash
   python obsidian-tools/organizer.py notes/ --action orphans
   ```

### Working with Large Files
1. **Chunk large documents** for LLM processing:
   ```bash
   python obsidian-tools/chunker.py notes/large-doc.md --save --output ./chunks
   ```

## 🔧 Advanced Configuration

### Frontmatter Standards

Recommended frontmatter fields:
```yaml
---
title: Note Title
tags: [tag1, tag2]
created: 2025-01-15T10:30:00
updated: 2025-01-20T15:45:00
---
```

### Integration with Git

Add to your `.git/hooks/pre-commit`:
```bash
#!/bin/bash
python obsidian-tools/markdown_linter.py notes/ --strict
if [ $? -ne 0 ]; then
    echo "Linting failed. Fix issues before committing."
    exit 1
fi
```

## 📝 Tips

- Start with `--dry-run` mode when using the organizer
- Use `--strict` mode for linting when preparing for publication
- Chunk files before feeding to LLMs (respects context limits)
- Run regular scans to catch broken links early
- Keep frontmatter consistent across your vault

## 🤝 Contributing

Feel free to extend these tools for your specific needs. Common additions:
- Custom linting rules
- Different chunking strategies
- Automated link fixing
- Template generation

## 📄 License

Open source - use as you wish!

---

**Ready to clean up your Obsidian vault?** Start with a scan:
```bash
python obsidian-tools/organizer.py notes/ --action scan
```
