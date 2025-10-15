# 🐛 BookWorm Learning System

**An adaptive, RAG-powered tutor agent for mastering programming fundamentals**

## Overview

BookWorm is a complete learning environment that combines:
- 🧠 **Adaptive Tutor Engine** - Socratic teaching that adapts to your pace
- 📚 **Structured Curriculum** - Progressive concept building with clear dependencies
- 🔍 **RAG Memory System** - Semantic search across all learning materials
- 💾 **Redis Integration** - Persistent progress tracking and spaced repetition
- 🎯 **Mastery-Based Progression** - Move forward when you're ready, not on schedule

## Quick Start

### 1. Install Dependencies

```bash
pip install redis numpy
```

### 2. Load the Capsule

```python
import sys
sys.path.append('3ox/BookWorm')

from capsule_loader import quick_load

# Load BookWorm system
capsule = quick_load()

# Start your learning session
session = capsule.create_student_session('lucius')
print(session['welcome_message'])
```

### 3. Begin Learning

```python
# The tutor engine is now active
tutor = session['tutor']
rag = session['rag']

# Interact with the tutor
response = tutor.assess_response(
    session_id=session['session_id'],
    response="I think variables are like labeled boxes that hold values"
)

print(response['feedback'])
print(response['next_prompt'])
```

## System Architecture

```
3ox/BookWorm/
├── brain.rs                      # Agent configuration
├── capsule_loader.py             # System initialization
├── README.md                     # This file
│
├── agents/                       # Agent profiles (future)
├── courses/                      # Curriculum definitions
│   └── fundamentals_curriculum.json
│
├── library/                      # Learning materials
│   ├── books/                    # Concept guides
│   │   └── variables_guide.md
│   └── exercises/                # Practice problems
│
├── mechanics/                    # Core engine
│   └── tutor_engine.py          # Adaptive teaching system
│
├── memory/                       # RAG integration
│   └── rag_integration.py       # Redis + vector search
│
└── sessions/                     # Active learning sessions
```

## The Four-Step Learning Process

### Step 1: ASSESSMENT
The tutor continuously assesses your understanding through natural conversation. Every response you give provides insight into your comprehension level, knowledge gaps, and learning style. No explicit tests - just authentic dialogue that reveals where you are.

### Step 2: ADAPTATION  
Based on assessment, the system adapts everything: difficulty level, teaching method, explanation depth, and concept selection. You always work in your zone of proximal development - challenged enough to grow, supported enough to succeed.

### Step 3: ENGAGEMENT
Learning happens through varied, active engagement: Socratic questions that spark thinking, hands-on exercises that build skills, and synthesis challenges that deepen understanding. The tutor celebrates progress and provides scaffolding when needed.

### Step 4: CONSOLIDATION
Spaced repetition moves concepts into long-term memory. The RAG system surfaces past learning at optimal moments, strengthening neural connections. Every interaction is stored, enabling contextual retrieval that feels like a tutor who truly knows you.

## Curriculum Structure

The fundamentals course covers 12 core concepts:

**Foundation Phase** (30-60 min each)
- Variables and Data Types
- Operators and Expressions  
- Conditional Logic (if/else)
- While Loops
- For Loops

**Application Phase** (60-90 min each)
- Functions and Parameters
- Lists and Arrays
- Dictionaries and Key-Value Pairs
- String Operations

**Integration Phase** (90-120 min each)
- Error Handling and Debugging
- Search Algorithms
- Sorting Algorithms

Each concept includes:
- Clear prerequisites (dependency graph)
- Estimated time commitment
- Practice exercises
- Real-world examples
- Mastery checkpoints

## RAG Integration

The RAG (Retrieval-Augmented Generation) system provides:

**Semantic Search**
```python
# Find relevant content for any query
results = rag.semantic_search(
    query="how do I handle errors in Python?",
    top_k=5
)

for result in results:
    print(result['text'])
    print(f"Relevance: {result['similarity_score']}")
```

**Contextual Retrieval**
```python
# Get comprehensive context for teaching a concept
context = rag.retrieve_context_for_concept(
    concept_id="variables_basics",
    student_id="lucius"
)

# Returns: definitions, past interactions, examples, and curated context
```

**Spaced Repetition**
```python
# Concepts due for review based on forgetting curve
due_items = rag.get_spaced_repetition_items("lucius")

for item in due_items:
    print(f"Review: {item['concept_id']}")
    print(f"Priority: {item['priority']}")
```

## Progress Tracking

All progress is stored in Redis with these schemas:

