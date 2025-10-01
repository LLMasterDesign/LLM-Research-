from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict
import json


def _iter_markdown_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.md"):
        if ".obsidian" in path.parts:
            continue
        yield path


def _split_by_headers(text: str) -> List[Dict[str, str]]:
    chunks: List[Dict[str, str]] = []
    current_title = ""
    current_lines: List[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            if current_lines:
                chunks.append({"title": current_title, "content": "\n".join(current_lines).strip()})
                current_lines = []
            current_title = line.lstrip("# ").strip()
        else:
            current_lines.append(line)
    if current_lines:
        chunks.append({"title": current_title, "content": "\n".join(current_lines).strip()})
    return [c for c in chunks if c["content"]]


def _split_by_max_chars(text: str, max_chars: int) -> List[Dict[str, str]]:
    parts: List[Dict[str, str]] = []
    buf: List[str] = []
    size = 0
    for line in text.splitlines():
        if size + len(line) + 1 > max_chars and buf:
            parts.append({"title": "", "content": "\n".join(buf).strip()})
            buf = []
            size = 0
        buf.append(line)
        size += len(line) + 1
    if buf:
        parts.append({"title": "", "content": "\n".join(buf).strip()})
    return [p for p in parts if p["content"]]


def chunk_directory(root: Path, out_path: Path, strategy: str = "headers", max_chars: int = 1200) -> int:
    total = 0
    with out_path.open("w", encoding="utf-8") as fout:
        for file_path in _iter_markdown_files(root):
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            if strategy == "headers":
                chunks = _split_by_headers(text)
            else:
                chunks = _split_by_max_chars(text, max_chars=max_chars)
            for idx, ch in enumerate(chunks):
                record = {
                    "file": str(file_path),
                    "index": idx,
                    "title": ch.get("title", ""),
                    "content": ch.get("content", ""),
                }
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                total += 1
    return total

