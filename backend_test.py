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

    def test_cascade_deletion(self):
        """Test cascade deletion - create pigeon, upload race results, delete pigeon, verify both are deleted"""
        print("\n🔍 Testing Cascade Deletion Workflow...")
        
        # Step 1: Create a pigeon with ring number that matches test file
        pigeon_data = {
            "ring_number": "BE501516325",  # Matches test_race_results.txt
            "name": "Cascade Test Pigeon",
            "country": "BE",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Test Breeder"
        }
        
        success, pigeon_response = self.run_test(
            "Create Pigeon for Cascade Test",
            "POST",
            "pigeons",
            200,
            data=pigeon_data
        )
        
        if not success or 'id' not in pigeon_response:
            print("❌ Failed to create pigeon for cascade test")
            return False
            
        test_pigeon_id = pigeon_response['id']
        print(f"   Created test pigeon ID: {test_pigeon_id}")
        
        # Step 2: Upload race results that include this pigeon's ring number
        try:
            with open('/app/test_race_results.txt', 'r') as f:
                txt_content = f.read()
        except FileNotFoundError:
            print("❌ test_race_results.txt file not found")
            return False
        
        files = {
            'file': ('test_race_results.txt', txt_content, 'text/plain')
        }
        
        success, upload_response = self.run_test(
            "Upload Race Results with Test Pigeon",
            "POST",
            "upload-race-results",
            200,
            files=files
        )
        
        if not success:
            print("❌ Failed to upload race results")
            return False
        
        # Step 3: Verify race results were created for the pigeon
        success, results_response = self.run_test(
            "Verify Race Results Created",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            print("❌ Failed to get race results")
            return False
        
        # Check if our pigeon has race results
        pigeon_results = [r for r in results_response if r.get('pigeon', {}).get('id') == test_pigeon_id]
        if not pigeon_results:
            print("❌ No race results found for test pigeon")
            return False
        
        print(f"   Found {len(pigeon_results)} race results for test pigeon")
        
        # Step 4: Delete the pigeon and verify cascade deletion
        success, delete_response = self.run_test(
            "Delete Pigeon (Cascade Deletion)",
            "DELETE",
            f"pigeons/{test_pigeon_id}",
            200
        )
        
        if not success:
            print("❌ Failed to delete pigeon")
            return False
        
        # Check if cascade deletion info is in response
        if 'race_results_deleted' in delete_response:
            print(f"   Cascade deletion removed {delete_response['race_results_deleted']} race results")
        
        # Step 5: Verify pigeon is deleted
        success, _ = self.run_test(
            "Verify Pigeon Deleted",
            "GET",
            f"pigeons/{test_pigeon_id}",
            404  # Should return 404 not found
        )
        
        if not success:
            print("❌ Pigeon was not properly deleted")
            return False
        
        # Step 6: Verify race results are also deleted (cascade)
        success, final_results = self.run_test(
            "Verify Race Results Cascade Deleted",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            print("❌ Failed to get race results for verification")
            return False
        
        # Check that no race results exist for the deleted pigeon
        remaining_results = [r for r in final_results if r.get('pigeon', {}).get('id') == test_pigeon_id]
        if remaining_results:
            print(f"❌ Cascade deletion failed - {len(remaining_results)} race results still exist")
            return False
        
        print("✅ Cascade deletion test passed - pigeon and race results properly deleted")
        return True

    def test_ring_number_matching(self):
        """Test ring number parsing and matching from TXT file"""
        print("\n🔍 Testing Ring Number Matching...")
        
        # Step 1: Create pigeons with ring numbers that match test_race_results.txt
        test_pigeons = [
            {
                "ring_number": "BE501516325",  # Matches "BE 501516325" in file
                "name": "Ring Match Test 1",
                "country": "BE",
                "gender": "Male",
                "color": "Blue",
                "breeder": "Test Breeder 1"
            },
            {
                "ring_number": "BE501516025",  # Matches "BE 501516025" in file
                "name": "Ring Match Test 2", 
                "country": "BE",
                "gender": "Female",
                "color": "Red",
                "breeder": "Test Breeder 2"
            },
            {
                "ring_number": "BE501120725",  # Matches "BE 501120725" in file
                "name": "Ring Match Test 3",
                "country": "BE", 
                "gender": "Male",
                "color": "Checker",
                "breeder": "Test Breeder 3"
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
                created_pigeons.append(response['id'])
                print(f"   Created pigeon: {pigeon_data['ring_number']} -> ID: {response['id']}")
            else:
                print(f"❌ Failed to create pigeon {pigeon_data['ring_number']}")
        
        if len(created_pigeons) != len(test_pigeons):
            print("❌ Failed to create all test pigeons")
            return False
        
        # Step 2: Upload the test_race_results.txt file
        try:
            with open('/app/test_race_results.txt', 'r') as f:
                txt_content = f.read()
        except FileNotFoundError:
            print("❌ test_race_results.txt file not found")
            return False
        
        files = {
            'file': ('test_race_results.txt', txt_content, 'text/plain')
        }
        
        success, upload_response = self.run_test(
            "Upload Test Race Results File",
            "POST", 
            "upload-race-results",
            200,
            files=files
        )
        
        if not success:
            print("❌ Failed to upload race results")
            return False
        
        print(f"   Upload response: {upload_response}")
        
        # Step 3: Verify race results are properly matched to registered pigeons
        success, results_response = self.run_test(
            "Get Race Results After Upload",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            print("❌ Failed to get race results")
            return False
        
        # Check that results were created for our registered pigeons
        matched_results = []
        for result in results_response:
            if result.get('pigeon') and result['pigeon']['id'] in created_pigeons:
                matched_results.append(result)
                print(f"   ✅ Matched result: Ring {result['ring_number']} -> Pigeon {result['pigeon']['name']}")
        
        if len(matched_results) == 0:
            print("❌ No race results matched to registered pigeons")
            return False
        
        # Step 4: Verify ring number normalization worked
        expected_rings = ["BE501516325", "BE501516025", "BE501120725"]
        matched_rings = [r['ring_number'] for r in matched_results]
        
        for expected_ring in expected_rings:
            if expected_ring in matched_rings:
                print(f"   ✅ Ring number {expected_ring} properly matched")
            else:
                print(f"   ❌ Ring number {expected_ring} not matched")
        
        # Cleanup - delete created pigeons
        for pigeon_id in created_pigeons:
            self.run_test(
                f"Cleanup Pigeon {pigeon_id}",
                "DELETE",
                f"pigeons/{pigeon_id}",
                200
            )
        
        success_count = len(matched_results)
        print(f"✅ Ring number matching test completed - {success_count} results matched")
        return success_count > 0

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

    def test_pairing_functionality(self):
        """Test complete pairing functionality workflow"""
        print("\n🔍 Testing Pairing Functionality...")
        
        # Step 1: Create male and female pigeons for pairing
        male_pigeon_data = {
            "ring_number": "BE123456789",
            "name": "Sire Test",
            "country": "BE",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Test Breeder"
        }
        
        female_pigeon_data = {
            "ring_number": "BE987654321",
            "name": "Dam Test",
            "country": "BE", 
            "gender": "Female",
            "color": "Red",
            "breeder": "Test Breeder"
        }
        
        # Create male pigeon
        success, male_response = self.run_test(
            "Create Male Pigeon for Pairing",
            "POST",
            "pigeons",
            200,
            data=male_pigeon_data
        )
        
        if not success or 'id' not in male_response:
            print("❌ Failed to create male pigeon")
            return False
        
        male_pigeon_id = male_response['id']
        print(f"   Created male pigeon ID: {male_pigeon_id}")
        
        # Create female pigeon
        success, female_response = self.run_test(
            "Create Female Pigeon for Pairing",
            "POST",
            "pigeons",
            200,
            data=female_pigeon_data
        )
        
        if not success or 'id' not in female_response:
            print("❌ Failed to create female pigeon")
            return False
        
        female_pigeon_id = female_response['id']
        print(f"   Created female pigeon ID: {female_pigeon_id}")
        
        # Step 2: Test creating a pairing
        pairing_data = {
            "sire_id": male_pigeon_id,
            "dam_id": female_pigeon_id,
            "expected_hatch_date": "2025-02-15",
            "notes": "Test pairing for breeding program"
        }
        
        success, pairing_response = self.run_test(
            "Create Pairing",
            "POST",
            "pairings",
            200,
            data=pairing_data
        )
        
        if not success or 'id' not in pairing_response:
            print("❌ Failed to create pairing")
            return False
        
        pairing_id = pairing_response['id']
        print(f"   Created pairing ID: {pairing_id}")
        
        # Step 3: Test getting all pairings
        success, pairings_response = self.run_test(
            "Get All Pairings",
            "GET",
            "pairings",
            200
        )
        
        if not success:
            print("❌ Failed to get pairings")
            return False
        
        # Step 4: Test gender validation - try to create pairing with wrong genders
        success, error_response = self.run_test(
            "Invalid Pairing - Wrong Gender (Should Fail)",
            "POST",
            "pairings",
            400,
            data={
                "sire_id": female_pigeon_id,  # Female as sire (should fail)
                "dam_id": male_pigeon_id,     # Male as dam (should fail)
                "notes": "This should fail"
            }
        )
        
        if not success:
            print("❌ Gender validation test failed")
            return False
        
        # Step 5: Test creating offspring from pairing
        offspring_data = {
            "ring_number": "BE555666777",
            "name": "Test Offspring",
            "country": "BE",
            "gender": "Male",
            "color": "Checker",
            "breeder": "Test Breeder"
        }
        
        success, offspring_response = self.run_test(
            "Create Offspring from Pairing",
            "POST",
            f"pairings/{pairing_id}/result",
            200,
            data=offspring_data
        )
        
        if not success:
            print("❌ Failed to create offspring from pairing")
            return False
        
        # Step 6: Verify offspring appears in pigeons collection
        success, pigeons_response = self.run_test(
            "Verify Offspring in Pigeons Collection",
            "GET",
            "pigeons?search=Test Offspring",
            200
        )
        
        if not success:
            print("❌ Failed to verify offspring in pigeons collection")
            return False
        
        offspring_found = any(p.get('ring_number') == 'BE555666777' for p in pigeons_response)
        if not offspring_found:
            print("❌ Offspring not found in pigeons collection")
            return False
        
        print("   ✅ Offspring successfully created and found in pigeons collection")
        
        # Cleanup - delete created pigeons (cascade deletion will handle race results)
        self.run_test("Cleanup Male Pigeon", "DELETE", f"pigeons/{male_pigeon_id}", 200)
        self.run_test("Cleanup Female Pigeon", "DELETE", f"pigeons/{female_pigeon_id}", 200)
        self.run_test("Cleanup Offspring Pigeon", "GET", "pigeons?search=Test Offspring", 200)
        
        # Find and delete offspring
        success, search_response = self.run_test("Find Offspring for Cleanup", "GET", "pigeons?search=Test Offspring", 200)
        if success and search_response:
            for pigeon in search_response:
                if pigeon.get('ring_number') == 'BE555666777':
                    self.run_test("Cleanup Offspring Pigeon", "DELETE", f"pigeons/{pigeon['id']}", 200)
                    break
        
        print("✅ Pairing functionality test completed successfully")
        return True

    def test_health_log_functionality(self):
        """Test complete health log functionality"""
        print("\n🔍 Testing Health Log Functionality...")
        
        # Step 1: Create a pigeon for health logs
        pigeon_data = {
            "ring_number": "BE111222333",
            "name": "Health Test Pigeon",
            "country": "BE",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Test Breeder"
        }
        
        success, pigeon_response = self.run_test(
            "Create Pigeon for Health Logs",
            "POST",
            "pigeons",
            200,
            data=pigeon_data
        )
        
        if not success or 'id' not in pigeon_response:
            print("❌ Failed to create pigeon for health logs")
            return False
        
        pigeon_id = pigeon_response['id']
        print(f"   Created pigeon ID: {pigeon_id}")
        
        # Step 2: Test creating different types of health logs
        health_logs = [
            {
                "pigeon_id": pigeon_id,
                "type": "health",
                "title": "Vaccination",
                "description": "Annual vaccination completed",
                "date": "2025-01-15",
                "reminder_date": "2026-01-15"
            },
            {
                "pigeon_id": pigeon_id,
                "type": "training",
                "title": "Flight Training",
                "description": "30km training flight completed",
                "date": "2025-01-16"
            },
            {
                "pigeon_id": pigeon_id,
                "type": "diet",
                "title": "Diet Change",
                "description": "Switched to high-protein feed",
                "date": "2025-01-17"
            }
        ]
        
        created_log_ids = []
        for i, log_data in enumerate(health_logs):
            success, log_response = self.run_test(
                f"Create {log_data['type'].title()} Log",
                "POST",
                "health-logs",
                200,
                data=log_data
            )
            
            if success and 'id' in log_response:
                created_log_ids.append(log_response['id'])
                print(f"   Created {log_data['type']} log ID: {log_response['id']}")
            else:
                print(f"❌ Failed to create {log_data['type']} log")
                return False
        
        # Step 3: Test getting all health logs
        success, all_logs_response = self.run_test(
            "Get All Health Logs",
            "GET",
            "health-logs",
            200
        )
        
        if not success:
            print("❌ Failed to get all health logs")
            return False
        
        # Step 4: Test filtering by pigeon_id
        success, pigeon_logs_response = self.run_test(
            "Get Health Logs by Pigeon ID",
            "GET",
            f"health-logs?pigeon_id={pigeon_id}",
            200
        )
        
        if not success:
            print("❌ Failed to get health logs by pigeon ID")
            return False
        
        # Verify we got the right logs
        if len(pigeon_logs_response) != 3:
            print(f"❌ Expected 3 logs for pigeon, got {len(pigeon_logs_response)}")
            return False
        
        # Step 5: Test filtering by type
        success, health_type_logs = self.run_test(
            "Get Health Logs by Type",
            "GET",
            "health-logs?type=health",
            200
        )
        
        if not success:
            print("❌ Failed to get health logs by type")
            return False
        
        # Step 6: Test pigeon validation - try to create log for non-existent pigeon
        success, error_response = self.run_test(
            "Invalid Health Log - Non-existent Pigeon (Should Fail)",
            "POST",
            "health-logs",
            404,
            data={
                "pigeon_id": "nonexistent-id",
                "type": "health",
                "title": "Should Fail",
                "date": "2025-01-15"
            }
        )
        
        if not success:
            print("❌ Pigeon validation test failed")
            return False
        
        # Step 7: Test deleting health logs
        for i, log_id in enumerate(created_log_ids):
            success, delete_response = self.run_test(
                f"Delete Health Log {i+1}",
                "DELETE",
                f"health-logs/{log_id}",
                200
            )
            
            if not success:
                print(f"❌ Failed to delete health log {log_id}")
                return False
        
        # Step 8: Verify logs are deleted
        success, final_logs_response = self.run_test(
            "Verify Health Logs Deleted",
            "GET",
            f"health-logs?pigeon_id={pigeon_id}",
            200
        )
        
        if not success:
            print("❌ Failed to verify health logs deletion")
            return False
        
        if len(final_logs_response) != 0:
            print(f"❌ Expected 0 logs after deletion, got {len(final_logs_response)}")
            return False
        
        # Cleanup - delete test pigeon
        self.run_test("Cleanup Health Test Pigeon", "DELETE", f"pigeons/{pigeon_id}", 200)
        
        print("✅ Health log functionality test completed successfully")
        return True

    def test_nonexistent_health_log_deletion(self):
        """Test deleting non-existent health log"""
        success, response = self.run_test(
            "Delete Non-existent Health Log (Should Fail)",
            "DELETE",
            "health-logs/nonexistent-id",
            404
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
    
    # NEW FUNCTIONALITY TESTS
    print("\n" + "🆕" * 20 + " NEW FUNCTIONALITY TESTS " + "🆕" * 20)
    test_results.append(tester.test_pairing_functionality())
    test_results.append(tester.test_health_log_functionality())
    test_results.append(tester.test_nonexistent_health_log_deletion())
    
    # PRIORITY TESTS - Cascade Deletion and Ring Number Matching
    print("\n" + "🎯" * 20 + " PRIORITY TESTS " + "🎯" * 20)
    test_results.append(tester.test_cascade_deletion())
    test_results.append(tester.test_ring_number_matching())
    
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