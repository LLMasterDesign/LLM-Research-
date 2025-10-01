"""
Τ{Raven} - Context Tracker Service
Maintains awareness of workspace state
"""

import os
import logging
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime

from .git_manager import GitManager

logger = logging.getLogger(__name__)


class ContextTracker:
    """Tracks and maintains workspace context."""
    
    def __init__(self, workspace_path: str):
        """
        Initialize Context Tracker.
        
        Args:
            workspace_path: Path to workspace directory
        """
        self.workspace_path = Path(workspace_path)
        self.git_manager = GitManager(workspace_path)
        
        logger.info(f"Context Tracker initialized for: {workspace_path}")
    
    def get_file_tree(self, max_files: int = 100) -> List[str]:
        """
        Get list of files in workspace.
        
        Args:
            max_files: Maximum number of files to return
            
        Returns:
            List of relative file paths
        """
        try:
            files = []
            
            # Common directories to ignore
            ignore_dirs = {
                '.git', '__pycache__', 'node_modules', '.venv', 'venv',
                '.pytest_cache', '.mypy_cache', 'dist', 'build', '.next',
                '.nuxt', 'coverage', '.idea', '.vscode'
            }
            
            # Common file patterns to ignore
            ignore_patterns = {
                '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
                '.class', '.o', '.obj', '.log', '.swp', '.DS_Store'
            }
            
            for root, dirs, filenames in os.walk(self.workspace_path):
                # Remove ignored directories from search
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                
                for filename in filenames:
                    # Skip ignored file patterns
                    if any(filename.endswith(pattern) for pattern in ignore_patterns):
                        continue
                    
                    file_path = Path(root) / filename
                    relative_path = file_path.relative_to(self.workspace_path)
                    files.append(str(relative_path))
                    
                    if len(files) >= max_files:
                        return files
            
            return sorted(files)
            
        except Exception as e:
            logger.error(f"Error getting file tree: {e}", exc_info=True)
            return []
    
    def get_git_info(self) -> Dict[str, Any]:
        """
        Get git repository information.
        
        Returns:
            Dictionary with git information
        """
        try:
            status = self.git_manager.get_status()
            recent_commits = self.git_manager.get_recent_commits(5)
            remote_info = self.git_manager.get_remote_info()
            
            return {
                'branch': status['branch'],
                'status': status['status'],
                'modified_count': status['modified_count'],
                'is_clean': status['is_clean'],
                'recent_commits': recent_commits,
                'remote': remote_info.get('origin', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Error getting git info: {e}", exc_info=True)
            return {
                'branch': 'unknown',
                'status': 'Error',
                'modified_count': 0,
                'is_clean': False,
                'recent_commits': '',
                'remote': 'unknown'
            }
    
    def get_workspace_summary(self) -> Dict[str, Any]:
        """
        Get high-level workspace summary.
        
        Returns:
            Dictionary with workspace summary
        """
        try:
            file_tree = self.get_file_tree(max_files=50)
            
            # Detect project type
            project_type = self._detect_project_type()
            
            # Get statistics
            stats = {
                'total_files': len(file_tree),
                'project_type': project_type,
                'last_updated': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting workspace summary: {e}", exc_info=True)
            return {}
    
    def _detect_project_type(self) -> str:
        """Detect the type of project based on files."""
        indicators = {
            'Python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
            'Node.js': ['package.json', 'yarn.lock', 'pnpm-lock.yaml'],
            'Rust': ['Cargo.toml', 'Cargo.lock'],
            'Go': ['go.mod', 'go.sum'],
            'Java': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
            'Ruby': ['Gemfile', 'Gemfile.lock'],
            'PHP': ['composer.json', 'composer.lock'],
            'C/C++': ['CMakeLists.txt', 'Makefile', 'configure.ac'],
        }
        
        detected_types = []
        
        for project_type, files in indicators.items():
            for indicator_file in files:
                if (self.workspace_path / indicator_file).exists():
                    detected_types.append(project_type)
                    break
        
        if not detected_types:
            return "Unknown"
        
        return ", ".join(detected_types)
    
    def get_full_context(self) -> Dict[str, Any]:
        """
        Get complete workspace context.
        
        Returns:
            Comprehensive context dictionary for AI
        """
        try:
            return {
                'workspace_path': str(self.workspace_path),
                'git_info': self.get_git_info(),
                'file_tree': self.get_file_tree(max_files=100),
                'workspace_summary': self.get_workspace_summary(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting full context: {e}", exc_info=True)
            return {
                'workspace_path': str(self.workspace_path),
                'git_info': {},
                'file_tree': [],
                'workspace_summary': {},
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def search_files(self, pattern: str, max_results: int = 20) -> List[str]:
        """
        Search for files matching a pattern.
        
        Args:
            pattern: Search pattern (filename or path fragment)
            max_results: Maximum number of results
            
        Returns:
            List of matching file paths
        """
        try:
            files = self.get_file_tree(max_files=500)
            pattern_lower = pattern.lower()
            
            matches = [
                f for f in files
                if pattern_lower in f.lower()
            ]
            
            return matches[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching files: {e}", exc_info=True)
            return []
