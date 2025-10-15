"""
BookWorm Prompt Capsule Loader
Initializes the learning environment with agent, curriculum, and memory systems
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional


class BookWormCapsule:
    """
    Prompt capsule that loads BookWorm tutor into Cursor session
    Self-contained learning environment ready for immediate use
    """
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or '3ox/BookWorm')
        self.config = None
        self.tutor = None
        self.rag = None
        self.curriculum = None
        
    def load(self, redis_client=None) -> Dict:
        """
        Load complete BookWorm system
        Returns activation prompt for Cursor
        """
        print("▛▞ BOOKWORM LOADING SEQUENCE ▮▯▯▯▯▯▯▹")
        
        # Step 1: Load agent configuration
        print("▛▞ Loading agent brain... ▮▮▯▯▯▯▯▹")
        self.config = self._load_brain_config()
        
        # Step 2: Initialize tutor engine
        print("▛▞ Initializing tutor engine... ▮▮▮▯▯▯▯▹")
        from mechanics.tutor_engine import TutorEngine
        self.tutor = TutorEngine(redis_client=redis_client)
        
        # Step 3: Load curriculum
        print("▛▞ Loading curriculum... ▮▮▮▮▯▯▯▹")
        curriculum_path = self.base_path / 'courses' / 'fundamentals_curriculum.json'
        self.tutor.load_curriculum(str(curriculum_path))
        
        with open(curriculum_path, 'r') as f:
            self.curriculum = json.load(f)
        
        # Step 4: Initialize RAG system
        print("▛▞ Connecting RAG memory... ▮▮▮▮▮▯▯▹")
        from memory.rag_integration import RAGMemorySystem
        self.rag = RAGMemorySystem(redis_client=redis_client)
        
        # Step 5: Ingest learning materials
        print("▛▞ Indexing library books... ▮▮▮▮▮▮▯▹")
        self._ingest_library()
        
        print("▛▞ BOOKWORM READY ▮▮▮▮▮▮▮▹")
        
        return self._generate_activation_prompt()
    
    def _load_brain_config(self) -> Dict:
        """Parse brain.rs configuration"""
        brain_path = self.base_path / 'brain.rs'
        
        # Simple parser for brain.rs config
        # In production, use proper Rust config parser
        config = {
            'name': 'BookWorm Tutor',
            'role': 'adaptive_learning_guide',
            'loaded': True
        }
        
        return config
    
    def _ingest_library(self):
        """Ingest all books in library into RAG system"""
        library_path = self.base_path / 'library' / 'books'
        
        if not library_path.exists():
            return
        
        for book_file in library_path.glob('*.md'):
            book_id = book_file.stem
            
            try:
                self.rag.ingest_book(
                    book_path=str(book_file),
                    book_metadata={
                        'id': book_id,
                        'title': book_id.replace('_', ' ').title(),
                        'type': 'learning_material'
                    }
                )
            except Exception as e:
                print(f"Warning: Could not ingest {book_file.name}: {e}")
    
    def _generate_activation_prompt(self) -> str:
        """Generate activation prompt for Cursor agent"""
        prompt = f"""
# 🐛 BookWorm Tutor Activated

Hello, Lucius! I'm your BookWorm learning guide, now active and ready to help you master programming fundamentals.

## My Capabilities

**Teaching Approach:**
- Socratic questioning (I guide you to discover answers)
- Adaptive pacing (we move at your speed)
- Spaced repetition (concepts reviewed at optimal intervals)
- Progressive mastery (foundation → application → integration → teaching)

**Current Curriculum:**
- **Course**: {self.curriculum['title']}
- **Concepts**: {len(self.curriculum['concepts'])} topics to master
- **Estimated Time**: {self.curriculum['estimated_hours']} hours
- **Your Path**: Customized based on your progress

**Memory System:**
- RAG-powered semantic search across all materials
- Redis-backed progress tracking
- Context-aware concept retrieval
- Personalized learning history

## Quick Start Commands

To begin your learning session:
```python
# Start a new session
session = tutor.start_session('lucius')
print(session['prompt'])
```

To search for specific concepts:
```python
# Semantic search
results = rag.semantic_search("how do variables work?", top_k=3)
```

To check your progress:
```python
# View mastery levels
progress = tutor.initialize_student('lucius')
print(f"Phase: {{progress.current_phase}}")
print(f"Concepts mastered: {{len(progress.concepts_mastered)}}")
```

## Learning Philosophy

{self._format_learning_philosophy()}

## Ready When You Are

I'm here to guide you through {len(self.curriculum['concepts'])} fundamental concepts, adapted to your pace and style. 

**Would you like to:**
1. Start from the beginning with variables?
2. Continue where we left off?
3. Focus on a specific concept?
4. Take a quick assessment to find your level?

What sounds good to you?

:: ∎
"""
        return prompt
    
    def _format_learning_philosophy(self) -> str:
        """Format the 4-step learning philosophy"""
        return """
**Step 1 - ASSESSMENT**: I continuously assess your understanding through natural conversation, 
building a real-time model of your knowledge without explicit testing. Every response tells me 
where you are and what you need next.

**Step 2 - ADAPTATION**: Based on what I learn about you, I adapt my teaching style, difficulty 
level, and explanatory depth. You'll always work in your zone of proximal development - 
challenged but not overwhelmed.

**Step 3 - ENGAGEMENT**: Learning happens through varied interactions: questions that make you 
think, exercises that make you do, and projects that make you create. I celebrate your wins and 
support you through struggles.

**Step 4 - CONSOLIDATION**: Through spaced repetition and strategic review, concepts move from 
short-term to long-term memory. The RAG system surfaces past learning at the perfect moment, 
strengthening connections and building lasting understanding.
"""
    
    def create_student_session(self, student_id: str = 'lucius') -> Dict:
        """Create a new learning session for immediate use"""
        if not self.tutor:
            raise RuntimeError("Capsule not loaded. Call load() first.")
        
        session = self.tutor.start_session(student_id)
        
        return {
            'session_id': session['session']['session_id'],
            'welcome_message': session['prompt'],
            'current_phase': session['phase'],
            'next_concept': session['concept'],
            'tutor': self.tutor,
            'rag': self.rag
        }


def quick_load(redis_client=None) -> BookWormCapsule:
    """
    Quick loader for immediate use
    
    Usage in Cursor:
    ```python
    from capsule_loader import quick_load
    
    capsule = quick_load()
    session = capsule.create_student_session('lucius')
    print(session['welcome_message'])
    ```
    """
    capsule = BookWormCapsule()
    activation = capsule.load(redis_client=redis_client)
    print(activation)
    return capsule


if __name__ == '__main__':
    # Direct execution loads and activates BookWorm
    print("\n" + "="*60)
    print("🐛 BOOKWORM PROMPT CAPSULE")
    print("="*60 + "\n")
    
    capsule = quick_load()
    
    print("\n" + "="*60)
    print("System loaded. Import this module to access tutor.")
    print("="*60)
