from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional
import fnmatch
import yaml


DEFAULT_INCLUDE = ["**/*.md"]
DEFAULT_EXCLUDE = [
    "**/.obsidian/**",
    ".obsidian/**",
    "**/.git/**",
    "**/node_modules/**",
    "**/.trash/**",
]


@dataclass
class Config:
    include: List[str] = field(default_factory=lambda: list(DEFAULT_INCLUDE))
    exclude: List[str] = field(default_factory=lambda: list(DEFAULT_EXCLUDE))
    chunk_strategy: str = "headers"  # or "tokens"
    max_chars: int = 1200
    chunk_format: str = "jsonl"  # or "markdown"


def _find_config_file(explicit: Optional[Path], root: Path) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    for name in ("obsidian.yml", "obsidian.yaml", ".obsidian-cli.yml", ".obsidian-cli.yaml"):
        candidate = root / name
        if candidate.exists():
            return candidate
    return None


def load_config(root: Path, config_path: Optional[Path] = None) -> Config:
    cfg = Config()
    cfg_file = _find_config_file(config_path, root)
    if not cfg_file:
        return cfg
    data = yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
    include = data.get("include")
    exclude = data.get("exclude")
    if isinstance(include, list):
        cfg.include = [str(x) for x in include]
    if isinstance(exclude, list):
        # Always ensure built-in exclusions remain unless user overrides fully
        cfg.exclude = [str(x) for x in exclude] or list(DEFAULT_EXCLUDE)
    if "chunk" in data and isinstance(data["chunk"], dict):
        c = data["chunk"]
        cfg.chunk_strategy = str(c.get("strategy", cfg.chunk_strategy))
        cfg.max_chars = int(c.get("max_chars", cfg.max_chars))
        cfg.chunk_format = str(c.get("format", cfg.chunk_format))
    return cfg


def iter_markdown_files(root: Path, include_globs: Optional[List[str]] = None, exclude_globs: Optional[List[str]] = None) -> Iterable[Path]:
    include = include_globs or DEFAULT_INCLUDE
    exclude = exclude_globs or DEFAULT_EXCLUDE
    seen: set[Path] = set()
    for pattern in include:
        for path in root.rglob(pattern):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if any(fnmatch.fnmatch(rel, ex) for ex in exclude):
                continue
            if path.suffix.lower() != ".md":
                continue
            if path in seen:
                continue
            seen.add(path)
            yield path

