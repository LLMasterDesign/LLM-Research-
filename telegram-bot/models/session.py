"""
Τ{Raven} - Session Models
User session and conversation state management
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class MessageRole(Enum):
    """Message role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """Conversation message."""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """User session."""
    user_id: int
    username: Optional[str]
    conversation_history: List[Message] = field(default_factory=list)
    workspace_path: str = "/workspace"
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict] = None):
        """Add a message to conversation history."""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.conversation_history.append(message)
        self.last_active = datetime.now()
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get recent messages from history."""
        return self.conversation_history[-count:]
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'workspace_path': self.workspace_path,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat(),
            'message_count': len(self.conversation_history),
            'metadata': self.metadata
        }


class SessionManager:
    """Manages user sessions."""
    
    def __init__(self):
        """Initialize session manager."""
        self.sessions: Dict[int, Session] = {}
    
    def get_or_create_session(self, user_id: int, username: Optional[str] = None) -> Session:
        """Get existing session or create new one."""
        if user_id not in self.sessions:
            self.sessions[user_id] = Session(
                user_id=user_id,
                username=username
            )
        return self.sessions[user_id]
    
    def get_session(self, user_id: int) -> Optional[Session]:
        """Get session by user ID."""
        return self.sessions.get(user_id)
    
    def delete_session(self, user_id: int):
        """Delete a session."""
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def clear_all_sessions(self):
        """Clear all sessions."""
        self.sessions.clear()
    
    def get_active_session_count(self) -> int:
        """Get number of active sessions."""
        return len(self.sessions)
