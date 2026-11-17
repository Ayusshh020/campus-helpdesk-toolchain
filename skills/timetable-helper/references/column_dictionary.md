# Column Dictionary — timetable.csv

This document defines the schema for `references/timetable.csv`, the authoritative source for all class schedule lookups.

---

## Column Definitions

| # | Column Name | Type | Allowed Values | Example | Notes |
|---|-------------|------|----------------|---------|-------|
| 1 | `batch` | String | `CSE-A`, `CSE-B` | `CSE-A` | Student batch identifier. Case-insensitive during lookup (normalized to uppercase). Do not guess batches not present in the CSV. |
| 2 | `day` | String | `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday` | `Monday` | Academic weekdays only. Saturday and Sunday are never present — a weekend query must return a "no classes scheduled on weekends" message. |
| 3 | `time_slot` | String | HH:MM-HH:MM (24-hour) | `09:00-10:00` | Start and end time of the class slot. Lab slots span 2 hours; lectures span 1 hour. Do not infer or construct slots not explicitly listed. |
| 4 | `course_code` | String | Alphanumeric codes; `L` suffix denotes lab | `CS301`, `CS301L` | Unique identifier for a course offering. Codes ending in `L` are always labs. |
| 5 | `course_name` | String | Full English name of the course | `Data Structures` | Human-readable name. For labs, the name ends with `Lab` (e.g., `Data Structures Lab`). |
| 6 | `faculty` | String | Full name with honorific | `Dr. P. Kumar` | The assigned instructor for that slot. For labs, this faculty is physically present in the lab room. Always report faculty for lab sessions. |
| 7 | `room` | String | `LH-###` for lecture halls, `LAB-##` for labs | `LH-101`, `LAB-02` | Physical location of the class. `LH` = Lecture Hall; `LAB` = Laboratory. Always report room for lab sessions alongside faculty. |
| 8 | `type` | String | `lecture`, `lab` | `lecture` | Session type. `lecture` = standard classroom session. `lab` = hands-on laboratory session (longer duration, different room prefix). |

---

## Usage Rules

- **Lookup key**: Always filter by both `batch` AND `day` together — a single field is insufficient.
- **Case normalization**: `batch` lookup is case-insensitive (e.g., `cse-a` → `CSE-A`); `day` lookup capitalizes the first letter (e.g., `monday` → `Monday`).
- **No interpolation**: Never generate or guess values. If a combination of `batch`+`day` returns zero rows, report no schedule found.
- **Lab completeness**: When `type == lab`, always include both `room` and `faculty` in the response — students need both to locate the session.
