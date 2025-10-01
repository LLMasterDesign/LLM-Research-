Obsidian CLI
============

A small CLI to lint and chunk Obsidian Markdown notes.

Quick start
-----------

1. Create venv and install in editable mode:

```bash
cd /workspace/obsidian_cli
. .venv/bin/activate
pip install -e .
```

2. See help:

```bash
obsidian --help
```

3. Lint a vault (auto-detects `.obsidian`):

```bash
obsidian lint /path/to/vault --fix
```

4. Chunk a vault to JSONL:

```bash
obsidian chunk /path/to/vault --out chunks.jsonl
```

