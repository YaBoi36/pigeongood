import requests
import sys
import json
from datetime import datetime
import io

class PigeonDashboardTester:
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
        
        # Step 1: Create male and female pigeons for pairing with unique ring numbers
        import time
        timestamp = str(int(time.time()))[-6:]  # Use last 6 digits of timestamp for uniqueness
        
        male_pigeon_data = {
            "ring_number": f"BE{timestamp}001",
            "name": "Sire Test",
            "country": "BE",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Test Breeder"
        }
        
        female_pigeon_data = {
            "ring_number": f"BE{timestamp}002",
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
            "ring_number": f"{timestamp}003",  # Just the number part
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
        
        offspring_found = any(p.get('ring_number') == f"BE{timestamp}003" for p in pigeons_response)
        if not offspring_found:
            print("❌ Offspring not found in pigeons collection")
            return False
        
        print("   ✅ Offspring successfully created and found in pigeons collection")
        
        # Cleanup - delete created pigeons (cascade deletion will handle race results)
        self.run_test("Cleanup Male Pigeon", "DELETE", f"pigeons/{male_pigeon_id}", 200)
        self.run_test("Cleanup Female Pigeon", "DELETE", f"pigeons/{female_pigeon_id}", 200)
        
        # Find and delete offspring
        success, search_response = self.run_test("Find Offspring for Cleanup", "GET", "pigeons?search=Test Offspring", 200)
        if success and search_response:
            for pigeon in search_response:
                if pigeon.get('ring_number') == f"BE{timestamp}003":
                    self.run_test("Cleanup Offspring Pigeon", "DELETE", f"pigeons/{pigeon['id']}", 200)
                    break
        
        print("✅ Pairing functionality test completed successfully")
        return True

    def test_health_log_functionality(self):
        """Test complete health log functionality"""
        print("\n🔍 Testing Health Log Functionality...")
        
        # Step 1: Create a pigeon for health logs with unique ring number
        import time
        timestamp = str(int(time.time()))[-6:]
        
        pigeon_data = {
            "ring_number": f"BE{timestamp}888",
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

    def test_ring_number_fix_in_pairing(self):
        """Test the ring number fix - verify full ring number (country + number) is created from pairing"""
        print("\n🔍 Testing Ring Number Fix in Pairing...")
        
        # Step 1: Create male and female pigeons for pairing
        import time
        timestamp = str(int(time.time()))[-6:]
        
        male_pigeon_data = {
            "ring_number": f"BE{timestamp}101",
            "name": "Ring Fix Male",
            "country": "BE",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Test Breeder"
        }
        
        female_pigeon_data = {
            "ring_number": f"BE{timestamp}102",
            "name": "Ring Fix Female",
            "country": "BE",
            "gender": "Female",
            "color": "Red",
            "breeder": "Test Breeder"
        }
        
        # Create male pigeon
        success, male_response = self.run_test(
            "Create Male Pigeon for Ring Fix Test",
            "POST",
            "pigeons",
            200,
            data=male_pigeon_data
        )
        
        if not success or 'id' not in male_response:
            print("❌ Failed to create male pigeon")
            return False
        
        male_pigeon_id = male_response['id']
        
        # Create female pigeon
        success, female_response = self.run_test(
            "Create Female Pigeon for Ring Fix Test",
            "POST",
            "pigeons",
            200,
            data=female_pigeon_data
        )
        
        if not success or 'id' not in female_response:
            print("❌ Failed to create female pigeon")
            return False
        
        female_pigeon_id = female_response['id']
        
        # Step 2: Create pairing
        pairing_data = {
            "sire_id": male_pigeon_id,
            "dam_id": female_pigeon_id,
            "notes": "Ring number fix test pairing"
        }
        
        success, pairing_response = self.run_test(
            "Create Pairing for Ring Fix Test",
            "POST",
            "pairings",
            200,
            data=pairing_data
        )
        
        if not success or 'id' not in pairing_response:
            print("❌ Failed to create pairing")
            return False
        
        pairing_id = pairing_response['id']
        
        # Step 3: Create offspring with ring number "123456" and country "BE"
        # This should result in full ring number "BE123456"
        offspring_data = {
            "ring_number": "123456",  # Just the number part
            "country": "BE",          # Country code
            "name": "Ring Fix Test Offspring",
            "gender": "Male",
            "color": "Checker",
            "breeder": "Test Breeder"
        }
        
        success, offspring_response = self.run_test(
            "Create Offspring with Ring Number Fix",
            "POST",
            f"pairings/{pairing_id}/result",
            200,
            data=offspring_data
        )
        
        if not success:
            print("❌ Failed to create offspring from pairing")
            return False
        
        print(f"   Offspring creation response: {offspring_response}")
        
        # Step 4: Verify the created pigeon has full ring number "BE123456"
        success, pigeons_response = self.run_test(
            "Get All Pigeons to Find Offspring",
            "GET",
            "pigeons",
            200
        )
        
        if not success:
            print("❌ Failed to get pigeons")
            return False
        
        # Find the offspring pigeon
        offspring_pigeon = None
        for pigeon in pigeons_response:
            if pigeon.get('ring_number') == 'BE123456':
                offspring_pigeon = pigeon
                break
        
        if not offspring_pigeon:
            print("❌ Offspring pigeon with ring number 'BE123456' not found")
            print(f"   Available pigeons: {[p.get('ring_number') for p in pigeons_response]}")
            return False
        
        print(f"   ✅ Found offspring pigeon with full ring number: {offspring_pigeon['ring_number']}")
        
        # Step 5: Verify the pigeon appears correctly in /api/pigeons
        if offspring_pigeon['ring_number'] != 'BE123456':
            print(f"❌ Expected ring number 'BE123456', got '{offspring_pigeon['ring_number']}'")
            return False
        
        if offspring_pigeon['country'] != 'BE':
            print(f"❌ Expected country 'BE', got '{offspring_pigeon['country']}'")
            return False
        
        print("   ✅ Ring number fix verified - full ring number 'BE123456' created correctly")
        
        # Cleanup
        self.run_test("Cleanup Male Pigeon", "DELETE", f"pigeons/{male_pigeon_id}", 200)
        self.run_test("Cleanup Female Pigeon", "DELETE", f"pigeons/{female_pigeon_id}", 200)
        self.run_test("Cleanup Offspring Pigeon", "DELETE", f"pigeons/{offspring_pigeon['id']}", 200)
        
        print("✅ Ring number fix test completed successfully")
        return True

    def test_loft_log_functionality(self):
        """Test complete loft log functionality"""
        print("\n🔍 Testing Loft Log Functionality...")
        
        # Step 1: Test creating different types of loft logs
        loft_logs = [
            {
                "loft_name": "Test Loft Alpha",
                "type": "health",
                "title": "Loft Vaccination",
                "description": "Vaccinated all pigeons in loft",
                "date": "2025-01-15",
                "reminder_date": "2026-01-15"
            },
            {
                "loft_name": "Test Loft Alpha",
                "type": "training",
                "title": "Loft Training Session",
                "description": "Group training flight for all pigeons",
                "date": "2025-01-16"
            },
            {
                "loft_name": "Test Loft Beta",
                "type": "diet",
                "title": "Feed Change",
                "description": "Changed to winter feed mix",
                "date": "2025-01-17"
            },
            {
                "loft_name": "Test Loft Beta",
                "type": "health",
                "title": "Health Check",
                "description": "Monthly health inspection",
                "date": "2025-01-18"
            }
        ]
        
        created_log_ids = []
        for i, log_data in enumerate(loft_logs):
            success, log_response = self.run_test(
                f"Create Loft {log_data['type'].title()} Log",
                "POST",
                "loft-logs",
                200,
                data=log_data
            )
            
            if success and 'id' in log_response:
                created_log_ids.append(log_response['id'])
                print(f"   Created loft {log_data['type']} log ID: {log_response['id']}")
            else:
                print(f"❌ Failed to create loft {log_data['type']} log")
                return False
        
        # Step 2: Test getting all loft logs
        success, all_logs_response = self.run_test(
            "Get All Loft Logs",
            "GET",
            "loft-logs",
            200
        )
        
        if not success:
            print("❌ Failed to get all loft logs")
            return False
        
        if len(all_logs_response) < 4:
            print(f"❌ Expected at least 4 loft logs, got {len(all_logs_response)}")
            return False
        
        # Step 3: Test filtering by loft_name
        success, alpha_logs_response = self.run_test(
            "Get Loft Logs by Loft Name (Alpha)",
            "GET",
            "loft-logs?loft_name=Test Loft Alpha",
            200
        )
        
        if not success:
            print("❌ Failed to get loft logs by loft name")
            return False
        
        alpha_logs_count = len([log for log in alpha_logs_response if log.get('loft_name') == 'Test Loft Alpha'])
        if alpha_logs_count != 2:
            print(f"❌ Expected 2 logs for 'Test Loft Alpha', got {alpha_logs_count}")
            return False
        
        print(f"   ✅ Found {alpha_logs_count} logs for 'Test Loft Alpha'")
        
        # Step 4: Test filtering by type
        success, health_logs_response = self.run_test(
            "Get Loft Logs by Type (health)",
            "GET",
            "loft-logs?type=health",
            200
        )
        
        if not success:
            print("❌ Failed to get loft logs by type")
            return False
        
        health_logs_count = len([log for log in health_logs_response if log.get('type') == 'health'])
        if health_logs_count < 2:
            print(f"❌ Expected at least 2 health logs, got {health_logs_count}")
            return False
        
        print(f"   ✅ Found {health_logs_count} health logs")
        
        # Step 5: Test filtering by both loft_name and type
        success, filtered_logs_response = self.run_test(
            "Get Loft Logs by Loft Name and Type",
            "GET",
            "loft-logs?loft_name=Test Loft Beta&type=health",
            200
        )
        
        if not success:
            print("❌ Failed to get loft logs by loft name and type")
            return False
        
        filtered_count = len([log for log in filtered_logs_response 
                            if log.get('loft_name') == 'Test Loft Beta' and log.get('type') == 'health'])
        if filtered_count != 1:
            print(f"❌ Expected 1 log for 'Test Loft Beta' health type, got {filtered_count}")
            return False
        
        print(f"   ✅ Found {filtered_count} log for 'Test Loft Beta' health type")
        
        # Step 6: Test deleting loft logs
        for i, log_id in enumerate(created_log_ids):
            success, delete_response = self.run_test(
                f"Delete Loft Log {i+1}",
                "DELETE",
                f"loft-logs/{log_id}",
                200
            )
            
            if not success:
                print(f"❌ Failed to delete loft log {log_id}")
                return False
        
        # Step 7: Verify logs are deleted
        success, final_logs_response = self.run_test(
            "Verify Loft Logs Deleted",
            "GET",
            "loft-logs?loft_name=Test Loft Alpha",
            200
        )
        
        if not success:
            print("❌ Failed to verify loft logs deletion")
            return False
        
        remaining_alpha_logs = len([log for log in final_logs_response if log.get('loft_name') == 'Test Loft Alpha'])
        if remaining_alpha_logs != 0:
            print(f"❌ Expected 0 logs for 'Test Loft Alpha' after deletion, got {remaining_alpha_logs}")
            return False
        
        print("✅ Loft log functionality test completed successfully")
        return True

    def test_combined_log_systems(self):
        """Test that both individual health logs and loft logs work together"""
        print("\n🔍 Testing Combined Log Systems...")
        
        # Step 1: Create a pigeon for individual health logs with unique ring number
        import time
        timestamp = str(int(time.time()))[-6:]
        
        pigeon_data = {
            "ring_number": f"BE{timestamp}999",
            "name": "Combined Test Pigeon",
            "country": "BE",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Test Breeder"
        }
        
        success, pigeon_response = self.run_test(
            "Create Pigeon for Combined Test",
            "POST",
            "pigeons",
            200,
            data=pigeon_data
        )
        
        if not success or 'id' not in pigeon_response:
            print("❌ Failed to create pigeon for combined test")
            return False
        
        pigeon_id = pigeon_response['id']
        
        # Step 2: Create individual health log
        individual_log_data = {
            "pigeon_id": pigeon_id,
            "type": "health",
            "title": "Individual Health Check",
            "description": "Personal health check for specific pigeon",
            "date": "2025-01-20"
        }
        
        success, individual_log_response = self.run_test(
            "Create Individual Health Log",
            "POST",
            "health-logs",
            200,
            data=individual_log_data
        )
        
        if not success or 'id' not in individual_log_response:
            print("❌ Failed to create individual health log")
            return False
        
        individual_log_id = individual_log_response['id']
        
        # Step 3: Create loft log
        loft_log_data = {
            "loft_name": "Combined Test Loft",
            "type": "health",
            "title": "Loft Health Check",
            "description": "General loft health inspection",
            "date": "2025-01-20"
        }
        
        success, loft_log_response = self.run_test(
            "Create Loft Log",
            "POST",
            "loft-logs",
            200,
            data=loft_log_data
        )
        
        if not success or 'id' not in loft_log_response:
            print("❌ Failed to create loft log")
            return False
        
        loft_log_id = loft_log_response['id']
        
        # Step 4: Verify both systems work independently
        success, individual_logs = self.run_test(
            "Get Individual Health Logs",
            "GET",
            f"health-logs?pigeon_id={pigeon_id}",
            200
        )
        
        if not success or len(individual_logs) != 1:
            print("❌ Individual health log system not working correctly")
            return False
        
        success, loft_logs = self.run_test(
            "Get Loft Logs",
            "GET",
            "loft-logs?loft_name=Combined Test Loft",
            200
        )
        
        if not success or len(loft_logs) != 1:
            print("❌ Loft log system not working correctly")
            return False
        
        print("   ✅ Both individual and loft log systems working independently")
        
        # Step 5: Test filtering works for both systems
        success, health_individual_logs = self.run_test(
            "Filter Individual Logs by Type",
            "GET",
            "health-logs?type=health",
            200
        )
        
        if not success:
            print("❌ Failed to filter individual logs by type")
            return False
        
        success, health_loft_logs = self.run_test(
            "Filter Loft Logs by Type",
            "GET",
            "loft-logs?type=health",
            200
        )
        
        if not success:
            print("❌ Failed to filter loft logs by type")
            return False
        
        print("   ✅ Filtering works for both log systems")
        
        # Step 6: Test deletion of both types
        success, _ = self.run_test(
            "Delete Individual Health Log",
            "DELETE",
            f"health-logs/{individual_log_id}",
            200
        )
        
        if not success:
            print("❌ Failed to delete individual health log")
            return False
        
        success, _ = self.run_test(
            "Delete Loft Log",
            "DELETE",
            f"loft-logs/{loft_log_id}",
            200
        )
        
        if not success:
            print("❌ Failed to delete loft log")
            return False
        
        print("   ✅ Deletion works for both log systems")
        
        # Cleanup
        self.run_test("Cleanup Combined Test Pigeon", "DELETE", f"pigeons/{pigeon_id}", 200)
        
        print("✅ Combined log systems test completed successfully")
        return True

    def test_data_integrity_after_updates(self):
        """Test that all existing functionality still works after updates"""
        print("\n🔍 Testing Data Integrity After Updates...")
        
        # Step 1: Test basic pigeon CRUD still works
        pigeon_data = {
            "ring_number": "BE555666777",
            "name": "Integrity Test Pigeon",
            "country": "BE",
            "gender": "Female",
            "color": "Red",
            "breeder": "Integrity Breeder"
        }
        
        success, pigeon_response = self.run_test(
            "Data Integrity - Create Pigeon",
            "POST",
            "pigeons",
            200,
            data=pigeon_data
        )
        
        if not success or 'id' not in pigeon_response:
            print("❌ Basic pigeon creation failed")
            return False
        
        pigeon_id = pigeon_response['id']
        
        # Step 2: Test pairing creation still works
        # Create another pigeon for pairing
        male_pigeon_data = {
            "ring_number": "BE555666778",
            "name": "Integrity Male Pigeon",
            "country": "BE",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Integrity Breeder"
        }
        
        success, male_response = self.run_test(
            "Data Integrity - Create Male Pigeon",
            "POST",
            "pigeons",
            200,
            data=male_pigeon_data
        )
        
        if not success or 'id' not in male_response:
            print("❌ Male pigeon creation failed")
            return False
        
        male_id = male_response['id']
        
        # Create pairing
        pairing_data = {
            "sire_id": male_id,
            "dam_id": pigeon_id,
            "notes": "Data integrity test pairing"
        }
        
        success, pairing_response = self.run_test(
            "Data Integrity - Create Pairing",
            "POST",
            "pairings",
            200,
            data=pairing_data
        )
        
        if not success:
            print("❌ Pairing creation failed")
            return False
        
        print("   ✅ Pairing creation still works correctly")
        
        # Step 3: Test cascade deletion still works
        success, delete_response = self.run_test(
            "Data Integrity - Test Cascade Deletion",
            "DELETE",
            f"pigeons/{pigeon_id}",
            200
        )
        
        if not success:
            print("❌ Cascade deletion failed")
            return False
        
        # Verify pigeon is deleted
        success, _ = self.run_test(
            "Data Integrity - Verify Pigeon Deleted",
            "GET",
            f"pigeons/{pigeon_id}",
            404
        )
        
        if not success:
            print("❌ Pigeon was not properly deleted")
            return False
        
        print("   ✅ Cascade deletion still works correctly")
        
        # Cleanup
        self.run_test("Cleanup Male Pigeon", "DELETE", f"pigeons/{male_id}", 200)
        
        print("✅ Data integrity test completed successfully")
        return True

    def test_result_1_file_upload_pipeline(self):
        """Test the complete race results file upload and parsing pipeline with result_1.txt"""
        print("\n🔍 Testing Result_1.txt File Upload Pipeline...")
        
        # Step 1: Create test pigeons with specific ring numbers from result_1.txt
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
                print(f"   Created pigeon: {pigeon_data['ring_number']} -> ID: {response['id']}")
            else:
                print(f"❌ Failed to create pigeon {pigeon_data['ring_number']}")
        
        if len(created_pigeons) != len(test_pigeons):
            print("❌ Failed to create all test pigeons")
            return False
        
        # Step 2: Upload the result_1.txt file
        try:
            with open('/app/result_1.txt', 'r') as f:
                txt_content = f.read()
        except FileNotFoundError:
            print("❌ result_1.txt file not found")
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
            print("❌ Failed to upload result_1.txt file")
            return False
        
        print(f"   Upload response: {upload_response}")
        
        # Step 3: Verify that all 4 races were processed
        races_processed = upload_response.get('races', 0)
        if races_processed != 4:
            print(f"❌ RACE PROCESSING ISSUE: Expected 4 races, got {races_processed}")
            print(f"   Parsed pigeon counts: {upload_response.get('parsed_pigeon_counts', [])}")
            return False
        else:
            print(f"   ✅ All 4 races processed successfully")
        
        # Step 4: Verify that results were created for registered pigeons
        results_created = upload_response.get('results', 0)
        if results_created == 0:
            print(f"❌ RESULT CREATION ISSUE: Expected results for registered pigeons, got {results_created}")
            return False
        else:
            print(f"   ✅ {results_created} results created for registered pigeons")
        
        # Step 5: Get race results and verify pigeon-result matching
        success, results_response = self.run_test(
            "Get Race Results After Upload",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            print("❌ Failed to get race results")
            return False
        
        # Step 6: Verify each registered pigeon has exactly 1 result (duplicate prevention)
        pigeon_results_count = {}
        matched_results = []
        
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
                        print(f"   ✅ Found result for pigeon {ring_number} in race {result.get('race', {}).get('category', 'Unknown')}")
                        break
        
        # Step 7: Verify duplicate prevention - each pigeon should have exactly 1 result
        duplicate_prevention_working = True
        for ring_number, count in pigeon_results_count.items():
            if count != 1:
                print(f"❌ DUPLICATE PREVENTION ISSUE: Ring {ring_number} has {count} results (expected 1)")
                duplicate_prevention_working = False
            else:
                print(f"   ✅ Ring {ring_number} has exactly 1 result (duplicate prevention working)")
        
        # Step 8: Verify specific ring numbers from review request
        expected_rings = ["BE504574322", "BE504813624", "BE505078525"]
        found_rings = list(pigeon_results_count.keys())
        
        for expected_ring in expected_rings:
            if expected_ring in found_rings:
                print(f"   ✅ Ring number {expected_ring} properly matched and has result")
            else:
                print(f"   ❌ Ring number {expected_ring} not found in results")
        
        # Step 9: Test uploading the same file again - should not create more results
        print("\n   🔄 Testing duplicate file upload prevention...")
        success, second_upload_response = self.run_test(
            "Upload Same File Again (Should Prevent Duplicates)",
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
                print(f"   ✅ Second upload created 0 additional results (duplicate prevention working)")
        
        # Cleanup - delete created pigeons
        for pigeon in created_pigeons:
            self.run_test(
                f"Cleanup Pigeon {pigeon['ring_number']}",
                "DELETE",
                f"pigeons/{pigeon['id']}",
                200
            )
        
        # Final assessment
        pipeline_working = (
            races_processed == 4 and 
            results_created > 0 and 
            len(matched_results) > 0 and 
            duplicate_prevention_working and
            len(found_rings) == len(expected_rings)
        )
        
        if pipeline_working:
            print("✅ Result_1.txt upload pipeline test PASSED")
            print(f"   - All 4 races processed: ✅")
            print(f"   - Results created for registered pigeons: ✅ ({results_created})")
            print(f"   - Duplicate prevention working: ✅")
            print(f"   - All expected ring numbers matched: ✅")
            return True
        else:
            print("❌ Result_1.txt upload pipeline test FAILED")
            print(f"   - Races processed: {races_processed}/4")
            print(f"   - Results created: {results_created}")
            print(f"   - Matched results: {len(matched_results)}")
            print(f"   - Duplicate prevention: {'✅' if duplicate_prevention_working else '❌'}")
            print(f"   - Ring numbers found: {len(found_rings)}/{len(expected_rings)}")
            return False

    def test_duplicate_prevention_multi_race_file(self):
        """Test duplicate prevention logic for multi-race files with same date"""
        print("\n🔍 Testing Duplicate Prevention for Multi-Race Files...")
        
        # Step 1: Create test pigeons that appear in result_new.txt
        import time
        timestamp = str(int(time.time()))[-6:]
        
        test_pigeons = [
            {
                "ring_number": "BE504574322",  # Appears in multiple races in result_new.txt
                "name": "Duplicate Test Pigeon 1",
                "country": "BE",
                "gender": "Male",
                "color": "Blue",
                "breeder": "VRANCKEN WILLY&DOCHTE"
            },
            {
                "ring_number": "BE504813624",  # Appears in multiple races in result_new.txt
                "name": "Duplicate Test Pigeon 2", 
                "country": "BE",
                "gender": "Female",
                "color": "Red",
                "breeder": "BRIERS VALENT.&ZN"
            },
            {
                "ring_number": "BE504965824",  # Appears in multiple races in result_new.txt
                "name": "Duplicate Test Pigeon 3",
                "country": "BE",
                "gender": "Male",
                "color": "Checker",
                "breeder": "HERMANS RUBEN"
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
        
        # Step 2: Upload the result_new.txt file which contains multiple races from same date (CHIMAY 09-08-25)
        try:
            with open('/app/result_new.txt', 'r') as f:
                txt_content = f.read()
        except FileNotFoundError:
            print("❌ result_new.txt file not found")
            return False
        
        files = {
            'file': ('result_new.txt', txt_content, 'text/plain')
        }
        
        success, upload_response = self.run_test(
            "Upload Multi-Race File (result_new.txt)",
            "POST", 
            "upload-race-results",
            200,
            files=files
        )
        
        if not success:
            print("❌ Failed to upload multi-race results file")
            return False
        
        print(f"   Upload response: {upload_response}")
        
        # Step 3: Verify race results and check for duplicates
        success, results_response = self.run_test(
            "Get Race Results After Multi-Race Upload",
            "GET",
            "race-results",
            200
        )
        
        if not success:
            print("❌ Failed to get race results")
            return False
        
        # Step 4: Check duplicate prevention - each pigeon should have only ONE result per date
        pigeon_results_by_ring = {}
        for result in results_response:
            if result.get('pigeon') and result['pigeon']['id'] in created_pigeons:
                ring_number = result['ring_number']
                if ring_number not in pigeon_results_by_ring:
                    pigeon_results_by_ring[ring_number] = []
                pigeon_results_by_ring[ring_number].append(result)
        
        duplicate_prevention_working = True
        for ring_number, results in pigeon_results_by_ring.items():
            if len(results) > 1:
                # Check if all results are from the same date
                dates = set()
                for result in results:
                    if result.get('race') and result['race'].get('date'):
                        dates.add(result['race']['date'])
                
                if len(dates) == 1:  # Same date, should be prevented
                    print(f"❌ DUPLICATE PREVENTION FAILED: Ring {ring_number} has {len(results)} results on same date {list(dates)[0]}")
                    duplicate_prevention_working = False
                else:
                    print(f"   ✅ Ring {ring_number} has {len(results)} results on different dates - OK")
            else:
                print(f"   ✅ Ring {ring_number} has {len(results)} result - duplicate prevention working")
        
        # Step 5: Verify that races were created for different categories
        success, races_response = self.run_test(
            "Get All Races After Upload",
            "GET",
            "races" if hasattr(self, 'get_races_endpoint') else "race-results",  # Fallback if no races endpoint
            200
        )
        
        if success and isinstance(races_response, list):
            chimay_races = []
            for item in races_response:
                # Check if it's a race or race result with race info
                race_info = item.get('race') if 'race' in item else item
                if race_info and race_info.get('race_name') == 'CHIMAY' and race_info.get('date') == '09-08-25':
                    chimay_races.append(race_info)
            
            if len(chimay_races) > 1:
                categories = [race.get('category', 'Unknown') for race in chimay_races]
                print(f"   ✅ Found {len(chimay_races)} CHIMAY races with categories: {categories}")
            else:
                print(f"   ⚠️  Found {len(chimay_races)} CHIMAY races (expected multiple)")
        
        # Step 6: Test uploading the same file again - should not create more duplicates
        print("\n   🔄 Testing duplicate file upload...")
        success, second_upload_response = self.run_test(
            "Upload Same File Again (Should Prevent Duplicates)",
            "POST",
            "upload-race-results",
            200,
            files=files
        )
        
        if success:
            # Check results count didn't increase inappropriately
            success, final_results = self.run_test(
                "Get Final Race Results",
                "GET",
                "race-results",
                200
            )
            
            if success:
                final_pigeon_results = {}
                for result in final_results:
                    if result.get('pigeon') and result['pigeon']['id'] in created_pigeons:
                        ring_number = result['ring_number']
                        if ring_number not in final_pigeon_results:
                            final_pigeon_results[ring_number] = []
                        final_pigeon_results[ring_number].append(result)
                
                # Should still have same number of results per pigeon
                for ring_number in pigeon_results_by_ring:
                    original_count = len(pigeon_results_by_ring[ring_number])
                    final_count = len(final_pigeon_results.get(ring_number, []))
                    if final_count > original_count:
                        print(f"❌ DUPLICATE PREVENTION FAILED: Ring {ring_number} results increased from {original_count} to {final_count}")
                        duplicate_prevention_working = False
                    else:
                        print(f"   ✅ Ring {ring_number} results stable: {final_count} (duplicate upload prevented)")
        
        # Cleanup - delete created pigeons
        for pigeon_id in created_pigeons:
            self.run_test(
                f"Cleanup Pigeon {pigeon_id}",
                "DELETE",
                f"pigeons/{pigeon_id}",
                200
            )
        
        if duplicate_prevention_working:
            print("✅ Duplicate prevention test PASSED - each pigeon has only one result per date")
            return True
        else:
            print("❌ Duplicate prevention test FAILED - duplicates were not properly prevented")
            return False

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
    
    # LATEST FIXES TESTING - Ring Number Fix and Loft Logs
    print("\n" + "🔧" * 20 + " LATEST FIXES TESTING " + "🔧" * 20)
    test_results.append(tester.test_ring_number_fix_in_pairing())
    test_results.append(tester.test_loft_log_functionality())
    test_results.append(tester.test_combined_log_systems())
    test_results.append(tester.test_data_integrity_after_updates())
    
    # NEW FUNCTIONALITY TESTS
    print("\n" + "🆕" * 20 + " NEW FUNCTIONALITY TESTS " + "🆕" * 20)
    test_results.append(tester.test_pairing_functionality())
    test_results.append(tester.test_health_log_functionality())
    test_results.append(tester.test_nonexistent_health_log_deletion())
    
    # PRIORITY TESTS - Cascade Deletion and Ring Number Matching
    print("\n" + "🎯" * 20 + " PRIORITY TESTS " + "🎯" * 20)
    test_results.append(tester.test_cascade_deletion())
    test_results.append(tester.test_ring_number_matching())
    
    # DUPLICATE PREVENTION TEST - Focus of this review
    print("\n" + "🚫" * 20 + " DUPLICATE PREVENTION TEST " + "🚫" * 20)
    test_results.append(tester.test_duplicate_prevention_multi_race_file())
    
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