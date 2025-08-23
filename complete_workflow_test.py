#!/usr/bin/env python3
"""
Complete End-to-End Workflow Test for Pigeon Racing Dashboard
Tests the exact workflow requested by the main agent.
"""

import requests
import sys
import json
import io
from datetime import datetime

class CompleteWorkflowTester:
    def __init__(self, base_url="https://pigeon-dashboard.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.pigeon_ids = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")

    def make_request(self, method, endpoint, data=None, files=None):
        """Make HTTP request to API"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {'Content-Type': 'application/json'} if not files else {}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            return response.status_code, response.json() if response.text else {}
        except Exception as e:
            print(f"Request error: {str(e)}")
            return 500, {}

    def step_1_verify_clean_state(self):
        """Step 1: Verify Clean State"""
        print("\n🔍 STEP 1: Verify Clean State")
        
        # Clear any existing data first
        status, response = self.make_request('POST', 'clear-test-data')
        if status == 200:
            print(f"   Cleared existing data: {response}")
        
        # Check dashboard stats
        status, stats = self.make_request('GET', 'dashboard-stats')
        if status == 200:
            expected_clean = {
                'total_races': 0,
                'total_wins': 0, 
                'total_results': 0,
                'total_pigeons': 0
            }
            
            clean_state = all(stats.get(key, -1) == expected_clean[key] for key in expected_clean)
            self.log_test(
                "Dashboard shows clean state (0 races, 0 wins, 0 results, 0 pigeons)",
                clean_state,
                f"Stats: {stats}"
            )
            return clean_state
        else:
            self.log_test("Get dashboard stats", False, f"Status: {status}")
            return False

    def step_2_add_test_pigeons(self):
        """Step 2: Add Test Pigeons"""
        print("\n🐦 STEP 2: Add Test Pigeons")
        
        pigeons_to_add = [
            {
                "ring_number": "501516325",
                "name": "Golden Sky",
                "country": "BE",
                "gender": "Male",
                "color": "Blue",
                "breeder": "Test User"
            },
            {
                "ring_number": "501516025", 
                "name": "Silver Arrow",
                "country": "BE",
                "gender": "Female",
                "color": "Silver",
                "breeder": "Test User"
            }
        ]
        
        success_count = 0
        for pigeon_data in pigeons_to_add:
            status, response = self.make_request('POST', 'pigeons', pigeon_data)
            if status == 200:
                self.pigeon_ids.append(response['id'])
                self.log_test(
                    f"Add pigeon {pigeon_data['name']} (Ring: {pigeon_data['country']}{pigeon_data['ring_number']})",
                    True,
                    f"ID: {response['id']}"
                )
                success_count += 1
            else:
                self.log_test(
                    f"Add pigeon {pigeon_data['name']}",
                    False,
                    f"Status: {status}, Response: {response}"
                )
        
        return success_count == 2

    def step_3_upload_race_results(self):
        """Step 3: Upload Race Results"""
        print("\n📁 STEP 3: Upload Race Results")
        
        # Create race results TXT file with both pigeons
        race_results_content = """----------------------------------------------------------------------
Data Technology Deerlijk
----------------------------------------------------------------------
LUMMEN 25-08-23 2000 Jongen Deelnemers: 150 LOSTIJD: 07:30:00

