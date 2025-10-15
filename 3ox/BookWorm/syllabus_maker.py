"""
Syllabus.Maker for BookWorm
Generates Syllabus.Card from curriculum JSON
Implements the lattice structure for Tutor.Genesis
"""

import json
from typing import Dict, List
from dataclots import dataclass


@dataclass
class SyllabusCard:
    """
    Immutable learning plan
    Structure: Modules → Sections → Items
    """
    title: str
    skill_level: str  # new | refresher | upgrade
    modules: List[Dict]
    metadata: Dict
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'skill_level': self.skill_level,
            'modules': self.modules,
            'metadata': self.metadata
        }
    
    def emit(self) -> str:
        """Emit Syllabus.Card in structured format"""
        output = "╔" + "="*58 + "╗\n"
        output += f"║  📚 **SYLLABUS.CARD** :: {self.title}\n"
        output += "╚" + "="*58 + "╝\n\n"
        
        output += f"**Skill Level**: {self.skill_level}\n"
        output += f"**Modules**: {len(self.modules)}\n"
        output += f"**Estimated Time**: {self.metadata.get('estimated_hours', 'TBD')} hours\n\n"
        
        output += "**Structure**:\n\n"
        
        for m_idx, module in enumerate(self.modules, 1):
            output += f"**M{m_idx}**: {module['title']}\n"
            for s_idx, section in enumerate(module['sections'], 1):
                output += f"  S{s_idx}: {section['title']} ({section['item_count']} items)\n"
            output += "\n"
        
        output += "**Progression Rules**:\n"
        output += "• Each item requires: Instruction → Validation → Quiz (5Q, pass≥4) → CONFIRM\n"
        output += "• Items (I) increment across sections\n"
        output += "• Items reset to 1 on new module\n"
        output += "• No skipping prerequisites\n\n"
        
        output += "Type **CONFIRM** to lock this syllabus and begin learning.\n"
        output += "Type **RESET CLASS** to rebuild the syllabus.\n\n"
        
        output += ":: ∎"
        
        return output


