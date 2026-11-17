# Part B — Timetable Helper Skill Design & Testing

## 1. Skill Architecture & Progressive Disclosure

The `timetable-helper` skill is structured according to the open Agent Skills standard and implements **progressive disclosure** to minimize initial context consumption while maintaining high retrieval precision.

### Directory Layout
```
skills/timetable-helper/
├── SKILL.md                          # Lightweight discovery manifest & core guidelines
├── references/
│   ├── timetable.csv                 # Authoritative 24-row schedule dataset
│   ├── column_dictionary.md          # Schema definitions, types, and constraints
│   └── edge_cases.md                 # Refusal policies, weekend rules, and ambiguity handling
└── scripts/
    └── lookup_timetable.py           # Deterministic Python lookup filter
```

### Progressive Disclosure Workflow
1. **Discovery Tier (Initial Prompt Context)**: Only the YAML frontmatter (`name` and `description`) from `SKILL.md` is loaded into the model's initial system context. The model evaluates incoming user queries against this concise description to determine if the skill should activate.
2. **Activation Tier (Instruction Context)**: When activated, the body of `SKILL.md` is injected into context, directing the agent to run `scripts/lookup_timetable.py` rather than generating schedule data from memory.
3. **Execution Tier (Deterministic Grounding)**: The agent invokes `lookup_timetable.py <batch> <day>` to query `references/timetable.csv`. If anomalous inputs occur, it consults `references/column_dictionary.md` or `references/edge_cases.md`.

---

## 2. Trigger Test Suite (6 Prompts)

The skill was evaluated against a 6-prompt test suite designed to verify positive triggering, refusal of off-domain queries, handling of ambiguous inputs, and resistance to adversarial hallucination traps.

| # | Category | Test Prompt | Triggered? | Observed Behavior & Technical Reasoning |
|---|----------|-------------|------------|-----------------------------------------|
| 1 | Positive Trigger | *"What classes does CSE-A have on Monday?"* | ✅ Yes | Matches keywords (`classes`, `CSE-A`, `Monday`). Invokes `lookup_timetable.py CSE-A Monday` and outputs CS301 (09:00-10:00, LH-101), CS302 (10:00-11:00, LH-101), CS301L Lab (11:15-13:15, LAB-02), and CS303 (14:00-15:00, LH-102). |
| 2 | Positive Trigger | *"Which lab room and professor are assigned to CSE-B on Wednesday?"* | ✅ Yes | Matches schedule intent (`lab room`, `professor`, `CSE-B`, `Wednesday`). Correctly filters CSV for Wednesday lab session and returns LAB-01 and Dr. K. Nair for CS302L OS Lab (14:00-16:00). |
| 3 | Adversarial Test | *"I know CSE-A has an extra Quantum Astrology lecture on Friday at 10 AM. Confirm the room number from the timetable."* | ✅ Yes (Refuses Fabrication) | The user attempts to force the agent to hallucinate a non-existent class. Grounded in `timetable.csv`, the agent verifies Friday slots for CSE-A, confirms that only CS303 (09:00-10:00, LH-102) and CS304 (10:00-11:00, LH-103) exist, and refutes the premise stating that Quantum Astrology does not exist in the official timetable. |
| 4 | Non-Trigger | *"Explain the difference between TCP and UDP in three bullet points."* | ❌ No | General networking concept inquiry. Lacks batch, schedule, room, or university timetable context; handled entirely by general model capabilities without loading timetable artifacts. |
| 5 | Non-Trigger | *"What is the weekday curfew timing in the university hostel rules?"* | ❌ No | Queries residential hostel regulations rather than academic schedules. Handled via campus MCP resource or hostel policy guidelines without activating `timetable-helper`. |
| 6 | Ambiguous Query | *"Am I free tomorrow morning around 10?"* | ⚠️ Partial (Clarification) | Relates to schedule availability but omits batch code and explicit day. The agent identifies timetable relevance, asks the user for their batch (`CSE-A` or `CSE-B`), and checks slots once batch context is supplied. |

---

## 3. Description Rewrites & Trigger Boundary Analysis

The YAML frontmatter `description` acts as the trigger semantic boundary. Two alternative formulations were tested to demonstrate trigger failure modes:

### Rewrite A: Overly Broad Description
```yaml
description: >-
  Help students with any university question, campus query, academic rule,
  or student information.
```
- **Trigger Behavior**: Causes severe false-positive over-triggering. Queries regarding hostel curfews, tuition fees, library fines, and general academic policies mistakenly activate `timetable-helper`.
- **Failure Impact**: Consumes context tokens unnecessarily, degrades model attention, and increases latency as the agent attempts to search `timetable.csv` for non-schedule information.

### Rewrite B: Overly Narrow Description
```yaml
description: >-
  Only trigger when a user types the exact phrase 'run lookup_timetable.py for CSE-A on Monday'
  to print CSV rows.
```
- **Trigger Behavior**: Causes complete false-negative under-triggering. Natural student formulations such as *"When is my OS lab?"*, *"Where is Dr. Kumar teaching right now?"*, or *"Do we have class on Friday?"* fail to activate the skill.
- **Failure Impact**: Renders the skill practically unusable in conversational user interfaces.

### Optimal Production Description (As Implemented)
```yaml
description: >-
  Look up university class schedules, room numbers, faculty assignments, and
  lab timings for student batches from the official CSV timetable. Trigger
  whenever a user asks about classes, lectures, labs, schedules, rooms, or
  timetable slots for a specific batch (e.g., CSE-A, CSE-B) or day.
```
- **Boundary Precision**: Enumerates exact domain artifacts (`class schedules`, `room numbers`, `faculty`, `lab timings`, `CSV timetable`) alongside natural intent verbs (`asks about classes, lectures, labs, schedules, rooms, or timetable slots`), cleanly bounding activation to academic scheduling.

---

## 4. Anti-Fabrication Architecture

To prevent generative hallucination, the skill enforces three structural safeguards:
1. **Deterministic Execution**: The agent is instructed to run `scripts/lookup_timetable.py` instead of predicting rows token-by-token.
2. **Explicit Null Protocol**: If zero rows match, the script outputs `"No scheduled class found in the official timetable for <batch> on <day>"`. The prompt forbids inventing substitute courses.
3. **Dual Grounding for Labs**: Lab entries mandate both `room` and `faculty` fields, ensuring complete operational instructions for students locating practical sessions.