NR  Naam                Ring        Afstand  Tijd      Snelheid
----------------------------------------------------------------------
1   Test User          BE 501516325  85000   08.1234   1450.5
2   Test User          BE 501516025  85000   08.1456   1420.3
----------------------------------------------------------------------
"""
        
        # First upload to get pigeon count confirmation
        files = {
            'file': ('race_results.txt', io.StringIO(race_results_content), 'text/plain')
        }
        
        status, response = self.make_request('POST', 'upload-race-results', files=files)
        if status == 200 and response.get('needs_pigeon_count_confirmation'):
            self.log_test(
                "Initial race results upload",
                True,
                f"Needs confirmation. Parsed count: {response.get('parsed_pigeon_counts', [])}"
            )
            
            # Confirm with 2000 pigeons as requested
            files = {
                'file': ('race_results.txt', io.StringIO(race_results_content), 'text/plain'),
                'confirmed_pigeon_count': ('', '2000')
            }
            
            status, response = self.make_request('POST', 'confirm-race-upload', files=files)
            if status == 200:
                self.log_test(
                    "Confirm race upload with 2000 pigeons",
                    True,
                    f"Processed: {response.get('races', 0)} races, {response.get('results', 0)} results"
                )
                return response.get('results', 0) > 0
            else:
                self.log_test("Confirm race upload", False, f"Status: {status}")
                return False
        else:
            self.log_test("Initial race results upload", False, f"Status: {status}")
            return False

    def step_4_verify_dashboard_statistics(self):
        """Step 4: Verify Dashboard Statistics Work Correctly"""
        print("\n📊 STEP 4: Verify Dashboard Statistics")
        
        status, stats = self.make_request('GET', 'dashboard-stats')
        if status != 200:
            self.log_test("Get dashboard stats", False, f"Status: {status}")
            return False
        
        print(f"   Current stats: {stats}")
        
        # Verify Total Races
        total_races = stats.get('total_races', 0)
        self.log_test(
            f"Total Races shows actual count: {total_races}",
            total_races == 1,
            "Should be 1 race"
        )
        
        # Verify Total Wins (position #1 results)
        total_wins = stats.get('total_wins', 0)
        self.log_test(
            f"Total Wins shows position #1 count: {total_wins}",
            total_wins == 1,
            "Should be 1 win (Golden Sky at position 1)"
        )
        
        # Verify Total Results
        total_results = stats.get('total_results', 0)
        self.log_test(
            f"Total Results shows actual count: {total_results}",
            total_results == 2,
            "Should be 2 results (both pigeons)"
        )
        
        # Verify Total Pigeons
        total_pigeons = stats.get('total_pigeons', 0)
        self.log_test(
            f"Total Pigeons shows actual count: {total_pigeons}",
            total_pigeons == 2,
            "Should be 2 pigeons"
        )
        
        # Calculate expected win rate
        expected_win_rate = (total_wins / total_results * 100) if total_results > 0 else 0
        print(f"   Expected win rate: {expected_win_rate}% (1 win / 2 results)")
        
        return all([
            total_races == 1,
            total_wins == 1,
            total_results == 2,
            total_pigeons == 2
        ])

    def step_5_verify_race_results_display(self):
        """Step 5: Verify Race Results Display"""
        print("\n🏁 STEP 5: Verify Race Results Display")
        
        status, results = self.make_request('GET', 'race-results')
        if status != 200:
            self.log_test("Get race results", False, f"Status: {status}")
            return False
        
        print(f"   Found {len(results)} race results")
        
        # Verify both pigeons appear exactly once
        ring_numbers = [result.get('ring_number', '') for result in results]
        expected_rings = ['BE501516325', 'BE501516025']
        
        both_pigeons_present = all(ring in ring_numbers for ring in expected_rings)
        self.log_test(
            "Both pigeons appear in results",
            both_pigeons_present,
            f"Found rings: {ring_numbers}"
        )
        
        # Verify each pigeon appears only once
        unique_results = len(set(ring_numbers)) == len(ring_numbers)
        self.log_test(
            "Each pigeon appears exactly once",
            unique_results,
            f"Unique count: {len(set(ring_numbers))}, Total count: {len(ring_numbers)}"
        )
        
        # Verify race details are accurate
        details_accurate = True
        for result in results:
            if not all([
                result.get('position') in [1, 2],
                result.get('speed', 0) > 1000,
                result.get('distance', 0) == 85000,
                result.get('coefficient', 0) > 0
            ]):
                details_accurate = False
                break
        
        self.log_test(
            "Race details are accurate (speeds, distances, coefficients)",
            details_accurate,
            "All results have valid position, speed, distance, and coefficient"
        )
        
        # Verify coefficients calculated with confirmed pigeon count (2000)
        coefficients_correct = True
        for result in results:
            expected_coeff = (result.get('position', 0) * 100) / 2000
            actual_coeff = result.get('coefficient', 0)
            if abs(actual_coeff - expected_coeff) > 0.01:  # Allow small floating point differences
                coefficients_correct = False
                print(f"   Coefficient mismatch: Expected {expected_coeff}, Got {actual_coeff}")
                break
        
        self.log_test(
            "Coefficients calculated with confirmed pigeon count (2000)",
            coefficients_correct,
            "All coefficients match (position × 100) ÷ 2000"
        )
        
        return all([
            both_pigeons_present,
            unique_results,
            details_accurate,
            coefficients_correct
        ])

    def run_complete_workflow(self):
        """Run the complete end-to-end workflow test"""
        print("🚀 COMPLETE END-TO-END WORKFLOW TEST")
        print("=" * 60)
        print("Testing the FINAL COMPLETE WORKFLOW to ensure all dashboard statistics work correctly.")
        print("Database has been completely cleared.")
        print()
        
        # Run all steps
        step_results = []
        step_results.append(self.step_1_verify_clean_state())
        step_results.append(self.step_2_add_test_pigeons())
        step_results.append(self.step_3_upload_race_results())
        step_results.append(self.step_4_verify_dashboard_statistics())
        step_results.append(self.step_5_verify_race_results_display())
        
        # Final summary
        print("\n" + "=" * 60)
        print("📋 SUCCESS CRITERIA VERIFICATION:")
        
        criteria = [
            "✅ Dashboard statistics reflect actual data (not hardcoded values)",
            "✅ Recent Race Results shows correct count and data", 
            "✅ Each pigeon appears once per race",
            "✅ Coefficients calculated with confirmed pigeon count",
            "✅ All statistics are mathematically correct"
        ]
        
        all_passed = all(step_results)
        if all_passed:
            print("🎉 ALL SUCCESS CRITERIA MET!")
            for criterion in criteria:
                print(f"   {criterion}")
        else:
            print("⚠️  SOME CRITERIA NOT MET:")
            failed_steps = [i+1 for i, result in enumerate(step_results) if not result]
            print(f"   Failed steps: {failed_steps}")
        
        print(f"\n📊 Overall Results: {self.tests_passed}/{self.tests_run} tests passed")
        return 0 if all_passed else 1

def main():
    tester = CompleteWorkflowTester()
    return tester.run_complete_workflow()

if __name__ == "__main__":
    sys.exit(main())