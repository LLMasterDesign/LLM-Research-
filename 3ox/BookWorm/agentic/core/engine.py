#!/usr/bin/env python3
"""
BookWorm Tutor Engine - Agentic Core
Implements Tutor.Genesis lattice-locked teaching system
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class LUPath:
    """Liminal Unit Path: ⧉:[M{m}.S{s}.I{i}]"""
    M: int
    S: int
    I: int
    
    def __str__(self):
        return f"⧉:[M{self.M}.S{self.S}.I{self.I}]"
    
    def section(self):
        return f"⧉:[M{self.M}.S{self.S}]"
    
    def module(self):
        return f"⧉:[M{self.M}]"


@dataclass
class InstructionBox:
    """Instruction content with LU stamp"""
    lu_path: str
    body: str
    notes: List[str] = field(default_factory=list)
    
    def emit(self) -> str:
        output = f"{self.lu_path}\n\n"
        output += f"**Instruction** ::\n{self.body}\n"
        if self.notes:
            output += "\n**Notes**:\n"
            for note in self.notes:
                output += f"• {note}\n"
        output += "\nType **DONE** when complete | **HELP** for assistance | **REPEAT** to review\n"
        output += "\n:: ∎"
        return output


@dataclass
class QuizBox:
    """Quiz with 5 questions"""
    lu_path: str
    questions: List[Dict]
    
    def emit(self) -> str:
        output = f"{self.lu_path}\n\n"
        output += "**Quiz** :: 5 Questions\n\n"
        for i, q in enumerate(self.questions, 1):
            output += f"{i}. {q['q']}\n"
            for choice in q['choices']:
                output += f"   {choice}\n"
            output += "\n"
        output += '**Submit answers**: "1:B, 2:A, 3:C, 4:D, 5:A"\n'
        output += "\n:: ∎"
        return output
    
    def score(self, answers: Dict[int, str]) -> Tuple[int, List[int]]:
        """Score quiz, return (correct_count, wrong_indices)"""
        correct = 0
        wrong = []
        for i, q in enumerate(self.questions, 1):
            user = answers.get(i, "").strip().upper()
            if user == q['answer'].upper():
                correct += 1
            else:
                wrong.append(i)
        return correct, wrong


class BookWormEngine:
    """
    Lattice-Locked Tutor Engine
    
    Flow: Instruction → DONE → Quiz(5) → Pass(≥4) → CONFIRM → Advance
    """
    
    def __init__(self, syllabus: Dict, student_id: str = "lucius"):
        self.syllabus = syllabus
        self.student_id = student_id
        
        # LU Counters
        self.M = 1
        self.S = 1
        self.I = 1
        
        # State
        self.mode = "instruction"  # instruction | quiz | waiting_confirm
        self.awaiting = "none"     # none | validation | answers | confirm
        self.current_quiz = None
        self.quiz_attempts = 0
        
        # Progress
        self.learned_items = []
        self.session_start = time.time()
        self.session_id = f"session_{int(self.session_start)}"
        
    def get_lu(self) -> LUPath:
        """Current LU path"""
        return LUPath(self.M, self.S, self.I)
    
    def start(self) -> str:
        """Start learning session"""
        output = "▛▞ BOOKWORM TUTOR ACTIVE ▮▮▮▮▮▮▮▹\n\n"
        output += f"Hello, {self.student_id.title()}! Ready to master programming fundamentals?\n\n"
        output += self.emit_syllabus_card()
        output += "\n\nType **CONFIRM** to lock this syllabus and begin learning.\n"
        return output
    
    def emit_syllabus_card(self) -> str:
        """Emit syllabus overview"""
        output = "╔" + "="*58 + "╗\n"
        output += "║  📚 **SYLLABUS.CARD** :: Programming Fundamentals\n"
        output += "╚" + "="*58 + "╝\n\n"
        
        output += f"**Modules**: {len(self.syllabus['modules'])}\n"
        output += f"**Total Concepts**: 12\n"
        output += f"**Estimated Time**: 40 hours\n\n"
        
        output += "**Structure**:\n\n"
        for m_idx, module in enumerate(self.syllabus['modules'], 1):
            output += f"**M{m_idx}**: {module['title']}\n"
            for s_idx, section in enumerate(module['sections'], 1):
                item_count = len(section['items'])
                output += f"  S{s_idx}: {section['title']} ({item_count} items)\n"
            output += "\n"
        
        output += "**Learning Flow**: Instruction → DONE → Quiz(5Q) → Pass(≥4) → CONFIRM → Advance\n"
        output += "\n:: ∎"
        return output
    
    def confirm_start(self) -> str:
        """Confirm syllabus and start teaching"""
        output = "✅ **Syllabus Locked**\n\n"
        output += "Beginning at ⧉:[M1.S1.I1]...\n\n"
        output += "="*60 + "\n\n"
        return output + self.emit_instruction()
    
    def emit_instruction(self) -> str:
        """Emit Instruction.Box for current LU"""
        lu = self.get_lu()
        
        # Get content from syllabus
        try:
            module = self.syllabus['modules'][self.M - 1]
            section = module['sections'][self.S - 1]
            item = section['items'][self.I - 1]
            
            instruction = InstructionBox(
                lu_path=str(lu),
                body=item['instruction'],
                notes=item.get('notes', [])
            )
        except (IndexError, KeyError):
            instruction = InstructionBox(
                lu_path=str(lu),
                body=f"Instruction placeholder for {lu}",
                notes=[]
            )
        
        self.mode = "instruction"
        self.awaiting = "validation"
        
        return instruction.emit()
    
    def handle_done(self) -> str:
        """Handle DONE token → emit quiz"""
        if self.awaiting != "validation":
            return "⚠️ No instruction to complete. Current state: " + self.mode
        
        return self.emit_quiz()
    
    def emit_quiz(self) -> str:
        """Emit Quiz.Box with 5 questions"""
        lu = self.get_lu()
        
        # Get quiz from syllabus
        try:
            module = self.syllabus['modules'][self.M - 1]
            section = module['sections'][self.S - 1]
            item = section['items'][self.I - 1]
            questions = item.get('quiz', self._default_quiz())
        except (IndexError, KeyError):
            questions = self._default_quiz()
        
        quiz = QuizBox(lu_path=str(lu), questions=questions)
        
        self.current_quiz = quiz
        self.mode = "quiz"
        self.awaiting = "answers"
        self.quiz_attempts += 1
        
        return quiz.emit()
    
    def score_quiz(self, answers_str: str) -> str:
        """Score quiz answers"""
        if not self.current_quiz:
            return "⚠️ No active quiz to score."
        
        # Parse answers: "1:B, 2:A, 3:C, 4:D, 5:A"
        answers = {}
        for part in answers_str.split(','):
            if ':' in part:
                q, a = part.split(':', 1)
                try:
                    answers[int(q.strip())] = a.strip()
                except ValueError:
                    continue
        
        if len(answers) != 5:
            return '⚠️ Invalid format. Provide 5 answers like: "1:B, 2:A, 3:C, 4:D, 5:A"'
        
        score, wrong = self.current_quiz.score(answers)
        
        if score >= 4:
            return self._handle_pass(score)
        else:
            return self._handle_fail(score, wrong)
    
    def _handle_pass(self, score: int) -> str:
        """Handle quiz pass"""
        lu = self.get_lu()
        
        output = f"✅ **Quiz Passed**: {score}/5\n\n"
        output += f"Excellent work on {lu}! You've demonstrated understanding.\n\n"
        output += "**PROCEED?**\n\n"
        output += "Type **CONFIRM** to advance to the next learning unit.\n"
        
        self.mode = "waiting_confirm"
        self.awaiting = "confirm"
        
        return output
    
    def _handle_fail(self, score: int, wrong: List[int]) -> str:
        """Handle quiz fail"""
        lu = self.get_lu()
        
        output = f"❌ **Quiz Score**: {score}/5 (need ≥4 to pass)\n\n"
        output += f"Questions {', '.join(map(str, wrong))} need review.\n\n"
        
        if self.quiz_attempts >= 2:
            output += "💡 **Suggestion**: Type **REPEAT** to review the instruction.\n\n"
        
        output += "**Options**:\n"
        output += "• **QUIZ** - Try again with new questions\n"
        output += "• **REPEAT** - Review the instruction\n"
        output += "• **HELP** - Get assistance\n"
        
        self.mode = "instruction"
        self.awaiting = "validation"
        
        return output
    
    def confirm_advance(self) -> str:
        """Advance LU counters"""
        if self.awaiting != "confirm":
            return "⚠️ Nothing to confirm right now."
        
        old_lu = self.get_lu()
        self.learned_items.append(str(old_lu))
        
        # Advance
        advanced_type = self._advance_counters()
        
        new_lu = self.get_lu()
        
        output = f"📍 **Progress**: {old_lu} → {new_lu}\n\n"
        
        if advanced_type == 'module':
            output += f"🎉 **Module {old_lu.M} Complete!**\n\n"
            output += self._emit_recap('major')
            output += "\n\n"
        elif advanced_type == 'section':
            output += f"✓ **Section {old_lu.M}.{old_lu.S} Complete!**\n\n"
        elif advanced_type == 'complete':
            return self._emit_course_complete()
        
        self.quiz_attempts = 0
        
        output += "="*60 + "\n\n"
        output += self.emit_instruction()
        
        return output
    
    def _advance_counters(self) -> str:
        """Advance M.S.I counters"""
        try:
            module = self.syllabus['modules'][self.M - 1]
            section = module['sections'][self.S - 1]
            item_count = len(section['items'])
            
            # More items in section?
            if self.I < item_count:
                self.I += 1
                return 'item'
            
            # More sections in module?
            if self.S < len(module['sections']):
                self.S += 1
                self.I += 1  # Items persist across sections
                return 'section'
            
            # More modules?
            if self.M < len(self.syllabus['modules']):
                self.M += 1
                self.S = 1
                self.I = 1  # Items reset on new module
                return 'module'
            
            return 'complete'
        except (IndexError, KeyError):
            return 'complete'
    
    def handle_repeat(self) -> str:
        """Re-emit current instruction"""
        return self.emit_instruction()
    
    def handle_help(self) -> str:
        """Emit assistance"""
        lu = self.get_lu()
        
        try:
            module = self.syllabus['modules'][self.M - 1]
            section = module['sections'][self.S - 1]
            item = section['items'][self.I - 1]
            tip = item.get('assist', "Review the instruction carefully.")
        except (IndexError, KeyError):
            tip = "Break the problem into smaller steps."
        
        output = f"{lu}\n\n"
        output += f"**Assist** ::\n{tip}\n\n"
        output += "Type **DONE** when ready | **REPEAT** to review instruction\n"
        output += "\n:: ∎"
        
        return output
    
    def handle_status(self) -> str:
        """Show current status"""
        lu = self.get_lu()
        
        output = f"📊 **Status**\n\n"
        output += f"**Current**: {lu}\n"
        output += f"**Mode**: {self.mode}\n"
        output += f"**Learned**: {len(self.learned_items)} items\n"
        
        elapsed = int((time.time() - self.session_start) / 60)
        output += f"**Session Time**: {elapsed} minutes\n"
        
        return output
    
    def _emit_recap(self, recap_type: str) -> str:
        """Emit progress recap"""
        lu = self.get_lu()
        
        if recap_type == 'major':
            lu_stamp = lu.module()
            learned = [item for item in self.learned_items if item.startswith(f"⧉:[M{self.M}")]
        else:
            lu_stamp = lu.section()
            learned = self.learned_items[-5:]
        
        output = f"{lu_stamp}\n\n"
        output += f"**Recap** ({recap_type}) ::\n\n"
        output += "**Learned**:\n"
        for item in learned[-5:]:
            output += f"✓ {item}\n"
        output += f"\n**Next**: {lu}\n"
        output += "\n:: ∎"
        
        return output
    
    def _emit_course_complete(self) -> str:
        """Course completion message"""
        output = "🏆 **COURSE COMPLETE!** 🏆\n\n"
        output += f"Congratulations, {self.student_id.title()}!\n\n"
        output += f"You've mastered all {len(self.learned_items)} learning units.\n"
        output += f"Total session time: {int((time.time() - self.session_start) / 60)} minutes\n\n"
        output += "You're now ready to build real applications with Python!\n\n"
        output += "Type **NEW CLASS** to start another course.\n"
        output += "\n:: ∎"
        return output
    
    def _default_quiz(self) -> List[Dict]:
        """Default quiz questions"""
        return [
            {
                'q': "Question placeholder 1",
                'choices': ["A. Option A", "B. Option B", "C. Option C"],
                'answer': "B"
            }
        ] * 5
    
    def handle_command(self, cmd: str) -> str:
        """Route commands to handlers"""
        cmd_upper = cmd.strip().upper()
        
        if cmd_upper == "CONFIRM":
            if self.M == 1 and self.S == 1 and self.I == 1 and self.mode == "instruction" and not self.learned_items:
                return self.confirm_start()
            else:
                return self.confirm_advance()
        elif cmd_upper == "DONE":
            return self.handle_done()
        elif cmd_upper == "REPEAT":
            return self.handle_repeat()
        elif cmd_upper == "HELP":
            return self.handle_help()
        elif cmd_upper == "STATUS":
            return self.handle_status()
        elif cmd_upper == "QUIZ":
            return self.emit_quiz()
        elif cmd_upper.startswith(("1:", "2:", "3:", "4:", "5:")):
            return self.score_quiz(cmd)
        else:
            return f"⚠️ Unknown command: '{cmd}'\n\n**Valid commands**: DONE | HELP | REPEAT | CONFIRM | QUIZ | STATUS"
