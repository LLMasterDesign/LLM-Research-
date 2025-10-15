# BookWorm Agentic Integration Map

## System Overview

The agentic folder contains a **production-ready, runnable** implementation of the BookWorm tutor following the Tutor.Genesis lattice-locked framework.

## Folder Structure

```
3ox/BookWorm/
├── agentic/                         # ← RUNNABLE SYSTEM (NEW)
│   ├── run.py                       # Main entry point
│   ├── tutor_genesis.gen            # Agent specification
│   ├── README.md                    # Full documentation
│   ├── QUICKSTART.md                # Get started guide
│   ├── INTEGRATION_MAP.md           # This file
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── engine.py                # Tutor engine (lockstep LU)
│   │
│   ├── artifacts/
│   │   └── syllabus_fundamentals.json  # M.S.I curriculum
│   │
│   ├── personas/                    # Future: Teaching styles
│   └── state/                       # Future: Redis persistence
│
├── brain.rs                         # Original agent config
├── capsule_loader.py                # Original loader (for reference)
├── mechanics/
│   └── tutor_engine.py              # Original adaptive engine
├── memory/
│   └── rag_integration.py           # RAG system (integrates with agentic)
├── library/                         # Learning materials (shared)
│   ├── books/
│   └── exercises/
└── courses/
    └── fundamentals_curriculum.json  # Original curriculum
```

## Integration Points

### 1. Agentic ↔ Library

**Books & Exercises** in `../library/` are referenced by the agentic system:

```python
# In future RAG integration
from memory.rag_integration import RAGMemorySystem

rag = RAGMemorySystem(redis_client)
rag.ingest_book('../library/books/variables_guide.md', metadata={...})

# In HELP command
def handle_help(self):
    concept = self.get_current_concept()
    # Search library for relevant content
    results = rag.semantic_search(f"explain {concept}", top_k=3)
```

### 2. Agentic ↔ RAG Memory

**RAG System** in `../memory/rag_integration.py` provides semantic search:

```python
# Connect RAG to agentic engine
from memory.rag_integration import RAGMemorySystem

class EnhancedBookWormEngine(BookWormEngine):
    def __init__(self, syllabus, student_id, redis_client=None):
        super().__init__(syllabus, student_id)
        self.rag = RAGMemorySystem(redis_client) if redis_client else None
    
    def handle_help(self):
        if self.rag:
            concept = self.get_current_concept_name()
            results = self.rag.semantic_search(concept, top_k=3)
            return self._format_rag_assist(results)
        else:
            return super().handle_help()
```

### 3. Agentic ↔ State Persistence

**Redis Schema** for saving/resuming:

```python
# In state/persistence.py (future)
class StateManager:
    def save_session(self, engine):
        self.redis.hset(
            f"bookworm:session:{engine.session_id}",
            mapping={
                'M': engine.M,
                'S': engine.S,
                'I': engine.I,
                'learned_items': json.dumps(engine.learned_items),
                'timestamp': time.time()
            }
        )
    
    def load_session(self, session_id):
        data = self.redis.hgetall(f"bookworm:session:{session_id}")
        # Reconstruct engine state
```

### 4. Agentic ↔ Original Components

**Coexistence Model**:

- **Agentic** = Runnable tutor with LU progression
- **Original** = Framework components for advanced features

Use original components to enhance agentic:

```python
# Use original adaptive engine for deeper assessment
from mechanics.tutor_engine import TutorEngine

class HybridEngine(BookWormEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.adaptive = TutorEngine()  # Original engine
    
    def assess_quiz_answers(self, answers, score):
        # Use original adaptive engine for deeper analysis
        return self.adaptive._analyze_response(answers, self.get_lu())
```

## Integration Workflow

### Adding RAG to Agentic System

**Step 1**: Install dependencies
```bash
cd /workspace
pip install redis numpy
```

**Step 2**: Start Redis
```bash
docker run -d -p 6379:6379 redis/redis-stack
```

