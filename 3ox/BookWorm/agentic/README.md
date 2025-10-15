# 🐛 BookWorm Agentic Tutor System

**Lattice-Locked Learning with LU Progression**

## Overview

This is the complete agentic implementation of BookWorm following the Tutor.Genesis framework. It uses lockstep LU (Liminal Unit) progression with mandatory quiz validation gates.

## Architecture

```
agentic/
├── run.py                           # Main runner (START HERE)
├── tutor_genesis.gen                # Agent specification
├── README.md                        # This file
│
├── core/
│   └── engine.py                    # Tutor engine with LU logic
│
├── artifacts/
│   └── syllabus_fundamentals.json   # M.S.I structured curriculum
│
├── personas/                        # Future: Teaching personas
└── state/                           # Future: Redis persistence
```

## Quick Start

### Run the Tutor

```bash
cd 3ox/BookWorm/agentic
python run.py
```

### Specify Student

```bash
python run.py --student lucius
```

## Learning Flow

```
1. START → Tutor emits Syllabus.Card
2. CONFIRM → Locks syllabus, begins at ⧉:[M1.S1.I1]
3. READ Instruction.Box
4. DONE → Triggers Quiz.Box (5 questions)
5. SUBMIT answers: "1:B, 2:A, 3:C, 4:D, 5:A"
6. PASS (≥4/5) → "PROCEED?"
7. CONFIRM → Advance to next LU
8. REPEAT from step 3
```

## LU Structure

**Liminal Unit Path**: `⧉:[M{module}.S{section}.I{item}]`

- **M**: Module (1-3)
- **S**: Section (within module)
- **I**: Item (within section)

**Example**: `⧉:[M1.S1.I2]` = Module 1, Section 1, Item 2

## Commands

### Learning Flow
- `CONFIRM` - Lock syllabus / Advance after quiz pass
- `DONE` - Complete instruction, trigger quiz
- `1:B,2:A,3:C,4:D,5:A` - Submit quiz answers

### Assistance
- `HELP` - Get hints and assistance
- `REPEAT` - Re-show current instruction
- `QUIZ` - Retry quiz with new questions

### Navigation
- `STATUS` - Show current LU and progress
- `RECAP` - View progress summary

### Control
- `EXIT` - Quit tutor

## Progression Rules

1. **Lockstep**: Must complete current LU before advancing
2. **Quiz Mandatory**: Every LU ends with 5-question quiz
3. **Pass Threshold**: Need ≥4/5 to pass
4. **No Skipping**: Must pass to advance
5. **Item Persistence**: Items (I) increment across sections
6. **Module Reset**: Items reset to 1 on new module

## Curriculum

**Module 1: Foundation** (2 sections, 6 items)
- S1: Variables and Data Types (3 items)
- S2: Operators and Expressions (3 items)

**Module 2: Application** (1 section, 1 item)
- S1: Control Flow - Conditions (1 item)

**Module 3: Integration** (1 section, 1 item)
- S1: Algorithms Basics (1 item)

**Total**: 3 modules, 4 sections, 7 items

## Example Session

