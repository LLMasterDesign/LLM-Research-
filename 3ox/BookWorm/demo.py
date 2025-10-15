#!/usr/bin/env python3
"""
BookWorm Demo Script
Demonstrates the learning system in action
"""

import sys
from pathlib import Path

# Add BookWorm to path
sys.path.insert(0, str(Path(__file__).parent))

from capsule_loader import quick_load
import json


def demo_session():
    """Run a demonstration learning session"""
    
    print("\n" + "="*70)
    print("🐛 BookWorm Demo - Interactive Learning Session")
    print("="*70 + "\n")
    
    # Load the system
    print("Loading BookWorm system...\n")
    capsule = quick_load()
    
    print("\n" + "="*70)
    print("Creating learning session for Lucius...")
    print("="*70 + "\n")
    
    # Start session
    session = capsule.create_student_session('lucius')
    
    print(session['welcome_message'])
    print("\n" + "-"*70 + "\n")
    
    # Simulate student responses
    print("📝 Simulating Learning Interaction\n")
    
    responses = [
        {
            'student': "I think a variable is like a container that stores a value, and you can change what's in it.",
            'context': 'Understanding variables concept'
        },
        {
            'student': "It's important because you can reuse the same value multiple times without repeating it, and you can update it as needed.",
            'context': 'Explaining importance'
        },
        {
            'student': "I'd name them with descriptive lowercase words separated by underscores, like student_count or max_temperature.",
            'context': 'Discussing naming conventions'
        }
    ]
    
    tutor = session['tutor']
    session_id = session['session_id']
    
    for i, interaction in enumerate(responses, 1):
        print(f"🎓 Interaction {i}")
        print(f"Context: {interaction['context']}")
        print(f"\nLucius: \"{interaction['student']}\"\n")
        
        # Get tutor response
        result = tutor.assess_response(
            session_id=session_id,
            response=interaction['student']
        )
        
        print(f"📊 Assessment: {result['feedback']}")
        print(f"✨ Encouragement: {result['encouragement']}")
        print(f"🎯 Mastery Level: {result['mastery_level'].name}\n")
        print(f"🧠 Next Prompt:\n{result['next_prompt']}")
        print("\n" + "-"*70 + "\n")
    
    # Demonstrate RAG search
    print("="*70)
    print("🔍 RAG System Demo - Semantic Search")
    print("="*70 + "\n")
    
    queries = [
        "how do variables work",
        "what are data types",
        "examples of using variables"
    ]
    
    rag = session['rag']
    
    for query in queries:
        print(f"Query: '{query}'")
        results = rag.semantic_search(query, top_k=2)
        
        if results:
            print(f"Found {len(results)} relevant chunks:\n")
            for j, result in enumerate(results, 1):
                preview = result['text'][:150].replace('\n', ' ')
                print(f"  {j}. {preview}...")
                print(f"     Similarity: {result['similarity_score']:.3f}\n")
        else:
            print("  (No results - library needs to be indexed)\n")
        
        print("-"*70 + "\n")
    
    # End session
    print("="*70)
    print("📊 Ending Session")
    print("="*70 + "\n")
    
    summary = tutor.end_session(session_id)
    
    print("Session Summary:")
    print(f"  Duration: {summary['duration_minutes']} minutes")
    print(f"  Interactions: {summary['interactions_count']}")
    print(f"  Concepts Covered: {len(summary['concepts_covered'])}")
    print(f"  Total Sessions: {summary['total_sessions']}")
    print(f"  Total Study Time: {summary['total_study_time']} minutes")
    print(f"\n{summary['message']}\n")
    
    print("="*70)
    print("✅ Demo Complete!")
    print("="*70 + "\n")
    
    # Show how to continue
    print("To start your own session, use:")
    print("\n```python")
    print("from capsule_loader import quick_load")
    print("")
    print("capsule = quick_load()")
    print("session = capsule.create_student_session('lucius')")
    print("```\n")


def demo_curriculum():
    """Display the curriculum structure"""
    
    print("\n" + "="*70)
    print("📚 Curriculum Overview")
    print("="*70 + "\n")
    
    curriculum_path = Path(__file__).parent / 'courses' / 'fundamentals_curriculum.json'
    
    with open(curriculum_path, 'r') as f:
        curriculum = json.load(f)
    
    print(f"Course: {curriculum['title']}")
    print(f"Description: {curriculum['description']}")
    print(f"Estimated Time: {curriculum['estimated_hours']} hours")
    print(f"Difficulty: {curriculum['difficulty']}")
    print(f"\nTotal Concepts: {len(curriculum['concepts'])}\n")
    
    print("Concept Progression:\n")
    
    phases = {
        'Foundation': [],
        'Application': [],
        'Advanced': []
    }
    
    for concept in curriculum['concepts']:
        if concept['difficulty'] <= 4:
            phases['Foundation'].append(concept)
        elif concept['difficulty'] <= 7:
            phases['Application'].append(concept)
        else:
            phases['Advanced'].append(concept)
    
    for phase, concepts in phases.items():
        print(f"📖 {phase} Phase ({len(concepts)} concepts)")
        for concept in concepts:
            prereqs = f" [requires: {', '.join(concept['prerequisites'])}]" if concept['prerequisites'] else ""
            print(f"   • {concept['name']} ({concept['estimated_time']} min){prereqs}")
        print()
    
    print("Milestones:")
    for milestone in curriculum['milestones']:
        print(f"  🏆 {milestone['title']}")
        print(f"     Badge: {milestone['badge']}")
        print(f"     Requires: {len(milestone['required_concepts'])} concepts\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'curriculum':
        demo_curriculum()
    else:
        # Note: This demo runs without Redis, so persistence is simulated
        print("\n⚠️  Note: Running without Redis - progress won't persist")
        print("   To enable persistence, start Redis and pass redis_client to quick_load()\n")
        
        demo_session()
        
        print("\nTry: python demo.py curriculum  # to see curriculum structure")