**Step 3**: Ingest library content
```python
# scripts/ingest_library.py
from memory.rag_integration import RAGMemorySystem
import redis

r = redis.Redis(decode_responses=True)
rag = RAGMemorySystem(r)

# Ingest all books
for book in Path('../library/books').glob('*.md'):
    rag.ingest_book(str(book), {'id': book.stem, 'type': 'book'})
```

**Step 4**: Connect to agentic engine
```python
# agentic/run.py (modified)
def interactive_session(student_id="lucius"):
    syllabus = load_syllabus()
    
    # Connect Redis & RAG
    redis_client = redis.Redis(decode_responses=True)
    rag = RAGMemorySystem(redis_client)
    
    # Enhanced engine
    engine = EnhancedBookWormEngine(syllabus, student_id, rag=rag)
```

### Adding Personas

**Step 1**: Define persona specs in `personas/`

```python
# personas/guide_patient.py
class GuidePatient:
    name = "Guide.Patient"
    style = "explanatory"
    voice = "Let's explore this together, Lucius."
    
    def format_instruction(self, content):
        # Patient, detailed explanations
        return f"Let's break this down step by step...\n\n{content}"

# personas/coach_socratic.py
class CoachSocratic:
    name = "Coach.Socratic"
    style = "questions_first"
    voice = "What do you think happens here?"
    
    def format_instruction(self, content):
        # Turn into probing questions
        return f"Before we begin, consider: {self._generate_question(content)}"
```

**Step 2**: Add persona switching to engine

```python
# agentic/core/engine.py (enhanced)
class BookWormEngine:
    def __init__(self, syllabus, student_id, persona="guide_patient"):
        # ...
        self.persona = self._load_persona(persona)
    
    def emit_instruction(self):
        raw_instruction = self._get_instruction_content()
        formatted = self.persona.format_instruction(raw_instruction)
        # ...
```

**Step 3**: Add SWITCH command

```python
def handle_command(self, cmd):
    if cmd.startswith("SWITCH TEACHER"):
        persona_id = cmd.split("→")[-1].strip()
        return self.switch_persona(persona_id)
```

## Data Flow Diagrams

### Current Agentic Flow

```
Student Input
     ↓
run.py (CLI)
     ↓
BookWormEngine
     ├─ Load Syllabus (artifacts/syllabus_fundamentals.json)
     ├─ Manage LU Counters (M, S, I)
     ├─ Emit Boxes (Instruction, Quiz, Assist)
     └─ Handle Commands (DONE, CONFIRM, HELP, etc.)
     ↓
Output to Student
```

### Future Enhanced Flow

```
Student Input
     ↓
run.py (CLI)
     ↓
EnhancedBookWormEngine
     ├─ Load Syllabus
     ├─ Connect RAG (memory/rag_integration.py)
     │    ├─ Redis Vector Store
     │    └─ Library Content (../library/)
     ├─ Connect State Manager (state/persistence.py)
     │    └─ Redis Session Store
     ├─ Load Persona (personas/)
     │    └─ Format Instructions
     ├─ Manage LU Counters
     ├─ Emit Boxes
     │    └─ Augment with RAG on HELP
     └─ Handle Commands
          ├─ HELP → RAG search
          ├─ PAUSE → Save state
          ├─ RESUME → Load state
          └─ SWITCH TEACHER → Change persona
     ↓
Output to Student
```

## Extending the System

### Add New Module to Syllabus

**Edit** `artifacts/syllabus_fundamentals.json`:

```json
{
  "modules": [
    ...existing modules...,
    {
      "id": "M4",
      "title": "Your New Module",
      "sections": [
        {
          "id": "M4.S1",
          "title": "Your Section",
          "items": [
            {
              "id": "M4.S1.I1",
              "instruction": "Your instruction text...",
              "notes": ["Note 1", "Note 2"],
              "assist": "Your assistance hint...",
              "quiz": [
                {
                  "q": "Question 1?",
                  "choices": ["A. ...", "B. ...", "C. ...", "D. ..."],
                  "answer": "B"
                },
                ... (5 total)
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### Add New Book to Library

**Create** `../library/books/new_topic.md`:

```markdown
# New Topic Guide

