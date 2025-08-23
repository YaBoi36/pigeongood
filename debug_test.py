import requests
import sys
import json

def debug_race_results():
    """Debug the race results to understand the data format"""
    api_url = "https://pigeon-dashboard.preview.emergentagent.com/api"
    
    print("🔍 Debugging Race Results Data")
    print("=" * 50)
    
    # Get race results
    response = requests.get(f"{api_url}/race-results")
    if response.status_code == 200:
        results = response.json()
        print(f"Found {len(results)} race results:")
        
        for i, result in enumerate(results[:3]):  # Show first 3 results
            print(f"\nResult {i+1}:")
            print(f"  ID: {result.get('id')}")
            print(f"  Ring Number: '{result.get('ring_number')}'")
            print(f"  Position: {result.get('position')}")
            print(f"  Coefficient: {result.get('coefficient')}")
            print(f"  Pigeon: {result.get('pigeon')}")
            print(f"  Race Total Pigeons: {result.get('race', {}).get('total_pigeons')}")
    
    # Get pigeons
    response = requests.get(f"{api_url}/pigeons")
    if response.status_code == 200:
        pigeons = response.json()
        print(f"\nFound {len(pigeons)} pigeons:")
        
        for pigeon in pigeons:
            print(f"  Ring Number: '{pigeon.get('ring_number')}'")
            print(f"  Name: {pigeon.get('name')}")

def test_with_correct_format():
    """Test with the exact ring number format"""
    api_url = "https://pigeon-dashboard.preview.emergentagent.com/api"
    
    print("\n🔍 Testing with Correct Ring Number Format")
    print("=" * 50)
    
    # Clear data first
    requests.post(f"{api_url}/clear-test-data")
    
    # Create pigeon with exact format from race results
    pigeon_data = {
        "ring_number": "BE50151632585000",  # Using the format I saw in results
        "name": "Golden Sky",
        "country": "BE",
        "gender": "Male",
        "color": "Blue",
        "breeder": "Test User"
    }
    
    response = requests.post(f"{api_url}/pigeons", json=pigeon_data)
    if response.status_code == 200:
        print("✅ Created pigeon with ring number: BE50151632585000")
        pigeon_id = response.json().get('id')
    else:
        print(f"❌ Failed to create pigeon: {response.text}")
        return
    
    # Upload race results with this exact ring number
    sample_txt_content = """----------------------------------------------------------------------
Data Technology Deerlijk
----------------------------------------------------------------------
QUIEVRAIN 22-05-21 357 Jongen Deelnemers: 45 LOSTIJD: 07:30:00

NR  Naam                Ring        Afstand  Tijd      Snelheid
----------------------------------------------------------------------
1   John Doe           BE 501516325  85000   08.1234   1450.5
2   Jane Smith         NL 987654321  85000   08.1456   1420.3
3   Bob Johnson        BE 111222333  85000   08.1678   1390.8
----------------------------------------------------------------------
"""
    
    files = {
        'file': ('race_results.txt', sample_txt_content, 'text/plain')
    }
    data = {'confirmed_pigeon_count': '357'}
    
    response = requests.post(f"{api_url}/confirm-race-upload", files=files, data=data)
    if response.status_code == 200:
        print("✅ Uploaded race results")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Failed to upload: {response.text}")
    
    # Check results
    response = requests.get(f"{api_url}/race-results")
    if response.status_code == 200:
        results = response.json()
        print(f"\nFound {len(results)} race results after upload:")
        
        for result in results:
            ring_number = result.get('ring_number')
            coefficient = result.get('coefficient')
            position = result.get('position')
            pigeon = result.get('pigeon')
            race = result.get('race', {})
            total_pigeons = race.get('total_pigeons', 0)
            
            print(f"  Ring: '{ring_number}', Position: {position}, Coefficient: {coefficient:.4f}")
            print(f"    Total Pigeons in Race: {total_pigeons}")
            print(f"    Expected Coefficient: {(position * 100) / total_pigeons:.4f}")
            print(f"    Pigeon Name: {pigeon.get('name') if pigeon else 'Unknown'}")
            
            if ring_number == 'BE50151632585000' and pigeon:
                print("✅ Ring number matching working!")
            elif ring_number == 'BE50151632585000':
                print("❌ Ring number not matched to pigeon")

if __name__ == "__main__":
    debug_race_results()
    test_with_correct_format()