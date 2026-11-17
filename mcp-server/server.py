#!/usr/bin/env python3
"""
Campus Helpdesk MCP Server
Exposes:
  - Tools: get_timetable(batch, day), get_fee_status(student_id)
  - Resource: campus://hostel/rules
Built using the official Python MCP SDK over stdio transport.

Compatibility Note:
Supports both mcp 1.x (FastMCP) and mcp 2.x (MCPServer).
"""
import sys
import json

try:
    from mcp.server.fastmcp import FastMCP
except (ImportError, ModuleNotFoundError):
    from mcp.server.mcpserver import MCPServer as FastMCP

mcp = FastMCP("campus-helpdesk-server")

# ── Authoritative Mock Data ─────────────────────────────────────────────────

TIMETABLE = {
    "CSE-A": {
        "Monday": [
            {"time_slot": "09:00-10:00", "course_code": "CS301", "course_name": "Data Structures", "faculty": "Dr. P. Kumar", "room": "LH-101", "type": "lecture"},
            {"time_slot": "10:00-11:00", "course_code": "CS302", "course_name": "Operating Systems", "faculty": "Dr. R. Singh", "room": "LH-101", "type": "lecture"},
            {"time_slot": "11:15-13:15", "course_code": "CS301L", "course_name": "Data Structures Lab", "faculty": "Dr. P. Kumar", "room": "LAB-02", "type": "lab"},
            {"time_slot": "14:00-15:00", "course_code": "CS303", "course_name": "Database Management Systems", "faculty": "Dr. S. Mehta", "room": "LH-102", "type": "lecture"},
        ],
        "Tuesday": [
            {"time_slot": "09:00-10:00", "course_code": "CS304", "course_name": "Computer Networks", "faculty": "Dr. A. Patel", "room": "LH-103", "type": "lecture"},
            {"time_slot": "10:00-11:00", "course_code": "CS301", "course_name": "Data Structures", "faculty": "Dr. P. Kumar", "room": "LH-101", "type": "lecture"},
            {"time_slot": "14:00-16:00", "course_code": "CS303L", "course_name": "DBMS Lab", "faculty": "Dr. S. Mehta", "room": "LAB-01", "type": "lab"},
        ],
        "Wednesday": [
            {"time_slot": "09:00-10:00", "course_code": "CS302", "course_name": "Operating Systems", "faculty": "Dr. R. Singh", "room": "LH-102", "type": "lecture"},
            {"time_slot": "10:00-11:00", "course_code": "CS303", "course_name": "Database Management Systems", "faculty": "Dr. S. Mehta", "room": "LH-102", "type": "lecture"},
            {"time_slot": "11:00-12:00", "course_code": "CS304", "course_name": "Computer Networks", "faculty": "Dr. A. Patel", "room": "LH-103", "type": "lecture"},
        ],
        "Thursday": [
            {"time_slot": "09:00-10:00", "course_code": "CS301", "course_name": "Data Structures", "faculty": "Dr. P. Kumar", "room": "LH-101", "type": "lecture"},
            {"time_slot": "14:00-16:00", "course_code": "CS302L", "course_name": "OS Lab", "faculty": "Dr. R. Singh", "room": "LAB-03", "type": "lab"},
        ],
        "Friday": [
            {"time_slot": "09:00-10:00", "course_code": "CS303", "course_name": "Database Management Systems", "faculty": "Dr. S. Mehta", "room": "LH-102", "type": "lecture"},
            {"time_slot": "10:00-11:00", "course_code": "CS304", "course_name": "Computer Networks", "faculty": "Dr. A. Patel", "room": "LH-103", "type": "lecture"},
        ],
    },
    "CSE-B": {
        "Monday": [
            {"time_slot": "09:00-10:00", "course_code": "CS301", "course_name": "Data Structures", "faculty": "Dr. M. Joshi", "room": "LH-201", "type": "lecture"},
            {"time_slot": "11:00-12:00", "course_code": "CS302", "course_name": "Operating Systems", "faculty": "Dr. K. Nair", "room": "LH-202", "type": "lecture"},
        ],
        "Tuesday": [
            {"time_slot": "09:00-10:00", "course_code": "CS303", "course_name": "Database Management Systems", "faculty": "Dr. V. Gupta", "room": "LH-201", "type": "lecture"},
            {"time_slot": "11:15-13:15", "course_code": "CS301L", "course_name": "Data Structures Lab", "faculty": "Dr. M. Joshi", "room": "LAB-04", "type": "lab"},
        ],
        "Wednesday": [
            {"time_slot": "09:00-10:00", "course_code": "CS304", "course_name": "Computer Networks", "faculty": "Dr. L. Rao", "room": "LH-203", "type": "lecture"},
            {"time_slot": "14:00-16:00", "course_code": "CS302L", "course_name": "OS Lab", "faculty": "Dr. K. Nair", "room": "LAB-01", "type": "lab"},
        ],
        "Thursday": [
            {"time_slot": "09:00-10:00", "course_code": "CS301", "course_name": "Data Structures", "faculty": "Dr. M. Joshi", "room": "LH-201", "type": "lecture"},
            {"time_slot": "10:00-11:00", "course_code": "CS303", "course_name": "Database Management Systems", "faculty": "Dr. V. Gupta", "room": "LH-201", "type": "lecture"},
        ],
        "Friday": [
            {"time_slot": "09:00-10:00", "course_code": "CS302", "course_name": "Operating Systems", "faculty": "Dr. K. Nair", "room": "LH-202", "type": "lecture"},
            {"time_slot": "14:00-16:00", "course_code": "CS303L", "course_name": "DBMS Lab", "faculty": "Dr. V. Gupta", "room": "LAB-04", "type": "lab"},
        ],
    },
}

