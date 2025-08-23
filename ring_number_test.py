import requests
import sys
import json
import io
from datetime import datetime

class RingNumberMatchingTester:
    def __init__(self, base_url="https://pigeon-dashboard.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_pigeons = []

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
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 800:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                        if len(response_data) > 0:
                            print(f"   First item: {response_data[0]}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:500]}...")

            return success, response.json() if response.text and response.status_code < 500 else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def clear_test_data(self):
        """Clear all test data"""
        print("\n🧹 Clearing test data...")
        success, response = self.run_test(
            "Clear Test Data",
            "POST",
            "clear-test-data",
            200
        )
        return success

    def test_create_test_pigeons(self):
        """Create test pigeons with ring numbers from TXT file scenario"""
        print("\n📝 STEP 1: Creating test pigeons with ring numbers that will be in TXT file")
        
        # Pigeon 1: Ring "501516325" -> will be saved as "BE501516325" (no space)
        pigeon1_data = {
            "ring_number": "BE501516325",  # No space - as user would register
            "name": "Golden Sky",
            "country": "BE",
            "gender": "Male",
            "color": "Blue",
            "breeder": "Test User"
        }
        
        success1, response1 = self.run_test(
            "Create Pigeon 1 (Golden Sky - BE501516325)",
            "POST",
            "pigeons",
            200,
            data=pigeon1_data
        )
        
        if success1 and 'id' in response1:
            self.created_pigeons.append(response1['id'])
            print(f"   ✅ Created Golden Sky with ring: {response1['ring_number']}")
        
        # Pigeon 2: Ring "501516025" -> will be saved as "BE501516025" (no space)
        pigeon2_data = {
            "ring_number": "BE501516025",  # No space - as user would register
            "name": "Silver Arrow",
            "country": "BE",
            "gender": "Female",
            "color": "Silver",
            "breeder": "Test User"
        }
        
        success2, response2 = self.run_test(
            "Create Pigeon 2 (Silver Arrow - BE501516025)",
            "POST",
            "pigeons",
            200,
            data=pigeon2_data
        )
        
        if success2 and 'id' in response2:
            self.created_pigeons.append(response2['id'])
            print(f"   ✅ Created Silver Arrow with ring: {response2['ring_number']}")
        
        return success1 and success2

    def test_upload_race_results_with_spaces(self):
        """Upload race results TXT file with spaces in ring numbers"""
        print("\n📤 STEP 2: Uploading race results with spaced ring numbers")
        
        # Create TXT content with SPACES in ring numbers (as they appear in real files)
        sample_txt_content = """----------------------------------------------------------------------
Data Technology Deerlijk
----------------------------------------------------------------------
QUIEVRAIN 22-05-21 357 Jongen Deelnemers: 357 LOSTIJD: 07:30:00

NR  Naam                Ring        Afstand  Tijd      Snelheid
----------------------------------------------------------------------
1   John Doe           BE 501516325  85000   08.1234   1450.5
2   Jane Smith         BE 501516025  85000   08.1456   1420.3
3   Bob Johnson        BE 111222333  85000   08.1678   1390.8
----------------------------------------------------------------------

LUMMEN 23-05-21 357 oude & jaar Deelnemers: 357 LOSTIJD: 08:00:00

NR  Naam                Ring        Afstand  Tijd      Snelheid
----------------------------------------------------------------------
1   Alice Brown        BE 501516325  90000   09.2345   1500.2
2   Charlie Davis      BE 501516025  90000   09.2567   1480.1
----------------------------------------------------------------------
"""
        
        # First upload without confirmation
        files = {
            'file': ('race_results.txt', sample_txt_content, 'text/plain')
        }
        
        success1, response1 = self.run_test(
            "Initial Upload (Should Need Confirmation)",
            "POST",
            "upload-race-results",
            200,
            files=files
        )
        
        if not success1:
            return False
            
        print(f"   📊 Parsed pigeon counts: {response1.get('parsed_pigeon_counts', [])}")
        print(f"   🔄 Needs confirmation: {response1.get('needs_pigeon_count_confirmation', False)}")
        
        # Now confirm with exact pigeon count
        files = {
            'file': ('race_results.txt', sample_txt_content, 'text/plain')
        }
        data = {
            'confirmed_pigeon_count': '357'
        }
        
        success2, response2 = self.run_test(
            "Confirmed Upload (357 pigeons)",
            "POST",
            "confirm-race-upload",
            200,
            files=files,
            data=data
        )
        
        if success2:
            print(f"   🏁 Races processed: {response2.get('races', 0)}")
            print(f"   📈 Results recorded: {response2.get('results', 0)}")
            print(f"   💡 Expected: 2 results (both pigeons should match)")
        
        return success2

    def test_verify_race_results(self):
        """Verify that race results show matched pigeons with names"""
        print("\n🔍 STEP 3: Verifying race results show matched pigeons")
        
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
        
        # Check if we have the expected results
        golden_sky_found = False
        silver_arrow_found = False
        
        for result in results:
            pigeon_name = result.get('pigeon', {}).get('name', 'Unknown') if result.get('pigeon') else 'Unknown'
            ring_number = result.get('ring_number', '')
            position = result.get('position', 0)
            
            print(f"   🏆 Position #{position}: {pigeon_name} (Ring: {ring_number})")
            
            if pigeon_name == "Golden Sky" and "501516325" in ring_number:
                golden_sky_found = True
                print(f"      ✅ Golden Sky found in position #{position}")
            elif pigeon_name == "Silver Arrow" and "501516025" in ring_number:
                silver_arrow_found = True
                print(f"      ✅ Silver Arrow found in position #{position}")
        
        success_match = golden_sky_found and silver_arrow_found
        
        if success_match:
            print(f"   🎉 SUCCESS: Both pigeons matched correctly!")
        else:
            print(f"   ❌ FAILURE: Missing matches - Golden Sky: {golden_sky_found}, Silver Arrow: {silver_arrow_found}")
        
        return success_match

    def test_verify_dashboard_stats(self):
        """Verify dashboard statistics reflect the matched results"""
        print("\n📊 STEP 4: Verifying dashboard statistics")
        
        success, response = self.run_test(
            "Get Dashboard Stats",
            "GET",
            "dashboard-stats",
            200
        )
        
        if not success:
            return False
            
        stats = response
        total_races = stats.get('total_races', 0)
        total_results = stats.get('total_results', 0)
        total_wins = stats.get('total_wins', 0)
        
        print(f"   🏁 Total Races: {total_races} (Expected: 2)")
        print(f"   📈 Total Results: {total_results} (Expected: 4 - 2 pigeons × 2 races)")
        print(f"   🏆 Total Wins: {total_wins} (Expected: 2 - 1 win per race)")
        
        # Calculate win rate
        win_rate = (total_wins / total_results * 100) if total_results > 0 else 0
        print(f"   📊 Win Rate: {win_rate:.1f}% (Expected: 50%)")
        
        # Check if stats are reasonable
        stats_correct = (
            total_races >= 2 and  # At least 2 races
            total_results >= 2 and  # At least 2 results (our pigeons matched)
            total_wins >= 1  # At least 1 win
        )
        
        if stats_correct:
            print(f"   ✅ Dashboard statistics look correct!")
        else:
            print(f"   ❌ Dashboard statistics seem incorrect")
        
        return stats_correct

    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 STEP 5: Cleaning up test data")
        
        # Delete created pigeons
        for pigeon_id in self.created_pigeons:
            success, response = self.run_test(
                f"Delete Pigeon {pigeon_id}",
                "DELETE",
                f"pigeons/{pigeon_id}",
                200
            )
        
        # Clear all test data
        return self.clear_test_data()

def main():
    print("🚀 RING NUMBER MATCHING TEST")
    print("Testing the FIXED ring number normalization system")
    print("=" * 70)
    print("SCENARIO:")
    print("- TXT file contains: 'BE 501516325' (with space)")
    print("- User registers as: 'BE501516325' (no space)")
    print("- System should normalize and match both formats")
    print("=" * 70)
    
    tester = RingNumberMatchingTester()
    
    # Clear any existing test data first
    tester.clear_test_data()
    
    # Run the comprehensive test scenario
    test_results = []
    
    # Step 1: Create test pigeons (as user would register them - no spaces)
    test_results.append(tester.test_create_test_pigeons())
    
    # Step 2: Upload race results (with spaces as in real TXT files)
    test_results.append(tester.test_upload_race_results_with_spaces())
    
    # Step 3: Verify race results show matched pigeons with names
    test_results.append(tester.test_verify_race_results())
    
    # Step 4: Verify dashboard statistics
    test_results.append(tester.test_verify_dashboard_stats())
    
    # Step 5: Cleanup
    test_results.append(tester.cleanup_test_data())
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 FINAL RESULTS: {tester.tests_passed}/{tester.tests_run} individual tests passed")
    
    all_scenarios_passed = all(test_results)
    
    if all_scenarios_passed:
        print("🎉 SUCCESS: Ring number matching is working correctly!")
        print("✅ The fix has resolved the space mismatch issue")
        print("✅ Registered pigeons now appear in race results with their names")
        print("✅ Dashboard statistics reflect real matched data")
        return 0
    else:
        print("❌ FAILURE: Ring number matching still has issues")
        print("⚠️  The fix may not be working as expected")
        return 1

if __name__ == "__main__":
    sys.exit(main())