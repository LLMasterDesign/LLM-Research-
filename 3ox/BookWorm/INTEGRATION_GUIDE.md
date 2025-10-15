# BookWorm Integration Guide

## Overview

This guide shows how to integrate BookWorm with your existing workspace tools and the upcoming RAG/Redis memory system.

## Integration with Obsidian Tools

BookWorm lives alongside the Obsidian vault management tools in this workspace. Here's how they work together:

### 1. Chunking Learning Materials

Use the existing chunker to prepare large books for RAG ingestion:

```python
from obsidian_cli.chunk import chunk_file
from memory.rag_integration import RAGMemorySystem

# Chunk a large learning book
chunks = chunk_file(
    '3ox/BookWorm/library/books/advanced_python.md',
    max_chars=1024,
    method='headers'
)

# Ingest each chunk into RAG
rag = RAGMemorySystem(redis_client)
for i, chunk in enumerate(chunks):
    rag._store_chunk(
        chunk_id=f"advanced_python:chunk:{i}",
        text=chunk.content,
        embedding=rag.embed(chunk.content),
        metadata={
            'book': 'advanced_python',
            'chunk_index': i,
            'header': chunk.header
        }
    )
```

### 2. Linting Learning Materials

Ensure all learning materials follow best practices:

```bash
# Lint all BookWorm books
python obsidian-tools/markdown_linter.py 3ox/BookWorm/library/books/

# Strict mode for publication-ready content
python obsidian-tools/markdown_linter.py --strict 3ox/BookWorm/library/books/
```

### 3. Organizing Course Materials

```bash
# Scan BookWorm library
python obsidian-tools/organizer.py 3ox/BookWorm/library/ --action scan

# Find broken links in learning materials
python obsidian-tools/organizer.py 3ox/BookWorm/library/ --action broken-links

# Add frontmatter to new books
python obsidian-tools/organizer.py 3ox/BookWorm/library/ --action add-frontmatter --execute
```

## Redis Integration

BookWorm is designed to work with Redis for persistence and vector similarity search.

### Setup Redis

#### Option 1: Docker (Recommended)
```bash
# Run Redis Stack (includes VSS module)
docker run -d \
  --name bookworm-redis \
  -p 6379:6379 \
  redis/redis-stack:latest
```

#### Option 2: Local Installation
```bash
# Install Redis
brew install redis  # macOS
sudo apt install redis  # Ubuntu

# Start Redis
redis-server
```

### Connect BookWorm to Redis

```python
import redis
from capsule_loader import quick_load

# Create Redis connection
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

# Load BookWorm with persistence
capsule = quick_load(redis_client=redis_client)

# Now all progress persists across sessions!
session = capsule.create_student_session('lucius')
```

### Redis Data Structure

BookWorm uses these Redis keys:

```
bookworm:student:{id}:profile          # Hash - student metadata
bookworm:student:{id}:sessions         # Sorted Set - session history
bookworm:student:{id}:mastery:{concept} # Hash - concept mastery
bookworm:student:{id}:knowledge_graph  # Graph - concept relationships
bookworm:student:{id}:concept_history:{concept} # List - interactions
bookworm:chunks:{chunk_id}             # Hash - text and metadata
bookworm:vectors:{chunk_id}            # Hash - embeddings
```

### Query Progress from Redis

```python
import redis
import json

r = redis.Redis(decode_responses=True)

# Get student profile
profile = r.hgetall('bookworm:student:lucius:profile')
print(f"Sessions: {profile['session_count']}")
print(f"Study time: {profile['total_study_time']} minutes")

# Get mastery for a concept
mastery = r.hgetall('bookworm:student:lucius:mastery:variables_basics')
print(f"Level: {mastery['level']}")
print(f"Practice count: {mastery['practice_count']}")

# Get recent sessions
sessions = r.zrange('bookworm:student:lucius:sessions', 0, -1)
for session_data in sessions:
    session = json.loads(session_data)
    print(f"Session {session['session_id']}: {len(session['interactions'])} interactions")
```

## RAG System Integration

The RAG (Retrieval-Augmented Generation) system provides semantic search and contextual learning.

### Ingesting New Books

```python
from memory.rag_integration import RAGMemorySystem

rag = RAGMemorySystem(redis_client)

# Ingest a new book
chunk_count = rag.ingest_book(
    book_path='3ox/BookWorm/library/books/new_topic.md',
    book_metadata={
        'id': 'new_topic',
        'title': 'New Topic Guide',
        'author': 'BookWorm Team',
        'difficulty': 3,
        'tags': ['beginner', 'fundamentals']
    }
)

print(f"Ingested {chunk_count} chunks")
```

### Semantic Search

```python
# Search across all learning materials
results = rag.semantic_search(
    query="how do I debug errors in my code?",
    top_k=5,
    filters={'difficulty': 3}  # Optional filtering
)

for result in results:
    print(f"\n{result['metadata']['title']}")
    print(result['text'][:200])
    print(f"Relevance: {result['similarity_score']:.3f}")
```

### Context-Aware Teaching

The tutor uses RAG to provide context-aware responses:

```python
# Get comprehensive teaching context
context = rag.retrieve_context_for_concept(
    concept_id='error_handling',
    student_id='lucius'
)

# Returns:
# - definitions: Concept explanations from knowledge base
# - student_history: Past interactions with this concept
# - examples: Practical examples
# - context_summary: Curated summary for teaching
```

### Spaced Repetition

```python
# Get concepts due for review
due_items = rag.get_spaced_repetition_items('lucius')

for item in due_items:
    print(f"Review: {item['concept_id']}")
    print(f"Last seen: {item['days_overdue']} days ago")
    print(f"Mastery level: {item['level']}")
    print(f"Priority: {item['priority']:.2f}\n")
```

