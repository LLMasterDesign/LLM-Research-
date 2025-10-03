import json
import os
import re
import sys
import shutil
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parents[1]
CAPSULES_DIR = ROOT / "capsules"
SCHEMAS_DIR = ROOT / "schemas"
REGISTRY_FILE = ROOT / "registry" / "index.json"

console = Console()


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "item"


def _validate_with_schema(data: dict, schema_name: str) -> Optional[str]:
    try:
        import jsonschema  # type: ignore
    except Exception:
        # Treat as soft warning so CLI remains usable without validator
        return None

    schema_path = SCHEMAS_DIR / schema_name
    if not schema_path.exists():
        return f"Schema not found: {schema_name}"

    schema = _load_json(schema_path)
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:  # type: ignore
        return str(e)
    return None


@click.group()
def cli():
    """ARC.Lab CLI for prompt capsules and lexicons."""


@cli.command()
@click.option("--query", "query", type=str, default="", help="Search text in capsule name, sector, tags")
@click.option("--sector", type=str, default="", help="Filter by sector")
@click.option("--tag", "tags", multiple=True, help="Filter by tag (repeatable)")
def list_capsules(query: str, sector: str, tags: list[str]):
    registry = _load_json(REGISTRY_FILE)
    rows = []
    for item in registry.get("capsules", []):
        if query and query.lower() not in (item.get("name", "") + " " + item.get("sector", "") + " " + " ".join(item.get("tags", []))).lower():
            continue
        if sector and item.get("sector") != sector:
            continue
        if tags and not set(tags).issubset(set(item.get("tags", []))):
            continue
        rows.append(item)

    table = Table(title="ARC.Lab Capsules")
    for col in ["id", "name", "version", "sector", "tags", "path"]:
        table.add_column(col)
    for r in rows:
        table.add_row(
            r.get("id", ""), r.get("name", ""), r.get("version", ""), r.get("sector", ""), ", ".join(r.get("tags", [])), r.get("path", "")
        )
    console.print(table)


