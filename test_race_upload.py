#!/usr/bin/env python3
import requests
import io

# Test race results upload
base_url = "https://flight-results-1.preview.emergentagent.com"
api_url = f"{base_url}/api"

# Create race results TXT file with both pigeons
race_results_content = """----------------------------------------------------------------------
Data Technology Deerlijk
----------------------------------------------------------------------
QUIEVRAIN 22-05-21 2000 Jongen Deelnemers: 150 LOSTIJD: 07:30:00

NR  Naam                Ring        Afstand  Tijd      Snelheid
----------------------------------------------------------------------
1   Test User          BE 501516325  85000   08.1234   1450.5
2   Test User          BE 501516025  85000   08.1456   1420.3
----------------------------------------------------------------------
"""

print("Race results content:")
print(race_results_content)
print("\n" + "="*50)

# First upload to get pigeon count confirmation
files = {
    'file': ('race_results.txt', io.StringIO(race_results_content), 'text/plain')
}

print("Uploading race results file...")
response = requests.post(f"{api_url}/upload-race-results", files=files)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200 and response.json().get('needs_pigeon_count_confirmation'):
    print("\nConfirming with 2000 pigeons...")
    files = {
        'file': ('race_results.txt', io.StringIO(race_results_content), 'text/plain'),
        'confirmed_pigeon_count': ('', '2000')
    }
    
    response = requests.post(f"{api_url}/confirm-race-upload", files=files)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

# Check results
print("\nChecking race results...")
response = requests.get(f"{api_url}/race-results")
print(f"Race results: {response.json()}")

print("\nChecking dashboard stats...")
response = requests.get(f"{api_url}/dashboard-stats")
print(f"Dashboard stats: {response.json()}")