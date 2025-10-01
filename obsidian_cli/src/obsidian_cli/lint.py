from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, List

from rich.text import Text
from mdformat import plugins
import mdformat


MARKDOWN_FILE_REGEX = re.compile(r"^.*\.md$")


@dataclass
class LintIssue:
    file_path: Path
    line: int
    message: str

    def __str__(self) -> str:  # for console print
        return f"{self.file_path}:{self.line}: {self.message}"


def _iter_markdown_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.md"):
        if ".obsidian" in path.parts:
            continue
        yield path


def _lint_file(contents: str, file_path: Path) -> List[LintIssue]:
    issues: List[LintIssue] = []
    lines = contents.splitlines()
    # Rule: ensure newline at end of file
    if not contents.endswith("\n"):
        issues.append(LintIssue(file_path, max(1, len(lines)), "Missing trailing newline"))

    # Rule: discourage Windows newlines
    if "\r\n" in contents:
        issues.append(LintIssue(file_path, 1, "Contains CRLF newlines; use LF"))

    # Rule: tab indentation discouraged in markdown text blocks
    for idx, line in enumerate(lines, start=1):
        if "\t" in line:
            issues.append(LintIssue(file_path, idx, "Contains tab character"))
            break

    # Rule: consecutive blank lines > 2
    if re.search(r"\n{3,}", contents):
        issues.append(LintIssue(file_path, 1, "Excessive blank lines"))

    return issues


def _apply_fixes(contents: str, file_path: Path) -> str:
    # Normalize newlines to LF
    fixed = contents.replace("\r\n", "\n")
    # Collapse >2 blank lines to 2
    fixed = re.sub(r"\n{3,}", "\n\n", fixed)
    # Format via mdformat with frontmatter/GFM plugins
    md_plugins = ["frontmatter", "gfm"]
    plugins.load_plugins()  # ensure entrypoints
    fixed = mdformat.text(fixed, options={"number": False}, extensions=md_plugins)
    if not fixed.endswith("\n"):
        fixed += "\n"
    return fixed


def lint_directory(root: Path, apply_fixes: bool = False) -> List[Text | str]:
    issues: List[Text | str] = []
    for file_path in _iter_markdown_files(root):
        contents = file_path.read_text(encoding="utf-8", errors="ignore")
        file_issues = _lint_file(contents, file_path)
        if apply_fixes:
            fixed = _apply_fixes(contents, file_path)
            if fixed != contents:
                file_path.write_text(fixed, encoding="utf-8")
        issues.extend(file_issues)
    return issues

