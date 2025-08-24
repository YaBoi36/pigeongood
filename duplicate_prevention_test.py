#!/usr/bin/env python3
"""
Duplicate Prevention Test for Multi-Race Files
Tests the fix for race results with multi-race files to ensure each pigeon only gets ONE result per date.
"""

import requests
import sys
import json
from datetime import datetime
import time

class DuplicatePreventionTester:
    def __init__(self, base_url="https://race-loft.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_pigeon_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                        if len(response_data) > 0:
                            print(f"   First item: {response_data[0]}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:300]}...")

            return success, response.json() if response.text and response.status_code < 500 else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def clear_test_data(self):
        """Clear all test data before starting"""
        print("\n🧹 Clearing existing test data...")
        success, response = self.run_test(
            "Clear Test Data",
            "POST",
            "clear-test-data",
            200
        )
        return success

    def create_test_pigeons(self):
        """Create the two test pigeons as specified in the test scenario"""
        print("\n📋 STEP 1: Creating Test Pigeons")
        
        # Pigeon 1: Golden Sky
        pigeon1_data = {
            "ring_number": "BE501516325",
            "name": "Golden Sky",
            "country": "BE",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Test User"
        }
        
        success1, response1 = self.run_test(
            "Create Pigeon 1 - Golden Sky",
            "POST",
            "pigeons",
            200,
            data=pigeon1_data
        )
        
        if success1 and 'id' in response1:
            self.created_pigeons.append(response1['id'])
            print(f"   ✅ Golden Sky created with ID: {response1['id']}")
        
        # Pigeon 2: Silver Arrow
        pigeon2_data = {
            "ring_number": "BE501516025",
            "name": "Silver Arrow",
            "country": "BE",
            "gender": "Female",
            "color": "Silver",
            "breeder": "Test User"
        }
        
        success2, response2 = self.run_test(
            "Create Pigeon 2 - Silver Arrow",
            "POST",
            "pigeons",
            200,
            data=pigeon2_data
        )
        
        if success2 and 'id' in response2:
            self.created_pigeons.append(response2['id'])
            print(f"   ✅ Silver Arrow created with ID: {response2['id']}")
        
        return success1 and success2

    def upload_race_results_with_duplicates(self):
        """Upload race results that contain both test pigeons"""
        print("\n📋 STEP 2: Uploading Race Results with Test Pigeons")
        
        # Create TXT content with both test pigeons appearing multiple times (to test duplicate prevention)
        race_txt_content = """----------------------------------------------------------------------
Data Technology Deerlijk
----------------------------------------------------------------------
QUIEVRAIN 22-05-21 2000 Jongen Deelnemers: 45 LOSTIJD: 07:30:00

NR  Naam                Ring        Afstand  Tijd      Snelheid
----------------------------------------------------------------------
1   Test User          BE 501516325  85000   08.1234   1450.5
2   Test User          BE 501516025  85000   08.1456   1420.3
3   Other User         BE 111222333  85000   08.1678   1390.8
4   Test User          BE 501516325  85000   08.1234   1450.5
5   Test User          BE 501516025  85000   08.1456   1420.3
----------------------------------------------------------------------
"""
        
        # Create file-like object
        files = {
            'file': ('race_results_with_duplicates.txt', race_txt_content, 'text/plain')
        }
        
        # First upload - should process and create results
        success, response = self.run_test(
            "Upload Race Results (Initial)",
            "POST",
            "upload-race-results",
            200,
            files=files
        )
        
        if success:
            print(f"   📊 Upload Response: {response}")
            if 'needs_pigeon_count_confirmation' in response and response['needs_pigeon_count_confirmation']:
                print("   ⚠️  Needs pigeon count confirmation")
                return self.confirm_race_upload(files, 2000)
        
        return success

    def confirm_race_upload(self, files, pigeon_count):
        """Confirm race upload with specified pigeon count"""
        print(f"\n📋 STEP 2b: Confirming Race Upload with {pigeon_count} pigeons")
        
        success, response = self.run_test(
            "Confirm Race Upload",
            "POST",
            "confirm-race-upload",
            200,
            files=files,
            data={'confirmed_pigeon_count': str(pigeon_count)}
        )
        
        if success:
            print(f"   📊 Confirmation Response: {response}")
        
        return success

    def verify_no_duplicates(self):
        """Verify that each pigeon appears only once per race"""
        print("\n📋 STEP 3: Verifying No Duplicate Results")
        
        success, response = self.run_test(
            "Get Race Results",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            return False
        
        results = response
        print(f"   📊 Total results found: {len(results)}")
        
        # Count occurrences of each pigeon
        pigeon_counts = {}
        race_pigeon_combinations = set()
        
        for result in results:
            ring_number = result.get('ring_number', '')
            race_id = result.get('race_id', '')
            
            # Count total occurrences
            if ring_number not in pigeon_counts:
                pigeon_counts[ring_number] = 0
            pigeon_counts[ring_number] += 1
            
            # Track race-pigeon combinations
            combination = f"{race_id}_{ring_number}"
            if combination in race_pigeon_combinations:
                print(f"   ❌ DUPLICATE FOUND: {ring_number} appears multiple times in race {race_id}")
                return False
            race_pigeon_combinations.add(combination)
        
        # Check our test pigeons specifically
        golden_sky_count = pigeon_counts.get('BE501516325', 0)
        silver_arrow_count = pigeon_counts.get('BE501516025', 0)
        
        print(f"   📊 Golden Sky (BE501516325) appears {golden_sky_count} times")
        print(f"   📊 Silver Arrow (BE501516025) appears {silver_arrow_count} times")
        
        # Verify each pigeon appears exactly once
        if golden_sky_count == 1 and silver_arrow_count == 1:
            print("   ✅ SUCCESS: Each pigeon appears exactly once per race")
            return True
        else:
            print(f"   ❌ FAILURE: Expected each pigeon to appear once, but Golden Sky: {golden_sky_count}, Silver Arrow: {silver_arrow_count}")
            return False

    def test_re_upload_prevention(self):
        """Test that re-uploading the same file doesn't create duplicates"""
        print("\n📋 STEP 4: Testing Re-Upload Prevention")
        
        # Get current result count
        success, response = self.run_test(
            "Get Results Before Re-upload",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            return False
        
        initial_count = len(response)
        print(f"   📊 Initial result count: {initial_count}")
        
        # Try to upload the same file again
        race_txt_content = """----------------------------------------------------------------------
Data Technology Deerlijk
----------------------------------------------------------------------
QUIEVRAIN 22-05-21 2000 Jongen Deelnemers: 45 LOSTIJD: 07:30:00

NR  Naam                Ring        Afstand  Tijd      Snelheid
----------------------------------------------------------------------
1   Test User          BE 501516325  85000   08.1234   1450.5
2   Test User          BE 501516025  85000   08.1456   1420.3
----------------------------------------------------------------------
"""
        
        files = {
            'file': ('race_results_duplicate.txt', race_txt_content, 'text/plain')
        }
        
        # Upload again with confirmed pigeon count
        success, response = self.run_test(
            "Re-upload Same Results",
            "POST",
            "confirm-race-upload",
            200,
            files=files,
            data={'confirmed_pigeon_count': '2000'}
        )
        
        if not success:
            return False
        
        # Check result count after re-upload
        success, response = self.run_test(
            "Get Results After Re-upload",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            return False
        
        final_count = len(response)
        print(f"   📊 Final result count: {final_count}")
        
        if final_count == initial_count:
            print("   ✅ SUCCESS: Re-upload prevention working - no new duplicates created")
            return True
        else:
            print(f"   ❌ FAILURE: Re-upload created {final_count - initial_count} additional results")
            return False

    def verify_only_registered_pigeons(self):
        """Verify that only registered pigeons appear in results"""
        print("\n📋 STEP 5: Verifying Only Registered Pigeons in Results")
        
        # Get all registered pigeons
        success, pigeons_response = self.run_test(
            "Get All Registered Pigeons",
            "GET",
            "pigeons",
            200
        )
        
        if not success:
            return False
        
        registered_rings = {pigeon['ring_number'] for pigeon in pigeons_response}
        print(f"   📊 Registered pigeon rings: {registered_rings}")
        
        # Get all race results
        success, results_response = self.run_test(
            "Get All Race Results",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            return False
        
        result_rings = {result['ring_number'] for result in results_response}
        print(f"   📊 Result pigeon rings: {result_rings}")
        
        # Check if all result rings are in registered rings
        unregistered_in_results = result_rings - registered_rings
        
        if not unregistered_in_results:
            print("   ✅ SUCCESS: Only registered pigeons appear in results")
            return True
        else:
            print(f"   ❌ FAILURE: Unregistered pigeons found in results: {unregistered_in_results}")
            return False

    def verify_coefficient_calculations(self):
        """Verify that coefficient calculations are correct"""
        print("\n📋 STEP 6: Verifying Coefficient Calculations")
        
        success, response = self.run_test(
            "Get Race Results for Coefficient Check",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            return False
        
        all_correct = True
        for result in response:
            position = result.get('position', 0)
            coefficient = result.get('coefficient', 0)
            ring_number = result.get('ring_number', '')
            
            # Expected coefficient: (position * 100) / total_pigeons
            # We used 2000 pigeons in our test
            expected_coefficient = (position * 100) / 2000
            
            if abs(coefficient - expected_coefficient) > 0.01:  # Allow small floating point differences
                print(f"   ❌ Incorrect coefficient for {ring_number}: expected {expected_coefficient}, got {coefficient}")
                all_correct = False
            else:
                print(f"   ✅ Correct coefficient for {ring_number}: {coefficient}")
        
        return all_correct

def main():
    print("🚀 Starting Duplicate Prevention System Tests")
    print("=" * 70)
    print("Testing the FIXED duplicate prevention system implementation")
    print("=" * 70)
    
    tester = DuplicatePreventionTester()
    
    # Clear any existing test data
    tester.clear_test_data()
    
    # Run the comprehensive duplicate prevention test
    test_results = []
    
    # Step 1: Create test pigeons
    test_results.append(tester.create_test_pigeons())
    
    # Step 2: Upload race results
    test_results.append(tester.upload_race_results_with_duplicates())
    
    # Step 3: Verify no duplicates
    test_results.append(tester.verify_no_duplicates())
    
    # Step 4: Test re-upload prevention
    test_results.append(tester.test_re_upload_prevention())
    
    # Step 5: Verify only registered pigeons
    test_results.append(tester.verify_only_registered_pigeons())
    
    # Step 6: Verify coefficient calculations
    test_results.append(tester.verify_coefficient_calculations())
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 DUPLICATE PREVENTION TEST RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if all(test_results):
        print("🎉 ALL DUPLICATE PREVENTION TESTS PASSED!")
        print("✅ Each pigeon appears only ONCE per race")
        print("✅ Only registered pigeons appear in results")
        print("✅ Re-upload protection works correctly")
        print("✅ Coefficient calculations are accurate")
        print("✅ Duplicate prevention system is working perfectly!")
        return 0
    else:
        failed_count = len([r for r in test_results if not r])
        print(f"⚠️  {failed_count} critical test(s) failed!")
        print("❌ Duplicate prevention system needs attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())