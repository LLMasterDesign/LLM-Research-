#!/usr/bin/env python3
"""
BookWorm Tutor - Main Runner
Agentic learning system with lattice-locked LU progression

Usage:
    python run.py                    # Interactive mode
    python run.py --student lucius   # Specify student
"""

import sys
import json
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from core.engine import BookWormEngine


def load_syllabus():
    """Load syllabus from JSON"""
    syllabus_path = Path(__file__).parent / 'artifacts' / 'syllabus_fundamentals.json'
    with open(syllabus_path, 'r') as f:
        return json.load(f)


def print_banner():
    """Print BookWorm banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🐛 BookWorm Tutor :: Lattice-Locked Learning System         ║
║   Programming Fundamentals with Adaptive Teaching            ║
║                                                               ║
║   Flow: Instruction → DONE → Quiz(5) → Pass → CONFIRM        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_help():
    """Print command help"""
    help_text = """
**Command Reference**:

**Learning Flow**:
  CONFIRM    - Confirm syllabus / Advance after quiz pass
  DONE       - Complete instruction, trigger quiz
  1:B,2:A... - Submit quiz answers
  
**Assistance**:
  HELP       - Get hints and assistance
  REPEAT     - Re-show current instruction
  QUIZ       - Retry quiz with new questions
  
**Navigation**:
  STATUS     - Show current LU and progress
  RECAP      - View progress summary
  PAUSE      - Save and pause (not implemented)
  RESUME     - Resume from save (not implemented)
  
**Control**:
  HELP       - Show this help
  EXIT       - Quit tutor

Type 'CONFIRM' to begin learning!
"""
    print(help_text)


def interactive_session(student_id="lucius"):
    """Run interactive tutoring session"""
    print_banner()
    
    # Load syllabus
    syllabus = load_syllabus()
    
    # Create engine
    engine = BookWormEngine(syllabus, student_id=student_id)
    
    # Start session
    print(engine.start())
    print()
    
    # Main loop
    while True:
        try:
            # Get user input
            user_input = input(f"\n{student_id}> ").strip()
            
            if not user_input:
                continue
            
            # Handle meta commands
            if user_input.upper() == 'EXIT':
                print("\n👋 Goodbye! Your progress has been recorded.\n")
                break
            elif user_input.upper() == 'HELP' and engine.mode == 'instruction' and engine.awaiting == 'none':
                print_help()
                continue
            
            # Route to engine
            response = engine.handle_command(user_input)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n\n⏸️ Session interrupted. Type RESUME to continue or EXIT to quit.\n")
            continue
        except EOFError:
            print("\n\n👋 Session ended.\n")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}\n")
            print("Type HELP for command list or STATUS for current state.\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BookWorm Tutor - Adaptive Learning System')
    parser.add_argument('--student', default='lucius', help='Student name')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    
    args = parser.parse_args()
    
    if args.demo:
        print("Demo mode not yet implemented. Use interactive mode.")
        return
    
    interactive_session(student_id=args.student)


if __name__ == '__main__':
    main()