```python
# Student profile
bookworm:student:{id}:profile

# Session history  
bookworm:student:{id}:sessions:{session_id}

# Concept mastery (0-4 scale)
bookworm:student:{id}:mastery:{concept}

# Learning graph relationships
bookworm:student:{id}:knowledge_graph

# Vector embeddings for semantic search
bookworm:vectors:{concept_id}
```

## Mastery Levels

Progress through five mastery levels:

0. **NOVICE** - Just introduced to the concept
1. **BEGINNER** - Basic understanding, can recognize
2. **INTERMEDIATE** - Can apply with guidance
3. **ADVANCED** - Can apply independently  
4. **EXPERT** - Can teach others, full mastery

Advancement requires demonstrated understanding, not time served.

## Usage Examples

### Example 1: Start Fresh
```python
from capsule_loader import quick_load

capsule = quick_load()
session = capsule.create_student_session('lucius')

# Tutor will assess your starting point
print(session['welcome_message'])
```

### Example 2: Continue Learning
```python
# System automatically loads your progress
session = capsule.create_student_session('lucius')

# You'll resume where you left off
print(f"Current phase: {session['current_phase']}")
print(f"Next concept: {session['next_concept']}")
```

### Example 3: Search Library
```python
# Search across all learning materials
results = capsule.rag.semantic_search(
    query="explain loops with examples",
    top_k=3
)

for r in results:
    print(r['text'][:200])  # Preview
```

### Example 4: Check Progress
```python
progress = capsule.tutor.initialize_student('lucius')

print(f"Sessions completed: {progress.session_count}")
print(f"Study time: {progress.total_study_time} minutes")
print(f"Concepts mastered: {len(progress.concepts_mastered)}")

# Detailed mastery breakdown
for concept, level in progress.concepts_mastered.items():
    print(f"  {concept}: {level.name}")
```

## Extending BookWorm

### Add New Concepts

Edit `courses/fundamentals_curriculum.json`:

```json
{
  "id": "new_concept",
  "name": "Your Concept Name",
  "description": "Clear, accessible explanation",
  "prerequisites": ["prior_concept_id"],
  "keywords": ["key", "terms"],
  "difficulty": 5,
  "estimated_time": 60,
  "resources": ["library/books/your_guide.md"]
}
```

### Add New Books

Create markdown files in `library/books/`:

```markdown
# Your Topic Guide

## Section 1
Content here...

## Section 2  
More content...
```

The RAG system will automatically chunk and index them.

### Customize Teaching Style

Edit `brain.rs` to adjust:
- `personality` - teaching persona
- `teaching_methods` - instructional approaches
- `interaction_style` - communication patterns
- `progression_model` - advancement criteria

## Integration with Existing Tools

BookWorm integrates with the Obsidian tools in this repo:

```python
# Chunk large learning materials
from obsidian_cli.chunk import chunk_file

chunks = chunk_file(
    'library/books/advanced_algorithms.md',
    max_chars=2000
)

# Each chunk gets embedded separately for fine-grained retrieval
for chunk in chunks:
    rag.ingest_book(chunk, metadata={...})
```

## Redis Setup (Optional)

For persistence, run Redis with VSS support:

```bash
# Using Docker
docker run -d -p 6379:6379 redis/redis-stack

# Or local installation
redis-server
```

Without Redis, the system runs in-memory (progress lost on restart).

## Philosophy

BookWorm embodies these learning principles:

**Socratic Method** - Questions over answers, discovery over delivery  
**Zone of Proximal Development** - Always challenging, never overwhelming  
**Mastery Learning** - Progress when ready, not on schedule  
**Spaced Repetition** - Review at optimal intervals  
**Active Recall** - Retrieve, don't just recognize  
**Elaborative Interrogation** - Ask "why?" and "how?"  
**Metacognition** - Reflect on your learning process

## Roadmap

Future enhancements:

- [ ] Multi-language support (JavaScript, Go, Rust)
- [ ] Visual concept maps
- [ ] Peer learning (connect students)
- [ ] Project-based capstones
- [ ] LLM integration for deeper response analysis
- [ ] Audio/video learning materials
- [ ] Gamification (XP, streaks, challenges)

## Contributing

BookWorm is designed to be extended. Add:
- New curricula in `courses/`
- New books in `library/books/`
- New exercises in `library/exercises/`
- Custom teaching mechanics in `mechanics/`

## License

Open source - learn freely, teach others, build upon it.

---

**Ready to learn, Lucius?**

```python
from capsule_loader import quick_load
capsule = quick_load()
```

:: ∎
