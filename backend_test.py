import requests
import sys
import json
from datetime import datetime
import io

class PigeonDashboardTester:
    def __init__(self, base_url="https://pigeon-results-1.preview.emergentagent.com"):
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

    def test_health_check(self):
        """Test API health check"""
        success, response = self.run_test(
            "API Health Check",
            "GET",
            "",
            200
        )
        return success

    def test_create_pigeon(self):
        """Test creating a new pigeon"""
        pigeon_data = {
            "ring_number": "BE 501516325",
            "name": "Golden Sky",
            "country": "NL",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Test Breeder",
            "sire_ring": "BE 123456789",
            "dam_ring": "BE 987654321"
        }
        
        success, response = self.run_test(
            "Create Pigeon",
            "POST",
            "pigeons",
            200,
            data=pigeon_data
        )
        
        if success and 'id' in response:
            self.created_pigeon_id = response['id']
            print(f"   Created pigeon ID: {self.created_pigeon_id}")
        
        return success

    def test_get_pigeons(self):
        """Test getting all pigeons"""
        success, response = self.run_test(
            "Get All Pigeons",
            "GET",
            "pigeons",
            200
        )
        return success

    def test_search_pigeons(self):
        """Test searching pigeons"""
        success, response = self.run_test(
            "Search Pigeons",
            "GET",
            "pigeons?search=Golden",
            200
        )
        return success

    def test_get_pigeon_by_id(self):
        """Test getting a specific pigeon"""
        if not self.created_pigeon_id:
            print("❌ Skipped - No pigeon ID available")
            return False
            
        success, response = self.run_test(
            "Get Pigeon by ID",
            "GET",
            f"pigeons/{self.created_pigeon_id}",
            200
        )
        return success

    def test_update_pigeon(self):
        """Test updating a pigeon"""
        if not self.created_pigeon_id:
            print("❌ Skipped - No pigeon ID available")
            return False
            
        update_data = {
            "ring_number": "BE 501516325",
            "name": "Golden Sky Updated",
            "country": "BE",
            "gender": "Male",
            "color": "Blue Checker",
            "breeder": "Updated Breeder"
        }
        
        success, response = self.run_test(
            "Update Pigeon",
            "PUT",
            f"pigeons/{self.created_pigeon_id}",
            200,
            data=update_data
        )
        return success

    def test_duplicate_ring_number(self):
        """Test creating pigeon with duplicate ring number"""
        pigeon_data = {
            "ring_number": "BE 501516325",  # Same as first pigeon
            "name": "Duplicate Test",
            "country": "NL",
            "gender": "Female",
            "color": "Red",
            "breeder": "Test Breeder"
        }
        
        success, response = self.run_test(
            "Duplicate Ring Number (Should Fail)",
            "POST",
            "pigeons",
            400,  # Should fail with 400
            data=pigeon_data
        )
        return success

    def test_upload_race_results(self):
        """Test uploading race results file"""
        # Create a sample TXT file content based on the parser format
        sample_txt_content = """----------------------------------------------------------------------
Data Technology Deerlijk
----------------------------------------------------------------------
QUIEVRAIN 22-05-21 1234 Jongen Deelnemers: 45 LOSTIJD: 07:30:00

NR  Naam                Ring        Afstand  Tijd      Snelheid
----------------------------------------------------------------------
1   John Doe           BE 501516325  12500   08.1234   1450.5
2   Jane Smith         NL 987654321  12500   08.1456   1420.3
3   Bob Johnson        BE 111222333  12500   08.1678   1390.8
----------------------------------------------------------------------
"""
        
        # Create file-like object
        files = {
            'file': ('race_results.txt', io.StringIO(sample_txt_content), 'text/plain')
        }
        
        success, response = self.run_test(
            "Upload Race Results",
            "POST",
            "upload-race-results",
            200,
            files=files
        )
        return success

    def test_get_race_results(self):
        """Test getting race results"""
        success, response = self.run_test(
            "Get Race Results",
            "GET",
            "race-results",
            200
        )
        return success

    def test_get_pigeon_stats(self):
        """Test getting pigeon statistics"""
        success, response = self.run_test(
            "Get Pigeon Stats",
            "GET",
            "pigeon-stats/BE 501516325",
            200
        )
        return success

    def test_get_dashboard_stats(self):
        """Test getting dashboard statistics"""
        success, response = self.run_test(
            "Get Dashboard Stats",
            "GET",
            "dashboard-stats",
            200
        )
        return success

    def test_invalid_file_upload(self):
        """Test uploading invalid file type"""
        files = {
            'file': ('invalid.pdf', io.StringIO("Invalid content"), 'application/pdf')
        }
        
        success, response = self.run_test(
            "Invalid File Upload (Should Fail)",
            "POST",
            "upload-race-results",
            400,  # Should fail with 400
            files=files
        )
        return success

    def test_get_nonexistent_pigeon(self):
        """Test getting non-existent pigeon"""
        success, response = self.run_test(
            "Get Non-existent Pigeon (Should Fail)",
            "GET",
            "pigeons/nonexistent-id",
            404  # Should fail with 404
        )
        return success

    def test_delete_pigeon(self):
        """Test deleting a pigeon"""
        if not self.created_pigeon_id:
            print("❌ Skipped - No pigeon ID available")
            return False
            
        success, response = self.run_test(
            "Delete Pigeon",
            "DELETE",
            f"pigeons/{self.created_pigeon_id}",
            200
        )
        return success

def main():
    print("🚀 Starting Pigeon Racing Dashboard API Tests")
    print("=" * 60)
    
    tester = PigeonDashboardTester()
    
    # Run all tests in logical order
    test_results = []
    
    # Basic functionality tests
    test_results.append(tester.test_health_check())
    test_results.append(tester.test_get_pigeons())
    test_results.append(tester.test_get_dashboard_stats())
    
    # Pigeon CRUD tests
    test_results.append(tester.test_create_pigeon())
    test_results.append(tester.test_get_pigeon_by_id())
    test_results.append(tester.test_search_pigeons())
    test_results.append(tester.test_update_pigeon())
    
    # Error handling tests
    test_results.append(tester.test_duplicate_ring_number())
    test_results.append(tester.test_get_nonexistent_pigeon())
    test_results.append(tester.test_invalid_file_upload())
    
    # Race results tests
    test_results.append(tester.test_upload_race_results())
    test_results.append(tester.test_get_race_results())
    test_results.append(tester.test_get_pigeon_stats())
    
    # Cleanup
    test_results.append(tester.test_delete_pigeon())
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())