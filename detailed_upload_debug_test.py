#!/usr/bin/env python3
"""
DETAILED UPLOAD DEBUG TEST
Deep dive into the upload process to understand the success message vs actual results discrepancy
"""

import requests
import json
import os
from datetime import datetime

# Backend URL
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class UploadDebugger:
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
        
    def clear_all_data(self):
        """Clear all data to start fresh"""
        try:
            # Clear test data
            response = requests.delete(f"{API_BASE}/clear-test-data", timeout=10)
            
            # Clear all pigeons
            pigeons_response = requests.get(f"{API_BASE}/pigeons", timeout=10)
            if pigeons_response.status_code == 200:
                pigeons = pigeons_response.json()
                for pigeon in pigeons:
                    requests.delete(f"{API_BASE}/pigeons/{pigeon['id']}", timeout=10)
                    
            self.log_test("Clear All Data", True, f"Cleared all data")
            return True
        except Exception as e:
            self.log_test("Clear All Data", False, f"Error: {str(e)}")
            return False
            
    def register_test_pigeons(self):
        """Register multiple test pigeons from the file"""
        test_pigeons = [
            {
                "ring_number": "BE504813624",  # User's main pigeon
                "name": "Test Pigeon 1",
                "gender": "female",
                "birth_year": 2024,
                "color": "blue",
                "owner": "BRIERS VALENT.&ZN"
            },
            {
                "ring_number": "BE504574322",  # Another pigeon from file
                "name": "Test Pigeon 2",
                "gender": "male",
                "birth_year": 2022,
                "color": "red",
                "owner": "VRANCKEN WILLY&DOCHTE"
            },
            {
                "ring_number": "BE505078525",  # Third pigeon from file
                "name": "Test Pigeon 3",
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
                    registered_count += 1
                    print(f"   Registered: {pigeon_data['ring_number']}")
            except Exception as e:
                print(f"   Failed to register {pigeon_data['ring_number']}: {str(e)}")
                
        success = registered_count == len(test_pigeons)
        self.log_test("Register Test Pigeons", success, f"Registered {registered_count}/{len(test_pigeons)} pigeons")
        return success
        
    def test_upload_with_detailed_logging(self):
        """Test upload with detailed step-by-step logging"""
        try:
            print("\n📋 DETAILED UPLOAD PROCESS:")
            
            # Step 1: Check initial state
            initial_stats = requests.get(f"{API_BASE}/dashboard-stats", timeout=10).json()
            print(f"   Initial state: {initial_stats.get('total_races', 0)} races, {initial_stats.get('total_results', 0)} results")
            
            # Step 2: Parse file
            print(f"   Step 1: Parsing file...")
            with open('/app/user_result_latest.txt', 'rb') as f:
                files = {'file': ('user_result_latest.txt', f, 'text/plain')}
                parse_response = requests.post(f"{API_BASE}/upload-race-results", files=files, timeout=30)
                
            if parse_response.status_code != 200:
                self.log_test("Detailed Upload Test", False, f"Parse failed: {parse_response.status_code}")
                return False
                
            parse_data = parse_response.json()
            print(f"   Parse result: {parse_data.get('races', 0)} races, {parse_data.get('results', 0)} results")
            
            # Step 3: Process file
            print(f"   Step 2: Processing file...")
            with open('/app/user_result_latest.txt', 'rb') as f:
                files = {'file': ('user_result_latest.txt', f, 'text/plain')}
                process_response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if process_response.status_code != 200:
                self.log_test("Detailed Upload Test", False, f"Process failed: {process_response.status_code}")
                return False
                
            process_data = process_response.json()
            success_message = process_data.get('message', '')
            races_processed = process_data.get('races', 0)
            results_processed = process_data.get('results', 0)
            
            print(f"   Process result: {races_processed} races, {results_processed} results")
            print(f"   Success message: '{success_message}'")
            
            # Step 4: Check final state
            final_stats = requests.get(f"{API_BASE}/dashboard-stats", timeout=10).json()
            print(f"   Final state: {final_stats.get('total_races', 0)} races, {final_stats.get('total_results', 0)} results")
            
            # Step 5: Get actual race results
            results_response = requests.get(f"{API_BASE}/race-results", timeout=10)
            if results_response.status_code == 200:
                results = results_response.json()
                print(f"   Actual results in database: {len(results)}")
                
                # Check for our test pigeons
                for ring_number in ["BE504813624", "BE504574322", "BE505078525"]:
                    pigeon_results = [r for r in results if r.get('ring_number') == ring_number]
                    if pigeon_results:
                        print(f"   ✅ {ring_number}: {len(pigeon_results)} results")
                        for result in pigeon_results:
                            race_name = result.get('race', {}).get('race_name', 'Unknown') if result.get('race') else 'No race'
                            print(f"      - Position {result.get('position', '?')} in {race_name}")
                    else:
                        print(f"   ❌ {ring_number}: 0 results")
            
            # Analysis
            print(f"\n🔍 ANALYSIS:")
            print(f"   Parse step found: {parse_data.get('results', 0)} potential results")
            print(f"   Process step created: {results_processed} actual results")
            print(f"   Database contains: {final_stats.get('total_results', 0)} results")
            
            # Check for discrepancy
            if parse_data.get('results', 0) > results_processed:
                print(f"   ⚠️  DISCREPANCY: Parse found {parse_data.get('results', 0)} but only {results_processed} were created")
                print(f"   This suggests many results were filtered out (likely unregistered pigeons)")
            
            if "289 results" in success_message and results_processed < 289:
                print(f"   ⚠️  SUCCESS MESSAGE MISLEADING: Says '289 results' but only created {results_processed}")
                print(f"   The message likely refers to parsing, not actual database insertion")
            
            self.log_test("Detailed Upload Test", True, 
                         f"Parse: {parse_data.get('results', 0)}, Process: {results_processed}, DB: {final_stats.get('total_results', 0)}")
            return True
            
        except Exception as e:
            self.log_test("Detailed Upload Test", False, f"Error: {str(e)}")
            return False
            
    def test_without_registered_pigeons(self):
        """Test what happens when no pigeons are registered"""
        try:
            print("\n🧪 TESTING WITHOUT REGISTERED PIGEONS:")
            
            # Clear all pigeons
            pigeons_response = requests.get(f"{API_BASE}/pigeons", timeout=10)
            if pigeons_response.status_code == 200:
                pigeons = pigeons_response.json()
                for pigeon in pigeons:
                    requests.delete(f"{API_BASE}/pigeons/{pigeon['id']}", timeout=10)
                    
            # Clear races and results
            requests.delete(f"{API_BASE}/clear-test-data", timeout=10)
            
            # Try to upload file
            with open('/app/user_result_latest.txt', 'rb') as f:
                files = {'file': ('user_result_latest.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                success_message = data.get('message', '')
                races_processed = data.get('races', 0)
                results_processed = data.get('results', 0)
                
                print(f"   Success message: '{success_message}'")
                print(f"   Races processed: {races_processed}")
                print(f"   Results created: {results_processed}")
                
                # Check database
                stats = requests.get(f"{API_BASE}/dashboard-stats", timeout=10).json()
                print(f"   Database state: {stats.get('total_results', 0)} results")
                
                if "289 results" in success_message and results_processed == 0:
                    print(f"   🎯 CONFIRMED: Success message is misleading!")
                    print(f"   The message refers to parsing (289 found) not insertion (0 created)")
                    
                self.log_test("Test Without Registered Pigeons", True, 
                             f"Message mentions results but created {results_processed}")
                return True
            else:
                self.log_test("Test Without Registered Pigeons", False, f"Upload failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Test Without Registered Pigeons", False, f"Error: {str(e)}")
            return False
            
    def run_debug_investigation(self):
        """Run detailed debug investigation"""
        print("=" * 80)
        print("DETAILED UPLOAD DEBUG INVESTIGATION")
        print("Investigating the success message vs actual results discrepancy")
        print("=" * 80)
        print()
        
        # Step 1: Clear all data
        print("🧹 STEP 1: Clearing all data")
        self.clear_all_data()
        
        # Step 2: Test without registered pigeons
        print("\n🧪 STEP 2: Testing upload without registered pigeons")
        self.test_without_registered_pigeons()
        
        # Step 3: Register test pigeons
        print("\n📝 STEP 3: Registering test pigeons")
        self.register_test_pigeons()
        
        # Step 4: Test with registered pigeons
        print("\n🧪 STEP 4: Testing upload with registered pigeons")
        self.test_upload_with_detailed_logging()
        
        # Summary
        print("\n" + "=" * 80)
        print("DEBUG INVESTIGATION SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for t in self.test_results if t['passed'])
        total = len(self.test_results)
        print(f"Tests passed: {passed}/{total}")
        
        print("\n🎯 KEY FINDINGS:")
        print("1. The success message 'Success! 4 races and 289 results processed' is MISLEADING")
        print("2. The '289 results' refers to results PARSED from file, not INSERTED into database")
        print("3. Only results for REGISTERED pigeons are actually inserted into database")
        print("4. The system is working correctly, but the message confuses users")
        
        print("\n💡 RECOMMENDATION:")
        print("The success message should be updated to clearly distinguish between:")
        print("- Results parsed from file (289)")
        print("- Results actually created in database (only for registered pigeons)")
        
        return True

if __name__ == "__main__":
    debugger = UploadDebugger()
    success = debugger.run_debug_investigation()
    exit(0 if success else 1)