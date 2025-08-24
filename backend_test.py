#!/usr/bin/env python3
"""
Backend Test Suite for User's Specific Result File Testing
Tests the scenario where user uploads result (1).txt file with pre-registered pigeons
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://flight-results-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class BackendTester:
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
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health Check", True, f"Version: {data.get('version', 'unknown')}")
                return True
            else:
                self.log_test("Backend Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection error: {str(e)}")
            return False
            
    def clear_test_data(self):
        """Clear existing test data"""
        try:
            # Clear race results and races
            response = requests.delete(f"{API_BASE}/clear-test-data", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Clear Test Data", True, f"Cleared {data.get('races_deleted', 0)} races, {data.get('results_deleted', 0)} results")
                return True
            else:
                self.log_test("Clear Test Data", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Clear Test Data", False, f"Error: {str(e)}")
            return False
            
    def register_key_pigeons(self):
        """Register the key pigeons from user's file"""
        key_pigeons = [
            {
                "ring_number": "BE504574322",
                "name": "Test Pigeon 1",
                "gender": "male",
                "birth_year": 2022,
                "color": "blue",
                "owner": "VRANCKEN WILLY&DOCHTE"
            },
            {
                "ring_number": "BE504813624", 
                "name": "Test Pigeon 2",
                "gender": "female",
                "birth_year": 2024,
                "color": "red",
                "owner": "BRIERS VALENT.&ZN"
            },
            {
                "ring_number": "BE505078525",
                "name": "Test Pigeon 3", 
                "gender": "male",
                "birth_year": 2025,
                "color": "checkered",
                "owner": "VANGEEL JO"
            },
            {
                "ring_number": "BE504232523",
                "name": "Test Pigeon 4",
                "gender": "female", 
                "birth_year": 2023,
                "color": "white",
                "owner": "BRIERS VALENT.&ZN"
            },
            {
                "ring_number": "BE504280523",
                "name": "Test Pigeon 5",
                "gender": "male",
                "birth_year": 2023, 
                "color": "black",
                "owner": "HERMANS RUBEN"
            }
        ]
        
        registered_count = 0
        for pigeon_data in key_pigeons:
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
                
        success = registered_count == len(key_pigeons)
        self.log_test("Register Key Pigeons", success, f"Registered {registered_count}/{len(key_pigeons)} pigeons")
        return success
        
    def upload_user_result_file(self):
        """Upload the user's specific result file"""
        try:
            # Read the user's result file
            with open('/app/user_result.txt', 'rb') as f:
                files = {'file': ('user_result.txt', f, 'text/plain')}
                
                # First, parse the file
                response = requests.post(f"{API_BASE}/upload-race-results", files=files, timeout=30)
                
            if response.status_code != 200:
                self.log_test("Upload User Result File - Parse", False, f"Parse failed with status: {response.status_code}")
                return False
                
            parse_data = response.json()
            self.log_test("Upload User Result File - Parse", True, 
                         f"Parsed {parse_data.get('races', 0)} races, {parse_data.get('results', 0)} results")
            
            # Now confirm and process the file
            with open('/app/user_result.txt', 'rb') as f:
                files = {'file': ('user_result.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                self.log_test("Upload User Result File - Process", True, 
                             f"Processed {data.get('races', 0)} races, {data.get('results', 0)} results")
                return True
            else:
                self.log_test("Upload User Result File - Process", False, f"Process failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Upload User Result File", False, f"Error: {str(e)}")
            return False
            
    def verify_race_results_created(self):
        """Verify that race results were created for registered pigeons"""
        try:
            response = requests.get(f"{API_BASE}/race-results", timeout=10)
            if response.status_code != 200:
                self.log_test("Verify Race Results Created", False, f"Failed to fetch results: {response.status_code}")
                return False
                
            results = response.json()
            
            # Check if we have results
            if not results:
                self.log_test("Verify Race Results Created", False, "No race results found")
                return False
                
            # Count results for our registered pigeons
            registered_ring_numbers = {p['ring_number'] for p in self.registered_pigeons}
            matching_results = [r for r in results if r['ring_number'] in registered_ring_numbers]
            
            # Verify we have results for our key pigeons
            found_rings = {r['ring_number'] for r in matching_results}
            expected_rings = {"BE504574322", "BE504813624", "BE505078525", "BE504232523", "BE504280523"}
            
            success = len(matching_results) > 0 and found_rings.intersection(expected_rings)
            
            if success:
                self.log_test("Verify Race Results Created", True, 
                             f"Found {len(matching_results)} results for registered pigeons")
                print(f"   Results found for rings: {sorted(found_rings)}")
                
                # Verify race details
                races_found = set()
                for result in matching_results:
                    if result.get('race'):
                        races_found.add(result['race']['race_name'])
                        
                print(f"   Races with results: {sorted(races_found)}")
                
            else:
                self.log_test("Verify Race Results Created", False, 
                             f"Only {len(matching_results)} results found for registered pigeons")
                
            return success
            
        except Exception as e:
            self.log_test("Verify Race Results Created", False, f"Error: {str(e)}")
            return False
            
    def test_duplicate_prevention(self):
        """Test that duplicate prevention works correctly"""
        try:
            # Upload the same file again
            with open('/app/user_result.txt', 'rb') as f:
                files = {'file': ('user_result.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                # Should process races but create 0 new results due to duplicates
                races_processed = data.get('races', 0)
                results_created = data.get('results', 0)
                
                success = races_processed > 0 and results_created == 0
                self.log_test("Test Duplicate Prevention", success, 
                             f"Re-upload: {races_processed} races, {results_created} new results (expected 0)")
                return success
            else:
                self.log_test("Test Duplicate Prevention", False, f"Re-upload failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Test Duplicate Prevention", False, f"Error: {str(e)}")
            return False
            
    def test_without_pre_registration(self):
        """Test uploading file without pre-registering pigeons"""
        try:
            # Clear all pigeons first
            for pigeon in self.registered_pigeons:
                try:
                    requests.delete(f"{API_BASE}/pigeons/{pigeon['id']}", timeout=10)
                except:
                    pass
                    
            # Clear test data
            requests.delete(f"{API_BASE}/clear-test-data", timeout=10)
            
            # Upload file without any registered pigeons
            with open('/app/user_result.txt', 'rb') as f:
                files = {'file': ('user_result.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                races_processed = data.get('races', 0)
                results_created = data.get('results', 0)
                
                # Should process races but create 0 results (no registered pigeons)
                success = races_processed > 0 and results_created == 0
                self.log_test("Test Without Pre-registration", success, 
                             f"No pigeons registered: {races_processed} races, {results_created} results (expected 0)")
                return success
            else:
                self.log_test("Test Without Pre-registration", False, f"Upload failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Test Without Pre-registration", False, f"Error: {str(e)}")
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
            
            success = len(races.intersection(expected_races)) >= 3  # At least 3 of 4 races
            self.log_test("Verify All Races Processed", success, 
                         f"Found races: {sorted(races)}")
            return success
            
        except Exception as e:
            self.log_test("Verify All Races Processed", False, f"Error: {str(e)}")
            return False
            
    def run_comprehensive_test(self):
        """Run the comprehensive test suite for user's specific scenario"""
        print("=" * 80)
        print("BACKEND TEST SUITE - USER'S SPECIFIC RESULT FILE TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing with user's file: /app/user_result.txt")
        print()
        
        # Test 1: Health check
        if not self.test_health_check():
            print("❌ Backend not available - stopping tests")
            return False
            
        # Test 2: Clear existing data
        self.clear_test_data()
        
        # Test 3: Register key pigeons
        if not self.register_key_pigeons():
            print("❌ Failed to register pigeons - stopping tests")
            return False
            
        # Test 4: Upload user's result file
        if not self.upload_user_result_file():
            print("❌ Failed to upload file - stopping tests")
            return False
            
        # Test 5: Verify race results were created
        if not self.verify_race_results_created():
            print("❌ No race results created for registered pigeons")
            
        # Test 6: Verify all races processed
        self.verify_all_races_processed()
        
        # Test 7: Test duplicate prevention
        self.test_duplicate_prevention()
        
        # Test 8: Test without pre-registration
        self.test_without_pre_registration()
        
        # Summary
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for t in self.test_results if t['passed'])
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print("❌ Some tests failed")
            for test in self.test_results:
                if not test['passed']:
                    print(f"   FAILED: {test['test']} - {test['message']}")
            return False

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)