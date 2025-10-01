"""
Τ{Raven} - AI Bridge Service
Handles communication with Anthropic Claude API
"""

import os
import logging
from typing import Dict, List, Any
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class AIBridge:
    """Bridge to AI services (Claude API)."""
    
    def __init__(self):
        """Initialize AI bridge with API credentials."""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = os.getenv('AI_MODEL', 'claude-sonnet-4')
        self.max_tokens = int(os.getenv('AI_MAX_TOKENS', 4096))
        self.temperature = float(os.getenv('AI_TEMPERATURE', 0.7))
        
        logger.info(f"AI Bridge initialized with model: {self.model}")
    
    def _build_system_prompt(self, workspace_context: Dict[str, Any]) -> str:
        """Build system prompt with workspace context."""
        return f"""You are Raven, an AI assistant embedded in a developer's workspace via Telegram.

WORKSPACE CONTEXT:
- Location: {workspace_context['workspace_path']}
- Git Branch: {workspace_context['git_info'].get('branch', 'unknown')}
- Git Status: {workspace_context['git_info'].get('status', 'unknown')}

RECENT COMMITS:
{workspace_context['git_info'].get('recent_commits', 'No commits')[:500]}

FILE STRUCTURE:
{self._format_file_tree(workspace_context.get('file_tree', []))[:1000]}

YOUR CAPABILITIES:
- Answer questions about the codebase with full context
- Explain code, functions, and architecture
- Suggest improvements and refactoring
- Help with debugging and problem-solving
- Execute git operations (through commands)
- Read and write files (through commands)

RESPONSE GUIDELINES:
- Be concise but thorough
- Use code blocks for code (markdown format)
- Provide actionable suggestions
- Reference specific files and line numbers when relevant
- Format for Telegram (markdown, max 4000 chars per message)
- Use emojis sparingly for clarity

Remember: You're responding via Telegram, so keep responses clear and mobile-friendly."""

    def _format_file_tree(self, file_tree: List[str]) -> str:
        """Format file tree for context."""
        if not file_tree:
            return "No files found"
        
        # Group by directory
        formatted = []
        for file_path in file_tree[:50]:  # Limit to 50 files
            formatted.append(f"  • {file_path}")
        
        if len(file_tree) > 50:
            formatted.append(f"  ... and {len(file_tree) - 50} more files")
        
        return "\n".join(formatted)
    
    async def ask_with_context(self, question: str, workspace_context: Dict[str, Any]) -> str:
        """
        Ask a question with full workspace context.
        
        Args:
            question: User's question
            workspace_context: Full workspace context from ContextTracker
            
        Returns:
            AI response as string
        """
        try:
            system_prompt = self._build_system_prompt(workspace_context)
            
            logger.info(f"Sending question to AI: {question[:100]}...")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )
            
            # Extract text from response
            answer = response.content[0].text
            
            logger.info(f"Received AI response ({len(answer)} chars)")
            
            return answer
            
        except Exception as e:
            logger.error(f"AI Bridge error: {e}", exc_info=True)
            raise Exception(f"AI service error: {str(e)}")
    
    async def ask_simple(self, question: str) -> str:
        """
        Ask a simple question without workspace context.
        
        Args:
            question: User's question
            
        Returns:
            AI response as string
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"AI Bridge error: {e}", exc_info=True)
            raise Exception(f"AI service error: {str(e)}")
    
    def stream_response(self, question: str, workspace_context: Dict[str, Any]):
        """
        Stream AI response (for future real-time updates).
        
        Args:
            question: User's question
            workspace_context: Full workspace context
            
        Yields:
            Chunks of AI response
        """
        # TODO: Implement streaming for real-time updates in Telegram
        # This would allow showing "AI is thinking..." with progressive updates
        pass