```
$ python run.py

╔═══════════════════════════════════════════════════════════════╗
║   🐛 BookWorm Tutor :: Lattice-Locked Learning System         ║
╚═══════════════════════════════════════════════════════════════╝

Hello, Lucius! Ready to master programming fundamentals?

╔══════════════════════════════════════════════════════════════╗
║  📚 **SYLLABUS.CARD** :: Programming Fundamentals
╚══════════════════════════════════════════════════════════════╝

**Modules**: 3
**Total Concepts**: 12
**Estimated Time**: 40 hours

**Structure**:

**M1**: Foundation: Core Concepts
  S1: Variables and Data Types (3 items)
  S2: Operators and Expressions (3 items)

**M2**: Application: Practical Skills
  S1: Control Flow - Conditions (1 items)

**M3**: Integration: Advanced Topics
  S1: Algorithms Basics (1 items)

Type **CONFIRM** to lock this syllabus and begin learning.

lucius> CONFIRM

✅ **Syllabus Locked**

Beginning at ⧉:[M1.S1.I1]...

============================================================

⧉:[M1.S1.I1]

**Instruction** ::
Learn what variables are and how they store data. Variables are named 
containers (like labeled boxes) that hold different types of values: 
numbers, text, or true/false. They let you store, reuse, and update 
values throughout your program.

**Notes**:
• Think of variables as labeled storage boxes
• Each variable has a name and a value
• You can change what's in the box anytime

Type **DONE** when complete | **HELP** for assistance | **REPEAT** to review

:: ∎

lucius> DONE

⧉:[M1.S1.I1]

**Quiz** :: 5 Questions

1. What is a variable?
   A. A function
   B. A named container for data
   C. A loop
   D. A file

2. Which is a valid variable name?
   A. 1age
   B. user-name
   C. user_name
   D. user name

3. What symbol assigns a value to a variable?
   A. ==
   B. =
   C. :
   D. ->

4. Can you change a variable's value after creation?
   A. Yes
   B. No
   C. Only once
   D. Never

5. What's the main purpose of variables?
   A. Decoration
   B. Store and reuse data
   C. Print output
   D. End programs

**Submit answers**: "1:B, 2:A, 3:C, 4:D, 5:A"

:: ∎

lucius> 1:B, 2:C, 3:B, 4:A, 5:B

✅ **Quiz Passed**: 5/5

Excellent work on ⧉:[M1.S1.I1]! You've demonstrated understanding.

**PROCEED?**

Type **CONFIRM** to advance to the next learning unit.

lucius> CONFIRM

📍 **Progress**: ⧉:[M1.S1.I1] → ⧉:[M1.S1.I2]

============================================================

⧉:[M1.S1.I2]

**Instruction** ::
Understand the main data types: integers (whole numbers), floats 
(decimals), strings (text), and booleans (True/False). Each type 
behaves differently...

[continues]
```

## Features

✅ **Lockstep Progression** - One LU at a time, no skipping  
✅ **Quiz Validation** - 5 questions per LU, must score ≥4  
✅ **LU Path Stamping** - All boxes stamped with ⧉:[M.S.I]  
✅ **Drift Prevention** - Stay on current LU until complete  
✅ **Help System** - Get assistance anytime  
✅ **Progress Tracking** - Know exactly where you are  
✅ **Structured Content** - Proper M.S.I syllabus  

## Implementation Details

### Engine Core

The `BookWormEngine` class in `core/engine.py` implements:
- LU counter management (M, S, I)
- State machine (instruction → quiz → waiting_confirm)
- Quiz scoring logic
- Advancement rules
- Box emission with LU stamps

### Syllabus Structure

`artifacts/syllabus_fundamentals.json` contains:
- 3 modules with multiple sections
- Each section has 1-3 items
- Each item has: instruction, notes, assist, quiz (5Q)
- Proper M.S.I hierarchy

### Quiz Mechanics

- Exactly 5 questions per LU
- Multiple choice (A-D)
- Pass threshold: 4/5
- Can retry unlimited times
- New questions on retry

## Future Enhancements

### Personas
- Guide.Patient (current default)
- Coach.Socratic (questions-first)
- Practitioner.Hands_On (code-first)
- Visualizer.Conceptual (analogies)

### State Persistence
- Redis backend for save/resume
- Session recovery
- Progress analytics
- Spaced repetition scheduling

### RAG Integration
- Semantic search on HELP
- Context-aware assistance
- Example retrieval
- Concept review suggestions

## Tutor.Genesis Compliance

This implementation follows the Tutor.Genesis specification:

✅ Lattice-locked progression  
✅ LU path stamping with ⧉:[M.S.I]  
✅ Mandatory quiz gates  
✅ Drift prevention  
✅ Thread lock (no skip/jump)  
✅ Validation → Quiz → Confirm flow  
✅ Boxed output with stamps  
✅ Command token interface  
✅ State persistence ready  
✅ Persona switching ready  

## Testing

```bash
# Run tutor
cd 3ox/BookWorm/agentic
python run.py

# Follow the prompts
# Type CONFIRM to start
# Work through LUs
# Type EXIT to quit
```

## Integration

This agentic system integrates with:
- BookWorm library (books in `../library/`)
- RAG system (when connected)
- Redis (for persistence)
- Obsidian tools (for content management)

## Status

**Production Ready**: ✅

- [x] Core engine complete
- [x] Syllabus with M.S.I structure
- [x] Quiz validation working
- [x] Interactive runner
- [x] Command interface
- [x] Progress tracking
- [ ] Redis persistence (ready for integration)
- [ ] RAG integration (ready for integration)
- [ ] Multiple personas (ready for implementation)

## For Lucius

This is your complete, runnable BookWorm tutor. Just:

```bash
cd 3ox/BookWorm/agentic
python run.py
```

Type `CONFIRM` when you see the syllabus, and start learning!

:: ∎
