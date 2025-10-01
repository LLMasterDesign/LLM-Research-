#!/usr/bin/env python3
"""
Markdown Chunker for Obsidian
Intelligently splits large markdown files into manageable chunks
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
import frontmatter
from rich.console import Console
import click

console = Console()


class MarkdownChunker:
    def __init__(self, max_chars=4000, max_tokens=1000):
        self.max_chars = max_chars
        self.max_tokens = max_tokens  # Approximate token count
    
    def estimate_tokens(self, text: str) -> int:
        """Rough estimation: ~4 chars per token"""
        return len(text) // 4
    
    def chunk_by_headers(self, content: str, metadata: Dict = None) -> List[Dict]:
        """Chunk content by headers while respecting size limits"""
        chunks = []
        lines = content.split('\n')
        
        current_chunk = []
        current_headers = []
        current_size = 0
        
        header_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        
        for line in lines:
            match = header_pattern.match(line)
            
            if match:
                # New header found
                level = len(match.group(1))
                title = match.group(2)
                
                # Update header stack
                current_headers = current_headers[:level-1] + [title]
                
                # Check if we need to flush current chunk
                if current_size > self.max_chars:
                    if current_chunk:
                        chunks.append({
                            'content': '\n'.join(current_chunk),
                            'headers': current_headers.copy(),
                            'size': current_size,
                            'tokens': self.estimate_tokens('\n'.join(current_chunk))
                        })
                        current_chunk = []
                        current_size = 0
            
            current_chunk.append(line)
            current_size += len(line) + 1  # +1 for newline
        
        # Add remaining content
        if current_chunk:
            chunks.append({
                'content': '\n'.join(current_chunk),
                'headers': current_headers.copy(),
                'size': current_size,
                'tokens': self.estimate_tokens('\n'.join(current_chunk))
            })
        
        return chunks
    
    def chunk_by_paragraphs(self, content: str) -> List[Dict]:
        """Chunk content by paragraphs when no headers are present"""
        chunks = []
        paragraphs = re.split(r'\n\s*\n', content)
        
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            if current_size + para_size > self.max_chars and current_chunk:
                chunks.append({
                    'content': '\n\n'.join(current_chunk),
                    'size': current_size,
                    'tokens': self.estimate_tokens('\n\n'.join(current_chunk))
                })
                current_chunk = []
                current_size = 0
            
            current_chunk.append(para)
            current_size += para_size + 2  # +2 for \n\n
        
        if current_chunk:
            chunks.append({
                'content': '\n\n'.join(current_chunk),
                'size': current_size,
                'tokens': self.estimate_tokens('\n\n'.join(current_chunk))
            })
        
        return chunks
    
    def chunk_file(self, file_path: Path, method='auto') -> List[Dict]:
        """Chunk a markdown file using specified method"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
        except Exception as e:
            console.print(f"[red]Error reading {file_path}: {e}[/red]")
            return []
        
        # Parse frontmatter
        try:
            post = frontmatter.loads(raw_content)
            metadata = post.metadata
            content = post.content
        except:
            metadata = {}
            content = raw_content
        
        # Determine chunking method
        if method == 'auto':
            # Check if content has headers
            if re.search(r'^#{1,6}\s+', content, re.MULTILINE):
                method = 'headers'
            else:
                method = 'paragraphs'
        
        # Chunk the content
        if method == 'headers':
            chunks = self.chunk_by_headers(content, metadata)
        else:
            chunks = self.chunk_by_paragraphs(content)
        
        # Add metadata to each chunk
        for i, chunk in enumerate(chunks):
            chunk['index'] = i
            chunk['total'] = len(chunks)
            chunk['source_file'] = str(file_path)
            chunk['metadata'] = metadata
        
        return chunks
    
    def save_chunks(self, chunks: List[Dict], output_dir: Path, base_name: str):
        """Save chunks to separate files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for chunk in chunks:
            filename = f"{base_name}_chunk_{chunk['index']+1:03d}_of_{chunk['total']:03d}.md"
            output_file = output_dir / filename
            
            # Build content with metadata
            content_parts = []
            
            # Add frontmatter
            if chunk['metadata']:
                content_parts.append('---')
                for key, value in chunk['metadata'].items():
                    content_parts.append(f'{key}: {value}')
                content_parts.append(f'chunk_index: {chunk["index"]+1}')
                content_parts.append(f'chunk_total: {chunk["total"]}')
                content_parts.append(f'source_file: {chunk["source_file"]}')
                content_parts.append('---')
                content_parts.append('')
            
            # Add chunk navigation
            content_parts.append(f'> Chunk {chunk["index"]+1} of {chunk["total"]}')
            if chunk.get('headers'):
                content_parts.append(f'> Path: {" → ".join(chunk["headers"])}')
            content_parts.append('')
            
            # Add content
            content_parts.append(chunk['content'])
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content_parts))
            
            console.print(f"  [green]✓[/green] {filename} ({chunk['size']} chars, ~{chunk['tokens']} tokens)")


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output directory')
@click.option('--max-chars', default=4000, help='Maximum characters per chunk')
@click.option('--method', type=click.Choice(['auto', 'headers', 'paragraphs']), default='auto', help='Chunking method')
@click.option('--save/--no-save', default=False, help='Save chunks to files')
def main(input_path, output, max_chars, method, save):
    """Chunk markdown files for better processing"""
    input_path = Path(input_path)
    chunker = MarkdownChunker(max_chars=max_chars)
    
    # Find files to chunk
    if input_path.is_file():
        files = [input_path]
    else:
        files = list(input_path.rglob('*.md'))
    
    console.print(f"\n[bold]Processing {len(files)} file(s)...[/bold]\n")
    
    total_chunks = 0
    
    for file in files:
        chunks = chunker.chunk_file(file, method=method)
        
        if not chunks:
            continue
        
        console.print(f"\n[bold cyan]{file.name}[/bold cyan]")
        console.print(f"  Original size: {file.stat().st_size} bytes")
        console.print(f"  Chunks created: {len(chunks)}")
        
        total_chunks += len(chunks)
        
        if save:
            if output:
                output_dir = Path(output) / file.stem
            else:
                output_dir = file.parent / f"{file.stem}_chunks"
            
            chunker.save_chunks(chunks, output_dir, file.stem)
        else:
            # Just display chunk info
            for chunk in chunks:
                header_path = " → ".join(chunk.get('headers', ['(no headers)']))
                console.print(f"    Chunk {chunk['index']+1}: {chunk['size']} chars (~{chunk['tokens']} tokens) - {header_path}")
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Files processed: {len(files)}")
    console.print(f"  Total chunks: {total_chunks}")
    
    if save:
        console.print(f"\n[bold green]✓ Chunks saved to output directory[/bold green]")
    else:
        console.print(f"\n[dim]Use --save to write chunks to files[/dim]")


if __name__ == '__main__':
    main()
