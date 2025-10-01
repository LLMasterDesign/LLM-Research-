import os
import sys
from pathlib import Path
import click
from rich.console import Console
from .config import load_config

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
@click.option("--config", "config_path", type=click.Path(path_type=Path), help="Optional YAML config file")
@click.option("--include", multiple=True, help="Include glob(s), defaults to **/*.md")
@click.option("--exclude", multiple=True, help="Exclude glob(s), defaults exclude .obsidian, .git, node_modules")
@click.option("--fix", is_flag=True, help="Apply fixes like formatting")
@click.option("--report", "report_path", type=click.Path(path_type=Path), help="Write lint report JSONL to path")
def lint(path: Path | None, config_path: Path | None, include: tuple[str, ...], exclude: tuple[str, ...], fix: bool, report_path: Path | None) -> None:
    """Lint markdown notes in a vault or directory."""
    root = find_vault_path(path)
    console.log(f"Lint target: {root}")
    try:
        from .lint import lint_directory
    except Exception as exc:  # pragma: no cover
        console.print(f"[red]Failed to import lint module: {exc}")
        sys.exit(2)
    cfg = load_config(root, config_path)
    include_globs = list(include) if include else cfg.include
    exclude_globs = list(exclude) if exclude else cfg.exclude
    issues = lint_directory(root, apply_fixes=fix, include_globs=include_globs, exclude_globs=exclude_globs, report_path=report_path)
    if issues:
        for issue in issues:
            console.print(issue)
        sys.exit(1)
    console.print("[green]No issues found")


@main.command()
@click.argument("path", required=False, type=click.Path(path_type=Path))
@click.option("--config", "config_path", type=click.Path(path_type=Path), help="Optional YAML config file")
@click.option("--include", multiple=True, help="Include glob(s), defaults to **/*.md")
@click.option("--exclude", multiple=True, help="Exclude glob(s), defaults exclude .obsidian, .git, node_modules")
@click.option("--out", "out_path", type=click.Path(path_type=Path), default=Path("chunks.jsonl"))
@click.option("--format", "out_format", type=click.Choice(["jsonl", "markdown"], case_sensitive=False), default="jsonl")
@click.option("--strategy", type=click.Choice(["headers", "tokens"], case_sensitive=False), default="headers")
@click.option("--max-chars", type=int, default=1200, help="Max chunk size for token strategy")
def chunk(path: Path | None, config_path: Path | None, include: tuple[str, ...], exclude: tuple[str, ...], out_path: Path, out_format: str, strategy: str, max_chars: int) -> None:
    """Chunk markdown notes to JSONL."""
    root = find_vault_path(path)
    console.log(f"Chunk target: {root}")
    try:
        from .chunk import chunk_directory
    except Exception as exc:  # pragma: no cover
        console.print(f"[red]Failed to import chunk module: {exc}")
        sys.exit(2)
    cfg = load_config(root, config_path)
    include_globs = list(include) if include else cfg.include
    exclude_globs = list(exclude) if exclude else cfg.exclude
    num = chunk_directory(root, include_globs=include_globs, exclude_globs=exclude_globs, out_path=out_path, out_format=out_format, strategy=strategy, max_chars=max_chars)
    console.print(f"[green]Wrote {num} chunks to {out_path}")

