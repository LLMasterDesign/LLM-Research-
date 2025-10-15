# 🚀 BookWorm Agentic - Quick Start

## Instant Launch (3 Steps)

### 1. Navigate to agentic folder
```bash
cd /workspace/3ox/BookWorm/agentic
```

### 2. Run the tutor
```bash
python run.py
```

### 3. Start learning
```
lucius> CONFIRM
```

That's it! You're now in a lattice-locked learning session.

---

## First Session Walk-Through

### Step 1: See the Syllabus

When you start, you'll see:

```
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

...

Type **CONFIRM** to lock this syllabus and begin learning.
```

### Step 2: Lock Syllabus

```
lucius> CONFIRM
```

The tutor responds:

```
✅ **Syllabus Locked**

Beginning at ⧉:[M1.S1.I1]...

============================================================

⧉:[M1.S1.I1]

**Instruction** ::
Learn what variables are and how they store data...

Type **DONE** when complete | **HELP** for assistance | **REPEAT** to review

:: ∎
```

### Step 3: Complete Instruction

Read the instruction, then:

```
lucius> DONE
```

### Step 4: Take Quiz

The tutor emits a quiz:

```
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

...

**Submit answers**: "1:B, 2:A, 3:C, 4:D, 5:A"

:: ∎
```

### Step 5: Submit Answers

```
lucius> 1:B, 2:C, 3:B, 4:A, 5:B
```

### Step 6: Pass & Advance

If you score ≥4/5:

```
✅ **Quiz Passed**: 5/5

Excellent work on ⧉:[M1.S1.I1]! You've demonstrated understanding.

**PROCEED?**

Type **CONFIRM** to advance to the next learning unit.
```

```
lucius> CONFIRM
```

### Step 7: Next LU

```
📍 **Progress**: ⧉:[M1.S1.I1] → ⧉:[M1.S1.I2]

============================================================

⧉:[M1.S1.I2]

**Instruction** ::
Understand the main data types...
```

Repeat from Step 3!

---

## Essential Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `CONFIRM` | Lock syllabus / Advance LU | After quiz pass |
| `DONE` | Complete instruction | When you finish reading |
| `1:B,2:A...` | Submit quiz answers | After quiz appears |
| `HELP` | Get assistance | When stuck |
| `REPEAT` | Re-show instruction | Need to review |
| `STATUS` | Show progress | Check where you are |
| `EXIT` | Quit tutor | End session |

---

## Understanding LU Paths

**LU Path Format**: `⧉:[M{module}.S{section}.I{item}]`

**Examples**:
- `⧉:[M1.S1.I1]` = Module 1, Section 1, Item 1 (first lesson)
- `⧉:[M1.S1.I2]` = Module 1, Section 1, Item 2 (second lesson)
- `⧉:[M1.S2.I4]` = Module 1, Section 2, Item 4 (fourth item overall)

**Progression Rules**:
- Items (I) increment within a module
- When section completes → S increments, I continues
- When module completes → M increments, I resets to 1

---

## Quiz Mechanics

**Every LU ends with a 5-question quiz**

- **Pass Threshold**: 4/5 or better
- **Format**: Multiple choice (A-D)
- **Submission**: `"1:B, 2:A, 3:C, 4:D, 5:A"`
- **Retries**: Unlimited (new questions each time)

**If you fail** (<4/5):
```
❌ **Quiz Score**: 3/5 (need ≥4 to pass)

**Options**:
• **QUIZ** - Try again with new questions
• **REPEAT** - Review the instruction
• **HELP** - Get assistance
```

---

## Typical Session Flow

```
START
  ↓
CONFIRM (lock syllabus)
  ↓
┌─────────────────────┐
│ READ Instruction    │
│   ⧉:[M.S.I]         │
└─────────────────────┘
  ↓
DONE
  ↓
┌─────────────────────┐
│ TAKE Quiz (5Q)      │
│   ⧉:[M.S.I]         │
└─────────────────────┘
  ↓
Submit: 1:B, 2:A, 3:C, 4:D, 5:A
  ↓
Pass (≥4/5)?
  │
  ├─ YES → "PROCEED?"
  │         ↓
  │      CONFIRM
  │         ↓
  │      Advance to next LU
  │         ↓
  │      (loop back to READ)
  │
  └─ NO → "Try again"
            ↓
         QUIZ / REPEAT / HELP
            ↓
         (loop back to TAKE Quiz)
```

---

## When You Need Help

### During Instruction

```
lucius> HELP
```

You'll get:
```
⧉:[M1.S1.I1]

**Assist** ::
Variables are the foundation of programming. Start by creating 
simple variables like: age = 25 or name = 'Lucius'. Try changing 
their values and printing them.

Type **DONE** when ready | **REPEAT** to review instruction

:: ∎
```

### During Quiz Failure

After failing a quiz, you can:

```
lucius> REPEAT    # Re-read instruction
lucius> HELP      # Get hints
lucius> QUIZ      # Try new questions
```

---

## Progress Tracking

### Check Status Anytime

```
lucius> STATUS
```

Response:
```
📊 **Status**

**Current**: ⧉:[M1.S1.I2]
**Mode**: instruction
**Learned**: 1 items
**Session Time**: 5 minutes
```

### View Progress Summary

```
lucius> RECAP
```

(Future feature - will show learned items and pending)

---

## Tips for Success

✅ **Read Carefully** - Instructions contain everything you need  
✅ **Use HELP** - Don't hesitate to ask for assistance  
✅ **REPEAT if Needed** - Review instruction before quiz  
✅ **Take Your Time** - No rush, focus on understanding  
✅ **Learn from Failures** - Quiz failures show what to review  
✅ **Track Progress** - Use STATUS to see how far you've come  

---

## Troubleshooting

### "No active quiz to score"
You tried to submit answers without taking a quiz. Type `DONE` first.

### "Invalid format" for quiz answers
Use this format: `1:B, 2:A, 3:C, 4:D, 5:A`
- Commas between answers
- Colon after number
- Capital letters

### "Nothing to confirm"
You tried to CONFIRM when not at a confirmation point. 
- First CONFIRM: After seeing syllabus
- Other CONFIRMs: After passing quiz

### Engine crashed
Restart with: `python run.py`
(Future: State persistence will let you resume)

---

## Next Steps

Once you've completed a few LUs, explore:

1. **Full Curriculum** - Work through all 3 modules
2. **RAG Integration** - Connect with semantic search (future)
3. **Personas** - Switch teaching styles (future)
4. **State Persistence** - Save/resume with Redis (future)

---

## Complete Example Session

```bash
$ cd /workspace/3ox/BookWorm/agentic
$ python run.py

[Banner appears]

lucius> CONFIRM

[Syllabus locks, M1.S1.I1 instruction appears]

lucius> DONE

[Quiz appears with 5 questions]

lucius> 1:B, 2:C, 3:B, 4:A, 5:B

✅ **Quiz Passed**: 5/5

lucius> CONFIRM

[Advances to M1.S1.I2]

lucius> HELP

[Assistance box appears]

lucius> DONE

[Quiz for I2 appears]

lucius> 1:A, 2:A, 3:C, 4:B, 5:D

✅ **Quiz Passed**: 5/5

lucius> CONFIRM

[Advances to M1.S1.I3]

lucius> STATUS

📊 **Status**
**Current**: ⧉:[M1.S1.I3]
**Learned**: 2 items

lucius> EXIT

👋 Goodbye!
```

---

## You're Ready!

```bash
cd /workspace/3ox/BookWorm/agentic
python run.py
```

Type `CONFIRM` and start mastering programming fundamentals! 🚀

:: ∎
