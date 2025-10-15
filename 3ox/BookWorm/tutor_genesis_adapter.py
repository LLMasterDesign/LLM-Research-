"""
Tutor.Genesis Adapter for BookWorm
Implements the lattice-locked LU system with validation gates and quiz mechanics
Based on: https://github.com/LLarzMasterD/LLMD-Prompt-Substructures/blob/main/Step-Tutor.v2.gen
"""

import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class TutorMode(Enum):
    """Tutor operating modes"""
    INSTRUCTION = "instruction"
    ASSIST = "assist"
    QUIZ = "quiz"


class AwaitingState(Enum):
    """What tutor is waiting for"""
    NONE = "none"
    VALIDATION = "validation"
    ANSWERS = "answers"
    CONFIRM = "confirm"


class RecapType(Enum):
    """Recap scope"""
    MINOR = "minor"  # Section-level
    MAJOR = "major"  # Module boundary


@dataclass
class LUPath:
    """Liminal Unit Path: ⧉:[M{m}.S{n}.I{k}]"""
    M: int  # Module
    S: int  # Section
    I: int  # Item
    
    def __str__(self):
        return f"⧉:[M{self.M}.S{self.S}.I{self.I}]"
    
    def section_only(self):
        """Return section-level path"""
        return f"⧉:[M{self.M}.S{self.S}]"
    
    def module_only(self):
        """Return module-level path"""
        return f"⧉:[M{self.M}]"


@dataclass
class InstructionBox:
    """Instruction.Box - Core teaching content"""
    lu_path: str
    body: str  # ≤3 sentences
    notes: List[str] = None
    
    def emit(self) -> str:
        output = f"{self.lu_path}\n\n"
        output += f"**Instruction** ::\n{self.body}\n"
        if self.notes:
            output += "\n**Notes**:\n"
            for note in self.notes:
                output += f"• {note}\n"
        output += "\n:: ∎"
        return output


@dataclass
class AssistBox:
    """Assist.Box - Help during validation"""
    lu_path: str
    tip: str  # One-sentence nudge
    steps: List[str] = None  # ≤3 micro-steps
    
    def emit(self) -> str:
        output = f"{self.lu_path}\n\n"
        output += f"**Assist** ::\n{self.tip}\n"
        if self.steps:
            output += "\n**Steps**:\n"
            for i, step in enumerate(self.steps[:3], 1):
                output += f"{i}. {step}\n"
        output += "\n:: ∎"
        return output


@dataclass
class QuizBox:
    """Quiz.Box - 5-question validation gate"""
    lu_path: str
    questions: List[Dict]  # Exactly 5 questions
    
    def emit(self) -> str:
        output = f"{self.lu_path}\n\n"
        output += "**Quiz** ::\n\n"
        for i, q in enumerate(self.questions, 1):
            output += f"{i}. {q['q']}\n"
            for choice in q['choices']:
                output += f"   {choice}\n"
            output += "\n"
        output += "**Submit your answers** (e.g., \"1:B, 2:A, 3:C, 4:A, 5:B\")\n"
        output += "\n:: ∎"
        return output
    
    def score(self, answers: Dict[int, str]) -> Tuple[int, List[int]]:
        """Score quiz answers. Returns (score, wrong_indices)"""
        correct = 0
        wrong = []
        for i, q in enumerate(self.questions, 1):
            user_answer = answers.get(i, "").strip().upper()
            if user_answer == q['answer'].upper():
                correct += 1
            else:
                wrong.append(i)
        return correct, wrong


@dataclass
class RecapBlock:
    """Recap.Block - Progress summary"""
    lu_path: str
    recap_type: RecapType
    learned: List[str]
    pending: List[str]
    next_lu: str
    notes: List[str] = None
    
    def emit(self) -> str:
        output = f"{self.lu_path}\n\n"
        output += f"**Recap** ({self.recap_type.value}) ::\n\n"
        
        if self.learned:
            output += "**Learned**:\n"
            for item in self.learned:
                output += f"✓ {item}\n"
            output += "\n"
        
        if self.pending:
            output += "**Pending**:\n"
            for item in self.pending:
                output += f"○ {item}\n"
            output += "\n"
        
        output += f"**Next**: {self.next_lu}\n"
        
        if self.notes:
            output += "\n**Notes**:\n"
            for note in self.notes:
                output += f"• {note}\n"
        
        output += "\n:: ∎"
        return output


