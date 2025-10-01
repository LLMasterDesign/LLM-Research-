import os
import sys
from pathlib import Path
import click
from rich.console import Console

console = Console()


def find_vault_path(path: Path | None) -> Path:
    if path is not None:
        return path
    # search upwards for .obsidian
    current = Path.cwd()
    for candidate in [current] + list(current.parents):
        if (candidate / ".obsidian").exists():
            return candidate
    return current


@click.group()
@click.version_option()
def main() -> None:
    """Obsidian utilities: lint and chunk markdown notes."""


@main.command()
@click.argument("path", required=False, type=click.Path(path_type=Path))
@click.option("--fix", is_flag=True, help="Apply fixes like formatting")
def lint(path: Path | None, fix: bool) -> None:
    """Lint markdown notes in a vault or directory."""
    root = find_vault_path(path)
    console.log(f"Lint target: {root}")
    try:
        from .lint import lint_directory
    except Exception as exc:  # pragma: no cover
        console.print(f"[red]Failed to import lint module: {exc}")
        sys.exit(2)
    issues = lint_directory(root, apply_fixes=fix)
    if issues:
        for issue in issues:
            console.print(issue)
        sys.exit(1)
    console.print("[green]No issues found")


@main.command()
@click.argument("path", required=False, type=click.Path(path_type=Path))
@click.option("--out", "out_path", type=click.Path(path_type=Path), default=Path("chunks.jsonl"))
@click.option("--strategy", type=click.Choice(["headers", "tokens"], case_sensitive=False), default="headers")
@click.option("--max-chars", type=int, default=1200, help="Max chunk size for token strategy")
def chunk(path: Path | None, out_path: Path, strategy: str, max_chars: int) -> None:
    """Chunk markdown notes to JSONL."""
    root = find_vault_path(path)
    console.log(f"Chunk target: {root}")
    try:
        from .chunk import chunk_directory
    except Exception as exc:  # pragma: no cover
        console.print(f"[red]Failed to import chunk module: {exc}")
        sys.exit(2)
    num = chunk_directory(root, out_path=out_path, strategy=strategy, max_chars=max_chars)
    console.print(f"[green]Wrote {num} chunks to {out_path}")

