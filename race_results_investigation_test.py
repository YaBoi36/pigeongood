#!/usr/bin/env python3
"""
URGENT RACE RESULTS INVESTIGATION TEST
Investigating why user sees "Success! 4 races and 289 results processed" but has 0 race results in database
"""

import requests
import json
import os
from datetime import datetime

# Backend URL - use localhost for testing
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class RaceResultsInvestigator:
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
        
    def test_backend_health(self):
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
            
    def check_current_database_state(self):
        """Check current state of database"""
        try:
            # Get dashboard stats
            response = requests.get(f"{API_BASE}/dashboard-stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                self.log_test("Database State Check", True, 
                             f"Pigeons: {stats.get('total_pigeons', 0)}, "
                             f"Races: {stats.get('total_races', 0)}, "
                             f"Results: {stats.get('total_results', 0)}")
                return stats
            else:
                self.log_test("Database State Check", False, f"Status code: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Database State Check", False, f"Error: {str(e)}")
            return None
            
    def check_registered_pigeons(self):
        """Check what pigeons are currently registered"""
        try:
            response = requests.get(f"{API_BASE}/pigeons", timeout=10)
            if response.status_code == 200:
                pigeons = response.json()
                ring_numbers = [p.get('ring_number', 'Unknown') for p in pigeons]
                
                # Check if BE504813624 is registered
                be504813624_registered = 'BE504813624' in ring_numbers
                
                self.log_test("Check Registered Pigeons", True, 
                             f"Found {len(pigeons)} registered pigeons: {ring_numbers}")
                
                if be504813624_registered:
                    print(f"   ✅ User's pigeon BE504813624 IS registered")
                else:
                    print(f"   ❌ User's pigeon BE504813624 is NOT registered")
                    
                return pigeons, be504813624_registered
            else:
                self.log_test("Check Registered Pigeons", False, f"Status code: {response.status_code}")
                return [], False
        except Exception as e:
            self.log_test("Check Registered Pigeons", False, f"Error: {str(e)}")
            return [], False
            
    def register_user_pigeon(self):
        """Register the user's specific pigeon BE504813624"""
        try:
            pigeon_data = {
                "ring_number": "BE504813624",
                "name": "User Test Pigeon",
                "gender": "female",
                "birth_year": 2024,
                "color": "blue",
                "owner": "BRIERS VALENT.&ZN"
            }
            
            response = requests.post(f"{API_BASE}/pigeons", json=pigeon_data, timeout=10)
            if response.status_code == 200:
                pigeon = response.json()
                self.log_test("Register User Pigeon", True, f"Registered BE504813624 with ID: {pigeon.get('id', 'unknown')}")
                return True
            else:
                self.log_test("Register User Pigeon", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Register User Pigeon", False, f"Error: {str(e)}")
            return False
            
    def test_file_parsing_step(self):
        """Test the file parsing step (upload-race-results)"""
        try:
            with open('/app/user_result_latest.txt', 'rb') as f:
                files = {'file': ('user_result_latest.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/upload-race-results", files=files, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                races_parsed = data.get('races', 0)
                results_parsed = data.get('results', 0)
                
                self.log_test("File Parsing Step", True, 
                             f"Parsed {races_parsed} races, {results_parsed} results")
                
                # Check if this matches user's reported numbers
                if races_parsed == 4 and results_parsed == 289:
                    print(f"   ✅ Matches user's report: 4 races and 289 results")
                else:
                    print(f"   ⚠️  Different from user's report (4 races, 289 results)")
                    
                return True, races_parsed, results_parsed
            else:
                self.log_test("File Parsing Step", False, f"Status code: {response.status_code}")
                return False, 0, 0
        except Exception as e:
            self.log_test("File Parsing Step", False, f"Error: {str(e)}")
            return False, 0, 0
            
    def test_file_processing_step(self):
        """Test the file processing step (confirm-race-upload)"""
        try:
            with open('/app/user_result_latest.txt', 'rb') as f:
                files = {'file': ('user_result_latest.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                races_processed = data.get('races', 0)
                results_processed = data.get('results', 0)
                message = data.get('message', '')
                
                self.log_test("File Processing Step", True, 
                             f"Processed {races_processed} races, {results_processed} results")
                print(f"   Message: {message}")
                
                return True, races_processed, results_processed
            else:
                self.log_test("File Processing Step", False, f"Status code: {response.status_code}")
                return False, 0, 0
        except Exception as e:
            self.log_test("File Processing Step", False, f"Error: {str(e)}")
            return False, 0, 0
            
    def verify_database_after_upload(self):
        """Verify database state after upload"""
        try:
            # Check dashboard stats
            stats_response = requests.get(f"{API_BASE}/dashboard-stats", timeout=10)
            if stats_response.status_code != 200:
                self.log_test("Verify Database After Upload", False, "Failed to get dashboard stats")
                return False
                
            stats = stats_response.json()
            
            # Check race results
            results_response = requests.get(f"{API_BASE}/race-results", timeout=10)
            if results_response.status_code != 200:
                self.log_test("Verify Database After Upload", False, "Failed to get race results")
                return False
                
            results = results_response.json()
            
            # Check for user's pigeon results
            user_results = [r for r in results if r.get('ring_number') == 'BE504813624']
            
            self.log_test("Verify Database After Upload", True, 
                         f"Database: {stats.get('total_races', 0)} races, "
                         f"{stats.get('total_results', 0)} results, "
                         f"{len(user_results)} results for BE504813624")
            
            if len(user_results) > 0:
                print(f"   ✅ Found results for user's pigeon BE504813624:")
                for result in user_results:
                    race_name = result.get('race', {}).get('race_name', 'Unknown') if result.get('race') else 'No race info'
                    print(f"      - Position {result.get('position', 'Unknown')} in {race_name}")
            else:
                print(f"   ❌ NO results found for user's pigeon BE504813624")
                
            return len(user_results) > 0
            
        except Exception as e:
            self.log_test("Verify Database After Upload", False, f"Error: {str(e)}")
            return False
            
    def test_duplicate_prevention_behavior(self):
        """Test if duplicate prevention is blocking results incorrectly"""
        try:
            # Try uploading the same file again
            with open('/app/user_result_latest.txt', 'rb') as f:
                files = {'file': ('user_result_latest.txt', f, 'text/plain')}
                response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                races_processed = data.get('races', 0)
                results_processed = data.get('results', 0)
                
                self.log_test("Duplicate Prevention Test", True, 
                             f"Re-upload: {races_processed} races, {results_processed} results (should be 0)")
                
                if results_processed == 0:
                    print(f"   ✅ Duplicate prevention working correctly")
                else:
                    print(f"   ⚠️  Duplicate prevention may not be working correctly")
                    
                return True
            else:
                self.log_test("Duplicate Prevention Test", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Duplicate Prevention Test", False, f"Error: {str(e)}")
            return False
            
    def analyze_file_content(self):
        """Analyze the user's file content"""
        try:
            with open('/app/user_result_latest.txt', 'r') as f:
                content = f.read()
                
            lines = content.split('\n')
            
            # Count races and results
            race_headers = []
            result_lines = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('---'):
                    continue
                    
                # Race header detection
                if 'CHIMAY' in line and ('09-08-25' in line or '25' in line):
                    race_headers.append(line)
                    
                # Result line detection (starts with number)
                if line and line[0].isdigit():
                    result_lines.append(line)
                    
            # Check for BE504813624 specifically
            be504813624_found = any('BE504813624' in line for line in result_lines)
            
            self.log_test("File Content Analysis", True, 
                         f"Found {len(race_headers)} race headers, {len(result_lines)} result lines")
            
            print(f"   Race headers found:")
            for header in race_headers:
                print(f"      - {header}")
                
            if be504813624_found:
                print(f"   ✅ BE504813624 found in file content")
                # Find the specific line
                for line in result_lines:
                    if 'BE504813624' in line:
                        print(f"      Line: {line}")
            else:
                print(f"   ❌ BE504813624 NOT found in file content")
                
            return True
            
        except Exception as e:
            self.log_test("File Content Analysis", False, f"Error: {str(e)}")
            return False
            
    def run_comprehensive_investigation(self):
        """Run comprehensive investigation of the race results issue"""
        print("=" * 80)
        print("URGENT RACE RESULTS INVESTIGATION")
        print("Investigating: User sees 'Success! 4 races and 289 results' but 0 results in database")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing with file: /app/user_result_latest.txt")
        print()
        
        # Step 1: Health check
        if not self.test_backend_health():
            print("❌ Backend not available - stopping investigation")
            return False
            
        # Step 2: Check current database state
        print("\n🔍 STEP 1: Current Database State")
        initial_stats = self.check_current_database_state()
        
        # Step 3: Check registered pigeons
        print("\n🔍 STEP 2: Registered Pigeons Check")
        pigeons, be504813624_registered = self.check_registered_pigeons()
        
        # Step 4: Register user's pigeon if not registered
        if not be504813624_registered:
            print("\n🔍 STEP 3: Registering User's Pigeon")
            self.register_user_pigeon()
        else:
            print("\n✅ User's pigeon BE504813624 is already registered")
            
        # Step 5: Analyze file content
        print("\n🔍 STEP 4: File Content Analysis")
        self.analyze_file_content()
        
        # Step 6: Test file parsing step
        print("\n🔍 STEP 5: File Parsing Test")
        parsing_success, races_parsed, results_parsed = self.test_file_parsing_step()
        
        # Step 7: Test file processing step
        print("\n🔍 STEP 6: File Processing Test")
        processing_success, races_processed, results_processed = self.test_file_processing_step()
        
        # Step 8: Verify database after upload
        print("\n🔍 STEP 7: Database Verification After Upload")
        database_has_results = self.verify_database_after_upload()
        
        # Step 9: Test duplicate prevention
        print("\n🔍 STEP 8: Duplicate Prevention Test")
        self.test_duplicate_prevention_behavior()
        
        # Step 10: Final database state check
        print("\n🔍 STEP 9: Final Database State")
        final_stats = self.check_current_database_state()
        
        # Summary and diagnosis
        print("\n" + "=" * 80)
        print("INVESTIGATION SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for t in self.test_results if t['passed'])
        total = len(self.test_results)
        print(f"Tests passed: {passed}/{total}")
        
        print("\n🔍 DIAGNOSIS:")
        
        if parsing_success and races_parsed == 4:
            print("✅ File parsing works correctly (4 races found)")
        else:
            print("❌ File parsing issue detected")
            
        if processing_success:
            print(f"✅ File processing completes (created {results_processed} results)")
        else:
            print("❌ File processing fails")
            
        if database_has_results:
            print("✅ Race results ARE created in database")
        else:
            print("❌ Race results are NOT created in database")
            
        # Root cause analysis
        print("\n🎯 ROOT CAUSE ANALYSIS:")
        
        if parsing_success and processing_success and not database_has_results:
            print("❌ CRITICAL BUG: Processing reports success but no results in database")
            print("   This indicates a bug in the database insertion logic")
        elif parsing_success and processing_success and database_has_results:
            print("✅ SYSTEM WORKING: Results are being created correctly")
            print("   User issue may be frontend display or user workflow related")
        elif not be504813624_registered:
            print("⚠️  USER WORKFLOW ISSUE: Pigeon not registered before upload")
            print("   User needs to register pigeons before uploading results")
        else:
            print("❓ UNCLEAR: Need more investigation")
            
        return database_has_results

if __name__ == "__main__":
    investigator = RaceResultsInvestigator()
    success = investigator.run_comprehensive_investigation()
    exit(0 if success else 1)