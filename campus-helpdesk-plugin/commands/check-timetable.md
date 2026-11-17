# /check-timetable

Look up the official class schedule for a student batch on a given day.

## Usage

```
/check-timetable <batch> <day>
```

**Arguments:**
- `<batch>` — Student batch code: `CSE-A` or `CSE-B`
- `<day>` — Full weekday name: `Monday`, `Tuesday`, `Wednesday`, `Thursday`, or `Friday`

## Examples

```
/check-timetable CSE-A Monday
/check-timetable CSE-B Wednesday
/check-timetable CSE-A Friday
```

## Behaviour

1. The command invokes `skills/timetable-helper/scripts/lookup_timetable.py <batch> <day>`.
2. Results are returned from `references/timetable.csv` only — no guesses or extrapolations.
3. For lab sessions, the response includes both the **room number** and the **faculty name**.
4. If `<batch>` is omitted, the agent will ask: *"Which batch are you in? (e.g., CSE-A or CSE-B)"*
5. For weekends (Saturday/Sunday), the response is: *"No classes are scheduled on weekends."*
6. If the batch or day is not found in the timetable, the response is: *"No scheduled class found in the official timetable for that query."*

## Data Source

All schedule data is read deterministically from:
```
skills/timetable-helper/references/timetable.csv
```

No LLM generation is used to produce timetable content.