class TutorGenesisEngine:
    """
    Lattice-Locked Tutor Engine
    
    Implements:
    - LU (Liminal Unit) progression: M.S.I counters
    - Lockstep flow: Instruction → Validation → Quiz(5) → Confirm → Advance
    - Drift prevention: Thread lock, no unplanned steps
    - State persistence: Resume with recap
    - Command tokens: DONE, HELP, REPEAT, CONFIRM, etc.
    """
    
    def __init__(self, syllabus_card: Dict, redis_client=None):
        self.syllabus = syllabus_card
        self.redis = redis_client
        
        # State counters
        self.M = 1  # Current module
        self.S = 1  # Current section
        self.I = 1  # Current item
        
        # Engine state
        self.mode = TutorMode.INSTRUCTION
        self.awaiting = AwaitingState.NONE
        self.current_box = None
        self.current_quiz = None
        self.quiz_attempts = 0
        
        # Session tracking
        self.session_id = f"session_{int(time.time())}"
        self.learned_items = []
        self.progress_log = []
        
    def get_lu_path(self) -> LUPath:
        """Get current LU path"""
        return LUPath(M=self.M, S=self.S, I=self.I)
    
    def start_instruction(self) -> str:
        """Emit Instruction.Box for current LU"""
        lu = self.get_lu_path()
        
        # Get instruction content from syllabus
        content = self._get_instruction_content(self.M, self.S, self.I)
        
        instruction = InstructionBox(
            lu_path=str(lu),
            body=content['body'],
            notes=content.get('notes', [])
        )
        
        self.mode = TutorMode.INSTRUCTION
        self.awaiting = AwaitingState.VALIDATION
        self.current_box = instruction
        
        self._log_progress(f"Instruction emitted: {lu}")
        
        output = instruction.emit()
        output += "\n\n**Available commands**: DONE (complete) | HELP (assistance) | REPEAT (re-emit)\n"
        
        return output
    
    def handle_validation_token(self, token: str) -> str:
        """Handle validation tokens: DONE, HELP, REPEAT"""
        token = token.strip().upper()
        
        if token == "DONE":
            # User asserts completion → move to quiz
            return self.emit_quiz()
        
        elif token == "HELP":
            # Emit Assist.Box
            return self.emit_assist()
        
        elif token == "REPEAT":
            # Re-emit current Instruction.Box
            if self.current_box:
                return self.current_box.emit() + "\n\n**Commands**: DONE | HELP | REPEAT\n"
            return "No instruction to repeat."
        
        else:
            return (
                f"⚠️ Unknown token: '{token}'\n\n"
                "**Valid commands**: DONE | HELP | REPEAT\n"
            )
    
    def emit_assist(self) -> str:
        """Emit Assist.Box for current LU"""
        lu = self.get_lu_path()
        
        # Get assist content from syllabus
        assist_content = self._get_assist_content(self.M, self.S, self.I)
        
        assist = AssistBox(
            lu_path=str(lu),
            tip=assist_content['tip'],
            steps=assist_content.get('steps', [])
        )
        
        self.mode = TutorMode.ASSIST
        # Remain in await.validation state
        
        output = assist.emit()
        output += "\n\n**Commands**: DONE (when ready) | REPEAT (see instruction again)\n"
        
        return output
    
    def emit_quiz(self) -> str:
        """Emit Quiz.Box - 5 questions for current LU"""
        lu = self.get_lu_path()
        
        # Generate 5 questions
        questions = self._generate_quiz_questions(self.M, self.S, self.I)
        
        quiz = QuizBox(
            lu_path=str(lu),
            questions=questions
        )
        
        self.mode = TutorMode.QUIZ
        self.awaiting = AwaitingState.ANSWERS
        self.current_quiz = quiz
        self.quiz_attempts += 1
        
        self._log_progress(f"Quiz emitted: {lu}, attempt {self.quiz_attempts}")
        
        return quiz.emit()
    
    def score_quiz(self, answers_str: str) -> str:
        """
        Score quiz answers and handle pass/fail
        
        Args:
            answers_str: Format "1:B, 2:A, 3:C, 4:A, 5:B" or similar
        """
        if not self.current_quiz:
            return "⚠️ No active quiz to score."
        
        # Parse answers
        answers = self._parse_answers(answers_str)
        
        if not answers or len(answers) != 5:
            return (
                "⚠️ Invalid answer format. Please provide 5 answers.\n"
                "Example: \"1:B, 2:A, 3:C, 4:A, 5:B\"\n"
            )
        
        # Score
        score, wrong = self.current_quiz.score(answers)
        
        self._log_progress(f"Quiz scored: {score}/5, wrong: {wrong}")
        
        if score >= 4:
            # PASS - proceed
            return self._handle_quiz_pass(score)
        else:
            # FAIL - re-quiz
            return self._handle_quiz_fail(score, wrong)
    
    def _handle_quiz_pass(self, score: int) -> str:
        """Handle quiz pass (≥4/5)"""
        lu = self.get_lu_path()
        
        output = f"✅ **Quiz Passed**: {score}/5\n\n"
        output += f"Great work on {lu}! You've demonstrated understanding.\n\n"
        output += "**PROCEED?**\n\n"
        output += "Type **CONFIRM** to advance to the next learning unit.\n"
        
        self.awaiting = AwaitingState.CONFIRM
        
        return output
    
    def _handle_quiz_fail(self, score: int, wrong: List[int]) -> str:
        """Handle quiz fail (<4/5)"""
        lu = self.get_lu_path()
        
        output = f"❌ **Quiz Score**: {score}/5 (need ≥4 to pass)\n\n"
        output += f"Questions {', '.join(map(str, wrong))} need review.\n\n"
        
        if self.quiz_attempts >= 2:
            output += "**Suggestion**: Type **REPEAT** to review the instruction, then try the quiz again.\n\n"
        
        output += "**Options**:\n"
        output += "• **QUIZ** - Try quiz again (different questions)\n"
        output += "• **REPEAT** - Review instruction\n"
        output += "• **HELP** - Get assistance\n"
        
        self.awaiting = AwaitingState.VALIDATION
        self.mode = TutorMode.INSTRUCTION
        
        return output
    
    def confirm_advance(self) -> str:
        """Handle CONFIRM token - advance LU counters"""
        if self.awaiting != AwaitingState.CONFIRM:
            return "⚠️ Nothing to confirm. Complete current instruction first."
        
        old_lu = self.get_lu_path()
        
        # Log completion
        self.learned_items.append(str(old_lu))
        self._log_progress(f"Completed: {old_lu}")
        
        # Advance counters based on syllabus structure
        advanced = self._advance_lu()
        
        new_lu = self.get_lu_path()
        
        # Generate brief progress message
        output = f"📍 **Progress**: {old_lu} → {new_lu}\n\n"
        
        if advanced == 'module':
            output += f"🎉 **Module {old_lu.M} Complete!**\n\n"
            # Major recap
            recap = self._generate_recap(RecapType.MAJOR)
            output += recap.emit() + "\n\n"
        elif advanced == 'section':
            output += f"✓ **Section {old_lu.M}.{old_lu.S} Complete!**\n\n"
            # Minor recap
            recap = self._generate_recap(RecapType.MINOR)
            output += recap.emit() + "\n\n"
        
        # Reset quiz attempts for new LU
        self.quiz_attempts = 0
        
        # Start next instruction
        output += "\n" + "="*60 + "\n\n"
        output += self.start_instruction()
        
        return output
    
    def _advance_lu(self) -> str:
        """
        Advance LU counters following progression rules:
        - Items (I) increment across sections within same module
        - Sections (S) increment when section completes
        - Modules (M) increment when module completes (I resets to 1)
        
        Returns: 'item', 'section', or 'module' indicating what advanced
        """
        # Get module/section structure from syllabus
        module = self.syllabus['modules'][self.M - 1]
        section = module['sections'][self.S - 1]
        
        # Check if more items in current section
        if self.I < section['item_count']:
            self.I += 1
            return 'item'
        
        # Check if more sections in current module
        if self.S < len(module['sections']):
            self.S += 1
            self.I += 1  # Items persist across sections
            return 'section'
        
        # Check if more modules
        if self.M < len(self.syllabus['modules']):
            self.M += 1
            self.S = 1
            self.I = 1  # Items reset on new module
            return 'module'
        
        # Course complete!
        return 'complete'
    
    def _generate_recap(self, recap_type: RecapType) -> RecapBlock:
        """Generate recap block"""
        lu = self.get_lu_path()
        
        if recap_type == RecapType.MINOR:
            # Section-level recap
            lu_path = lu.section_only()
            learned = self.learned_items[-5:]  # Last 5 items
            pending = self._get_pending_items()
            next_lu = str(LUPath(self.M, self.S, self.I))
        else:
            # Module-level recap
            lu_path = lu.module_only()
            learned = [item for item in self.learned_items if item.startswith(f"⧉:[M{self.M}")]
            pending = []
            next_lu = str(LUPath(self.M + 1, 1, 1)) if self.M < len(self.syllabus['modules']) else "Course Complete"
        
        return RecapBlock(
            lu_path=lu_path,
            recap_type=recap_type,
            learned=learned,
            pending=pending,
            next_lu=next_lu
        )
    
    def handle_command(self, command: str) -> str:
        """Handle command tokens"""
        cmd = command.strip().upper()
        
        if cmd == "PAUSE":
            return self.emit_pause()
        elif cmd == "RESUME":
            return self.emit_resume()
        elif cmd == "RECAP":
            recap = self._generate_recap(RecapType.MINOR)
            return recap.emit()
        elif cmd == "CONFIRM":
            return self.confirm_advance()
        elif cmd == "QUIZ":
            return self.emit_quiz()
        elif cmd in ["DONE", "HELP", "REPEAT"]:
            return self.handle_validation_token(cmd)
        else:
            return f"⚠️ Unknown command: '{cmd}'"
    
    def emit_pause(self) -> str:
        """Pause session with recap"""
        recap = self._generate_recap(RecapType.MINOR)
        
        # Save state to Redis
        if self.redis:
            self._save_state()
        
        output = "⏸️ **Session Paused**\n\n"
        output += recap.emit()
        output += "\n\nType **RESUME** to continue from where you left off.\n"
        
        return output
    
    def emit_resume(self) -> str:
        """Resume session from saved state"""
        # Load state from Redis
        if self.redis:
            self._load_state()
        
        lu = self.get_lu_path()
        recap = self._generate_recap(RecapType.MINOR)
        
        output = "▶️ **Session Resumed**\n\n"
        output += recap.emit()
        output += f"\n\nContinuing at {lu}...\n\n"
        output += "="*60 + "\n\n"
        output += self.start_instruction()
        
        return output
    
    def _get_instruction_content(self, M: int, S: int, I: int) -> Dict:
        """Get instruction content from syllabus"""
        try:
            module = self.syllabus['modules'][M - 1]
            section = module['sections'][S - 1]
            item = section['items'][I - 1]
            return item['instruction']
        except (IndexError, KeyError):
            return {
                'body': f"Instruction content for M{M}.S{S}.I{I} (placeholder)",
                'notes': []
            }
    
    def _get_assist_content(self, M: int, S: int, I: int) -> Dict:
        """Get assist content from syllabus"""
        try:
            module = self.syllabus['modules'][M - 1]
            section = module['sections'][S - 1]
            item = section['items'][I - 1]
            return item.get('assist', {
                'tip': "Review the instruction carefully and try again.",
                'steps': []
            })
        except (IndexError, KeyError):
            return {
                'tip': "Review the material and try again.",
                'steps': []
            }
    
    def _generate_quiz_questions(self, M: int, S: int, I: int) -> List[Dict]:
        """Generate 5 quiz questions for current LU"""
        try:
            module = self.syllabus['modules'][M - 1]
            section = module['sections'][S - 1]
            item = section['items'][I - 1]
            return item.get('quiz', self._default_quiz())
        except (IndexError, KeyError):
            return self._default_quiz()
    
    def _default_quiz(self) -> List[Dict]:
        """Default quiz questions (placeholder)"""
        return [
            {
                'q': "What is the main concept of this lesson?",
                'choices': ["A. Concept A", "B. Concept B", "C. Concept C"],
                'answer': "B"
            }
        ] * 5
    
    def _get_pending_items(self) -> List[str]:
        """Get list of pending items in current section"""
        try:
            module = self.syllabus['modules'][self.M - 1]
            section = module['sections'][self.S - 1]
            pending = []
            for i in range(self.I, section['item_count'] + 1):
                pending.append(f"I{i}: {section['items'][i-1].get('title', f'Item {i}')}")
            return pending
        except (IndexError, KeyError):
            return []
    
    def _parse_answers(self, answers_str: str) -> Dict[int, str]:
        """Parse answer string into dict"""
        answers = {}
        parts = answers_str.split(',')
        for part in parts:
            if ':' in part:
                q_num, answer = part.split(':', 1)
                try:
                    answers[int(q_num.strip())] = answer.strip()
                except ValueError:
                    continue
        return answers
    
    def _log_progress(self, message: str):
        """Log progress entry"""
        entry = {
            'timestamp': time.time(),
            'M': self.M,
            'S': self.S,
            'I': self.I,
            'mode': self.mode.value,
            'message': message
        }
        self.progress_log.append(entry)
    
    def _save_state(self):
        """Save tutor state to Redis"""
        if not self.redis:
            return
        
        state = {
            'M': self.M,
            'S': self.S,
            'I': self.I,
            'mode': self.mode.value,
            'awaiting': self.awaiting.value,
            'learned_items': self.learned_items,
            'quiz_attempts': self.quiz_attempts,
            'timestamp': time.time()
        }
        
        key = f"bookworm:tutor:state:{self.session_id}"
        self.redis.hset(key, mapping={'state': json.dumps(state)})
    
    def _load_state(self):
        """Load tutor state from Redis"""
        if not self.redis:
            return
        
        key = f"bookworm:tutor:state:{self.session_id}"
        data = self.redis.hget(key, 'state')
        
        if data:
            state = json.loads(data)
            self.M = state['M']
            self.S = state['S']
            self.I = state['I']
            self.mode = TutorMode(state['mode'])
            self.awaiting = AwaitingState(state['awaiting'])
            self.learned_items = state['learned_items']
            self.quiz_attempts = state['quiz_attempts']


:: ∎
