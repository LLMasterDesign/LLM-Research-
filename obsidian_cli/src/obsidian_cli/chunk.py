from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict, Optional
import json
from .config import iter_markdown_files


def _iter_markdown_files(root: Path, include_globs: Optional[List[str]] = None, exclude_globs: Optional[List[str]] = None) -> Iterable[Path]:
    yield from iter_markdown_files(root, include_globs=include_globs, exclude_globs=exclude_globs)


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


def _write_markdown_chunk(out_dir: Path, source: Path, idx: int, title: str, content: str) -> None:
    rel = source.with_suffix("")
    # create a mirrored directory structure under out_dir
    rel_dir = out_dir / rel.parent.name
    rel_dir.mkdir(parents=True, exist_ok=True)
    base = rel.stem
    target = rel_dir / f"{base}__{idx:04d}.md"
    parts: List[str] = []
    parts.append("---\n" + f"source: {str(source)}\nindex: {idx}\n" + "---\n")
    if title:
        parts.append(f"# {title}\n\n")
    parts.append(content.strip() + "\n")
    target.write_text("".join(parts), encoding="utf-8")


def chunk_directory(root: Path, include_globs: Optional[List[str]] = None, exclude_globs: Optional[List[str]] = None, out_path: Path = Path("chunks.jsonl"), out_format: str = "jsonl", strategy: str = "headers", max_chars: int = 1200) -> int:
    total = 0
    if out_format.lower() == "markdown":
        out_dir = out_path
        out_dir.mkdir(parents=True, exist_ok=True)
        for file_path in _iter_markdown_files(root, include_globs=include_globs, exclude_globs=exclude_globs):
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            chunks = _split_by_headers(text) if strategy == "headers" else _split_by_max_chars(text, max_chars=max_chars)
            for idx, ch in enumerate(chunks):
                _write_markdown_chunk(out_dir, file_path, idx, ch.get("title", ""), ch.get("content", ""))
                total += 1
        return total
    # default jsonl
    with out_path.open("w", encoding="utf-8") as fout:
        for file_path in _iter_markdown_files(root, include_globs=include_globs, exclude_globs=exclude_globs):
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            chunks = _split_by_headers(text) if strategy == "headers" else _split_by_max_chars(text, max_chars=max_chars)
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

