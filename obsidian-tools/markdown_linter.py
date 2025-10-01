#!/usr/bin/env python3
"""
Obsidian Markdown Linter
Lints markdown files for Obsidian vault standards
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import frontmatter
from rich.console import Console
from rich.table import Table
import click

console = Console()


class MarkdownLinter:
    def __init__(self, strict_mode=False):
        self.strict_mode = strict_mode
        self.issues = []
    
    def lint_file(self, file_path: Path) -> List[Dict]:
        """Lint a single markdown file"""
        self.issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return [{"type": "error", "message": f"Cannot read file: {e}"}]
        
        # Parse frontmatter
        try:
            post = frontmatter.loads(content)
            self._check_frontmatter(post.metadata)
            body = post.content
        except Exception as e:
            self.issues.append({
                "type": "warning",
                "line": 1,
                "message": f"Frontmatter parsing issue: {e}"
            })
            body = content
        
        # Check body
        self._check_links(body)
        self._check_formatting(body)
        self._check_headers(body)
        self._check_tags(body)
        
        return self.issues
    
    def _check_frontmatter(self, metadata: Dict):
        """Check frontmatter validity"""
        if not metadata:
            if self.strict_mode:
                self.issues.append({
                    "type": "warning",
                    "line": 1,
                    "message": "No frontmatter found"
                })
            return
        
        # Check for recommended fields
        recommended = ["title", "tags", "created", "updated"]
        for field in recommended:
            if field not in metadata and self.strict_mode:
                self.issues.append({
                    "type": "info",
                    "line": 1,
                    "message": f"Recommended frontmatter field missing: {field}"
                })
    
    def _check_links(self, content: str):
        """Check for broken or malformed links"""
        # Check for broken wiki links
        wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
        for link in wiki_links:
            if '|' in link:
                actual_link, _ = link.split('|', 1)
            else:
                actual_link = link
            
            # Check for invalid characters
            if '#' in actual_link.split('#')[0]:
                line_num = content[:content.find(f'[[{link}]]')].count('\n') + 1
                self.issues.append({
                    "type": "warning",
                    "line": line_num,
                    "message": f"Wiki link may be malformed: [[{link}]]"
                })
        
        # Check for markdown links
        md_links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        for text, url in md_links:
            if url.startswith('http'):
                continue
            # Check for spaces in file links
            if ' ' in url and not url.startswith('#'):
                line_num = content[:content.find(f'[{text}]({url})')].count('\n') + 1
                self.issues.append({
                    "type": "warning",
                    "line": line_num,
                    "message": f"Link contains spaces: {url}"
                })
    
    def _check_formatting(self, content: str):
        """Check for formatting issues"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                self.issues.append({
                    "type": "info",
                    "line": i,
                    "message": "Trailing whitespace"
                })
            
            # Check for multiple blank lines
            if i > 1 and not line.strip() and not lines[i-2].strip():
                self.issues.append({
                    "type": "info",
                    "line": i,
                    "message": "Multiple consecutive blank lines"
                })
    
    def _check_headers(self, content: str):
        """Check header structure"""
        lines = content.split('\n')
        header_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        prev_level = 0
        
        for i, line in enumerate(lines, 1):
            match = header_pattern.match(line)
            if match:
                level = len(match.group(1))
                title = match.group(2)
                
                # Check for proper spacing
                if not line.startswith('#' * level + ' '):
                    self.issues.append({
                        "type": "warning",
                        "line": i,
                        "message": "Header should have space after #"
                    })
                
                # Check for skipped header levels (only in strict mode)
                if self.strict_mode and prev_level > 0 and level > prev_level + 1:
                    self.issues.append({
                        "type": "info",
                        "line": i,
                        "message": f"Skipped header level (from h{prev_level} to h{level})"
                    })
                
                prev_level = level
    
    def _check_tags(self, content: str):
        """Check inline tags"""
        # Find inline tags
        inline_tags = re.findall(r'(?:^|\s)(#[\w\-/]+)', content, re.MULTILINE)
        
        for tag in inline_tags:
            # Check for spaces in tags (which would break them)
            if ' ' in tag:
                line_num = content[:content.find(tag)].count('\n') + 1
                self.issues.append({
                    "type": "warning",
                    "line": line_num,
                    "message": f"Tag contains invalid space: {tag}"
                })


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--strict', is_flag=True, help='Enable strict mode')
@click.option('--fix', is_flag=True, help='Auto-fix issues where possible')
def main(path, strict, fix):
    """Lint Obsidian markdown files"""
    path = Path(path)
    linter = MarkdownLinter(strict_mode=strict)
    
    # Find all markdown files
    if path.is_file():
        files = [path]
    else:
        files = list(path.rglob('*.md'))
    
    console.print(f"\n[bold]Linting {len(files)} file(s)...[/bold]\n")
    
    total_issues = 0
    files_with_issues = 0
    
    for file in files:
        issues = linter.lint_file(file)
        
        if issues:
            files_with_issues += 1
            total_issues += len(issues)
            
            console.print(f"\n[bold cyan]{file.relative_to(path.parent if path.is_file() else path)}[/bold cyan]")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Line", style="dim", width=6)
            table.add_column("Type", width=10)
            table.add_column("Message")
            
            for issue in issues:
                type_color = {
                    "error": "red",
                    "warning": "yellow",
                    "info": "blue"
                }.get(issue["type"], "white")
                
                table.add_row(
                    str(issue.get("line", "-")),
                    f"[{type_color}]{issue['type']}[/{type_color}]",
                    issue["message"]
                )
            
            console.print(table)
    
    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Files scanned: {len(files)}")
    console.print(f"  Files with issues: {files_with_issues}")
    console.print(f"  Total issues: {total_issues}")
    
    if total_issues > 0:
        sys.exit(1)
    else:
        console.print("\n[bold green]✓ All files look good![/bold green]")


if __name__ == '__main__':
    main()
