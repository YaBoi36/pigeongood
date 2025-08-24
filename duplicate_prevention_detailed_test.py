#!/usr/bin/env python3
"""
Detailed Duplicate Prevention Test
Tests the specific duplicate prevention logic issue found in the investigation
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

def clear_all_data():
    """Clear all data"""
    requests.delete(f"{API_BASE}/clear-test-data", timeout=10)
    pigeons_response = requests.get(f"{API_BASE}/pigeons", timeout=10)
    if pigeons_response.status_code == 200:
        pigeons = pigeons_response.json()
        for pigeon in pigeons:
            requests.delete(f"{API_BASE}/pigeons/{pigeon['id']}", timeout=10)

def register_test_pigeon():
    """Register one test pigeon"""
    pigeon_data = {
        "ring_number": "BE504574322",
        "name": "Test Pigeon",
        "gender": "male",
        "birth_year": 2022,
        "color": "blue",
        "owner": "VRANCKEN WILLY&DOCHTE"
    }
    response = requests.post(f"{API_BASE}/pigeons", json=pigeon_data, timeout=10)
    return response.status_code == 200

def test_duplicate_prevention_bug():
    """Test the duplicate prevention bug"""
    print("Testing duplicate prevention logic...")
    
    # Clear and setup
    clear_all_data()
    if not register_test_pigeon():
        print("❌ Failed to register pigeon")
        return False
    
    # Test case: Same pigeon, same date, different race categories
    content = """Data Technology Deerlijk - Licentie 30253

CHIMAY 09-08-25 32 Oude Deelnemers: 32 LOSTIJD: 08:00

NR NAAM                    RING         AFSTAND  TIJD      SNELH   COEFF
 1 VRANCKEN WILLY&DOCHTE   BE 504574322  85000   08.15.30  1200.5   3.12

---

CHIMAY 09-08-25 26 Jaarduiven Deelnemers: 26 LOSTIJD: 08:00

NR NAAM                    RING         AFSTAND  TIJD      SNELH   COEFF
 1 VRANCKEN WILLY&DOCHTE   BE 504574322  85000   08.17.30  1190.5   3.84
"""
    
    # Upload file
    with open('/tmp/duplicate_test.txt', 'w') as f:
        f.write(content)
        
    with open('/tmp/duplicate_test.txt', 'rb') as f:
        files = {'file': ('duplicate_test.txt', f, 'text/plain')}
        response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
        
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        return False
        
    data = response.json()
    races_created = data.get('races', 0)
    results_created = data.get('results', 0)
    
    print(f"Races created: {races_created}")
    print(f"Results created: {results_created}")
    
    # Get actual results to analyze
    results_response = requests.get(f"{API_BASE}/race-results", timeout=10)
    if results_response.status_code == 200:
        results = results_response.json()
        print(f"Total results in database: {len(results)}")
        
        for result in results:
            race_name = result.get('race', {}).get('race_name', 'Unknown') if result.get('race') else 'No race'
            print(f"  - Ring: {result['ring_number']}, Race: {race_name}, Position: {result['position']}")
    
    # The bug: Should create only 1 result per pigeon per date, but creates 2
    # because it checks race_name equality instead of just date
    if results_created == 2:
        print("🐛 BUG CONFIRMED: Duplicate prevention allows multiple results for same pigeon on same date")
        print("   Issue: Logic checks race_name equality instead of preventing all results for same date")
        return False
    elif results_created == 1:
        print("✅ Duplicate prevention working correctly")
        return True
    else:
        print(f"❓ Unexpected result count: {results_created}")
        return False

def test_deletion_and_reupload():
    """Test deletion followed by re-upload"""
    print("\nTesting deletion and re-upload scenario...")
    
    # Get current results
    results_response = requests.get(f"{API_BASE}/race-results", timeout=10)
    if results_response.status_code != 200:
        print("❌ Failed to get results")
        return False
        
    results = results_response.json()
    if not results:
        print("❌ No results to delete")
        return False
    
    # Delete one result
    result_to_delete = results[0]
    delete_response = requests.delete(f"{API_BASE}/race-results/{result_to_delete['id']}", timeout=10)
    if delete_response.status_code != 200:
        print(f"❌ Failed to delete result: {delete_response.status_code}")
        return False
    
    print(f"Deleted result for ring: {result_to_delete['ring_number']}")
    
    # Wait a moment for database to update
    time.sleep(1)
    
    # Re-upload the same file
    content = """Data Technology Deerlijk - Licentie 30253

CHIMAY 09-08-25 32 Oude Deelnemers: 32 LOSTIJD: 08:00

NR NAAM                    RING         AFSTAND  TIJD      SNELH   COEFF
 1 VRANCKEN WILLY&DOCHTE   BE 504574322  85000   08.15.30  1200.5   3.12

---

CHIMAY 09-08-25 26 Jaarduiven Deelnemers: 26 LOSTIJD: 08:00

NR NAAM                    RING         AFSTAND  TIJD      SNELH   COEFF
 1 VRANCKEN WILLY&DOCHTE   BE 504574322  85000   08.17.30  1190.5   3.84
"""
    
    with open('/tmp/reupload_test.txt', 'w') as f:
        f.write(content)
        
    with open('/tmp/reupload_test.txt', 'rb') as f:
        files = {'file': ('reupload_test.txt', f, 'text/plain')}
        response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
        
    if response.status_code != 200:
        print(f"❌ Re-upload failed: {response.status_code}")
        return False
        
    reupload_data = response.json()
    new_results = reupload_data.get('results', 0)
    
    print(f"New results created on re-upload: {new_results}")
    
    # Check final state
    final_response = requests.get(f"{API_BASE}/race-results", timeout=10)
    if final_response.status_code == 200:
        final_results = final_response.json()
        print(f"Final total results: {len(final_results)}")
        
        # If duplicate prevention is working correctly after deletion,
        # we should be able to create new results
        if new_results > 0:
            print("✅ Duplicate prevention correctly allows new results after deletion")
            return True
        else:
            print("🐛 BUG: Duplicate prevention incorrectly blocks new results after deletion")
            return False
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("DETAILED DUPLICATE PREVENTION TEST")
    print("=" * 60)
    
    # Test 1: Duplicate prevention bug
    bug_test_passed = test_duplicate_prevention_bug()
    
    # Test 2: Deletion and re-upload
    deletion_test_passed = test_deletion_and_reupload()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if not bug_test_passed:
        print("🐛 CRITICAL BUG FOUND: Duplicate prevention logic is flawed")
        print("   - Allows multiple results for same pigeon on same date")
        print("   - Checks race_name equality instead of date-only prevention")
        
    if not deletion_test_passed:
        print("🐛 WORKFLOW BUG: Deletion + re-upload doesn't work correctly")
        
    if bug_test_passed and deletion_test_passed:
        print("✅ All tests passed - no issues found")
    else:
        print("❌ Issues found that explain user's problem")