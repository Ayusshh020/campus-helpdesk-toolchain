---
name: timetable-helper
description: >-
  Look up university class schedules, room numbers, faculty assignments, and
  lab timings for student batches from the official CSV timetable. Trigger
  whenever a user asks about classes, lectures, labs, schedules, rooms, or
  timetable slots for a specific batch (e.g., CSE-A, CSE-B) or day.
---

# Timetable Helper

## Instructions

1. Always query `scripts/lookup_timetable.py` or inspect `references/timetable.csv` before answering any schedule question.
2. Never invent, extrapolate, or guess classes, rooms, or instructors not explicitly present in `references/timetable.csv`.
3. If a batch, day, or course is missing from the CSV, state clearly: "No scheduled class found in the official timetable for that query."
4. Consult `references/column_dictionary.md` for schema definitions and `references/edge_cases.md` for holidays, cancelled slots, and lab groupings.
5. Weekend queries (Saturday or Sunday): explain that no classes are scheduled on weekends.
6. If a batch is not specified in the query, ask: "Which batch are you in? (e.g., CSE-A or CSE-B)"
7. For lab sessions, always report both the lab room number and the faculty name as both are relevant to the student.
