#!/usr/bin/env python3
"""
User Investigation Test Suite
Investigates why user is not seeing race results after uploading their txt file.
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://flight-results-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class UserInvestigationTester:
    def __init__(self):
        self.investigation_results = []
        self.system_state = {}
        
    def log_investigation(self, step_name, status, details=""):
        """Log investigation step"""
        print(f"🔍 {step_name}: {status}")
        if details:
            print(f"   {details}")
        self.investigation_results.append({
            'step': step_name,
            'status': status,
            'details': details
        })
        
    def check_backend_health(self):
        """Check if backend is running and accessible"""
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_investigation("Backend Health Check", "✅ HEALTHY", 
                                     f"Version: {data.get('version', 'unknown')}")
                return True
            else:
                self.log_investigation("Backend Health Check", "❌ UNHEALTHY", 
                                     f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_investigation("Backend Health Check", "❌ UNREACHABLE", 
                                 f"Connection error: {str(e)}")
            return False
            
    def check_current_system_state(self):
        """Check current counts of pigeons, races, and race results"""
        try:
            # Check pigeons count
            response = requests.get(f"{API_BASE}/pigeons", timeout=10)
            if response.status_code == 200:
                pigeons = response.json()
                pigeon_count = len(pigeons)
                self.system_state['pigeons'] = pigeons
                self.system_state['pigeon_count'] = pigeon_count
                
                # Log some pigeon details
                if pigeon_count > 0:
                    ring_numbers = [p.get('ring_number', 'N/A') for p in pigeons[:5]]
                    self.log_investigation("Current Pigeons", f"✅ {pigeon_count} REGISTERED", 
                                         f"Sample ring numbers: {ring_numbers}")
                else:
                    self.log_investigation("Current Pigeons", "⚠️ NONE REGISTERED", 
                                         "No pigeons found in system")
            else:
                self.log_investigation("Current Pigeons", "❌ ERROR", 
                                     f"Failed to fetch pigeons: {response.status_code}")
                
            # Check race results count
            response = requests.get(f"{API_BASE}/race-results", timeout=10)
            if response.status_code == 200:
                race_results = response.json()
                results_count = len(race_results)
                self.system_state['race_results'] = race_results
                self.system_state['results_count'] = results_count
                
                if results_count > 0:
                    # Analyze race results
                    unique_races = set()
                    unique_rings = set()
                    for result in race_results:
                        if result.get('race'):
                            unique_races.add(result['race'].get('race_name', 'Unknown'))
                        unique_rings.add(result.get('ring_number', 'N/A'))
                    
                    self.system_state['unique_races'] = list(unique_races)
                    self.system_state['unique_result_rings'] = list(unique_rings)
                    
                    self.log_investigation("Current Race Results", f"✅ {results_count} RESULTS FOUND", 
                                         f"Races: {list(unique_races)[:3]}, Ring samples: {list(unique_rings)[:5]}")
                else:
                    self.log_investigation("Current Race Results", "⚠️ NO RESULTS", 
                                         "No race results found in system")
            else:
                self.log_investigation("Current Race Results", "❌ ERROR", 
                                     f"Failed to fetch race results: {response.status_code}")
                
            # Check races count
            response = requests.get(f"{API_BASE}/dashboard-stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                race_count = stats.get('total_races', 0)
                self.system_state['race_count'] = race_count
                self.log_investigation("Current Races", f"✅ {race_count} RACES", 
                                     f"Total races in system: {race_count}")
            else:
                self.log_investigation("Current Races", "❌ ERROR", 
                                     f"Failed to fetch race stats: {response.status_code}")
                
        except Exception as e:
            self.log_investigation("System State Check", "❌ ERROR", f"Exception: {str(e)}")
            
    def check_backend_logs(self):
        """Check backend logs for recent errors"""
        try:
            # Since we can't directly access logs, we'll test API endpoints for errors
            test_endpoints = [
                ("/api/pigeons", "Pigeons endpoint"),
                ("/api/race-results", "Race results endpoint"),
                ("/api/dashboard-stats", "Dashboard stats endpoint")
            ]
            
            all_healthy = True
            for endpoint, name in test_endpoints:
                try:
                    response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
                    if response.status_code != 200:
                        self.log_investigation(f"API Health - {name}", "❌ ERROR", 
                                             f"Status: {response.status_code}")
                        all_healthy = False
                    else:
                        self.log_investigation(f"API Health - {name}", "✅ OK", "Responding normally")
                except Exception as e:
                    self.log_investigation(f"API Health - {name}", "❌ ERROR", f"Exception: {str(e)}")
                    all_healthy = False
                    
            if all_healthy:
                self.log_investigation("Backend API Health", "✅ ALL ENDPOINTS HEALTHY", 
                                     "No obvious API errors detected")
            else:
                self.log_investigation("Backend API Health", "⚠️ SOME ISSUES DETECTED", 
                                     "Check individual endpoint results above")
                
        except Exception as e:
            self.log_investigation("Backend Log Check", "❌ ERROR", f"Exception: {str(e)}")
            
    def analyze_ring_number_matching(self):
        """Analyze ring number matching between pigeons and results"""
        if not self.system_state.get('pigeons') or not self.system_state.get('race_results'):
            self.log_investigation("Ring Number Matching", "⚠️ INSUFFICIENT DATA", 
                                 "Need both pigeons and race results to analyze matching")
            return
            
        try:
            pigeon_rings = set(p.get('ring_number', '') for p in self.system_state['pigeons'])
            result_rings = set(r.get('ring_number', '') for r in self.system_state['race_results'])
            
            # Find matches and mismatches
            matches = pigeon_rings.intersection(result_rings)
            pigeon_only = pigeon_rings - result_rings
            result_only = result_rings - pigeon_rings
            
            if matches:
                self.log_investigation("Ring Number Matching", f"✅ {len(matches)} MATCHES FOUND", 
                                     f"Matching rings: {list(matches)[:5]}")
            else:
                self.log_investigation("Ring Number Matching", "❌ NO MATCHES", 
                                     "No ring numbers match between pigeons and results")
                
            if pigeon_only:
                self.log_investigation("Unmatched Pigeons", f"⚠️ {len(pigeon_only)} PIGEONS NO RESULTS", 
                                     f"Pigeon rings without results: {list(pigeon_only)[:5]}")
                
            if result_only:
                self.log_investigation("Unmatched Results", f"⚠️ {len(result_only)} RESULTS NO PIGEONS", 
                                     f"Result rings without pigeons: {list(result_only)[:5]}")
                
        except Exception as e:
            self.log_investigation("Ring Number Analysis", "❌ ERROR", f"Exception: {str(e)}")
            
    def test_file_upload_process(self):
        """Test the file upload process with a sample file"""
        try:
            # Check if user's result file exists
            user_file_path = '/app/user_result.txt'
            if not os.path.exists(user_file_path):
                # Check for alternative file names
                possible_files = ['/app/result_1.txt', '/app/result (1).txt']
                for file_path in possible_files:
                    if os.path.exists(file_path):
                        user_file_path = file_path
                        break
                        
            if not os.path.exists(user_file_path):
                self.log_investigation("File Upload Test", "⚠️ NO TEST FILE", 
                                     "User's result file not found for testing")
                return
                
            # Test file parsing
            with open(user_file_path, 'rb') as f:
                files = {'file': (os.path.basename(user_file_path), f, 'text/plain')}
                response = requests.post(f"{API_BASE}/upload-race-results", files=files, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                races_parsed = data.get('races', 0)
                results_parsed = data.get('results', 0)
                self.log_investigation("File Upload - Parse", "✅ PARSING SUCCESS", 
                                     f"Parsed {races_parsed} races, {results_parsed} potential results")
                
                # Test file processing
                with open(user_file_path, 'rb') as f:
                    files = {'file': (os.path.basename(user_file_path), f, 'text/plain')}
                    response = requests.post(f"{API_BASE}/confirm-race-upload", files=files, timeout=30)
                    
                if response.status_code == 200:
                    data = response.json()
                    races_created = data.get('races', 0)
                    results_created = data.get('results', 0)
                    self.log_investigation("File Upload - Process", "✅ PROCESSING SUCCESS", 
                                         f"Created {races_created} races, {results_created} results")
                else:
                    self.log_investigation("File Upload - Process", "❌ PROCESSING FAILED", 
                                         f"Status: {response.status_code}, Response: {response.text[:200]}")
            else:
                self.log_investigation("File Upload - Parse", "❌ PARSING FAILED", 
                                     f"Status: {response.status_code}, Response: {response.text[:200]}")
                
        except Exception as e:
            self.log_investigation("File Upload Test", "❌ ERROR", f"Exception: {str(e)}")
            
    def diagnose_root_cause(self):
        """Diagnose the root cause based on investigation results"""
        print("\n" + "="*80)
        print("🔍 ROOT CAUSE ANALYSIS")
        print("="*80)
        
        # Analyze the findings
        pigeon_count = self.system_state.get('pigeon_count', 0)
        results_count = self.system_state.get('results_count', 0)
        race_count = self.system_state.get('race_count', 0)
        
        print(f"📊 SYSTEM STATE SUMMARY:")
        print(f"   • Registered Pigeons: {pigeon_count}")
        print(f"   • Race Results: {results_count}")
        print(f"   • Total Races: {race_count}")
        
        # Determine root cause
        if pigeon_count == 0:
            print(f"\n🎯 ROOT CAUSE IDENTIFIED: NO PIGEONS REGISTERED")
            print(f"   • User has not registered any pigeons in the system")
            print(f"   • The system requires pigeons to be registered BEFORE uploading result files")
            print(f"   • Results only appear for pigeons that exist in the system")
            print(f"\n💡 SOLUTION:")
            print(f"   1. User must register their pigeons first using the 'Add Pigeon' feature")
            print(f"   2. Then upload the race result file")
            print(f"   3. Results will appear for registered pigeons only")
            
        elif pigeon_count > 0 and results_count == 0:
            print(f"\n🎯 ROOT CAUSE IDENTIFIED: RING NUMBER MISMATCH")
            print(f"   • Pigeons are registered but no results created")
            print(f"   • Likely mismatch between registered ring numbers and file content")
            print(f"   • File may have been processed but no matching pigeons found")
            print(f"\n💡 SOLUTION:")
            print(f"   1. Check registered pigeon ring numbers match those in the result file")
            print(f"   2. Ensure ring number format is consistent (e.g., BE504574322)")
            print(f"   3. Re-upload the result file after verifying ring numbers")
            
        elif pigeon_count > 0 and results_count > 0:
            # Check if there are matching ring numbers
            pigeon_rings = set(p.get('ring_number', '') for p in self.system_state.get('pigeons', []))
            result_rings = set(r.get('ring_number', '') for r in self.system_state.get('race_results', []))
            matches = pigeon_rings.intersection(result_rings)
            
            if matches:
                print(f"\n🎯 SYSTEM STATUS: WORKING CORRECTLY")
                print(f"   • {len(matches)} pigeons have race results")
                print(f"   • Results should be visible in the frontend")
                print(f"   • If user can't see results, it may be a frontend display issue")
                print(f"\n💡 NEXT STEPS:")
                print(f"   1. Check frontend display functionality")
                print(f"   2. Verify API endpoints are returning data correctly")
                print(f"   3. Check browser console for JavaScript errors")
            else:
                print(f"\n🎯 ROOT CAUSE IDENTIFIED: NO MATCHING RING NUMBERS")
                print(f"   • Pigeons and results exist but ring numbers don't match")
                print(f"   • Registered rings: {list(pigeon_rings)[:5]}")
                print(f"   • Result rings: {list(result_rings)[:5]}")
                print(f"\n💡 SOLUTION:")
                print(f"   1. Register pigeons with ring numbers that match the result file")
                print(f"   2. Or update existing pigeon ring numbers to match")
        else:
            print(f"\n🎯 SYSTEM STATUS: CLEAN STATE")
            print(f"   • No pigeons, races, or results in system")
            print(f"   • System is ready for fresh data")
            print(f"\n💡 NEXT STEPS:")
            print(f"   1. Register pigeons first")
            print(f"   2. Upload result file")
            print(f"   3. Verify results appear")
            
    def run_investigation(self):
        """Run the complete investigation"""
        print("="*80)
        print("🔍 USER ISSUE INVESTIGATION")
        print("PROBLEM: User uploaded result file but no results are showing up")
        print("="*80)
        print(f"Backend URL: {BACKEND_URL}")
        print()
        
        # Step 1: Check backend health
        if not self.check_backend_health():
            print("❌ Backend not accessible - investigation cannot continue")
            return False
            
        # Step 2: Check current system state
        print("\n📊 CHECKING CURRENT SYSTEM STATE...")
        self.check_current_system_state()
        
        # Step 3: Check backend API health
        print("\n🔧 CHECKING BACKEND API HEALTH...")
        self.check_backend_logs()
        
        # Step 4: Analyze ring number matching
        print("\n🔗 ANALYZING RING NUMBER MATCHING...")
        self.analyze_ring_number_matching()
        
        # Step 5: Test file upload process
        print("\n📁 TESTING FILE UPLOAD PROCESS...")
        self.test_file_upload_process()
        
        # Step 6: Diagnose root cause
        self.diagnose_root_cause()
        
        return True

if __name__ == "__main__":
    investigator = UserInvestigationTester()
    investigator.run_investigation()