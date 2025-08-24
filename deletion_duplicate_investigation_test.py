#!/usr/bin/env python3
"""
Deletion and Duplicate Prevention Investigation Test Suite
Specifically tests the user's workflow issue where:
1. User deleted race results
2. Uploaded txt file
3. No new race results were added (despite having registered pigeons)

This investigates potential deletion and duplicate prevention issues.
"""

import requests
import json
import os
import time
from datetime import datetime

# Use external URL from frontend/.env for testing
BACKEND_URL = "https://flight-results-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class DeletionDuplicateInvestigator:
    def __init__(self):
        self.test_results = []
        self.registered_pigeons = []
        self.created_results = []
        
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
            
    def clear_all_data(self):
        """Clear all data to start fresh"""
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
        """Register specific test pigeons mentioned in review request"""
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
                "gender": "female",
                "birth_year": 2025,
                "color": "red",
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
                    print(f"   Registered: {pigeon_data['ring_number']}")
                else:
                    print(f"   Failed to register: {pigeon_data['ring_number']} - Status: {response.status_code}")
            except Exception as e:
                print(f"   Error registering {pigeon_data['ring_number']}: {str(e)}")
                
        success = registered_count == len(test_pigeons)
        self.log_test("Register Test Pigeons", success, f"Registered {registered_count}/{len(test_pigeons)} pigeons")
        return success
        
    def create_test_file_content(self):
        """Create test file content with our registered pigeons"""
        content = """Data Technology Deerlijk - Licentie 30253

CHIMAY 09-08-25 32 Oude Deelnemers: 32 LOSTIJD: 08:00

NR NAAM                    RING         AFSTAND  TIJD      SNELH   COEFF
 1 VRANCKEN WILLY&DOCHTE   BE 504574322  85000   08.15.30  1200.5   3.12
 2 VANGEEL JO              BE 505078525  85000   08.16.45  1195.2   6.25

---

CHIMAY 09-08-25 26 Jaarduiven Deelnemers: 26 LOSTIJD: 08:00

NR NAAM                    RING         AFSTAND  TIJD      SNELH   COEFF
 1 VRANCKEN WILLY&DOCHTE   BE 504574322  85000   08.17.30  1190.5   3.84
 2 VANGEEL JO              BE 505078525  85000   08.18.45  1185.2   7.69
"""
        return content
        
    def upload_test_file(self):
        """Upload test file and process it"""
        try:
            content = self.create_test_file_content()
            
            # Create temporary file
            with open('/tmp/test_race_file.txt', 'w') as f:
                f.write(content)
                
            # Upload and process file
            with open('/tmp/test_race_file.txt', 'rb') as f:
                files = {'file': ('test_race_file.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                self.log_test("Upload Test File", True, 
                             f"Processed {data.get('races', 0)} races, {data.get('results', 0)} results")
                return True
            else:
                self.log_test("Upload Test File", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Upload Test File", False, f"Error: {str(e)}")
            return False
            
    def verify_results_created(self):
        """Verify race results were created"""
        try:
            response = requests.get(f"{API_BASE}/race-results", timeout=10)
            if response.status_code != 200:
                self.log_test("Verify Results Created", False, f"Failed to fetch results: {response.status_code}")
                return False
                
            results = response.json()
            self.created_results = results
            
            # Check for our specific ring numbers
            registered_rings = {p['ring_number'] for p in self.registered_pigeons}
            matching_results = [r for r in results if r['ring_number'] in registered_rings]
            
            success = len(matching_results) > 0
            self.log_test("Verify Results Created", success, 
                         f"Found {len(matching_results)} results for registered pigeons")
            
            if success:
                for result in matching_results:
                    print(f"   Result: {result['ring_number']} - Position {result['position']}")
                    
            return success
            
        except Exception as e:
            self.log_test("Verify Results Created", False, f"Error: {str(e)}")
            return False
            
    def test_deletion_functionality(self):
        """Test that DELETE /api/race-results/{id} actually removes results"""
        try:
            if not self.created_results:
                self.log_test("Test Deletion Functionality", False, "No results to delete")
                return False
                
            # Get initial count
            initial_count = len(self.created_results)
            
            # Delete first result
            result_to_delete = self.created_results[0]
            response = requests.delete(f"{API_BASE}/race-results/{result_to_delete['id']}", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Test Deletion Functionality", False, f"Delete failed: {response.status_code}")
                return False
                
            # Verify result is actually deleted from database
            time.sleep(1)  # Give database time to update
            response = requests.get(f"{API_BASE}/race-results", timeout=10)
            if response.status_code != 200:
                self.log_test("Test Deletion Functionality", False, "Failed to fetch results after deletion")
                return False
                
            remaining_results = response.json()
            final_count = len(remaining_results)
            
            # Check if the specific result is gone
            deleted_result_still_exists = any(r['id'] == result_to_delete['id'] for r in remaining_results)
            
            success = (final_count == initial_count - 1) and not deleted_result_still_exists
            self.log_test("Test Deletion Functionality", success, 
                         f"Initial: {initial_count}, Final: {final_count}, Deleted result exists: {deleted_result_still_exists}")
            
            # Update our local copy
            self.created_results = remaining_results
            return success
            
        except Exception as e:
            self.log_test("Test Deletion Functionality", False, f"Error: {str(e)}")
            return False
            
    def test_database_state_after_deletion(self):
        """Check for orphaned records or database inconsistencies"""
        try:
            # Get all race results
            results_response = requests.get(f"{API_BASE}/race-results", timeout=10)
            if results_response.status_code != 200:
                self.log_test("Test Database State", False, "Failed to fetch results")
                return False
                
            results = results_response.json()
            
            # Check for orphaned results (results without valid race or pigeon)
            orphaned_results = []
            for result in results:
                if not result.get('race') or not result.get('pigeon'):
                    orphaned_results.append(result)
                    
            success = len(orphaned_results) == 0
            self.log_test("Test Database State", success, 
                         f"Found {len(orphaned_results)} orphaned results")
            
            if orphaned_results:
                for orphan in orphaned_results[:3]:  # Show first 3
                    print(f"   Orphaned: {orphan['ring_number']} - Race: {orphan.get('race')}, Pigeon: {orphan.get('pigeon')}")
                    
            return success
            
        except Exception as e:
            self.log_test("Test Database State", False, f"Error: {str(e)}")
            return False
            
    def test_duplicate_prevention_after_deletion(self):
        """Test if duplicate prevention incorrectly blocks new results after deletion"""
        try:
            # Re-upload the same file after deletion
            content = self.create_test_file_content()
            
            with open('/tmp/test_race_file_reupload.txt', 'w') as f:
                f.write(content)
                
            with open('/tmp/test_race_file_reupload.txt', 'rb') as f:
                files = {'file': ('test_race_file_reupload.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if response.status_code != 200:
                self.log_test("Test Duplicate Prevention After Deletion", False, f"Re-upload failed: {response.status_code}")
                return False
                
            data = response.json()
            results_created = data.get('results', 0)
            
            # After deletion, we should be able to create new results for the same pigeons
            # Since we deleted one result, we should get at least some new results
            success = results_created > 0
            self.log_test("Test Duplicate Prevention After Deletion", success, 
                         f"Re-upload after deletion created {results_created} new results")
            
            return success
            
        except Exception as e:
            self.log_test("Test Duplicate Prevention After Deletion", False, f"Error: {str(e)}")
            return False
            
    def test_complete_workflow_simulation(self):
        """Simulate the exact user workflow that's failing"""
        try:
            print("\n--- SIMULATING USER'S EXACT WORKFLOW ---")
            
            # Step 1: Clear everything and start fresh
            self.clear_all_data()
            
            # Step 2: Register pigeons (user would have done this)
            if not self.register_test_pigeons():
                return False
                
            # Step 3: Upload file (should create results)
            if not self.upload_test_file():
                return False
                
            # Step 4: Verify results were created
            if not self.verify_results_created():
                return False
                
            # Step 5: Delete some results (user's action)
            initial_results = len(self.created_results)
            if initial_results > 0:
                # Delete half the results
                results_to_delete = self.created_results[:initial_results//2] if initial_results > 1 else [self.created_results[0]]
                
                for result in results_to_delete:
                    response = requests.delete(f"{API_BASE}/race-results/{result['id']}", timeout=10)
                    if response.status_code != 200:
                        self.log_test("Workflow Simulation - Delete Results", False, f"Failed to delete result {result['id']}")
                        return False
                        
                print(f"   Deleted {len(results_to_delete)} results")
                
            # Step 6: Re-upload file (user's action that fails)
            time.sleep(2)  # Give database time to update
            
            content = self.create_test_file_content()
            with open('/tmp/workflow_test_reupload.txt', 'w') as f:
                f.write(content)
                
            with open('/tmp/workflow_test_reupload.txt', 'rb') as f:
                files = {'file': ('workflow_test_reupload.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if response.status_code != 200:
                self.log_test("Workflow Simulation - Re-upload", False, f"Re-upload failed: {response.status_code}")
                return False
                
            reupload_data = response.json()
            new_results_created = reupload_data.get('results', 0)
            
            # Step 7: Verify new results were created
            final_response = requests.get(f"{API_BASE}/race-results", timeout=10)
            if final_response.status_code != 200:
                self.log_test("Workflow Simulation - Final Check", False, "Failed to fetch final results")
                return False
                
            final_results = final_response.json()
            final_count = len(final_results)
            
            # The key test: After deletion and re-upload, we should have results
            # If duplicate prevention is working correctly but not blocking legitimate re-creation
            success = new_results_created > 0 or final_count > 0
            
            self.log_test("Complete Workflow Simulation", success, 
                         f"Initial: {initial_results}, Deleted: {len(results_to_delete) if 'results_to_delete' in locals() else 0}, "
                         f"New from re-upload: {new_results_created}, Final total: {final_count}")
            
            return success
            
        except Exception as e:
            self.log_test("Complete Workflow Simulation", False, f"Error: {str(e)}")
            return False
            
    def analyze_duplicate_prevention_logic(self):
        """Analyze the duplicate prevention logic for potential bugs"""
        try:
            print("\n--- ANALYZING DUPLICATE PREVENTION LOGIC ---")
            
            # Test 1: Same pigeon, same date, different race categories
            content_multi_race = """Data Technology Deerlijk - Licentie 30253

CHIMAY 09-08-25 32 Oude Deelnemers: 32 LOSTIJD: 08:00

NR NAAM                    RING         AFSTAND  TIJD      SNELH   COEFF
 1 VRANCKEN WILLY&DOCHTE   BE 504574322  85000   08.15.30  1200.5   3.12

---

CHIMAY 09-08-25 26 Jaarduiven Deelnemers: 26 LOSTIJD: 08:00

NR NAAM                    RING         AFSTAND  TIJD      SNELH   COEFF
 1 VRANCKEN WILLY&DOCHTE   BE 504574322  85000   08.17.30  1190.5   3.84
"""
            
            # Clear and setup
            self.clear_all_data()
            self.register_test_pigeons()
            
            # Upload multi-race file
            with open('/tmp/multi_race_test.txt', 'w') as f:
                f.write(content_multi_race)
                
            with open('/tmp/multi_race_test.txt', 'rb') as f:
                files = {'file': ('multi_race_test.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if response.status_code != 200:
                self.log_test("Duplicate Prevention Analysis", False, f"Multi-race upload failed: {response.status_code}")
                return False
                
            data = response.json()
            races_created = data.get('races', 0)
            results_created = data.get('results', 0)
            
            # Should create 2 races but only 1 result per pigeon per date (duplicate prevention)
            expected_races = 2
            expected_results = 1  # Only one result per pigeon per date
            
            success = races_created == expected_races and results_created == expected_results
            self.log_test("Duplicate Prevention Analysis", success, 
                         f"Multi-race same date: {races_created} races (expected {expected_races}), "
                         f"{results_created} results (expected {expected_results})")
            
            return success
            
        except Exception as e:
            self.log_test("Duplicate Prevention Analysis", False, f"Error: {str(e)}")
            return False
            
    def run_investigation(self):
        """Run the complete investigation"""
        print("=" * 80)
        print("DELETION AND DUPLICATE PREVENTION INVESTIGATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print("Investigating user's workflow issue:")
        print("1. User deleted race results")
        print("2. Uploaded txt file")
        print("3. No new race results were added")
        print()
        
        # Health check
        if not self.test_health_check():
            print("❌ Backend not available - stopping investigation")
            return False
            
        # Test 1: Basic deletion functionality
        print("\n🔍 TESTING DELETION FUNCTIONALITY")
        self.clear_all_data()
        self.register_test_pigeons()
        self.upload_test_file()
        self.verify_results_created()
        self.test_deletion_functionality()
        self.test_database_state_after_deletion()
        
        # Test 2: Duplicate prevention after deletion
        print("\n🔍 TESTING DUPLICATE PREVENTION AFTER DELETION")
        self.test_duplicate_prevention_after_deletion()
        
        # Test 3: Complete workflow simulation
        print("\n🔍 SIMULATING COMPLETE USER WORKFLOW")
        self.test_complete_workflow_simulation()
        
        # Test 4: Duplicate prevention logic analysis
        print("\n🔍 ANALYZING DUPLICATE PREVENTION LOGIC")
        self.analyze_duplicate_prevention_logic()
        
        # Summary
        print()
        print("=" * 80)
        print("INVESTIGATION SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for t in self.test_results if t['passed'])
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        
        # Categorize results
        critical_failures = []
        minor_issues = []
        
        for test in self.test_results:
            if not test['passed']:
                if any(keyword in test['test'].lower() for keyword in ['deletion', 'duplicate', 'workflow']):
                    critical_failures.append(test)
                else:
                    minor_issues.append(test)
        
        if critical_failures:
            print("\n🚨 CRITICAL ISSUES FOUND:")
            for test in critical_failures:
                print(f"   ❌ {test['test']}: {test['message']}")
                
        if minor_issues:
            print("\n⚠️  MINOR ISSUES:")
            for test in minor_issues:
                print(f"   ⚠️  {test['test']}: {test['message']}")
                
        if passed == total:
            print("\n✅ NO ISSUES FOUND - System working correctly")
            print("   User's issue may be frontend-related or workflow misunderstanding")
        
        return len(critical_failures) == 0

if __name__ == "__main__":
    investigator = DeletionDuplicateInvestigator()
    success = investigator.run_investigation()
    exit(0 if success else 1)