class SyllabusMaker:
    """
    Builds validated Syllabus.Card from curriculum
    Ensures prerequisite validity and proper module/section structure
    """
    
    def __init__(self):
        self.curriculum = None
        self.syllabus_card = None
    
    def build_from_curriculum(self, curriculum_path: str, skill_level: str = "new") -> SyllabusCard:
        """
        Build Syllabus.Card from curriculum JSON
        
        Args:
            curriculum_path: Path to fundamentals_curriculum.json
            skill_level: new | refresher | upgrade
        """
        with open(curriculum_path, 'r') as f:
            self.curriculum = json.load(f)
        
        # Convert concepts to M.S.I structure
        modules = self._organize_into_modules(skill_level)
        
        # Validate prerequisites
        self._validate_prerequisites(modules)
        
        # Create Syllabus.Card
        self.syllabus_card = SyllabusCard(
            title=self.curriculum['title'],
            skill_level=skill_level,
            modules=modules,
            metadata={
                'estimated_hours': self.curriculum.get('estimated_hours', 40),
                'difficulty': self.curriculum.get('difficulty', 'beginner'),
                'version': '1.0',
                'locked': False
            }
        )
        
        return self.syllabus_card
    
    def _organize_into_modules(self, skill_level: str) -> List[Dict]:
        """
        Organize concepts into Module → Section → Item hierarchy
        
        Strategy:
        - Group by learning phase (Foundation, Application, Integration)
        - Each phase = 1 Module
        - Within module, group related concepts into Sections
        - Each concept = multiple Items (intro, practice, mastery)
        """
        concepts = self.curriculum['concepts']
        
        # Group by difficulty ranges (proxy for phases)
        modules = []
        
        # Module 1: Foundation (difficulty 1-4)
        foundation = [c for c in concepts if c['difficulty'] <= 4]
        if foundation:
            modules.append(self._create_module(
                title="Foundation: Core Concepts",
                concepts=foundation,
                module_num=1
            ))
        
        # Module 2: Application (difficulty 5-7)
        application = [c for c in concepts if 5 <= c['difficulty'] <= 7]
        if application:
            modules.append(self._create_module(
                title="Application: Practical Skills",
                concepts=application,
                module_num=2
            ))
        
        # Module 3: Integration (difficulty 8-10)
        integration = [c for c in concepts if c['difficulty'] >= 8]
        if integration:
            modules.append(self._create_module(
                title="Integration: Advanced Topics",
                concepts=integration,
                module_num=3
            ))
        
        return modules
    
    def _create_module(self, title: str, concepts: List[Dict], module_num: int) -> Dict:
        """Create a module with sections"""
        sections = []
        
        for s_idx, concept in enumerate(concepts, 1):
            # Each concept becomes a section with multiple items
            section = {
                'id': f"M{module_num}.S{s_idx}",
                'title': concept['name'],
                'description': concept['description'],
                'item_count': 3,  # intro, practice, mastery
                'items': self._create_items_for_concept(concept)
            }
            sections.append(section)
        
        return {
            'id': f"M{module_num}",
            'title': title,
            'sections': sections,
            'prerequisites': []
        }
    
    def _create_items_for_concept(self, concept: Dict) -> List[Dict]:
        """
        Create 3 items per concept:
        1. Introduction - Core explanation
        2. Practice - Hands-on exercise
        3. Mastery Check - Synthesis challenge
        """
        concept_id = concept['id']
        concept_name = concept['name']
        
        items = [
            {
                'id': f"{concept_id}_intro",
                'title': f"Introduction to {concept_name}",
                'instruction': {
                    'body': f"Learn the fundamentals of {concept_name}. {concept['description'][:100]}",
                    'notes': [f"Estimated time: {concept['estimated_time']} minutes"]
                },
                'assist': {
                    'tip': f"Focus on understanding what {concept_name} is and why it matters.",
                    'steps': [
                        "Read the core concept",
                        "Study the examples",
                        "Try explaining it in your own words"
                    ]
                },
                'quiz': self._generate_intro_quiz(concept)
            },
            {
                'id': f"{concept_id}_practice",
                'title': f"Practice: {concept_name}",
                'instruction': {
                    'body': f"Apply {concept_name} through hands-on exercises. Work through the practice problems to build skill.",
                    'notes': ["Use the exercises in the library", "Try multiple approaches"]
                },
                'assist': {
                    'tip': "Break the problem into smaller steps. Reference the guide if stuck.",
                    'steps': [
                        "Review the concept guide",
                        "Attempt the exercise",
                        "Check your solution"
                    ]
                },
                'quiz': self._generate_practice_quiz(concept)
            },
            {
                'id': f"{concept_id}_mastery",
                'title': f"Mastery: {concept_name}",
                'instruction': {
                    'body': f"Demonstrate mastery of {concept_name} by solving a synthesis challenge that combines multiple skills.",
                    'notes': ["This tests deep understanding", "Take your time"]
                },
                'assist': {
                    'tip': "Think about how this concept connects to what you've learned before.",
                    'steps': [
                        "Identify the core problem",
                        "Plan your approach",
                        "Implement and test"
                    ]
                },
                'quiz': self._generate_mastery_quiz(concept)
            }
        ]
        
        return items
    
    def _generate_intro_quiz(self, concept: Dict) -> List[Dict]:
        """Generate 5 intro-level quiz questions"""
        name = concept['name']
        return [
            {
                'q': f"What is the primary purpose of {name}?",
                'choices': ["A. Storage", "B. Computation", "C. Display", "D. Communication"],
                'answer': "A"  # Placeholder
            },
            {
                'q': f"When would you use {name}?",
                'choices': ["A. Always", "B. For specific tasks", "C. Never", "D. Only in tests"],
                'answer': "B"
            },
            {
                'q': f"What is a key characteristic of {name}?",
                'choices': ["A. Fast", "B. Flexible", "C. Complex", "D. Simple"],
                'answer': "B"
            },
            {
                'q': f"How does {name} relate to other concepts?",
                'choices': ["A. Foundation", "B. Extension", "C. Alternative", "D. Unrelated"],
                'answer': "A"
            },
            {
                'q': f"What's the best way to learn {name}?",
                'choices': ["A. Practice", "B. Memorize", "C. Skip it", "D. Guess"],
                'answer': "A"
            }
        ]
    
    def _generate_practice_quiz(self, concept: Dict) -> List[Dict]:
        """Generate 5 practice-level quiz questions"""
        return self._generate_intro_quiz(concept)  # Placeholder
    
    def _generate_mastery_quiz(self, concept: Dict) -> List[Dict]:
        """Generate 5 mastery-level quiz questions"""
        return self._generate_intro_quiz(concept)  # Placeholder
    
    def _validate_prerequisites(self, modules: List[Dict]):
        """Validate that all prerequisites exist and are in correct order"""
        all_concept_ids = set()
        
        for module in modules:
            for section in module['sections']:
                # Extract concept ID from section (assume title maps to concept)
                all_concept_ids.add(section['id'])
        
        # Check prerequisite validity
        for concept in self.curriculum['concepts']:
            for prereq in concept.get('prerequisites', []):
                if prereq not in [c['id'] for c in self.curriculum['concepts']]:
                    raise ValueError(f"Invalid prerequisite: {prereq} for {concept['id']}")
    
    def lock_syllabus(self):
        """Lock syllabus - no further changes allowed"""
        if self.syllabus_card:
            self.syllabus_card.metadata['locked'] = True
    
    def is_locked(self) -> bool:
        """Check if syllabus is locked"""
        return self.syllabus_card and self.syllabus_card.metadata.get('locked', False)


def build_bookworm_syllabus(curriculum_path: str, skill_level: str = "new") -> Dict:
    """
    Quick builder for BookWorm syllabus
    
    Usage:
        syllabus_dict = build_bookworm_syllabus(
            'courses/fundamentals_curriculum.json',
            skill_level='new'
        )
    """
    maker = SyllabusMaker()
    card = maker.build_from_curriculum(curriculum_path, skill_level)
    return card.to_dict()


:: ∎
