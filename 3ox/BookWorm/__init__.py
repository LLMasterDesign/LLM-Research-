"""
BookWorm Learning System
An adaptive, RAG-powered tutor for programming fundamentals
"""

__version__ = "1.0.0"
__author__ = "BookWorm Team"

# Quick imports for easy access
from .capsule_loader import BookWormCapsule, quick_load
from .mechanics.tutor_engine import TutorEngine, LearningPhase, MasteryLevel
from .memory.rag_integration import RAGMemorySystem

__all__ = [
    'BookWormCapsule',
    'quick_load',
    'TutorEngine',
    'LearningPhase',
    'MasteryLevel',
    'RAGMemorySystem'
]

# ASCII Art Banner
BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🐛 BookWorm Learning System                                 ║
║   Adaptive · RAG-Powered · Mastery-Based                     ║
║                                                               ║
║   "Learn at your pace, master at your level"                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""

def print_banner():
    """Print the BookWorm banner"""
    print(BANNER)
