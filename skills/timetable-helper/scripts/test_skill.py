#!/usr/bin/env python3
"""Automated trigger test suite for timetable-helper skill."""
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOOKUP_PY = os.path.join(SCRIPT_DIR, "lookup_timetable.py")

def test_positive_monday():
    res = subprocess.run([sys.executable, LOOKUP_PY, "CSE-A", "Monday"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "CS301 - Data Structures" in res.stdout
    print("PASS: Positive test (CSE-A Monday) verified")

def test_positive_lab():
    res = subprocess.run([sys.executable, LOOKUP_PY, "CSE-B", "Wednesday"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "LAB-01" in res.stdout
    assert "Dr. K. Nair" in res.stdout
    print("PASS: Lab faculty and room verified for CSE-B Wednesday")

def test_adversarial_rejection():
    res = subprocess.run([sys.executable, LOOKUP_PY, "CSE-A", "Friday"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Quantum Astrology" not in res.stdout
    assert "CS303" in res.stdout
    print("PASS: Adversarial hallucination check verified")

if __name__ == "__main__":
    print("--- Running Timetable Skill Verification ---")
    test_positive_monday()
    test_positive_lab()
    test_adversarial_rejection()
    print("--- All Skill Tests Succeeded ---")
