#!/usr/bin/env python3
"""
Unit and integration test suite for Campus Helpdesk MCP Server.
Tests tool invocation, input validation, error handling, and resource retrieval.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server import get_timetable, get_fee_status, get_hostel_rules, TIMETABLE, FEE_RECORDS, HOSTEL_RULES

def test_suite():
    print("=" * 60)
    print("RUNNING CAMPUS HELPDESK MCP SERVER TEST SUITE")
    print("=" * 60)
    passed = 0
    total = 0

    # Test 1: get_timetable valid CSE-A Monday
    total += 1
    try:
        res = get_timetable("CSE-A", "Monday")
        assert res["batch"] == "CSE-A"
        assert res["day"] == "Monday"
        assert res["count"] == 4
        assert res["entries"][0]["course_code"] == "CS301"
        print("✅ PASS: get_timetable('CSE-A', 'Monday') -> 4 classes verified")
        passed += 1
    except Exception as e:
        print(f"❌ FAIL: get_timetable('CSE-A', 'Monday') -> {e}")

    # Test 2: get_timetable valid CSE-B Wednesday
    total += 1
    try:
        res = get_timetable("CSE-B", "Wednesday")
        assert res["batch"] == "CSE-B"
        assert res["day"] == "Wednesday"
        assert res["count"] == 2
        print("✅ PASS: get_timetable('CSE-B', 'Wednesday') -> 2 classes verified")
        passed += 1
    except Exception as e:
        print(f"❌ FAIL: get_timetable('CSE-B', 'Wednesday') -> {e}")

    # Test 3: get_timetable invalid day (Saturday) -> ValueError
    total += 1
    try:
        get_timetable("CSE-A", "Saturday")
        print("❌ FAIL: get_timetable('CSE-A', 'Saturday') should have raised ValueError")
    except ValueError as e:
        print(f"✅ PASS: get_timetable('CSE-A', 'Saturday') correctly raised ValueError: {e}")
        passed += 1

    # Test 4: get_timetable invalid batch -> ValueError
    total += 1
    try:
        get_timetable("CSE-Z", "Monday")
        print("❌ FAIL: get_timetable('CSE-Z', 'Monday') should have raised ValueError")
    except ValueError as e:
        print(f"✅ PASS: get_timetable('CSE-Z', 'Monday') correctly raised ValueError: {e}")
        passed += 1

    # Test 5: get_fee_status valid STU1001
    total += 1
    try:
        res = get_fee_status("STU1001")
        assert res["student_id"] == "STU1001"
        assert res["status"] == "PAID"
        assert res["balance_inr"] == 0
        print(f"✅ PASS: get_fee_status('STU1001') -> {res['name']} ({res['status']}) verified")
        passed += 1
    except Exception as e:
        print(f"❌ FAIL: get_fee_status('STU1001') -> {e}")

    # Test 6: get_fee_status valid STU1002 (pending)
    total += 1
    try:
        res = get_fee_status("STU1002")
        assert res["status"] == "PENDING"
        assert res["balance_inr"] == 45000
        print(f"✅ PASS: get_fee_status('STU1002') -> {res['name']} ({res['status']}, INR {res['balance_inr']}) verified")
        passed += 1
    except Exception as e:
        print(f"❌ FAIL: get_fee_status('STU1002') -> {e}")

    # Test 7: get_fee_status invalid ID -> ValueError
    total += 1
    try:
        get_fee_status("UNKNOWN_999")
        print("❌ FAIL: get_fee_status('UNKNOWN_999') should have raised ValueError")
    except ValueError as e:
        print(f"✅ PASS: get_fee_status('UNKNOWN_999') correctly raised ValueError: {e}")
        passed += 1

    # Test 8: hostel rules resource
    total += 1
    try:
        rules = get_hostel_rules()
        assert "Curfew Policy" in rules
        assert "10:00 PM" in rules
        print(f"✅ PASS: get_hostel_rules() -> {len(rules)} chars retrieved and verified")
        passed += 1
    except Exception as e:
        print(f"❌ FAIL: get_hostel_rules() -> {e}")

    print("=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 60)
    if passed != total:
        sys.exit(1)

if __name__ == "__main__":
    test_suite()