FEE_RECORDS = {
    "STU1001": {"student_id": "STU1001", "name": "Ayush Mishra", "semester": "Sem 5", "status": "PAID", "balance_inr": 0, "receipt_id": "RCP-2026-881"},
    "STU1002": {"student_id": "STU1002", "name": "Priya Sharma", "semester": "Sem 5", "status": "PENDING", "balance_inr": 45000, "receipt_id": None},
    "STU1003": {"student_id": "STU1003", "name": "Rahul Verma", "semester": "Sem 5", "status": "PARTIAL", "balance_inr": 22500, "receipt_id": "RCP-2026-712"},
}

VALID_DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}

HOSTEL_RULES = """# Official University Hostel Rules – Nimbus Labs University

## Curfew Policy
- Weekdays (Monday–Friday): All residential students must return to their respective hostel blocks by 10:00 PM.
- Weekends (Saturday–Sunday): Extended curfew is permitted until 11:30 PM with biometric check-in.
- Overnight leave requires a written application submitted to the warden 48 hours in advance.

## Electrical Appliances Policy
- Permitted items: Personal laptops, mobile phone chargers, and low-wattage electric kettles (maximum 1000W).
- Strictly prohibited: Induction cooktops, microwave ovens, immersion water heaters, and heavy electric irons.
- Any prohibited appliance found during room inspection will be confiscated immediately and subject to a fine.

## Quiet Hours & Conduct
- Mandatory quiet hours are observed daily from 11:00 PM to 06:00 AM.
- Playing loud music, shouting in corridors, or hosting gatherings during quiet hours is prohibited.
- Disciplinary ladder: 1st violation = written warning, 2nd violation = parent notification, 3rd violation = hostel suspension.

## Visitor & Common Room Guidelines
- External day visitors are permitted only in the designated ground-floor visitor lounge between 09:00 AM and 08:00 PM.
- Visitors must sign the visitor ledger at reception; overnight visitors are strictly prohibited.

## Campus Wi-Fi Usage
- Campus Wi-Fi is provided 24/7 for educational and research purposes.
- P2P file sharing, unauthorized penetration testing, and bandwidth-monopolizing activities are prohibited.
""".strip()


# ── MCP Tools ───────────────────────────────────────────────────────────────

@mcp.tool()
def get_timetable(batch: str, day: str) -> dict:
    """Return verified class schedule entries for an exact university batch (e.g., CSE-A) and weekday (e.g., Monday).
    Returns a structured dictionary with batch, day, entries list (including time_slot, course_code, course_name,
    faculty, room, and type), and count. Raises ValueError for unknown batch or invalid/weekend day names."""
    batch_norm = batch.strip().upper()
    day_norm = day.strip().capitalize()
    
    if day_norm not in VALID_DAYS:
        raise ValueError(
            f"Invalid day '{day}'. Official timetable covers weekdays only: {', '.join(sorted(VALID_DAYS))}."
        )
    if batch_norm not in TIMETABLE:
        raise ValueError(
            f"Unknown batch '{batch}'. Valid batches in the current system: {', '.join(sorted(TIMETABLE.keys()))}."
        )
    
    entries = TIMETABLE[batch_norm].get(day_norm, [])
    return {"batch": batch_norm, "day": day_norm, "entries": entries, "count": len(entries)}


@mcp.tool()
def get_fee_status(student_id: str) -> dict:
    """Look up tuition fee payment status, remaining balance, and receipt ID for a valid student ID (e.g., STU1001).
    Returns a dictionary containing student_id, name, semester, status (PAID/PENDING/PARTIAL), balance_inr, and receipt_id.
    Raises ValueError for unrecognized student IDs."""
    sid = student_id.strip().upper()
    if sid not in FEE_RECORDS:
        raise ValueError(
            f"Student ID '{student_id}' not found. Valid mock student IDs: {', '.join(sorted(FEE_RECORDS.keys()))}."
        )
    return FEE_RECORDS[sid]


# ── MCP Resources ────────────────────────────────────────────────────────────

@mcp.resource("campus://hostel/rules")
def get_hostel_rules() -> str:
    """Official university hostel regulations covering curfew hours, electrical appliances, visitor policy, and conduct."""
    return HOSTEL_RULES


# ── Stdio Server Entrypoint ─────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
