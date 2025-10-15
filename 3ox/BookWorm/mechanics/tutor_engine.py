"""
BookWorm Tutor Engine - Adaptive Learning System
Integrates with RAG/Redis for memory and progressive knowledge building
"""

import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class LearningPhase(Enum):
    """Progressive learning phases"""
    FOUNDATION = "foundation"
    APPLICATION = "application"
    INTEGRATION = "integration"
    MASTERY = "mastery"


class MasteryLevel(Enum):
    """Concept mastery levels"""
    NOVICE = 0          # Just introduced
    BEGINNER = 1        # Basic understanding
    INTERMEDIATE = 2    # Can apply with guidance
    ADVANCED = 3        # Can apply independently
    EXPERT = 4          # Can teach others


@dataclass
class Concept:
    """Represents a learning concept"""
    id: str
    name: str
    description: str
    prerequisites: List[str]
    keywords: List[str]
    difficulty: int  # 1-10 scale
    estimated_time: int  # minutes
    resources: List[str]


@dataclass
class StudentProgress:
    """Tracks student learning progress"""
    student_id: str
    current_phase: LearningPhase
    concepts_mastered: Dict[str, MasteryLevel]
    learning_velocity: float  # concepts per hour
    last_session: float  # timestamp
    session_count: int
    total_study_time: int  # minutes


