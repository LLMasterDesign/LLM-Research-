"""
Τ{Raven} - Git Manager Service
Handles all git operations
"""

import os
import logging
import subprocess
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class GitManager:
    """Manages git operations in the workspace."""
    
    def __init__(self, repo_path: str):
        """
        Initialize Git Manager.
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = Path(repo_path)
        
        if not self.is_git_repo():
            logger.warning(f"{repo_path} is not a git repository")
    
    def is_git_repo(self) -> bool:
        """Check if path is a git repository."""
        git_dir = self.repo_path / '.git'
        return git_dir.exists()
    
    async def execute_command(self, git_command: str) -> str:
        """
        Execute a git command.
        
        Args:
            git_command: Git command (without 'git' prefix)
            
        Returns:
            Command output as string
        """
        try:
            full_command = f"git {git_command}"
            
            logger.info(f"Executing: {full_command}")
            
            result = subprocess.run(
                full_command,
                shell=True,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout if result.stdout else result.stderr
            
            if result.returncode != 0:
                logger.warning(f"Git command failed with code {result.returncode}: {output}")
            
            return output or "Command completed with no output"
            
        except subprocess.TimeoutExpired:
            return "❌ Command timed out after 30 seconds"
        except Exception as e:
            logger.error(f"Git command error: {e}", exc_info=True)
            return f"❌ Error: {str(e)}"
    
    def get_status(self) -> Dict[str, any]:
        """
        Get git repository status.
        
        Returns:
            Dictionary with status information
        """
        try:
            status_output = subprocess.run(
                ['git', 'status', '--short'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            ).stdout
            
            branch_output = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            ).stdout.strip()
            
            # Count modified files
            modified_count = len([line for line in status_output.split('\n') if line.strip()])
            
            return {
                'branch': branch_output,
                'status': status_output or 'Clean working directory',
                'modified_count': modified_count,
                'is_clean': modified_count == 0
            }
            
        except Exception as e:
            logger.error(f"Error getting git status: {e}", exc_info=True)
            return {
                'branch': 'unknown',
                'status': 'Error retrieving status',
                'modified_count': 0,
                'is_clean': False
            }
    
    def get_recent_commits(self, count: int = 5) -> str:
        """
        Get recent commits.
        
        Args:
            count: Number of commits to retrieve
            
        Returns:
            Formatted commit history
        """
        try:
            result = subprocess.run(
                ['git', 'log', f'-{count}', '--oneline', '--decorate'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.stdout if result.stdout else "No commits found"
            
        except Exception as e:
            logger.error(f"Error getting commits: {e}", exc_info=True)
            return "Error retrieving commits"
    
    def get_diff(self, staged: bool = False) -> str:
        """
        Get git diff.
        
        Args:
            staged: If True, show staged changes; if False, show unstaged
            
        Returns:
            Diff output
        """
        try:
            cmd = ['git', 'diff']
            if staged:
                cmd.append('--staged')
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.stdout if result.stdout else "No changes"
            
        except Exception as e:
            logger.error(f"Error getting diff: {e}", exc_info=True)
            return f"Error: {str(e)}"
    
    def get_current_branch(self) -> str:
        """Get current branch name."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Error getting branch: {e}")
            return "unknown"
    
    def get_remote_info(self) -> Dict[str, str]:
        """Get remote repository information."""
        try:
            remote_url = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            ).stdout.strip()
            
            return {
                'origin': remote_url or 'No remote configured'
            }
        except Exception as e:
            logger.error(f"Error getting remote info: {e}")
            return {'origin': 'unknown'}
