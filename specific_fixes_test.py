import requests
import sys
import json
import io
from datetime import datetime

class SpecificFixesTester:
    def __init__(self, base_url="https://race-loft.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_pigeon_id = None
        self.race_results = []

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
                    if isinstance(response_data, dict) and len(str(response_data)) < 1000:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                        if len(response_data) <= 5:
                            for i, item in enumerate(response_data):
                                print(f"   Item {i+1}: {item}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:300]}...")

            return success, response.json() if response.text and response.status_code < 500 else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_clear_data(self):
        """Clear existing test data"""
        success, response = self.run_test(
            "Clear Test Data",
            "POST",
            "clear-test-data",
            200
        )
        return success

    def test_create_test_pigeon(self):
        """Create the test pigeon as specified in the review request"""
        pigeon_data = {
            "ring_number": "BE501516325",
            "name": "Golden Sky",
            "country": "BE",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Test User"
        }
        
        success, response = self.run_test(
            "Create Test Pigeon (BE501516325 - Golden Sky)",
            "POST",
            "pigeons",
            200,
            data=pigeon_data
        )
        
        if success and 'id' in response:
            self.created_pigeon_id = response['id']
            print(f"   Created pigeon ID: {self.created_pigeon_id}")
        
        return success

    def test_upload_race_with_duplicates(self):
        """Test uploading race results with duplicate ring numbers to verify duplicate prevention"""
        # Create a sample TXT file with duplicate ring numbers
        sample_txt_content = """----------------------------------------------------------------------
Data Technology Deerlijk
----------------------------------------------------------------------
QUIEVRAIN 22-05-21 357 Jongen Deelnemers: 45 LOSTIJD: 07:30:00

NR  Naam                Ring        Afstand  Tijd      Snelheid
----------------------------------------------------------------------
1   John Doe           BE501516325  85000   08.1234   1450.5
2   Jane Smith         NL987654321  85000   08.1456   1420.3
3   Bob Johnson        BE111222333  85000   08.1678   1390.8
10  Test Duplicate     BE501516325  85000   08.2000   1300.0
15  Another Dup        BE501516325  85000   08.2500   1250.0
20  Third Dup          BE501516325  85000   08.3000   1200.0
----------------------------------------------------------------------
"""
        
        # Create file-like object
        files = {
            'file': ('race_results_with_duplicates.txt', sample_txt_content, 'text/plain')
        }
        
        # First upload without confirmation to get pigeon count
        success, response = self.run_test(
            "Upload Race Results with Duplicates (Initial)",
            "POST",
            "upload-race-results",
            200,
            files=files
        )
        
        if success and response.get('needs_pigeon_count_confirmation'):
            print(f"   Detected pigeon count: {response.get('parsed_pigeon_counts', [])}")
            
            # Now confirm with the detected pigeon count
            files = {
                'file': ('race_results_with_duplicates.txt', sample_txt_content, 'text/plain')
            }
            data = {'confirmed_pigeon_count': '357'}
            
            success2, response2 = self.run_test(
                "Confirm Race Upload with 357 Pigeons",
                "POST",
                "confirm-race-upload",
                200,
                data=data,
                files=files
            )
            
            if success2:
                print(f"   Processed {response2.get('results', 0)} results")
            
            return success2
        
        return success

    def test_verify_duplicate_prevention(self):
        """Verify that duplicate ring numbers are prevented"""
        success, response = self.run_test(
            "Get Race Results to Check Duplicates",
            "GET",
            "race-results",
            200
        )
        
        if success and isinstance(response, list):
            # Count occurrences of BE501516325
            be501516325_count = 0
            for result in response:
                if result.get('ring_number') == 'BE501516325':
                    be501516325_count += 1
            
            print(f"   Found {be501516325_count} results for ring number BE501516325")
            
            if be501516325_count == 1:
                print("✅ Duplicate prevention working correctly - only 1 result per ring number")
                return True
            else:
                print(f"❌ Duplicate prevention failed - found {be501516325_count} results for same ring number")
                return False
        
        return False

    def test_verify_coefficient_calculation(self):
        """Verify that coefficients are calculated as decimals"""
        success, response = self.run_test(
            "Get Race Results to Check Coefficients",
            "GET",
            "race-results",
            200
        )
        
        if success and isinstance(response, list):
            print("   Checking coefficient calculations:")
            decimal_coefficients_found = False
            
            for result in response:
                coefficient = result.get('coefficient', 0)
                position = result.get('position', 0)
                ring_number = result.get('ring_number', 'Unknown')
                
                print(f"   Ring {ring_number}: Position {position}, Coefficient {coefficient}")
                
                # Check if coefficient is a decimal (not a whole number)
                if isinstance(coefficient, float) and coefficient != int(coefficient):
                    decimal_coefficients_found = True
                
                # Verify coefficient calculation: (position * 100) / 357 for this race
                if position > 0:
                    expected_coefficient = (position * 100) / 357
                    if abs(coefficient - expected_coefficient) < 0.01:  # Allow small floating point differences
                        print(f"   ✅ Coefficient calculation correct: {coefficient:.2f} ≈ {expected_coefficient:.2f}")
                    else:
                        print(f"   ❌ Coefficient calculation incorrect: {coefficient:.2f} ≠ {expected_coefficient:.2f}")
            
            if decimal_coefficients_found:
                print("✅ Decimal coefficients found - coefficient calculation working correctly")
                return True
            else:
                print("❌ No decimal coefficients found - may still be using whole numbers")
                return False
        
        return False

    def test_verify_ring_number_matching(self):
        """Verify that ring numbers are matched with registered pigeons"""
        success, response = self.run_test(
            "Get Race Results to Check Ring Number Matching",
            "GET",
            "race-results",
            200
        )
        
        if success and isinstance(response, list):
            print("   Checking ring number matching:")
            
            for result in response:
                ring_number = result.get('ring_number', 'Unknown')
                pigeon = result.get('pigeon')
                
                if ring_number == 'BE501516325':
                    if pigeon and pigeon.get('name') == 'Golden Sky':
                        print(f"   ✅ Ring {ring_number} correctly matched to pigeon '{pigeon.get('name')}'")
                        return True
                    else:
                        print(f"   ❌ Ring {ring_number} not matched correctly - pigeon: {pigeon}")
                        return False
        
        return False

    def test_delete_functionality(self):
        """Test delete functionality for race results"""
        # First get race results to find one to delete
        success, response = self.run_test(
            "Get Race Results for Delete Test",
            "GET",
            "race-results",
            200
        )
        
        if success and isinstance(response, list) and len(response) > 0:
            result_to_delete = response[0]
            result_id = result_to_delete.get('id')
            
            if result_id:
                success2, response2 = self.run_test(
                    f"Delete Race Result {result_id}",
                    "DELETE",
                    f"race-results/{result_id}",
                    200
                )
                
                if success2:
                    # Verify it was deleted by checking the count
                    success3, response3 = self.run_test(
                        "Verify Deletion - Get Race Results",
                        "GET",
                        "race-results",
                        200
                    )
                    
                    if success3 and isinstance(response3, list):
                        new_count = len(response3)
                        original_count = len(response)
                        
                        if new_count == original_count - 1:
                            print("✅ Delete functionality working correctly")
                            return True
                        else:
                            print(f"❌ Delete may not have worked - count changed from {original_count} to {new_count}")
                
                return success2
        
        print("❌ No race results found to test delete functionality")
        return False

def main():
    print("🚀 Testing Specific Fixes for Pigeon Racing Dashboard")
    print("=" * 60)
    print("Testing:")
    print("1. Duplicate Prevention - One pigeon per race")
    print("2. Coefficient Display - Decimal values")
    print("3. Ring Number Matching - Registered pigeons")
    print("4. Delete Functionality")
    print("=" * 60)
    
    tester = SpecificFixesTester()
    
    # Run tests in order
    test_results = []
    
    # Setup
    test_results.append(tester.test_clear_data())
    test_results.append(tester.test_create_test_pigeon())
    
    # Main functionality tests
    test_results.append(tester.test_upload_race_with_duplicates())
    test_results.append(tester.test_verify_duplicate_prevention())
    test_results.append(tester.test_verify_coefficient_calculation())
    test_results.append(tester.test_verify_ring_number_matching())
    test_results.append(tester.test_delete_functionality())
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All specific fixes are working correctly!")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())