## What is New Topic?

Explanation...

## Why It Matters

Importance...

## Examples

Code examples...

## Practice

Exercises...
```

**Ingest** into RAG:

```python
rag.ingest_book('../library/books/new_topic.md', {
    'id': 'new_topic',
    'title': 'New Topic Guide',
    'type': 'book'
})
```

### Add Custom Command

**In** `agentic/core/engine.py`:

```python
def handle_command(self, cmd):
    cmd_upper = cmd.strip().upper()
    
    # ... existing commands ...
    
    elif cmd_upper == "MYNEWCOMMAND":
        return self.handle_mynewcommand()
    
    # ...

def handle_mynewcommand(self):
    """Handle your custom command"""
    return "Custom response here"
```

## Migration Path

### From Original to Agentic

If you were using the original BookWorm system:

**Original Usage**:
```python
from capsule_loader import quick_load
capsule = quick_load()
session = capsule.create_student_session('lucius')
```

**New Agentic Usage**:
```bash
cd 3ox/BookWorm/agentic
python run.py
```

**Both can coexist!** Use:
- **Agentic**: For structured, lockstep learning with quiz gates
- **Original**: For adaptive, free-form exploration

### Hybrid Approach

Combine both systems:

```python
# Use agentic for core progression
from agentic.core.engine import BookWormEngine

# Use original for advanced features
from mechanics.tutor_engine import TutorEngine
from memory.rag_integration import RAGMemorySystem

class UltimateBookWorm(BookWormEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.adaptive = TutorEngine()
        self.rag = RAGMemorySystem(redis_client)
    
    # Combine the best of both worlds
```

## Testing Integration

### Test RAG Connection

```python
# test_rag_integration.py
from memory.rag_integration import RAGMemorySystem
import redis

r = redis.Redis(decode_responses=True)
rag = RAGMemorySystem(r)

# Ingest test content
rag.ingest_book('../library/books/variables_guide.md', {'id': 'test'})

# Search
results = rag.semantic_search("what are variables", top_k=3)
assert len(results) > 0
print("✓ RAG integration working")
```

### Test State Persistence

```python
# test_state.py
from agentic.core.engine import BookWormEngine
import json
import redis

r = redis.Redis(decode_responses=True)

# Create engine, advance a few LUs
engine = BookWormEngine(syllabus, "test_user")
# ... advance through some LUs ...

# Save state
state = {
    'M': engine.M,
    'S': engine.S,
    'I': engine.I,
    'learned': engine.learned_items
}
r.hset('bookworm:test:state', mapping={'data': json.dumps(state)})

# Load state
loaded = json.loads(r.hget('bookworm:test:state', 'data'))
assert loaded['M'] == engine.M
print("✓ State persistence working")
```

## Status & Roadmap

### ✅ Complete (Agentic System)
- [x] LU progression engine
- [x] Quiz validation gates
- [x] Command interface
- [x] Syllabus with M.S.I structure
- [x] Interactive CLI runner
- [x] Documentation

### 🔄 Integration Ready
- [ ] RAG connection (hooks ready)
- [ ] State persistence (schema ready)
- [ ] Persona switching (registry ready)
- [ ] Library search on HELP
- [ ] Spaced repetition

### 🎯 Future Enhancements
- [ ] Web UI
- [ ] Voice interface
- [ ] Visualizations (progress graphs)
- [ ] Multi-language curricula
- [ ] Collaborative learning

## Summary

**Agentic folder** = Complete, runnable tutor system following Tutor.Genesis

**Integration strategy**:
1. Use agentic for core learning flow
2. Connect original components (RAG, adaptive engine) for enhanced features
3. Share library content across both systems
4. Persist state in Redis for resume capability

**Quick Start**:
```bash
cd /workspace/3ox/BookWorm/agentic
python run.py
```

:: ∎
