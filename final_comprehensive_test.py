import requests
import sys
import json

class ComprehensiveFixesTester:
    def __init__(self, base_url="https://race-loft.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        
        if details:
            print(f"   {details}")

    def clear_and_setup(self):
        """Clear data and set up test environment"""
        print("🧹 Setting up test environment...")
        
        # Clear existing data
        response = requests.post(f"{self.api_url}/clear-test-data")
        success = response.status_code == 200
        self.log_test("Clear existing test data", success)
        
        # Create the test pigeon as specified in the review request
        pigeon_data = {
            "ring_number": "BE501516325",
            "name": "Golden Sky", 
            "country": "BE",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Test User"
        }
        
        response = requests.post(f"{self.api_url}/pigeons", json=pigeon_data)
        success = response.status_code == 200
        self.log_test("Create test pigeon (BE501516325 - Golden Sky)", success)
        
        return success

    def test_pigeon_count_confirmation(self):
        """Test the pigeon count confirmation popup functionality"""
        print("\n📊 Testing Pigeon Count Confirmation...")
        
        # Create race results file with 357 pigeons mentioned
        sample_txt_content = """----------------------------------------------------------------------
Data Technology Deerlijk
----------------------------------------------------------------------
QUIEVRAIN 22-05-21 357 Jongen Deelnemers: 45 LOSTIJD: 07:30:00

NR  Naam                Ring        Afstand  Tijd      Snelheid
----------------------------------------------------------------------
1   John Doe           BE 501516325  85000   08.1234   1450.5
2   Jane Smith         NL 987654321  85000   08.1456   1420.3
3   Bob Johnson        BE 111222333  85000   08.1678   1390.8
10  Test User          BE 501516325  85000   08.2000   1300.0
----------------------------------------------------------------------
"""
        
        files = {
            'file': ('race_results.txt', sample_txt_content, 'text/plain')
        }
        
        # First upload - should trigger confirmation
        response = requests.post(f"{self.api_url}/upload-race-results", files=files)
        
        if response.status_code == 200:
            data = response.json()
            needs_confirmation = data.get('needs_pigeon_count_confirmation', False)
            parsed_count = data.get('parsed_pigeon_counts', [])
            
            self.log_test("Initial upload triggers pigeon count confirmation", needs_confirmation, 
                         f"Detected {parsed_count[0] if parsed_count else 'unknown'} pigeons")
            
            if needs_confirmation and parsed_count:
                # Now confirm with 357 pigeons
                files = {
                    'file': ('race_results.txt', sample_txt_content, 'text/plain')
                }
                data = {'confirmed_pigeon_count': '357'}
                
                response = requests.post(f"{self.api_url}/confirm-race-upload", files=files, data=data)
                success = response.status_code == 200
                
                if success:
                    result_data = response.json()
                    results_count = result_data.get('results', 0)
                    self.log_test("Confirm upload with 357 pigeons", success, 
                                 f"Processed {results_count} results")
                    return True
                else:
                    self.log_test("Confirm upload with 357 pigeons", False, response.text[:200])
                    return False
            else:
                return False
        else:
            self.log_test("Initial upload triggers pigeon count confirmation", False, response.text[:200])
            return False

    def test_duplicate_prevention(self):
        """Test that duplicate ring numbers are prevented in the same race"""
        print("\n🚫 Testing Duplicate Prevention...")
        
        response = requests.get(f"{self.api_url}/race-results")
        if response.status_code == 200:
            results = response.json()
            
            # Count occurrences of each ring number
            ring_counts = {}
            for result in results:
                ring = result.get('ring_number', '')
                ring_counts[ring] = ring_counts.get(ring, 0) + 1
            
            print(f"   Found {len(results)} total results")
            print("   Ring number occurrences:")
            
            duplicates_found = False
            for ring, count in ring_counts.items():
                print(f"     {ring}: {count} times")
                if count > 1:
                    duplicates_found = True
            
            success = not duplicates_found
            self.log_test("No duplicate ring numbers in same race", success,
                         "Each ring number appears only once" if success else "Duplicate ring numbers found")
            return success
        else:
            self.log_test("Get race results for duplicate check", False)
            return False

    def test_coefficient_calculation(self):
        """Test that coefficients are calculated as decimals with correct formula"""
        print("\n🧮 Testing Coefficient Calculation...")
        
        response = requests.get(f"{self.api_url}/race-results")
        if response.status_code == 200:
            results = response.json()
            
            decimal_coefficients = 0
            correct_calculations = 0
            total_results = len(results)
            
            print("   Checking coefficient calculations:")
            
            for result in results:
                position = result.get('position', 0)
                coefficient = result.get('coefficient', 0)
                ring = result.get('ring_number', 'Unknown')
                race = result.get('race', {})
                total_pigeons = race.get('total_pigeons', 0)
                
                # Check if coefficient is decimal
                if isinstance(coefficient, float) and coefficient != int(coefficient):
                    decimal_coefficients += 1
                
                # Check calculation: (position * 100) / total_pigeons
                if total_pigeons > 0:
                    expected = (position * 100) / total_pigeons
                    if abs(coefficient - expected) < 0.01:
                        correct_calculations += 1
                        print(f"     ✅ {ring}: Position {position}, Coefficient {coefficient:.4f} (Expected: {expected:.4f})")
                    else:
                        print(f"     ❌ {ring}: Position {position}, Coefficient {coefficient:.4f} (Expected: {expected:.4f})")
                else:
                    print(f"     ⚠️  {ring}: No total pigeons data")
            
            decimal_success = decimal_coefficients > 0
            calculation_success = correct_calculations == total_results
            
            self.log_test("Coefficients are decimal values", decimal_success,
                         f"{decimal_coefficients}/{total_results} coefficients are decimals")
            
            self.log_test("Coefficient calculations are correct", calculation_success,
                         f"{correct_calculations}/{total_results} calculations are correct")
            
            return decimal_success and calculation_success
        else:
            self.log_test("Get race results for coefficient check", False)
            return False

    def test_ring_number_matching(self):
        """Test that ring numbers are matched with registered pigeons"""
        print("\n🔗 Testing Ring Number Matching...")
        
        response = requests.get(f"{self.api_url}/race-results")
        if response.status_code == 200:
            results = response.json()
            
            matched_pigeons = 0
            be501516325_matched = False
            
            print("   Checking ring number matching:")
            
            for result in results:
                ring = result.get('ring_number', '')
                pigeon = result.get('pigeon')
                
                if pigeon:
                    matched_pigeons += 1
                    pigeon_name = pigeon.get('name', 'Unknown')
                    print(f"     ✅ {ring} → {pigeon_name}")
                    
                    if ring == 'BE501516325' and pigeon_name == 'Golden Sky':
                        be501516325_matched = True
                else:
                    print(f"     ❌ {ring} → No match")
            
            success = be501516325_matched
            self.log_test("BE501516325 matched to Golden Sky", success,
                         f"Found {matched_pigeons} matched pigeons total")
            
            return success
        else:
            self.log_test("Get race results for ring matching check", False)
            return False

    def test_delete_functionality(self):
        """Test delete functionality for race results"""
        print("\n🗑️  Testing Delete Functionality...")
        
        # Get current results
        response = requests.get(f"{self.api_url}/race-results")
        if response.status_code != 200:
            self.log_test("Get race results for delete test", False)
            return False
        
        results = response.json()
        if len(results) == 0:
            self.log_test("Delete functionality test", False, "No results to delete")
            return False
        
        original_count = len(results)
        result_to_delete = results[0]
        result_id = result_to_delete.get('id')
        
        # Delete the result
        response = requests.delete(f"{self.api_url}/race-results/{result_id}")
        delete_success = response.status_code == 200
        
        if delete_success:
            # Verify deletion
            response = requests.get(f"{self.api_url}/race-results")
            if response.status_code == 200:
                new_results = response.json()
                new_count = len(new_results)
                
                success = new_count == original_count - 1
                self.log_test("Delete race result", success,
                             f"Count changed from {original_count} to {new_count}")
                return success
            else:
                self.log_test("Verify deletion", False)
                return False
        else:
            self.log_test("Delete race result", False, response.text[:200])
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Comprehensive Testing of Pigeon Racing Dashboard Fixes")
        print("=" * 70)
        print("Testing the following fixes:")
        print("1. Duplicate Prevention - One pigeon per race")
        print("2. Coefficient Display - Decimal values with correct calculation")
        print("3. Ring Number Matching - Registered pigeons show names")
        print("4. Pigeon Count Confirmation - Popup appears and functions")
        print("5. Delete Functionality - Delete buttons work properly")
        print("=" * 70)
        
        # Setup
        if not self.clear_and_setup():
            print("❌ Setup failed, aborting tests")
            return False
        
        # Run tests
        test_results = []
        test_results.append(self.test_pigeon_count_confirmation())
        test_results.append(self.test_duplicate_prevention())
        test_results.append(self.test_coefficient_calculation())
        test_results.append(self.test_ring_number_matching())
        test_results.append(self.test_delete_functionality())
        
        # Summary
        print("\n" + "=" * 70)
        print(f"📊 Final Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All fixes are working correctly!")
            return True
        else:
            failed = self.tests_run - self.tests_passed
            print(f"⚠️  {failed} test(s) failed. Issues need to be addressed.")
            return False

def main():
    tester = ComprehensiveFixesTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())