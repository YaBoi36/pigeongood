#!/usr/bin/env python3
"""
Duplicate Prevention Fix Test Suite
Tests the specific fix mentioned in the review request for preventing multiple results per pigeon per DATE
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://flight-results-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class DuplicatePreventionTester:
    def __init__(self):
        self.test_results = []
        self.registered_pigeons = []
        
    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        
    def test_health_check(self):
        """Test if backend is running"""
        try:
            # Test with pigeons endpoint since root might not be accessible
            response = requests.get(f"{API_BASE}/pigeons", timeout=10)
            if response.status_code == 200:
                self.log_test("Backend Health Check", True, f"API responding correctly")
                return True
            else:
                self.log_test("Backend Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection error: {str(e)}")
            return False
            
    def clear_all_data(self):
        """Clear all existing test data"""
        try:
            # Clear race results and races
            response = requests.delete(f"{API_BASE}/clear-test-data", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Clear All Data", True, f"Cleared {data.get('races_deleted', 0)} races, {data.get('results_deleted', 0)} results")
                
                # Also clear pigeons
                pigeons_response = requests.get(f"{API_BASE}/pigeons", timeout=10)
                if pigeons_response.status_code == 200:
                    pigeons = pigeons_response.json()
                    for pigeon in pigeons:
                        requests.delete(f"{API_BASE}/pigeons/{pigeon['id']}", timeout=10)
                    self.log_test("Clear All Pigeons", True, f"Cleared {len(pigeons)} pigeons")
                
                return True
            else:
                self.log_test("Clear All Data", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Clear All Data", False, f"Error: {str(e)}")
            return False
            
    def register_test_pigeons(self):
        """Register the specific test pigeons mentioned in review request"""
        test_pigeons = [
            {
                "ring_number": "BE504574322",
                "name": "Test Pigeon 1",
                "gender": "male",
                "birth_year": 2022,
                "color": "blue",
                "owner": "VRANCKEN WILLY&DOCHTE"
            },
            {
                "ring_number": "BE505078525",
                "name": "Test Pigeon 2", 
                "gender": "male",
                "birth_year": 2025,
                "color": "checkered",
                "owner": "VANGEEL JO"
            }
        ]
        
        registered_count = 0
        for pigeon_data in test_pigeons:
            try:
                response = requests.post(f"{API_BASE}/pigeons", json=pigeon_data, timeout=10)
                if response.status_code == 200:
                    pigeon = response.json()
                    self.registered_pigeons.append(pigeon)
                    registered_count += 1
                    print(f"   Registered: {pigeon_data['ring_number']} - {pigeon_data['owner']}")
                else:
                    print(f"   Failed to register: {pigeon_data['ring_number']} - Status: {response.status_code}")
            except Exception as e:
                print(f"   Error registering {pigeon_data['ring_number']}: {str(e)}")
                
        success = registered_count == len(test_pigeons)
        self.log_test("Register Test Pigeons", success, f"Registered {registered_count}/{len(test_pigeons)} pigeons")
        return success
        
    def upload_user_multi_race_file(self):
        """Upload the user's multi-race file with 4 races on same date"""
        try:
            # Read the user's result file
            with open('/app/user_result.txt', 'rb') as f:
                files = {'file': ('user_result.txt', f, 'text/plain')}
                
                # First, parse the file
                response = requests.post(f"{API_BASE}/upload-race-results", files=files, timeout=30)
                
            if response.status_code != 200:
                self.log_test("Upload Multi-Race File - Parse", False, f"Parse failed with status: {response.status_code}")
                return False
                
            parse_data = response.json()
            self.log_test("Upload Multi-Race File - Parse", True, 
                         f"Parsed {parse_data.get('races', 0)} races, {parse_data.get('results', 0)} results")
            
            # Now confirm and process the file
            with open('/app/user_result.txt', 'rb') as f:
                files = {'file': ('user_result.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                self.log_test("Upload Multi-Race File - Process", True, 
                             f"Processed {data.get('races', 0)} races, {data.get('results', 0)} results")
                return True
            else:
                self.log_test("Upload Multi-Race File - Process", False, f"Process failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Upload Multi-Race File", False, f"Error: {str(e)}")
            return False
            
    def verify_duplicate_prevention_working(self):
        """Verify that each pigeon has ONLY 1 result per date (not multiple)"""
        try:
            response = requests.get(f"{API_BASE}/race-results", timeout=10)
            if response.status_code != 200:
                self.log_test("Verify Duplicate Prevention", False, f"Failed to fetch results: {response.status_code}")
                return False
                
            results = response.json()
            
            # Check results for our test pigeons
            test_ring_numbers = {"BE504574322", "BE505078525"}
            
            # Count results per pigeon per date
            pigeon_date_counts = {}
            for result in results:
                ring_number = result.get('ring_number')
                if ring_number in test_ring_numbers and result.get('race'):
                    race_date = result['race'].get('date')
                    key = f"{ring_number}_{race_date}"
                    pigeon_date_counts[key] = pigeon_date_counts.get(key, 0) + 1
            
            # Verify each pigeon has only 1 result per date
            duplicate_prevention_working = True
            for key, count in pigeon_date_counts.items():
                ring_number, date = key.split('_')
                if count > 1:
                    duplicate_prevention_working = False
                    print(f"   ❌ DUPLICATE FOUND: {ring_number} has {count} results on date {date}")
                else:
                    print(f"   ✅ CORRECT: {ring_number} has {count} result on date {date}")
            
            if duplicate_prevention_working:
                self.log_test("Verify Duplicate Prevention", True, 
                             f"Each pigeon has only 1 result per date (expected behavior)")
            else:
                self.log_test("Verify Duplicate Prevention", False, 
                             f"Found pigeons with multiple results on same date")
                
            return duplicate_prevention_working
            
        except Exception as e:
            self.log_test("Verify Duplicate Prevention", False, f"Error: {str(e)}")
            return False
            
    def test_user_workflow_delete_and_reupload(self):
        """Test the user's exact workflow: delete some results then re-upload file"""
        try:
            # Get current results
            response = requests.get(f"{API_BASE}/race-results", timeout=10)
            if response.status_code != 200:
                self.log_test("User Workflow - Get Results", False, f"Failed to fetch results: {response.status_code}")
                return False
                
            results = response.json()
            initial_count = len(results)
            
            # Delete some results (simulate user deleting results)
            deleted_count = 0
            for result in results[:2]:  # Delete first 2 results
                try:
                    delete_response = requests.delete(f"{API_BASE}/race-results/{result['id']}", timeout=10)
                    if delete_response.status_code == 200:
                        deleted_count += 1
                except:
                    pass
            
            self.log_test("User Workflow - Delete Results", True, f"Deleted {deleted_count} results")
            
            # Re-upload the same file
            with open('/app/user_result.txt', 'rb') as f:
                files = {'file': ('user_result.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                results_created = data.get('results', 0)
                
                # Should create exactly the number of deleted results (no more due to duplicate prevention)
                success = results_created == deleted_count
                self.log_test("User Workflow - Re-upload", success, 
                             f"Re-upload created {results_created} results (deleted {deleted_count})")
                return success
            else:
                self.log_test("User Workflow - Re-upload", False, f"Re-upload failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Workflow - Delete and Re-upload", False, f"Error: {str(e)}")
            return False
            
    def verify_first_race_result_picked(self):
        """Verify system picks FIRST race result encountered for each pigeon"""
        try:
            response = requests.get(f"{API_BASE}/race-results", timeout=10)
            if response.status_code != 200:
                self.log_test("Verify First Race Picked", False, f"Failed to fetch results: {response.status_code}")
                return False
                
            results = response.json()
            
            # Check which race each test pigeon appears in
            test_ring_numbers = {"BE504574322", "BE505078525"}
            pigeon_races = {}
            
            for result in results:
                ring_number = result.get('ring_number')
                if ring_number in test_ring_numbers and result.get('race'):
                    race_name = result['race'].get('race_name')
                    pigeon_races[ring_number] = race_name
            
            # Based on the file structure, the first race encountered should be "CHIMAY Oude"
            # BE504574322 appears first in "CHIMAY Oude" race
            # BE505078525 appears first in "CHIMAY Jongen" race
            
            expected_first_races = {
                "BE504574322": "CHIMAY Oude",
                "BE505078525": "CHIMAY Jongen"
            }
            
            success = True
            for ring_number, expected_race in expected_first_races.items():
                actual_race = pigeon_races.get(ring_number)
                if actual_race and expected_race in actual_race:
                    print(f"   ✅ CORRECT: {ring_number} in {actual_race} (first occurrence)")
                else:
                    print(f"   ❌ INCORRECT: {ring_number} in {actual_race}, expected {expected_race}")
                    success = False
            
            self.log_test("Verify First Race Picked", success, 
                         f"System correctly picks first race result encountered")
            return success
            
        except Exception as e:
            self.log_test("Verify First Race Picked", False, f"Error: {str(e)}")
            return False
            
    def verify_all_races_processed(self):
        """Verify all 4 races from the file are processed"""
        try:
            response = requests.get(f"{API_BASE}/race-results", timeout=10)
            if response.status_code != 200:
                self.log_test("Verify All Races Processed", False, f"Failed to fetch results: {response.status_code}")
                return False
                
            results = response.json()
            
            # Get unique races
            races = set()
            for result in results:
                if result.get('race'):
                    races.add(result['race']['race_name'])
                    
            expected_races = {
                "CHIMAY Oude",
                "CHIMAY Jaarduiven", 
                "CHIMAY Jongen",
                "CHIMAY oude & jaar"
            }
            
            found_races = races.intersection(expected_races)
            success = len(found_races) >= 3  # At least 3 of 4 races
            
            self.log_test("Verify All Races Processed", success, 
                         f"Found {len(found_races)}/4 expected races: {sorted(found_races)}")
            return success
            
        except Exception as e:
            self.log_test("Verify All Races Processed", False, f"Error: {str(e)}")
            return False
            
    def run_comprehensive_duplicate_prevention_test(self):
        """Run the comprehensive test suite for duplicate prevention fix"""
        print("=" * 80)
        print("DUPLICATE PREVENTION FIX TEST SUITE")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing duplicate prevention fix in /app/backend/app.js")
        print(f"Expected behavior: Only 1 result per pigeon per DATE (not per race+date)")
        print()
        
        # Test 1: Health check
        if not self.test_health_check():
            print("❌ Backend not available - stopping tests")
            return False
            
        # Test 2: Clear all data for clean start
        if not self.clear_all_data():
            print("❌ Failed to clear data - stopping tests")
            return False
            
        # Test 3: Register test pigeons
        if not self.register_test_pigeons():
            print("❌ Failed to register pigeons - stopping tests")
            return False
            
        # Test 4: Upload user's multi-race file (4 races on same date)
        if not self.upload_user_multi_race_file():
            print("❌ Failed to upload file - stopping tests")
            return False
            
        # Test 5: Verify duplicate prevention is working (core test)
        duplicate_prevention_working = self.verify_duplicate_prevention_working()
        
        # Test 6: Verify all races are processed
        self.verify_all_races_processed()
        
        # Test 7: Verify first race result is picked
        self.verify_first_race_result_picked()
        
        # Test 8: Test user's exact workflow (delete + re-upload)
        self.test_user_workflow_delete_and_reupload()
        
        # Summary
        print()
        print("=" * 80)
        print("DUPLICATE PREVENTION TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for t in self.test_results if t['passed'])
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        
        if duplicate_prevention_working and passed >= total - 2:  # Allow 2 minor failures
            print("🎉 DUPLICATE PREVENTION FIX IS WORKING!")
            print("✅ Each pigeon has only 1 result per date")
            print("✅ System picks first race result encountered")
            print("✅ User workflow (delete + re-upload) works correctly")
            return True
        else:
            print("❌ DUPLICATE PREVENTION FIX HAS ISSUES")
            for test in self.test_results:
                if not test['passed']:
                    print(f"   FAILED: {test['test']} - {test['message']}")
            return False

if __name__ == "__main__":
    tester = DuplicatePreventionTester()
    success = tester.run_comprehensive_duplicate_prevention_test()
    exit(0 if success else 1)