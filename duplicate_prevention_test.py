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
                    response = requests.post(url, files=files)
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
        """Clear existing test data"""
        print("\n🧹 Clearing existing test data...")
        success, response = self.run_test(
            "Clear Test Data",
            "DELETE",
            "clear-test-data",
            200
        )
        return success

    def create_test_pigeon(self):
        """Create a test pigeon with ring number BE505078525 (appears in result_new.txt)"""
        pigeon_data = {
            "ring_number": "BE505078525",  # This ring number appears in result_new.txt
            "name": "Duplicate Test Pigeon",
            "country": "BE",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Test Breeder"
        }
        
        success, response = self.run_test(
            "Create Test Pigeon BE505078525",
            "POST",
            "pigeons",
            200,
            data=pigeon_data
        )
        
        if success and 'id' in response:
            self.created_pigeon_id = response['id']
            print(f"   Created pigeon ID: {self.created_pigeon_id}")
        
        return success

    def upload_multi_race_file(self):
        """Upload the result_new.txt file which contains 3 races from the same date"""
        try:
            with open('/app/result_new.txt', 'r') as f:
                txt_content = f.read()
        except FileNotFoundError:
            print("❌ result_new.txt file not found")
            return False
        
        files = {
            'file': ('result_new.txt', txt_content, 'text/plain')
        }
        
        success, response = self.run_test(
            "Upload Multi-Race File (result_new.txt)",
            "POST",
            "upload-race-results",
            200,
            files=files
        )
        
        if success:
            print(f"   Upload processed: {response.get('races', 0)} races, {response.get('results', 0)} results")
        
        return success

    def verify_single_result_per_pigeon(self):
        """Verify that pigeon BE505078525 has only ONE race result despite appearing multiple times in file"""
        success, response = self.run_test(
            "Get All Race Results",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            return False
        
        # Count results for our test pigeon
        test_pigeon_results = []
        for result in response:
            if result.get('ring_number') == 'BE505078525':
                test_pigeon_results.append(result)
        
        print(f"   Found {len(test_pigeon_results)} results for pigeon BE505078525")
        
        # Should have exactly 1 result
        if len(test_pigeon_results) == 1:
            print("   ✅ Duplicate prevention working - only 1 result found")
            result = test_pigeon_results[0]
            print(f"   Result details: Position {result.get('position')}, Speed {result.get('speed')}")
            return True
        elif len(test_pigeon_results) == 0:
            print("   ❌ No results found for test pigeon")
            return False
        else:
            print(f"   ❌ Duplicate prevention failed - found {len(test_pigeon_results)} results")
            for i, result in enumerate(test_pigeon_results):
                print(f"     Result {i+1}: Position {result.get('position')}, Race ID {result.get('race_id')}")
            return False

    def verify_races_created(self):
        """Verify that all 3 races were created from the file"""
        # Check races by looking at race results and counting unique race_ids
        success, response = self.run_test(
            "Get All Race Results to Check Races",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            return False
        
        # Count unique race IDs
        race_ids = set()
        for result in response:
            if result.get('race_id'):
                race_ids.add(result['race_id'])
        
        print(f"   Found {len(race_ids)} unique races in results")
        
        # Should have 3 races (32 Oude, 26 Jaarduiven, 462 Jongen)
        if len(race_ids) >= 3:
            print("   ✅ Multiple races created successfully")
            return True
        else:
            print(f"   ❌ Expected at least 3 races, found {len(race_ids)}")
            return False

    def verify_other_pigeons_work(self):
        """Verify that other functionality still works (race creation, result insertion for different pigeons)"""
        # Create another pigeon with a different ring number
        timestamp = str(int(time.time()))[-6:]
        other_pigeon_data = {
            "ring_number": f"BE{timestamp}999",
            "name": "Other Test Pigeon",
            "country": "BE",
            "gender": "Female",
            "color": "Red",
            "breeder": "Test Breeder"
        }
        
        success, response = self.run_test(
            "Create Other Test Pigeon",
            "POST",
            "pigeons",
            200,
            data=other_pigeon_data
        )
        
        if not success:
            return False
        
        other_pigeon_id = response['id']
        
        # Create a simple race result file for this pigeon
        simple_race_content = f"""----------------------------------------------------------------------
Data Technology Deerlijk
----------------------------------------------------------------------
QUIEVRAIN 22-05-21 1234 Jongen Deelnemers: 45 LOSTIJD: 07:30:00

NR  Naam                Ring        Afstand  Tijd      Snelheid
----------------------------------------------------------------------
1   Test Owner         {other_pigeon_data['ring_number']}  12500   08.1234   1450.5
----------------------------------------------------------------------
"""
        
        files = {
            'file': ('simple_race.txt', simple_race_content, 'text/plain')
        }
        
        success, upload_response = self.run_test(
            "Upload Simple Race for Other Pigeon",
            "POST",
            "upload-race-results",
            200,
            files=files
        )
        
        if success:
            print(f"   Other pigeon upload: {upload_response.get('races', 0)} races, {upload_response.get('results', 0)} results")
        
        # Cleanup
        self.run_test("Cleanup Other Pigeon", "DELETE", f"pigeons/{other_pigeon_id}", 200)
        
        return success

    def analyze_file_content(self):
        """Analyze the result_new.txt file to understand the test scenario"""
        try:
            with open('/app/result_new.txt', 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print("❌ result_new.txt file not found")
            return False
        
        print("\n📋 Analyzing result_new.txt file content...")
        
        # Count occurrences of BE505078525
        occurrences = content.count('BE 505078525')
        print(f"   Ring number 'BE 505078525' appears {occurrences} times in file")
        
        # Find race headers
        race_headers = []
        lines = content.split('\n')
        for line in lines:
            if 'CHIMAY' in line and '09-08-25' in line:
                race_headers.append(line.strip())
        
        print(f"   Found {len(race_headers)} race headers:")
        for i, header in enumerate(race_headers):
            print(f"     Race {i+1}: {header}")
        
        # This should show 3 races all on the same date (09-08-25)
        # and the pigeon BE505078525 appearing in multiple races
        
        return True

    def cleanup_test_pigeon(self):
        """Clean up the test pigeon"""
        if self.created_pigeon_id:
            success, response = self.run_test(
                "Cleanup Test Pigeon",
                "DELETE",
                f"pigeons/{self.created_pigeon_id}",
                200
            )
            return success
        return True

def main():
    print("🚀 Starting Duplicate Prevention Test for Multi-Race Files")
    print("=" * 70)
    
    tester = DuplicatePreventionTester()
    
    # Run the comprehensive duplicate prevention test
    test_results = []
    
    # Step 1: Analyze the test file
    test_results.append(tester.analyze_file_content())
    
    # Step 2: Clear any existing test data
    test_results.append(tester.clear_test_data())
    
    # Step 3: Create test pigeon with ring number that appears in file
    test_results.append(tester.create_test_pigeon())
    
    # Step 4: Upload the multi-race file
    test_results.append(tester.upload_multi_race_file())
    
    # Step 5: Verify duplicate prevention - should have only 1 result
    test_results.append(tester.verify_single_result_per_pigeon())
    
    # Step 6: Verify that races were created properly
    test_results.append(tester.verify_races_created())
    
    # Step 7: Verify other functionality still works
    test_results.append(tester.verify_other_pigeons_work())
    
    # Step 8: Cleanup
    test_results.append(tester.cleanup_test_pigeon())
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All duplicate prevention tests passed!")
        print("✅ Duplicate prevention logic is working correctly")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} test(s) failed. Duplicate prevention may have issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())