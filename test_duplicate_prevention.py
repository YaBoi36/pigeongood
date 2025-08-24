#!/usr/bin/env python3
"""
Test duplicate prevention logic specifically for pigeons appearing in multiple races on same date
"""

import requests
import json
import sys

class DuplicatePreventionTest:
    def __init__(self, base_url="https://flight-results-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {'Content-Type': 'application/json'} if not files else {}

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

    def test_duplicate_prevention_same_date(self):
        """Test that pigeons appearing in multiple races on same date only get 1 result"""
        print("\n" + "="*80)
        print("🚫 TESTING DUPLICATE PREVENTION - SAME DATE MULTIPLE RACES")
        print("="*80)
        
        # Step 1: Clear test data
        print("\n📋 Step 1: Clear existing test data")
        success, _ = self.run_test("Clear Test Data", "POST", "clear-test-data", 200)
        
        # Step 2: Create pigeons that appear in multiple races in result_1.txt
        print("\n📋 Step 2: Create pigeons that appear in multiple races")
        test_pigeons = [
            {
                "ring_number": "BE504574322",  # Appears in races 1 (Oude) and 4 (Oude+jaarse)
                "name": "VRANCKEN Multi-Race Pigeon",
                "country": "BE",
                "gender": "Male",
                "color": "Blue",
                "breeder": "VRANCKEN WILLY&DOCHTE"
            },
            {
                "ring_number": "BE504813624",  # Appears in races 2 (Jaarduiven) and 4 (Oude+jaarse)
                "name": "BRIERS Multi-Race Pigeon", 
                "country": "BE",
                "gender": "Female",
                "color": "Red",
                "breeder": "BRIERS VALENT.&ZN"
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
                print(f"   ✅ Created pigeon: {pigeon_data['ring_number']} -> ID: {response['id']}")
            else:
                print(f"❌ Failed to create pigeon {pigeon_data['ring_number']}")
                return False
        
        # Step 3: Upload result_1.txt file
        print("\n📋 Step 3: Upload result_1.txt file")
        try:
            with open('/app/result_1.txt', 'r') as f:
                txt_content = f.read()
        except FileNotFoundError:
            print("❌ result_1.txt file not found")
            return False
        
        files = {'file': ('result_1.txt', txt_content, 'text/plain')}
        
        success, upload_response = self.run_test(
            "Upload result_1.txt File",
            "POST", 
            "upload-race-results",
            200,
            files=files
        )
        
        if not success:
            print("❌ Failed to upload result_1.txt file")
            return False
        
        # Step 4: Verify duplicate prevention
        print("\n📋 Step 4: Verify duplicate prevention")
        success, results_response = self.run_test(
            "Get Race Results",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            print("❌ Failed to get race results")
            return False
        
        # Analyze results for our test pigeons
        pigeon_results = {}
        for result in results_response:
            if result.get('pigeon'):
                pigeon_id = result['pigeon']['id']
                ring_number = result['ring_number']
                
                # Check if this is one of our test pigeons
                for created_pigeon in created_pigeons:
                    if created_pigeon['id'] == pigeon_id:
                        if ring_number not in pigeon_results:
                            pigeon_results[ring_number] = []
                        pigeon_results[ring_number].append({
                            'race_category': result.get('race', {}).get('category', 'Unknown'),
                            'race_date': result.get('race', {}).get('date', 'Unknown'),
                            'position': result.get('position', 0)
                        })
                        break
        
        print(f"   📊 Results found for test pigeons:")
        for ring_number, results in pigeon_results.items():
            print(f"     Ring {ring_number}: {len(results)} result(s)")
            for result in results:
                print(f"       - Race: {result['race_category']}, Date: {result['race_date']}, Position: {result['position']}")
        
        # Step 5: Verify duplicate prevention is working
        print("\n📋 Step 5: Verify duplicate prevention logic")
        duplicate_prevention_working = True
        
        for ring_number, results in pigeon_results.items():
            if len(results) > 1:
                # Check if all results are from the same date
                dates = set(result['race_date'] for result in results)
                if len(dates) == 1:
                    print(f"❌ DUPLICATE PREVENTION FAILED: Ring {ring_number} has {len(results)} results on same date {list(dates)[0]}")
                    duplicate_prevention_working = False
                else:
                    print(f"   ✅ Ring {ring_number} has {len(results)} results on different dates - OK")
            elif len(results) == 1:
                print(f"   ✅ Ring {ring_number} has exactly 1 result - duplicate prevention working")
            else:
                print(f"   ⚠️  Ring {ring_number} has 0 results")
        
        # Step 6: Test uploading the same file again
        print("\n📋 Step 6: Test uploading same file again")
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
                print(f"❌ DUPLICATE FILE UPLOAD ISSUE: Second upload created {second_results_created} additional results")
                duplicate_prevention_working = False
            else:
                print(f"   ✅ Second upload created 0 additional results")
        
        # Step 7: Cleanup
        print("\n📋 Step 7: Cleanup test data")
        for pigeon in created_pigeons:
            self.run_test(
                f"Delete Pigeon {pigeon['ring_number']}",
                "DELETE",
                f"pigeons/{pigeon['id']}",
                200
            )
        
        # Final assessment
        print("\n" + "="*80)
        print("📊 DUPLICATE PREVENTION TEST RESULTS")
        print("="*80)
        
        if duplicate_prevention_working:
            print("✅ DUPLICATE PREVENTION TEST PASSED")
            print("   ✅ Each pigeon has only 1 result per date")
            print("   ✅ Duplicate file upload prevented")
            print("   ✅ Multi-race files handled correctly")
            return True
        else:
            print("❌ DUPLICATE PREVENTION TEST FAILED")
            print("   ❌ Duplicates were not properly prevented")
            return False

def main():
    print("🚫 Duplicate Prevention Test - Multi-Race Same Date")
    print("Testing duplicate prevention for pigeons in multiple races on same date")
    
    tester = DuplicatePreventionTest()
    
    success = tester.test_duplicate_prevention_same_date()
    
    if success:
        print("\n🎉 DUPLICATE PREVENTION TEST PASSED!")
        return 0
    else:
        print("\n⚠️  DUPLICATE PREVENTION TEST FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())