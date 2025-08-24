#!/usr/bin/env python3
"""
Backend Test Suite for Data Clearing and System Verification
Tests clearing all data from the system and verifying clean state
"""

import requests
import json
import os
from datetime import datetime

# Use localhost for direct backend testing
BACKEND_URL = "http://localhost:8001"

API_BASE = f"{BACKEND_URL}/api"

class DataClearingTester:
    def __init__(self):
        self.test_results = []
        
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
                self.log_test("Backend Health Check", True, f"Backend is running")
                return True
            else:
                self.log_test("Backend Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection error: {str(e)}")
            return False
            
    def get_system_stats(self):
        """Get current system statistics"""
        try:
            response = requests.get(f"{API_BASE}/dashboard", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return None
            
    def clear_all_pigeons(self):
        """Clear all registered pigeons from the system"""
        try:
            # First get all pigeons
            response = requests.get(f"{API_BASE}/pigeons", timeout=10)
            if response.status_code != 200:
                self.log_test("Clear All Pigeons", False, f"Failed to fetch pigeons: {response.status_code}")
                return False
                
            pigeons = response.json()
            deleted_count = 0
            
            # Delete each pigeon (this will cascade delete race results)
            for pigeon in pigeons:
                try:
                    delete_response = requests.delete(f"{API_BASE}/pigeons/{pigeon['id']}", timeout=10)
                    if delete_response.status_code == 200:
                        deleted_count += 1
                    else:
                        print(f"   Failed to delete pigeon {pigeon.get('ring_number', pigeon['id'])}")
                except Exception as e:
                    print(f"   Error deleting pigeon {pigeon.get('ring_number', pigeon['id'])}: {str(e)}")
                    
            self.log_test("Clear All Pigeons", True, f"Deleted {deleted_count} pigeons")
            return True
            
        except Exception as e:
            self.log_test("Clear All Pigeons", False, f"Error: {str(e)}")
            return False
            
    def clear_races_and_results(self):
        """Clear all races and race results"""
        try:
            response = requests.delete(f"{API_BASE}/clear-test-data", timeout=10)
            if response.status_code == 200:
                data = response.json()
                races_deleted = data.get('races_deleted', 0)
                results_deleted = data.get('results_deleted', 0)
                self.log_test("Clear Races and Results", True, 
                             f"Cleared {races_deleted} races, {results_deleted} race results")
                return True
            else:
                self.log_test("Clear Races and Results", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Clear Races and Results", False, f"Error: {str(e)}")
            return False
            
    def verify_system_is_clean(self):
        """Verify that the system has 0 pigeons, 0 races, 0 race results"""
        try:
            stats = self.get_system_stats()
            if stats is None:
                self.log_test("Verify System is Clean", False, "Could not get system stats")
                return False
                
            pigeons = stats.get('total_pigeons', -1)
            races = stats.get('total_races', -1)
            results = stats.get('total_results', -1)
            
            is_clean = pigeons == 0 and races == 0 and results == 0
            
            if is_clean:
                self.log_test("Verify System is Clean", True, 
                             f"System is clean: {pigeons} pigeons, {races} races, {results} results")
            else:
                self.log_test("Verify System is Clean", False, 
                             f"System not clean: {pigeons} pigeons, {races} races, {results} results")
                             
            return is_clean
            
        except Exception as e:
            self.log_test("Verify System is Clean", False, f"Error: {str(e)}")
            return False
            
    def test_basic_functionality_after_clearing(self):
        """Test that basic functionality still works after clearing"""
        try:
            # Test 1: Create a test pigeon
            test_pigeon = {
                "ring_number": "BE999999999",
                "name": "Test Pigeon",
                "gender": "male",
                "birth_year": 2024,
                "color": "blue",
                "owner": "Test Owner"
            }
            
            response = requests.post(f"{API_BASE}/pigeons", json=test_pigeon, timeout=10)
            if response.status_code != 200:
                self.log_test("Test Basic Functionality - Create Pigeon", False, 
                             f"Failed to create pigeon: {response.status_code}")
                return False
                
            created_pigeon = response.json()
            pigeon_id = created_pigeon['id']
            
            # Test 2: Verify pigeon was created
            response = requests.get(f"{API_BASE}/pigeons", timeout=10)
            if response.status_code != 200:
                self.log_test("Test Basic Functionality - Get Pigeons", False, 
                             f"Failed to get pigeons: {response.status_code}")
                return False
                
            pigeons = response.json()
            if len(pigeons) != 1 or pigeons[0]['ring_number'] != "BE999999999":
                self.log_test("Test Basic Functionality - Verify Pigeon", False, 
                             f"Pigeon not found or incorrect data")
                return False
                
            # Test 3: Delete the test pigeon
            response = requests.delete(f"{API_BASE}/pigeons/{pigeon_id}", timeout=10)
            if response.status_code != 200:
                self.log_test("Test Basic Functionality - Delete Pigeon", False, 
                             f"Failed to delete pigeon: {response.status_code}")
                return False
                
            # Test 4: Verify pigeon was deleted
            response = requests.get(f"{API_BASE}/pigeons", timeout=10)
            if response.status_code != 200:
                self.log_test("Test Basic Functionality - Verify Deletion", False, 
                             f"Failed to get pigeons after deletion: {response.status_code}")
                return False
                
            pigeons = response.json()
            if len(pigeons) != 0:
                self.log_test("Test Basic Functionality - Verify Deletion", False, 
                             f"Pigeon not deleted, still {len(pigeons)} pigeons")
                return False
                
            self.log_test("Test Basic Functionality", True, 
                         "All basic CRUD operations working correctly")
            return True
            
        except Exception as e:
            self.log_test("Test Basic Functionality", False, f"Error: {str(e)}")
            return False
            
    def test_api_endpoints_responsive(self):
        """Test that all main API endpoints are responsive"""
        endpoints_to_test = [
            ("/api/pigeons", "GET"),
            ("/api/race-results", "GET"),
            ("/api/dashboard", "GET")
        ]
        
        all_responsive = True
        
        for endpoint, method in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                    
                if response.status_code == 200:
                    print(f"   ✅ {method} {endpoint} - Responsive")
                else:
                    print(f"   ❌ {method} {endpoint} - Status: {response.status_code}")
                    all_responsive = False
                    
            except Exception as e:
                print(f"   ❌ {method} {endpoint} - Error: {str(e)}")
                all_responsive = False
                
        self.log_test("API Endpoints Responsive", all_responsive, 
                     f"Tested {len(endpoints_to_test)} endpoints")
        return all_responsive
        
    def run_data_clearing_test(self):
        """Run the comprehensive data clearing test suite"""
        print("=" * 80)
        print("BACKEND TEST SUITE - DATA CLEARING AND SYSTEM VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print()
        
        # Test 1: Health check
        if not self.test_health_check():
            print("❌ Backend not available - stopping tests")
            return False
            
        # Show initial system state
        print("\n📊 INITIAL SYSTEM STATE:")
        initial_stats = self.get_system_stats()
        if initial_stats:
            print(f"   Pigeons: {initial_stats.get('total_pigeons', 'unknown')}")
            print(f"   Races: {initial_stats.get('total_races', 'unknown')}")
            print(f"   Race Results: {initial_stats.get('total_results', 'unknown')}")
        
        print("\n🧹 CLEARING ALL DATA:")
        
        # Test 2: Clear all pigeons (this will cascade delete race results)
        self.clear_all_pigeons()
        
        # Test 3: Clear all races and remaining race results
        self.clear_races_and_results()
        
        print("\n✅ VERIFICATION:")
        
        # Test 4: Verify system is clean
        if not self.verify_system_is_clean():
            print("❌ System is not clean - data clearing failed")
            
        print("\n🔧 FUNCTIONALITY TESTING:")
        
        # Test 5: Test basic functionality still works
        self.test_basic_functionality_after_clearing()
        
        # Test 6: Test API endpoints are responsive
        self.test_api_endpoints_responsive()
        
        # Final verification
        print("\n📊 FINAL SYSTEM STATE:")
        final_stats = self.get_system_stats()
        if final_stats:
            print(f"   Pigeons: {final_stats.get('total_pigeons', 'unknown')}")
            print(f"   Races: {final_stats.get('total_races', 'unknown')}")
            print(f"   Race Results: {final_stats.get('total_results', 'unknown')}")
        
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
            print("✅ System is cleared and ready for user testing")
            print("\nUser can now:")
            print("1. Register pigeons manually")
            print("2. Upload their result file")
            print("3. See results appear")
            return True
        else:
            print("❌ Some tests failed")
            for test in self.test_results:
                if not test['passed']:
                    print(f"   FAILED: {test['test']} - {test['message']}")
            return False

if __name__ == "__main__":
    tester = DataClearingTester()
    success = tester.run_data_clearing_test()
    exit(0 if success else 1)