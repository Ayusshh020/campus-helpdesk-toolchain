#!/usr/bin/env python3
"""Deterministic timetable lookup — no LLM guesswork."""
import argparse, csv, os, sys

def load_timetable(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def lookup(rows, batch, day):
    b = batch.strip().upper()
    d = day.strip().capitalize()
    return [r for r in rows if r['batch'].upper() == b and r['day'].capitalize() == d]

def format_results(results, batch, day):
    if not results:
        return f"No scheduled class found in the official timetable for {batch} on {day}."
    lines = [f"Schedule for {results[0]['batch']} on {results[0]['day']}:", "-"*60]
    for r in results:
        lines.append(f"  {r['time_slot']}  |  {r['course_code']} - {r['course_name']}")
        lines.append(f"           Faculty: {r['faculty']}  |  Room: {r['room']}  |  Type: {r['type']}")
        lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Look up class timetable by batch and day.")
    parser.add_argument("batch", help="Batch code, e.g. CSE-A")
    parser.add_argument("day", help="Day name, e.g. Monday")
    args = parser.parse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'references', 'timetable.csv')
    if not os.path.exists(csv_path):
        print(f"Error: timetable.csv not found at {csv_path}", file=sys.stderr)
        sys.exit(1)
    rows = load_timetable(csv_path)
    results = lookup(rows, args.batch, args.day)
    print(format_results(results, args.batch, args.day))

if __name__ == '__main__':
    main()
