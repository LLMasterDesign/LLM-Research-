#!/usr/bin/env python3
"""
Obsidian Vault Organizer
Cleans up and organizes Obsidian markdown files
"""

import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import frontmatter
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
import click

console = Console()


class VaultOrganizer:
    def __init__(self, vault_path: Path, dry_run=True):
        self.vault_path = vault_path
        self.dry_run = dry_run
        self.stats = {
            'files_processed': 0,
            'files_moved': 0,
            'files_renamed': 0,
            'duplicates_found': 0,
            'orphans_found': 0,
            'broken_links': 0
        }
    
    def find_duplicates(self) -> Dict[str, List[Path]]:
        """Find duplicate files by name"""
        files_by_name = {}
        
        for md_file in self.vault_path.rglob('*.md'):
            name = md_file.name.lower()
            if name not in files_by_name:
                files_by_name[name] = []
            files_by_name[name].append(md_file)
        
        # Filter to only duplicates
        duplicates = {name: paths for name, paths in files_by_name.items() if len(paths) > 1}
        self.stats['duplicates_found'] = len(duplicates)
        
        return duplicates
    
    def find_orphans(self) -> List[Path]:
        """Find files with no incoming links"""
        all_files = {f.stem for f in self.vault_path.rglob('*.md')}
        linked_files = set()
        
        for md_file in self.vault_path.rglob('*.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                # Find wiki-style links
                wiki_links = re.findall(r'\[\[([^\]]+?)(?:\|[^\]]+)?\]\]', content)
                for link in wiki_links:
                    # Remove section anchors
                    link = link.split('#')[0].strip()
                    if link:
                        linked_files.add(link)
            except:
                pass
        
        orphans = [self.vault_path / f"{name}.md" for name in (all_files - linked_files)
                   if (self.vault_path / f"{name}.md").exists()]
        
        self.stats['orphans_found'] = len(orphans)
        return orphans
    
    def find_broken_links(self) -> Dict[Path, List[str]]:
        """Find broken wiki-style links"""
        broken = {}
        all_files = {f.stem for f in self.vault_path.rglob('*.md')}
        
        for md_file in self.vault_path.rglob('*.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                wiki_links = re.findall(r'\[\[([^\]]+?)(?:\|[^\]]+)?\]\]', content)
                
                file_broken = []
                for link in wiki_links:
                    # Remove section anchors
                    target = link.split('#')[0].strip()
                    if target and target not in all_files:
                        file_broken.append(link)
                
                if file_broken:
                    broken[md_file] = file_broken
            except:
                pass
        
        self.stats['broken_links'] = sum(len(links) for links in broken.values())
        return broken
    
    def organize_by_tags(self) -> Dict[str, List[Path]]:
        """Organize files by their tags"""
        by_tags = {}
        
        for md_file in self.vault_path.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                    tags = post.get('tags', [])
                    
                    if isinstance(tags, str):
                        tags = [tags]
                    
                    if not tags:
                        # Look for inline tags
                        inline_tags = re.findall(r'(?:^|\s)#([\w\-/]+)', post.content, re.MULTILINE)
                        tags = inline_tags[:3]  # Limit to first 3
                    
                    if tags:
                        primary_tag = tags[0] if isinstance(tags, list) else tags
                        if primary_tag not in by_tags:
                            by_tags[primary_tag] = []
                        by_tags[primary_tag].append(md_file)
                    else:
                        if 'untagged' not in by_tags:
                            by_tags['untagged'] = []
                        by_tags['untagged'].append(md_file)
            except:
                if 'untagged' not in by_tags:
                    by_tags['untagged'] = []
                by_tags['untagged'].append(md_file)
        
        return by_tags
    
    def clean_filename(self, name: str) -> str:
        """Clean up filename to Obsidian-friendly format"""
        # Remove special characters
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        # Replace multiple spaces/underscores with single space
        name = re.sub(r'[\s_]+', ' ', name)
        # Remove leading/trailing spaces and dots
        name = name.strip('. ')
        return name
    
    def add_frontmatter(self, file_path: Path):
        """Add or update frontmatter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Add missing fields
            if 'created' not in post.metadata:
                post['created'] = datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
            
            if 'updated' not in post.metadata:
                post['updated'] = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            
            if 'title' not in post.metadata:
                post['title'] = file_path.stem
            
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(frontmatter.dumps(post))
            
            return True
        except Exception as e:
            console.print(f"[red]Error processing {file_path}: {e}[/red]")
            return False
    
    def move_by_tag(self, by_tags: Dict[str, List[Path]]):
        """Move files into folders by tag"""
        for tag, files in by_tags.items():
            # Clean tag name for folder
            folder_name = self.clean_filename(tag)
            target_dir = self.vault_path / folder_name
            
            if not self.dry_run:
                target_dir.mkdir(exist_ok=True)
            
            for file in files:
                if file.parent != target_dir:
                    target_file = target_dir / file.name
                    
                    console.print(f"  Move: {file.relative_to(self.vault_path)} → {target_file.relative_to(self.vault_path)}")
                    
                    if not self.dry_run:
                        shutil.move(str(file), str(target_file))
                    
                    self.stats['files_moved'] += 1


@click.command()
@click.argument('vault_path', type=click.Path(exists=True))
@click.option('--action', type=click.Choice(['scan', 'duplicates', 'orphans', 'broken-links', 'organize-tags', 'add-frontmatter']), 
              default='scan', help='Action to perform')
@click.option('--dry-run/--execute', default=True, help='Show what would be done without making changes')
def main(vault_path, action, dry_run):
    """Organize and clean up Obsidian vault"""
    vault_path = Path(vault_path)
    organizer = VaultOrganizer(vault_path, dry_run=dry_run)
    
    console.print(f"\n[bold]Obsidian Vault Organizer[/bold]")
    console.print(f"Vault: {vault_path}")
    console.print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}\n")
    
    if action == 'scan':
        console.print("[bold]Scanning vault...[/bold]\n")
        
        # Duplicates
        duplicates = organizer.find_duplicates()
        if duplicates:
            console.print(f"[yellow]Found {len(duplicates)} duplicate file names:[/yellow]")
            for name, paths in list(duplicates.items())[:5]:
                console.print(f"  • {name}")
                for path in paths:
                    console.print(f"    - {path.relative_to(vault_path)}")
        
        # Orphans
        orphans = organizer.find_orphans()
        if orphans:
            console.print(f"\n[yellow]Found {len(orphans)} orphaned files (no incoming links)[/yellow]")
            for orphan in orphans[:10]:
                console.print(f"  • {orphan.relative_to(vault_path)}")
        
        # Broken links
        broken = organizer.find_broken_links()
        if broken:
            console.print(f"\n[red]Found {organizer.stats['broken_links']} broken links in {len(broken)} files[/red]")
            for file, links in list(broken.items())[:5]:
                console.print(f"  • {file.relative_to(vault_path)}")
                for link in links[:3]:
                    console.print(f"    - [[{link}]]")
        
        # Organization by tags
        by_tags = organizer.organize_by_tags()
        console.print(f"\n[cyan]Files by tags:[/cyan]")
        table = Table()
        table.add_column("Tag", style="cyan")
        table.add_column("Count", justify="right")
        
        for tag, files in sorted(by_tags.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            table.add_row(tag, str(len(files)))
        
        console.print(table)
    
    elif action == 'duplicates':
        duplicates = organizer.find_duplicates()
        console.print(f"[bold]Duplicate Files Report[/bold]\n")
        
        for name, paths in duplicates.items():
            console.print(f"[yellow]{name}[/yellow]")
            for path in paths:
                console.print(f"  {path.relative_to(vault_path)}")
            console.print()
    
    elif action == 'orphans':
        orphans = organizer.find_orphans()
        console.print(f"[bold]Orphaned Files ({len(orphans)} total)[/bold]\n")
        
        for orphan in orphans:
            console.print(f"  • {orphan.relative_to(vault_path)}")
    
    elif action == 'broken-links':
        broken = organizer.find_broken_links()
        console.print(f"[bold]Broken Links Report[/bold]\n")
        
        for file, links in broken.items():
            console.print(f"[cyan]{file.relative_to(vault_path)}[/cyan]")
            for link in links:
                console.print(f"  • [[{link}]]")
            console.print()
    
    elif action == 'organize-tags':
        by_tags = organizer.organize_by_tags()
        console.print(f"[bold]Organizing files by tags...[/bold]\n")
        organizer.move_by_tag(by_tags)
        
        console.print(f"\n[bold]Files moved: {organizer.stats['files_moved']}[/bold]")
    
    elif action == 'add-frontmatter':
        console.print(f"[bold]Adding/updating frontmatter...[/bold]\n")
        
        for md_file in vault_path.rglob('*.md'):
            if organizer.add_frontmatter(md_file):
                organizer.stats['files_processed'] += 1
                console.print(f"  [green]✓[/green] {md_file.relative_to(vault_path)}")
        
        console.print(f"\n[bold]Files processed: {organizer.stats['files_processed']}[/bold]")
    
    if dry_run:
        console.print("\n[dim]This was a dry run. Use --execute to apply changes.[/dim]")


if __name__ == '__main__':
    main()
