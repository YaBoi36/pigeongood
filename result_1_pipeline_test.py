#!/usr/bin/env python3
"""
Focused test for result_1.txt file upload and parsing pipeline
Testing the specific issues mentioned in the review request
"""

import requests
import json
import sys

class Result1PipelineTest:
    def __init__(self, base_url="https://flight-results-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def log(self, message):
        print(f"   {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 {name}...")
        
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

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:300]}...")

            return success, response.json() if response.text and response.status_code < 500 else {}

        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False, {}

    def test_result_1_pipeline(self):
        """Test the complete result_1.txt upload and parsing pipeline"""
        print("\n" + "="*80)
        print("🎯 TESTING RESULT_1.TXT PIPELINE - FOCUS OF REVIEW REQUEST")
        print("="*80)
        
        # Step 1: Clear any existing test data
        print("\n📋 Step 1: Clear existing test data")
        success, _ = self.run_test(
            "Clear Test Data",
            "POST",
            "clear-test-data",
            200
        )
        
        # Step 2: Create test pigeons with specific ring numbers from result_1.txt
        print("\n📋 Step 2: Create test pigeons with ring numbers from result_1.txt")
        test_pigeons = [
            {
                "ring_number": "BE504574322",  # Appears in races 1 and 4
                "name": "VRANCKEN Test Pigeon",
                "country": "BE",
                "gender": "Male",
                "color": "Blue",
                "breeder": "VRANCKEN WILLY&DOCHTE"
            },
            {
                "ring_number": "BE504813624",  # Appears in races 2 and 4
                "name": "BRIERS Test Pigeon", 
                "country": "BE",
                "gender": "Female",
                "color": "Red",
                "breeder": "BRIERS VALENT.&ZN"
            },
            {
                "ring_number": "BE505078525",  # Appears in race 3
                "name": "VANGEEL Test Pigeon",
                "country": "BE",
                "gender": "Male",
                "color": "Checker",
                "breeder": "VANGEEL JO"
            }
        ]
        
        created_pigeons = []
        for pigeon_data in test_pigeons:
            success, response = self.run_test(
                f"Create Pigeon {pigeon_data['ring_number']}",
                "POST",
                "pigeons",
                200,
                data=pigeon_data
            )
            
            if success and 'id' in response:
                created_pigeons.append({
                    'id': response['id'],
                    'ring_number': pigeon_data['ring_number']
                })
                self.log(f"✅ Created pigeon: {pigeon_data['ring_number']} -> ID: {response['id']}")
            else:
                self.log(f"❌ Failed to create pigeon {pigeon_data['ring_number']}")
                return False
        
        if len(created_pigeons) != 3:
            print("❌ CRITICAL: Failed to create all 3 test pigeons")
            return False
        
        print(f"✅ Successfully created {len(created_pigeons)} test pigeons")
        
        # Step 3: Upload result_1.txt file
        print("\n📋 Step 3: Upload result_1.txt file")
        try:
            with open('/app/result_1.txt', 'r') as f:
                txt_content = f.read()
        except FileNotFoundError:
            print("❌ CRITICAL: result_1.txt file not found")
            return False
        
        files = {
            'file': ('result_1.txt', txt_content, 'text/plain')
        }
        
        success, upload_response = self.run_test(
            "Upload result_1.txt File",
            "POST", 
            "upload-race-results",
            200,
            files=files
        )
        
        if not success:
            print("❌ CRITICAL: Failed to upload result_1.txt file")
            return False
        
        # Step 4: Analyze upload results
        print("\n📋 Step 4: Analyze upload results")
        races_processed = upload_response.get('races', 0)
        results_created = upload_response.get('results', 0)
        parsed_counts = upload_response.get('parsed_pigeon_counts', [])
        
        print(f"   📊 Races processed: {races_processed}")
        print(f"   📊 Results created: {results_created}")
        print(f"   📊 Parsed pigeon counts: {parsed_counts}")
        
        # Issue 1: Check if all 4 races were processed
        if races_processed != 4:
            print(f"❌ ISSUE 1 CONFIRMED: Only {races_processed} out of 4 races processed")
            print("   Expected: 4 races (32 Oude, 26 Jaarduiven, 462 Jongen, 58 Oude+jaarse)")
            print(f"   Actual: {races_processed} races")
        else:
            print("✅ All 4 races processed correctly")
        
        # Issue 2: Check if results were created for registered pigeons
        if results_created == 0:
            print(f"❌ ISSUE 2 CONFIRMED: 0 results created despite registered pigeons")
            print("   Expected: At least 1 result per registered pigeon")
            print(f"   Actual: {results_created} results")
        else:
            print(f"✅ {results_created} results created for registered pigeons")
        
        # Step 5: Get race results to verify pigeon-result matching
        print("\n📋 Step 5: Verify pigeon-result matching")
        success, results_response = self.run_test(
            "Get Race Results",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            print("❌ Failed to get race results")
            return False
        
        # Analyze results
        matched_results = []
        pigeon_results_count = {}
        
        for result in results_response:
            if result.get('pigeon'):
                pigeon_id = result['pigeon']['id']
                ring_number = result['ring_number']
                
                # Check if this is one of our test pigeons
                for created_pigeon in created_pigeons:
                    if created_pigeon['id'] == pigeon_id:
                        matched_results.append(result)
                        if ring_number not in pigeon_results_count:
                            pigeon_results_count[ring_number] = 0
                        pigeon_results_count[ring_number] += 1
                        race_category = result.get('race', {}).get('category', 'Unknown')
                        self.log(f"✅ Found result for {ring_number} in race category: {race_category}")
                        break
        
        print(f"   📊 Matched results: {len(matched_results)}")
        print(f"   📊 Pigeon results count: {pigeon_results_count}")
        
        # Step 6: Test duplicate prevention
        print("\n📋 Step 6: Test duplicate prevention")
        duplicate_prevention_working = True
        for ring_number, count in pigeon_results_count.items():
            if count != 1:
                print(f"❌ DUPLICATE ISSUE: Ring {ring_number} has {count} results (expected 1)")
                duplicate_prevention_working = False
            else:
                self.log(f"✅ Ring {ring_number} has exactly 1 result")
        
        # Step 7: Verify specific ring numbers from review request
        print("\n📋 Step 7: Verify specific ring numbers from review request")
        expected_rings = ["BE504574322", "BE504813624", "BE505078525"]
        found_rings = list(pigeon_results_count.keys())
        
        for expected_ring in expected_rings:
            if expected_ring in found_rings:
                self.log(f"✅ Ring {expected_ring} found in results")
            else:
                print(f"❌ MISSING: Ring {expected_ring} not found in results")
        
        # Step 8: Test duplicate file upload prevention
        print("\n📋 Step 8: Test duplicate file upload prevention")
        success, second_upload_response = self.run_test(
            "Upload Same File Again",
            "POST",
            "upload-race-results",
            200,
            files=files
        )
        
        if success:
            second_results_created = second_upload_response.get('results', 0)
            if second_results_created > 0:
                print(f"❌ DUPLICATE FILE ISSUE: Second upload created {second_results_created} additional results")
                duplicate_prevention_working = False
            else:
                self.log("✅ Second upload created 0 additional results")
        
        # Step 9: Cleanup
        print("\n📋 Step 9: Cleanup test data")
        for pigeon in created_pigeons:
            self.run_test(
                f"Delete Pigeon {pigeon['ring_number']}",
                "DELETE",
                f"pigeons/{pigeon['id']}",
                200
            )
        
        # Final Assessment
        print("\n" + "="*80)
        print("📊 FINAL ASSESSMENT")
        print("="*80)
        
        issues_found = []
        
        if races_processed != 4:
            issues_found.append(f"Only {races_processed}/4 races processed")
        
        if results_created == 0:
            issues_found.append("0 results created despite registered pigeons")
        
        if len(matched_results) == 0:
            issues_found.append("No results matched to registered pigeons")
        
        if not duplicate_prevention_working:
            issues_found.append("Duplicate prevention not working correctly")
        
        if len(found_rings) != len(expected_rings):
            issues_found.append(f"Only {len(found_rings)}/{len(expected_rings)} expected ring numbers found")
        
        if issues_found:
            print("❌ PIPELINE TEST FAILED - Issues found:")
            for i, issue in enumerate(issues_found, 1):
                print(f"   {i}. {issue}")
            return False
        else:
            print("✅ PIPELINE TEST PASSED - All issues resolved:")
            print(f"   ✅ All 4 races processed")
            print(f"   ✅ {results_created} results created for registered pigeons")
            print(f"   ✅ {len(matched_results)} results matched to registered pigeons")
            print(f"   ✅ Duplicate prevention working correctly")
            print(f"   ✅ All {len(expected_rings)} expected ring numbers found")
            return True

def main():
    print("🚀 Result_1.txt Pipeline Test - Focus of Review Request")
    print("Testing file upload and parsing pipeline issues")
    
    tester = Result1PipelineTest()
    
    success = tester.test_result_1_pipeline()
    
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} API calls passed")
    
    if success:
        print("🎉 PIPELINE TEST PASSED - All issues resolved!")
        return 0
    else:
        print("⚠️  PIPELINE TEST FAILED - Issues still exist")
        return 1

if __name__ == "__main__":
    sys.exit(main())