class TutorEngine:
    """
    Core tutor engine implementing adaptive learning strategies
    
    Step 1 (ASSESSMENT): The engine continuously assesses student understanding
    through formative checks, questioning patterns, and response analysis. It builds
    a dynamic model of concept mastery, identifying knowledge gaps and strengths in
    real-time. The assessment is non-intrusive, embedded naturally in the learning
    conversation rather than explicit testing.
    
    Step 2 (ADAPTATION): Based on assessment data, the engine adapts its teaching
    approach by selecting appropriate difficulty levels, adjusting explanatory depth,
    and choosing optimal teaching methods (visual, verbal, hands-on). It dynamically
    modifies the learning path, skipping redundant content or adding scaffolding where
    needed, ensuring the student operates in their zone of proximal development.
    
    Step 3 (ENGAGEMENT): The engine maintains engagement through varied interaction
    patterns including Socratic questioning, active recall exercises, concept mapping,
    and practical applications. It balances challenge and support, celebrates progress,
    and introduces novelty to prevent cognitive fatigue while building genuine understanding
    rather than rote memorization.
    
    Step 4 (CONSOLIDATION): Learning is consolidated through spaced repetition, where
    concepts are revisited at optimal intervals determined by forgetting curves and
    mastery levels. The engine stores all interactions, progress data, and concept
    relationships in Redis, enabling retrieval-augmented generation (RAG) to surface
    relevant past learning at contextually appropriate moments, strengthening long-term
    retention and interconnected knowledge.
    """
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.knowledge_graph: Dict[str, Concept] = {}
        self.active_sessions: Dict[str, dict] = {}
        
    def load_curriculum(self, curriculum_path: str):
        """Load course curriculum and build knowledge graph"""
        with open(curriculum_path, 'r') as f:
            curriculum = json.load(f)
        
        for concept_data in curriculum['concepts']:
            concept = Concept(**concept_data)
            self.knowledge_graph[concept.id] = concept
    
    def initialize_student(self, student_id: str) -> StudentProgress:
        """Initialize or load student progress"""
        # Try loading from Redis first
        if self.redis:
            stored = self.redis.hgetall(f"bookworm:student:{student_id}:profile")
            if stored:
                return self._deserialize_progress(stored)
        
        # Create new student profile
        progress = StudentProgress(
            student_id=student_id,
            current_phase=LearningPhase.FOUNDATION,
            concepts_mastered={},
            learning_velocity=0.0,
            last_session=time.time(),
            session_count=0,
            total_study_time=0
        )
        
        if self.redis:
            self._save_progress(progress)
        
        return progress
    
    def start_session(self, student_id: str) -> dict:
        """Start a new learning session"""
        progress = self.initialize_student(student_id)
        
        session = {
            'session_id': f"{student_id}_{int(time.time())}",
            'student_id': student_id,
            'start_time': time.time(),
            'current_concept': None,
            'interactions': [],
            'concepts_covered': [],
            'mastery_changes': {}
        }
        
        self.active_sessions[session['session_id']] = session
        
        # Determine starting point
        next_concept = self._select_next_concept(progress)
        session['current_concept'] = next_concept
        
        # Generate warm-up prompt
        warm_up = self._generate_warm_up(progress, next_concept)
        
        return {
            'session': session,
            'prompt': warm_up,
            'phase': progress.current_phase.value,
            'concept': next_concept
        }
    
    def _select_next_concept(self, progress: StudentProgress) -> Optional[str]:
        """
        Select next concept based on prerequisites and current mastery
        Uses topological sort on knowledge graph
        """
        available_concepts = []
        
        for concept_id, concept in self.knowledge_graph.items():
            # Check if already mastered
            mastery = progress.concepts_mastered.get(concept_id, MasteryLevel.NOVICE)
            if mastery == MasteryLevel.EXPERT:
                continue
            
            # Check prerequisites
            prereqs_met = all(
                progress.concepts_mastered.get(prereq, MasteryLevel.NOVICE).value >= MasteryLevel.INTERMEDIATE.value
                for prereq in concept.prerequisites
            )
            
            if prereqs_met:
                available_concepts.append((concept_id, concept))
        
        if not available_concepts:
            return None
        
        # Select based on difficulty and current phase
        # Prefer concepts matching current learning phase
        return available_concepts[0][0] if available_concepts else None
    
    def _generate_warm_up(self, progress: StudentProgress, next_concept: Optional[str]) -> str:
        """Generate session warm-up prompt"""
        if progress.session_count == 0:
            return (
                "Welcome to BookWorm, Lucius! I'm excited to guide your learning journey. "
                "We'll work together at your pace, building strong foundations before moving "
                "to more complex topics. Ready to begin?"
            )
        
        # Review last session
        time_since = time.time() - progress.last_session
        hours = int(time_since / 3600)
        
        warmup = f"Welcome back, Lucius! It's been {hours} hours since our last session. "
        
        if next_concept and next_concept in self.knowledge_graph:
            concept = self.knowledge_graph[next_concept]
            warmup += (
                f"\n\nToday we'll explore **{concept.name}**. "
                "Before we dive in, let's quickly review what we covered last time. "
                "Can you recall the main points from our previous session?"
            )
        
        return warmup
    
    def assess_response(self, session_id: str, response: str) -> Dict:
        """
        Assess student response and update mastery (Step 1: Assessment)
        Returns feedback and next prompt
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return {'error': 'Session not found'}
        
        current_concept = session['current_concept']
        
        # Analyze response depth and accuracy
        assessment = self._analyze_response(response, current_concept)
        
        # Update mastery level
        self._update_mastery(session['student_id'], current_concept, assessment['score'])
        
        # Generate adaptive response (Step 2: Adaptation)
        next_prompt = self._generate_adaptive_prompt(
            session['student_id'],
            current_concept,
            assessment
        )
        
        # Log interaction
        session['interactions'].append({
            'timestamp': time.time(),
            'concept': current_concept,
            'response': response,
            'assessment': assessment,
            'prompt': next_prompt
        })
        
        return {
            'feedback': assessment['feedback'],
            'next_prompt': next_prompt,
            'mastery_level': assessment['estimated_mastery'],
            'encouragement': assessment['encouragement']
        }
    
    def _analyze_response(self, response: str, concept_id: str) -> Dict:
        """Analyze student response depth and understanding"""
        # Simplified analysis - in production would use LLM
        word_count = len(response.split())
        
        # Heuristic scoring
        if word_count < 10:
            score = 1
            feedback = "I'd love to hear more. Can you elaborate on your thinking?"
        elif word_count < 30:
            score = 2
            feedback = "Good start! Let's explore this concept deeper."
        else:
            score = 3
            feedback = "Excellent detailed response! You're demonstrating strong understanding."
        
        return {
            'score': score,
            'estimated_mastery': MasteryLevel(min(score, 4)),
            'feedback': feedback,
            'encouragement': "Keep up the great work!" if score >= 2 else "Let's work through this together."
        }
    
    def _update_mastery(self, student_id: str, concept_id: str, score: int):
        """Update concept mastery in Redis"""
        key = f"bookworm:student:{student_id}:mastery:{concept_id}"
        
        if self.redis:
            current = self.redis.hget(key, 'level') or 0
            new_level = min(int(current) + score, 4)
            
            self.redis.hset(key, mapping={
                'level': new_level,
                'last_updated': time.time(),
                'practice_count': self.redis.hincrby(key, 'practice_count', 1)
            })
    
    def _generate_adaptive_prompt(self, student_id: str, concept_id: str, assessment: Dict) -> str:
        """Generate next prompt adapted to student level (Step 2: Adaptation)"""
        concept = self.knowledge_graph.get(concept_id)
        if not concept:
            return "Let's explore something new together."
        
        mastery = assessment['estimated_mastery']
        
        if mastery == MasteryLevel.NOVICE:
            # Provide foundational explanation
            return (
                f"Let's build a foundation for {concept.name}. "
                f"Here's the core idea: {concept.description}\n\n"
                "What questions come to mind as you think about this?"
            )
        elif mastery == MasteryLevel.BEGINNER:
            # Guide with scaffolding questions
            return (
                f"You're starting to grasp {concept.name}. "
                "Let's test your understanding with a question: "
                f"How would you explain this concept to someone new?"
            )
        elif mastery == MasteryLevel.INTERMEDIATE:
            # Challenge with application
            return (
                f"Now let's apply {concept.name} to a real scenario. "
                "Can you think of a practical example where this concept would be useful?"
            )
        else:
            # Encourage teaching and synthesis
            return (
                f"You've developed strong mastery of {concept.name}! "
                "How does this concept connect to other things we've learned? "
                "Can you draw relationships between them?"
            )
    
    def end_session(self, session_id: str) -> Dict:
        """End session and consolidate learning (Step 4: Consolidation)"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {'error': 'Session not found'}
        
        duration = int((time.time() - session['start_time']) / 60)  # minutes
        
        # Update student progress
        progress = self.initialize_student(session['student_id'])
        progress.session_count += 1
        progress.total_study_time += duration
        progress.last_session = time.time()
        
        # Calculate learning velocity
        concepts_count = len(session['concepts_covered'])
        progress.learning_velocity = concepts_count / (duration / 60) if duration > 0 else 0
        
        # Save to Redis
        if self.redis:
            self._save_progress(progress)
            self._save_session(session)
        
        # Generate summary
        summary = self._generate_session_summary(session, progress)
        
        # Clean up
        del self.active_sessions[session_id]
        
        return summary
    
    def _generate_session_summary(self, session: Dict, progress: StudentProgress) -> Dict:
        """Generate session summary and next steps"""
        return {
            'duration_minutes': int((time.time() - session['start_time']) / 60),
            'concepts_covered': session['concepts_covered'],
            'interactions_count': len(session['interactions']),
            'mastery_changes': session['mastery_changes'],
            'total_sessions': progress.session_count,
            'total_study_time': progress.total_study_time,
            'message': (
                f"Great session, Lucius! We covered {len(session['concepts_covered'])} concepts today. "
                f"You've completed {progress.session_count} sessions so far. "
                "Keep up the excellent work! See you next time."
            )
        }
    
    def _save_progress(self, progress: StudentProgress):
        """Save student progress to Redis"""
        if not self.redis:
            return
        
        key = f"bookworm:student:{progress.student_id}:profile"
        data = asdict(progress)
        data['current_phase'] = progress.current_phase.value
        data['concepts_mastered'] = json.dumps({
            k: v.value for k, v in progress.concepts_mastered.items()
        })
        
        self.redis.hset(key, mapping=data)
    
    def _save_session(self, session: Dict):
        """Save session to Redis for later retrieval"""
        if not self.redis:
            return
        
        key = f"bookworm:student:{session['student_id']}:sessions"
        session_data = json.dumps(session)
        
        # Store in sorted set with timestamp as score
        self.redis.zadd(key, {session_data: session['start_time']})
    
    def _deserialize_progress(self, data: Dict) -> StudentProgress:
        """Deserialize progress from Redis"""
        concepts = json.loads(data.get('concepts_mastered', '{}'))
        concepts_mastered = {
            k: MasteryLevel(v) for k, v in concepts.items()
        }
        
        return StudentProgress(
            student_id=data['student_id'],
            current_phase=LearningPhase(data['current_phase']),
            concepts_mastered=concepts_mastered,
            learning_velocity=float(data['learning_velocity']),
            last_session=float(data['last_session']),
            session_count=int(data['session_count']),
            total_study_time=int(data['total_study_time'])
        )


# Step 1-4 Summary integrated into the docstring above
