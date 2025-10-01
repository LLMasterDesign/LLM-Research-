"""
Τ{Raven} - Command Handlers
All Telegram bot command implementations
"""

import os
import logging
from typing import List
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from ..services.ai_bridge import AIBridge
from ..services.git_manager import GitManager
from ..services.context_tracker import ContextTracker

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user
    
    welcome_message = f"""
🌟 **Welcome to Τ{{Raven}} - Telegram Command Station** 🌟

Hello {user.first_name}! I'm your AI-powered development assistant.

I have full access to your workspace at:
📂 `{os.getenv('WORKSPACE_PATH', '/workspace')}`

**What I can do:**
🤖 Answer questions about your code
📝 Read and edit files
🔧 Execute git operations
⚡ Run shell commands
🧠 Maintain conversation context

**Quick Start:**
• Just type your question naturally, or use `/ask`
• Use `/help` to see all available commands
• Use `/context` to see what I know about your workspace

Let's build something amazing together! 🚀
"""
    
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.MARKDOWN
    )
    
    logger.info(f"User {user.id} ({user.username}) started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = """
📚 **Τ{Raven} Command Reference** 📚

**Conversation Commands:**
`/ask <question>` - Ask me anything about your code
`/context` - Show current workspace state
`/session reset` - Start a fresh conversation

**File Operations:**
`/file <path>` - Read a file
`/file <path> <content>` - Write to a file

**Git Operations:**
`/git status` - Show git status
`/git log` - Show recent commits
`/git diff` - Show uncommitted changes
`/git <command>` - Run any git command

**Execution:**
`/run <command>` - Execute a shell command
⚠️ Use with caution - commands run with full access

**Tips:**
• You can ask questions without using /ask
• I remember conversation context automatically
• Use backticks for code: \\`code here\\`
• I can read your entire repository for context

**Examples:**
`/ask What does the main function do?`
`/file src/config.py`
`/git status`
`/run pytest tests/`

Need more help? Just ask! 💬
"""
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /ask command - main AI interaction."""
    if not context.args:
        await update.message.reply_text(
            "Please provide a question. Example:\n"
            "`/ask How does the authentication work?`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    question = ' '.join(context.args)
    user = update.effective_user
    
    logger.info(f"User {user.id} asked: {question}")
    
    # Send typing indicator
    await update.message.chat.send_action('typing')
    
    # Send initial status message
    status_msg = await update.message.reply_text("🧠 Analyzing workspace context...")
    
    try:
        # Get context tracker from bot data
        context_tracker: ContextTracker = context.bot_data.get('context_tracker')
        
        # Build context
        await status_msg.edit_text("📂 Loading workspace information...")
        workspace_context = context_tracker.get_full_context()
        
        # Query AI
        await status_msg.edit_text("🤔 Consulting AI...")
        ai_bridge = AIBridge()
        response = await ai_bridge.ask_with_context(question, workspace_context)
        
        # Delete status message
        await status_msg.delete()
        
        # Send response (split if too long)
        if len(response) > 4000:
            # Split into chunks
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await update.message.reply_text(
                        f"💡 **Response** (Part {i+1}/{len(chunks)}):\n\n{chunk}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text(
                        f"📄 **Part {i+1}/{len(chunks)}**:\n\n{chunk}",
                        parse_mode=ParseMode.MARKDOWN
                    )
        else:
            await update.message.reply_text(
                f"💡 {response}",
                parse_mode=ParseMode.MARKDOWN
            )
        
        logger.info(f"Successfully responded to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        await status_msg.edit_text(
            f"❌ Error: {str(e)}\n\nPlease try again or rephrase your question."
        )


async def context_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /context command - show workspace state."""
    await update.message.chat.send_action('typing')
    
    try:
        context_tracker: ContextTracker = context.bot_data.get('context_tracker')
        workspace_context = context_tracker.get_full_context()
        
        # Format context information
        context_text = f"""
📊 **Workspace Context**

**Location:** `{workspace_context['workspace_path']}`
**Git Branch:** `{workspace_context['git_info'].get('branch', 'N/A')}`
**Status:** {workspace_context['git_info'].get('status', 'Unknown')}

**Recent Activity:**
{workspace_context['git_info'].get('recent_commits', 'No commits found')[:500]}

**File Summary:**
• Total files: {len(workspace_context.get('file_tree', []))}
• Modified files: {workspace_context['git_info'].get('modified_count', 0)}

**System:**
• OS: Linux
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Use `/ask` to query specific information about the workspace.
"""
        
        await update.message.reply_text(context_text, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Error getting context: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error retrieving context: {str(e)}")


async def git_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle git operations."""
    if not context.args:
        await update.message.reply_text(
            "Usage: `/git <command>`\n\n"
            "Examples:\n"
            "`/git status`\n"
            "`/git log --oneline -5`\n"
            "`/git diff`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    git_args = ' '.join(context.args)
    
    await update.message.chat.send_action('typing')
    
    try:
        git_manager = GitManager(os.getenv('WORKSPACE_PATH', '/workspace'))
        result = await git_manager.execute_command(git_args)
        
        if len(result) > 4000:
            result = result[:3900] + "\n\n... (output truncated)"
        
        await update.message.reply_text(
            f"```\n{result}\n```",
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Git command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Git error: {str(e)}")


async def file_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle file operations."""
    if not context.args:
        await update.message.reply_text(
            "Usage: `/file <path> [content]`\n\n"
            "Examples:\n"
            "`/file README.md` - Read file\n"
            "`/file test.txt Hello!` - Write to file",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    file_path = context.args[0]
    workspace_path = os.getenv('WORKSPACE_PATH', '/workspace')
    full_path = os.path.join(workspace_path, file_path)
    
    # Security check - ensure path is within workspace
    if not os.path.abspath(full_path).startswith(os.path.abspath(workspace_path)):
        await update.message.reply_text("❌ Access denied: Path outside workspace")
        return
    
    try:
        if len(context.args) == 1:
            # Read file
            if not os.path.exists(full_path):
                await update.message.reply_text(f"❌ File not found: `{file_path}`", parse_mode=ParseMode.MARKDOWN)
                return
            
            with open(full_path, 'r') as f:
                content = f.read()
            
            if len(content) > 4000:
                content = content[:3900] + "\n\n... (file truncated)"
            
            await update.message.reply_text(
                f"📄 **{file_path}**\n\n```\n{content}\n```",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Write file
            content = ' '.join(context.args[1:])
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
            
            await update.message.reply_text(
                f"✅ Written to `{file_path}`",
                parse_mode=ParseMode.MARKDOWN
            )
            
    except Exception as e:
        logger.error(f"File operation error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ File error: {str(e)}")


async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle shell command execution."""
    if not context.args:
        await update.message.reply_text(
            "Usage: `/run <command>`\n\n"
            "⚠️ **Warning:** Commands execute with full access.\n\n"
            "Example: `/run ls -la`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    command = ' '.join(context.args)
    
    # Security warning
    await update.message.reply_text(
        f"⚡ Executing: `{command}`\n\nPlease wait...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        import subprocess
        
        result = subprocess.run(
            command,
            shell=True,
            cwd=os.getenv('WORKSPACE_PATH', '/workspace'),
            capture_output=True,
            text=True,
            timeout=int(os.getenv('COMMAND_TIMEOUT', 300))
        )
        
        output = result.stdout if result.stdout else result.stderr
        
        if len(output) > 4000:
            output = output[:3900] + "\n\n... (output truncated)"
        
        status_emoji = "✅" if result.returncode == 0 else "❌"
        
        await update.message.reply_text(
            f"{status_emoji} Exit code: {result.returncode}\n\n```\n{output}\n```",
            parse_mode=ParseMode.MARKDOWN
        )
        
    except subprocess.TimeoutExpired:
        await update.message.reply_text("⏱️ Command timed out")
    except Exception as e:
        logger.error(f"Command execution error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Execution error: {str(e)}")


async def session_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle session management."""
    if not context.args:
        await update.message.reply_text(
            "Usage: `/session <action>`\n\n"
            "Actions:\n"
            "• `reset` - Start fresh conversation\n"
            "• `info` - Show session information",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    action = context.args[0].lower()
    
    if action == 'reset':
        # Clear conversation history (implementation depends on session storage)
        await update.message.reply_text(
            "🔄 Session reset! Starting fresh conversation.\n\n"
            "Previous context has been cleared."
        )
    elif action == 'info':
        user = update.effective_user
        await update.message.reply_text(
            f"📊 **Session Information**\n\n"
            f"User: {user.first_name} (@{user.username})\n"
            f"User ID: `{user.id}`\n"
            f"Workspace: `{os.getenv('WORKSPACE_PATH', '/workspace')}`\n"
            f"Active: Yes",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(f"❌ Unknown action: {action}")