## Integration with LLM Systems

BookWorm is designed to work with LLM backends for enhanced teaching.

### OpenAI Integration

```python
import openai
from mechanics.tutor_engine import TutorEngine

class EnhancedTutor(TutorEngine):
    """Tutor with LLM-powered response analysis"""
    
    def _analyze_response(self, response: str, concept_id: str):
        """Use LLM to deeply analyze student response"""
        
        concept = self.knowledge_graph[concept_id]
        
        prompt = f"""
        Analyze this student response about {concept.name}:
        
        Student: "{response}"
        
        Assess:
        1. Understanding level (0-4)
        2. Misconceptions (if any)
        3. Next teaching step
        
        Respond in JSON format.
        """
        
        analysis = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse and return enhanced assessment
        return json.loads(analysis.choices[0].message.content)
```

### Custom Embedding Models

```python
from sentence_transformers import SentenceTransformer

# Use a better embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def custom_embedding(text: str):
    return model.encode(text).tolist()

# Pass to RAG system
rag = RAGMemorySystem(
    redis_client=redis_client,
    embedding_function=custom_embedding
)
```

## Creating Multi-Course Systems

Extend BookWorm to support multiple courses:

```python
# Create new curriculum
cat > 3ox/BookWorm/courses/web_dev_curriculum.json <<EOF
{
  "course_id": "web_dev_001",
  "title": "Web Development Fundamentals",
  "concepts": [...]
}
EOF

# Load specific curriculum
tutor.load_curriculum('3ox/BookWorm/courses/web_dev_curriculum.json')

# Students can take multiple courses
session1 = tutor.start_session('lucius', course='fundamentals_001')
session2 = tutor.start_session('lucius', course='web_dev_001')
```

## Agent Configuration

Customize teaching style by editing `brain.rs`:

```rust
agent_config {
    name: "Custom Tutor",
    personality: "energetic_coach",  // vs. "patient_socratic_mentor"
    
    teaching_methods: [
        "project_based_learning",     // More hands-on
        "visual_demonstrations",      // Include diagrams
        "pair_programming_simulation" // Collaborative style
    ],
    
    progression_model: "xp_based",   // vs. "mastery_based"
    difficulty_adaptation: "dynamic_assessment"
}
```

## Monitoring and Analytics

Track learning metrics:

```python
def get_student_analytics(student_id: str, redis_client):
    """Generate learning analytics"""
    
    profile = redis_client.hgetall(f'bookworm:student:{student_id}:profile')
    
    # Get all mastery records
    mastery_keys = redis_client.keys(f'bookworm:student:{student_id}:mastery:*')
    
    analytics = {
        'total_sessions': int(profile.get('session_count', 0)),
        'total_time': int(profile.get('total_study_time', 0)),
        'concepts_attempted': len(mastery_keys),
        'mastery_distribution': {},
        'learning_velocity': float(profile.get('learning_velocity', 0))
    }
    
    # Count mastery levels
    for key in mastery_keys:
        mastery = redis_client.hgetall(key)
        level = int(mastery.get('level', 0))
        analytics['mastery_distribution'][level] = \
            analytics['mastery_distribution'].get(level, 0) + 1
    
    return analytics

# Usage
analytics = get_student_analytics('lucius', redis_client)
print(json.dumps(analytics, indent=2))
```

## Testing Integration

```python
# test_integration.py
import pytest
from capsule_loader import BookWormCapsule
from memory.rag_integration import RAGMemorySystem

def test_full_learning_flow(redis_client):
    """Test complete learning flow"""
    
    capsule = BookWormCapsule()
    capsule.load(redis_client)
    
    # Start session
    session = capsule.create_student_session('test_user')
    assert session['session_id']
    
    # Submit response
    result = capsule.tutor.assess_response(
        session_id=session['session_id'],
        response="Variables are containers for data"
    )
    
    assert result['feedback']
    assert result['mastery_level']
    
    # Search for content
    results = capsule.rag.semantic_search("variables", top_k=3)
    assert len(results) > 0
    
    # End session
    summary = capsule.tutor.end_session(session['session_id'])
    assert summary['duration_minutes'] >= 0

def test_spaced_repetition(redis_client):
    """Test spaced repetition algorithm"""
    
    rag = RAGMemorySystem(redis_client)
    
    # Simulate past learning
    import time
    redis_client.hset(
        'bookworm:student:test_user:mastery:concept_1',
        mapping={
            'level': 2,
            'last_updated': time.time() - (8 * 86400)  # 8 days ago
        }
    )
    
    # Get due items
    due = rag.get_spaced_repetition_items('test_user')
    
    # Should be due (interval for level 2 is 7 days)
    assert any(item['concept_id'] == 'concept_1' for item in due)
```

## Deployment

### Standalone Server

```python
# server.py
from flask import Flask, request, jsonify
from capsule_loader import quick_load
import redis

app = Flask(__name__)

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
capsule = quick_load(redis_client=redis_client)

@app.route('/session/start', methods=['POST'])
def start_session():
    student_id = request.json['student_id']
    session = capsule.create_student_session(student_id)
    return jsonify(session)

@app.route('/session/respond', methods=['POST'])
def respond():
    session_id = request.json['session_id']
    response = request.json['response']
    
    result = capsule.tutor.assess_response(session_id, response)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
```

## Next Steps

1. **Add Content**: Create more books in `library/books/`
2. **Build Exercises**: Add practice problems in `library/exercises/`
3. **Custom Curriculum**: Define new courses in `courses/`
4. **Enhance RAG**: Integrate better embedding models
5. **Add Visualizations**: Build progress dashboards
6. **Multi-Modal**: Add images, videos, interactive demos

:: ∎
