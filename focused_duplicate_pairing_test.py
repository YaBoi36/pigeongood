#!/usr/bin/env python3
"""
Focused Backend Test Suite for the Review Request
Tests the two specific fixes mentioned:
1. Duplicate Ring Number Prevention with BE504727824
2. Breeding & Pairing Functionality end-to-end
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

def log_test(test_name, passed, message=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"   {message}")
    return passed

def main():
    print("=" * 80)
    print("FOCUSED TEST - DUPLICATE PREVENTION & PAIRING FUNCTIONALITY")
    print("=" * 80)
    print("Testing the specific requirements from the review request:")
    print("1. Duplicate Ring Number Prevention with BE504727824")
    print("2. Pairing functionality end-to-end")
    print()
    
    all_passed = True
    
    # ========== TEST 1: DUPLICATE PREVENTION ==========
    print("🔍 TESTING DUPLICATE RING NUMBER PREVENTION")
    print("-" * 50)
    
    # Check if BE504727824 already exists
    response = requests.get(f"{API_BASE}/pigeons")
    pigeons = response.json()
    existing_pigeon = next((p for p in pigeons if p['ring_number'] == 'BE504727824'), None)
    
    if existing_pigeon:
        print(f"   Found existing pigeon: {existing_pigeon['name']} ({existing_pigeon['ring_number']})")
        
        # Try to create duplicate
        duplicate_data = {
            "ring_number": "BE504727824",
            "name": "Duplicate Test",
            "gender": "female",
            "birth_year": 2023,
            "color": "red",
            "owner": "Different Owner"
        }
        
        response = requests.post(f"{API_BASE}/pigeons", json=duplicate_data)
        if response.status_code == 400:
            error_data = response.json()
            if "already exists" in error_data.get('detail', ''):
                all_passed &= log_test("Duplicate Prevention", True, f"Correctly blocked duplicate: {error_data['detail']}")
            else:
                all_passed &= log_test("Duplicate Prevention", False, f"Wrong error message: {error_data.get('detail')}")
        else:
            all_passed &= log_test("Duplicate Prevention", False, f"Expected 400 error, got {response.status_code}")
        
        # Verify original still exists unchanged
        response = requests.get(f"{API_BASE}/pigeons")
        pigeons = response.json()
        original_still_there = any(p['ring_number'] == 'BE504727824' and p['name'] == existing_pigeon['name'] for p in pigeons)
        duplicate_not_created = not any(p['ring_number'] == 'BE504727824' and p['name'] == 'Duplicate Test' for p in pigeons)
        
        if original_still_there and duplicate_not_created:
            all_passed &= log_test("Original Pigeon Unchanged", True, "Original pigeon preserved, duplicate not created")
        else:
            all_passed &= log_test("Original Pigeon Unchanged", False, "Original pigeon state changed")
    else:
        all_passed &= log_test("Find Existing Pigeon", False, "BE504727824 not found - cannot test duplicate prevention")
    
    print()
    
    # ========== TEST 2: PAIRING FUNCTIONALITY ==========
    print("🔍 TESTING PAIRING FUNCTIONALITY")
    print("-" * 50)
    
    # Find or create male and female pigeons for pairing
    male_pigeon = next((p for p in pigeons if p['gender'] and p['gender'].lower() == 'male'), None)
    female_pigeon = next((p for p in pigeons if p['gender'] and p['gender'].lower() == 'female'), None)
    
    if not male_pigeon:
        # Create male pigeon
        male_data = {
            "ring_number": "BE999888777",
            "name": "Test Male for Pairing",
            "gender": "male",
            "birth_year": 2021,
            "color": "blue",
            "owner": "Test Owner"
        }
        response = requests.post(f"{API_BASE}/pigeons", json=male_data)
        if response.status_code == 200:
            male_pigeon = response.json()
        else:
            all_passed &= log_test("Create Male Pigeon", False, "Failed to create male pigeon")
    
    if not female_pigeon:
        # Create female pigeon
        female_data = {
            "ring_number": "BE777666555",
            "name": "Test Female for Pairing",
            "gender": "female",
            "birth_year": 2021,
            "color": "red",
            "owner": "Test Owner"
        }
        response = requests.post(f"{API_BASE}/pigeons", json=female_data)
        if response.status_code == 200:
            female_pigeon = response.json()
        else:
            all_passed &= log_test("Create Female Pigeon", False, "Failed to create female pigeon")
    
    if male_pigeon and female_pigeon:
        print(f"   Using male: {male_pigeon['name']} ({male_pigeon['ring_number']})")
        print(f"   Using female: {female_pigeon['name']} ({female_pigeon['ring_number']})")
        
        # Test POST /api/pairings
        pairing_data = {
            "sire_id": male_pigeon['id'],
            "dam_id": female_pigeon['id'],
            "expected_hatch_date": "2024-05-15",
            "notes": "Test pairing for review"
        }
        
        response = requests.post(f"{API_BASE}/pairings", json=pairing_data)
        if response.status_code == 200:
            pairing = response.json()
            all_passed &= log_test("Create Pairing", True, f"Created pairing ID: {pairing['id']}")
            
            # Test GET /api/pairings
            response = requests.get(f"{API_BASE}/pairings")
            if response.status_code == 200:
                pairings = response.json()
                found = any(p['id'] == pairing['id'] for p in pairings)
                all_passed &= log_test("Fetch Pairings", found, f"Found {len(pairings)} pairings")
            else:
                all_passed &= log_test("Fetch Pairings", False, f"Failed to fetch pairings: {response.status_code}")
            
            # Test POST /api/pairings/:pairing_id/result
            offspring_data = {
                "ring_number": "555444333",
                "country": "BE",
                "name": "Review Test Offspring",
                "gender": "male",
                "birth_year": 2024,
                "color": "checkered",
                "birth_date": "2024-05-20",
                "notes": "Offspring from review test"
            }
            
            response = requests.post(f"{API_BASE}/pairings/{pairing['id']}/result", json=offspring_data)
            if response.status_code == 200:
                result = response.json()
                offspring = result.get('pigeon')
                if offspring:
                    expected_ring = "BE555444333"
                    if offspring['ring_number'] == expected_ring:
                        all_passed &= log_test("Create Offspring", True, f"Created offspring: {expected_ring}")
                        
                        # Verify offspring appears in pigeons list
                        response = requests.get(f"{API_BASE}/pigeons")
                        if response.status_code == 200:
                            pigeons = response.json()
                            offspring_in_list = next((p for p in pigeons if p['ring_number'] == expected_ring), None)
                            if offspring_in_list:
                                has_pedigree = (offspring_in_list.get('sire_ring') == male_pigeon['ring_number'] and 
                                              offspring_in_list.get('dam_ring') == female_pigeon['ring_number'])
                                if has_pedigree:
                                    all_passed &= log_test("Offspring in Pigeons List", True, "Offspring found with correct pedigree")
                                else:
                                    all_passed &= log_test("Offspring Pedigree", False, f"Missing pedigree: sire={offspring_in_list.get('sire_ring')}, dam={offspring_in_list.get('dam_ring')}")
                            else:
                                all_passed &= log_test("Offspring in Pigeons List", False, "Offspring not found in pigeons list")
                        else:
                            all_passed &= log_test("Fetch Pigeons for Verification", False, "Failed to fetch pigeons")
                    else:
                        all_passed &= log_test("Create Offspring", False, f"Wrong ring number: expected {expected_ring}, got {offspring['ring_number']}")
                else:
                    all_passed &= log_test("Create Offspring", False, "No pigeon data in response")
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                all_passed &= log_test("Create Offspring", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            all_passed &= log_test("Create Pairing", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
    else:
        all_passed &= log_test("Setup Pairing Test", False, "Could not find or create male/female pigeons")
    
    print()
    
    # ========== TEST 3: VALIDATION TESTS ==========
    print("🔍 TESTING VALIDATION")
    print("-" * 50)
    
    if male_pigeon and female_pigeon:
        # Test gender validation
        wrong_gender_pairing = {
            "sire_id": female_pigeon['id'],  # Female as sire
            "dam_id": male_pigeon['id'],     # Male as dam
            "expected_hatch_date": "2024-06-15",
            "notes": "Wrong gender test"
        }
        
        response = requests.post(f"{API_BASE}/pairings", json=wrong_gender_pairing)
        if response.status_code == 400:
            error_data = response.json()
            if "must be male" in error_data.get('detail', '') or "must be female" in error_data.get('detail', ''):
                all_passed &= log_test("Gender Validation", True, f"Correctly rejected wrong genders: {error_data.get('detail')}")
            else:
                all_passed &= log_test("Gender Validation", False, f"Wrong error message: {error_data.get('detail')}")
        else:
            all_passed &= log_test("Gender Validation", False, f"Expected 400 for gender validation, got {response.status_code}")
        
        # Test non-existent pigeon validation
        invalid_pairing = {
            "sire_id": "non-existent-id",
            "dam_id": female_pigeon['id'],
            "expected_hatch_date": "2024-06-15",
            "notes": "Invalid pigeon test"
        }
        
        response = requests.post(f"{API_BASE}/pairings", json=invalid_pairing)
        if response.status_code == 404:
            error_data = response.json()
            all_passed &= log_test("Non-existent Pigeon Validation", True, f"Correctly rejected non-existent pigeon: {error_data.get('detail')}")
        else:
            all_passed &= log_test("Non-existent Pigeon Validation", False, f"Expected 404, got {response.status_code}")
    
    print()
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Duplicate ring number prevention is working correctly")
        print("✅ Pairing functionality works end-to-end:")
        print("   - Create pairing with gender validation")
        print("   - Fetch pairings")
        print("   - Create offspring with parent pedigree")
        print("   - Offspring appears in pigeons collection")
        print("✅ All validation is working correctly")
        return True
    else:
        print("❌ Some tests failed - see details above")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)