@cli.command()
@click.argument("capsule_path", type=click.Path(path_type=Path))
@click.option("--id", "capsule_id", required=True)
@click.option("--name", required=True)
@click.option("--sector", required=True)
@click.option("--version", default="0.1.0")
@click.option("--tag", "tags", multiple=True)
@click.option("--desc", "description", default="")
@click.option("--lexicon", "lexicon_path", type=click.Path(path_type=Path), required=False)
@click.option("--force", is_flag=True, help="Overwrite if exists")
def create_capsule(capsule_path: Path, capsule_id: str, name: str, sector: str, version: str, tags: list[str], description: str, lexicon_path: Optional[Path], force: bool):
    """Create a new capsule JSON file and register it."""
    capsule_path = capsule_path if capsule_path.suffix == ".json" else capsule_path.with_suffix(".json")
    if capsule_path.exists() and not force:
        console.print(f"[red]Refusing to overwrite existing file:[/red] {capsule_path}")
        sys.exit(1)

    capsule = {
        "id": capsule_id,
        "name": name,
        "version": version,
        "sector": sector,
        "description": description,
        "tags": list(tags),
        "prompts": [
            {
                "id": "system",
                "title": "System Primer",
                "role": "system",
                "content": "You are an expert assistant for {sector}.",
                "variables": ["sector"]
            }
        ]
    }

    if lexicon_path and lexicon_path.exists():
        capsule["lexicon"] = str(lexicon_path)

    err = _validate_with_schema(capsule, "capsule.schema.json")
    if err:
        console.print(f"[yellow]Validation warning:[/yellow] {err}")

    _save_json(capsule_path, capsule)
    console.print(f"[green]Created capsule:[/green] {capsule_path}
")

    # Update registry
    registry = _load_json(REGISTRY_FILE) if REGISTRY_FILE.exists() else {"capsules": []}
    # Remove any prior entry with same id
    registry["capsules"] = [c for c in registry.get("capsules", []) if c.get("id") != capsule_id]
    registry["capsules"].append({
        "id": capsule_id,
        "name": name,
        "version": version,
        "sector": sector,
        "tags": list(tags),
        "path": str(capsule_path.relative_to(ROOT))
    })

    err = _validate_with_schema(registry, "registry.schema.json")
    if err:
        console.print(f"[yellow]Registry validation warning:[/yellow] {err}")
    _save_json(REGISTRY_FILE, registry)
    console.print(f"[green]Updated registry:[/green] {REGISTRY_FILE}")


@cli.command()
@click.argument("capsule_path", type=click.Path(path_type=Path))
@click.option("--with-schema", is_flag=True, help="Validate against schema")
@click.option("--show-prompts", is_flag=True, help="Print prompt titles")
@click.option("--resolve-lexicon", is_flag=True, help="Load and summarize external lexicon if referenced")
def inspect_capsule(capsule_path: Path, with_schema: bool, show_prompts: bool, resolve_lexicon: bool):
    """Inspect a capsule JSON file."""
    data = _load_json(capsule_path)

    if with_schema:
        err = _validate_with_schema(data, "capsule.schema.json")
        if err:
            console.print(f"[red]Schema errors:[/red] {err}")
        else:
            console.print("[green]Capsule conforms to schema[/green]")

    table = Table(title=os.fspath(capsule_path))
    for k in ["id", "name", "version", "sector", "tags", "description", "lexicon"]:
        table.add_column(k)
    table.add_row(
        str(data.get("id")), str(data.get("name")), str(data.get("version")), str(data.get("sector")), ", ".join(data.get("tags", [])), str(data.get("description", "")), str(data.get("lexicon", ""))
    )
    console.print(table)

    if show_prompts:
        ptable = Table(title="Prompts")
        ptable.add_column("id"); ptable.add_column("title"); ptable.add_column("role")
        for p in data.get("prompts", []):
            ptable.add_row(p.get("id", ""), p.get("title", ""), p.get("role", ""))
        console.print(ptable)

    if resolve_lexicon and isinstance(data.get("lexicon"), str):
        lex_path = (ROOT / data["lexicon"]).resolve()
        try:
            lex = _load_json(lex_path)
            err = _validate_with_schema(lex, "lexicon.schema.json")
            if err:
                console.print(f"[yellow]Lexicon validation warning:[/yellow] {err}")
            ltable = Table(title=f"Lexicon: {lex.get('name', '')}")
            ltable.add_column("term"); ltable.add_column("pos"); ltable.add_column("power")
            for t in lex.get("terms", [])[:25]:
                ltable.add_row(t.get("term", ""), t.get("pos", ""), str(t.get("power", "")))
            console.print(ltable)
        except FileNotFoundError:
            console.print(f"[red]Lexicon file not found:[/red] {lex_path}")


@cli.command()
@click.option("--query", type=str, required=True)
@click.option("--in", "in_field", type=click.Choice(["term", "pos"]) , default="term")
@click.argument("lexicon_path", type=click.Path(path_type=Path))
def search_lexicon(query: str, in_field: str, lexicon_path: Path):
    """Search a lexicon by term or part-of-speech."""
    lex = _load_json(lexicon_path)
    err = _validate_with_schema(lex, "lexicon.schema.json")
    if err:
        console.print(f"[yellow]Lexicon validation warning:[/yellow] {err}")
    matches = []
    for t in lex.get("terms", []):
        val = t.get(in_field, "")
        if isinstance(val, str) and query.lower() in val.lower():
            matches.append(t)
    table = Table(title=f"Matches for '{query}' in {os.fspath(lexicon_path)}")
    table.add_column("term"); table.add_column("pos"); table.add_column("power")
    for t in matches[:50]:
        table.add_row(t.get("term", ""), t.get("pos", ""), str(t.get("power", "")))
    console.print(table)


@cli.command()
@click.argument("source_path", type=click.Path(path_type=Path))
@click.option("--name", type=str, help="Override lexicon name")
@click.option("--industry", type=str, default="", help="Optional industry tag")
@click.option("--dest", "dest_basename", type=str, help="Optional destination filename (no extension)")
def import_lexicon(source_path: Path, name: Optional[str], industry: str, dest_basename: Optional[str]):
    """Import a lexicon (.json or .txt) into ARC.Lab/lexicons as JSON.

    - For .json, file is validated and copied
    - For .txt, each non-empty line becomes a {term, pos: "phrase"}
    """
    src = source_path
    if not src.exists():
        console.print(f"[red]Source not found:[/red] {src}")
        sys.exit(1)

    lex_dir = ROOT / "lexicons"
    lex_dir.mkdir(parents=True, exist_ok=True)

    if src.suffix.lower() == ".json":
        data = _load_json(src)
        if name:
            data["name"] = name
        if industry:
            data["industry"] = industry
        base = dest_basename or _slugify(data.get("name") or src.stem)
        dest = lex_dir / f"{base}.json"
        err = _validate_with_schema(data, "lexicon.schema.json")
        if err:
            console.print(f"[yellow]Validation warning:[/yellow] {err}")
        _save_json(dest, data)
        console.print(f"[green]Imported lexicon:[/green] {dest}")
    elif src.suffix.lower() == ".txt":
        lines = src.read_text(encoding="utf-8").splitlines()
        terms = []
        for line in lines:
            term = line.strip()
            if not term or term.startswith("#"):
                continue
            terms.append({"term": term, "pos": "phrase", "power": 3})
        lname = name or src.stem
        base = dest_basename or _slugify(lname)
        dest = lex_dir / f"{base}.json"
        data = {"name": lname, "industry": industry, "terms": terms}
        _save_json(dest, data)
        console.print(f"[green]Converted and imported lexicon:[/green] {dest}
First 5 terms: {[t['term'] for t in terms[:5]]}")
    else:
        console.print("[red]Unsupported file type. Use .json or .txt[/red]")
        sys.exit(1)


@cli.command()
@click.argument("capsule_path", type=click.Path(path_type=Path))
def register_capsule(capsule_path: Path):
    """Validate and add an existing capsule to the registry."""
    data = _load_json(capsule_path)
    err = _validate_with_schema(data, "capsule.schema.json")
    if err:
        console.print(f"[yellow]Validation warning:[/yellow] {err}")

    entry = {
        "id": data.get("id", ""),
        "name": data.get("name", ""),
        "version": data.get("version", ""),
        "sector": data.get("sector", ""),
        "tags": data.get("tags", []),
        "path": os.fspath(capsule_path.relative_to(ROOT)) if capsule_path.is_absolute() else os.fspath(capsule_path)
    }
    registry = _load_json(REGISTRY_FILE) if REGISTRY_FILE.exists() else {"capsules": []}
    registry["capsules"] = [c for c in registry.get("capsules", []) if c.get("id") != entry["id"]]
    registry["capsules"].append(entry)
    err = _validate_with_schema(registry, "registry.schema.json")
    if err:
        console.print(f"[yellow]Registry validation warning:[/yellow] {err}")
    _save_json(REGISTRY_FILE, registry)
    console.print(f"[green]Registered capsule:[/green] {entry['id']} -> {REGISTRY_FILE}")


@cli.command()
def validate_registry():
    """Validate registry entries and referenced capsule files."""
    reg = _load_json(REGISTRY_FILE)
    rows = []
    for item in reg.get("capsules", []):
        cpath = (ROOT / item.get("path", "")).resolve()
        status = "ok"
        if not cpath.exists():
            status = "missing"
        else:
            try:
                data = _load_json(cpath)
                err = _validate_with_schema(data, "capsule.schema.json")
                if err:
                    status = "warn"
            except Exception as e:
                status = f"error: {e}"
        rows.append((item.get("id", ""), os.fspath(cpath), status))

    table = Table(title="Registry Validation")
    table.add_column("id"); table.add_column("path"); table.add_column("status")
    for rid, path, status in rows:
        table.add_row(rid, path, status)
    console.print(table)


@cli.command()
@click.argument("capsule_path", type=click.Path(path_type=Path))
@click.argument("lexicon_path", type=click.Path(path_type=Path))
def link_lexicon(capsule_path: Path, lexicon_path: Path):
    """Attach a lexicon file to a capsule (stores relative path)."""
    data = _load_json(capsule_path)
    rel = os.fspath(lexicon_path if not lexicon_path.is_absolute() else lexicon_path.relative_to(ROOT))
    data["lexicon"] = rel
    err = _validate_with_schema(data, "capsule.schema.json")
    if err:
        console.print(f"[yellow]Validation warning:[/yellow] {err}")
    _save_json(capsule_path, data)
    console.print(f"[green]Linked lexicon:[/green] {rel} -> {os.fspath(capsule_path)}")


if __name__ == "__main__":
    cli()
