#!/usr/bin/env python3
"""
Comprehensive Diagnosis for User's Race Results Issue
Provides detailed analysis of why user is not seeing race results
"""

import requests
import json
import os
from datetime import datetime

BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

def get_system_state():
    """Get complete system state"""
    try:
        # Get pigeons
        response = requests.get(f"{API_BASE}/pigeons", timeout=10)
        pigeons = response.json() if response.status_code == 200 else []
        
        # Get race results
        response = requests.get(f"{API_BASE}/race-results", timeout=10)
        race_results = response.json() if response.status_code == 200 else []
        
        # Get dashboard stats
        response = requests.get(f"{API_BASE}/dashboard-stats", timeout=10)
        stats = response.json() if response.status_code == 200 else {}
        
        return {
            'pigeons': pigeons,
            'race_results': race_results,
            'stats': stats
        }
    except Exception as e:
        print(f"Error getting system state: {e}")
        return None

def analyze_ring_numbers_in_file():
    """Analyze ring numbers in the user's result file"""
    file_path = '/app/user_result.txt'
    if not os.path.exists(file_path):
        return []
    
    ring_numbers = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Look for lines with ring numbers (format: BE followed by numbers)
                if 'BE ' in line and any(char.isdigit() for char in line):
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'BE' and i + 1 < len(parts):
                            ring_number = f"BE{parts[i + 1]}"
                            if ring_number not in ring_numbers:
                                ring_numbers.append(ring_number)
    except Exception as e:
        print(f"Error reading file: {e}")
    
    return ring_numbers

def test_frontend_api():
    """Test the frontend API endpoints that would be used to display results"""
    try:
        # Test the external URL that frontend would use
        frontend_url = "https://flight-results-1.preview.emergentagent.com"
        
        print(f"Testing frontend API endpoints...")
        
        # Test pigeons endpoint
        try:
            response = requests.get(f"{frontend_url}/api/pigeons", timeout=10)
            print(f"Frontend Pigeons API: Status {response.status_code}")
            if response.status_code == 200:
                pigeons = response.json()
                print(f"  Found {len(pigeons)} pigeons via frontend API")
        except Exception as e:
            print(f"Frontend Pigeons API: ERROR - {e}")
        
        # Test race results endpoint
        try:
            response = requests.get(f"{frontend_url}/api/race-results", timeout=10)
            print(f"Frontend Race Results API: Status {response.status_code}")
            if response.status_code == 200:
                results = response.json()
                print(f"  Found {len(results)} race results via frontend API")
        except Exception as e:
            print(f"Frontend Race Results API: ERROR - {e}")
            
    except Exception as e:
        print(f"Error testing frontend API: {e}")

def main():
    print("="*80)
    print("🔍 COMPREHENSIVE DIAGNOSIS - USER'S RACE RESULTS ISSUE")
    print("="*80)
    
    # Get current system state
    print("1. CHECKING CURRENT SYSTEM STATE...")
    state = get_system_state()
    
    if not state:
        print("❌ Cannot access backend - diagnosis cannot continue")
        return
    
    pigeons = state['pigeons']
    race_results = state['race_results']
    stats = state['stats']
    
    print(f"   📊 System Status:")
    print(f"      • Registered Pigeons: {len(pigeons)}")
    print(f"      • Race Results: {len(race_results)}")
    print(f"      • Total Races: {stats.get('total_races', 0)}")
    print(f"      • Total Wins: {stats.get('total_wins', 0)}")
    
    # Show registered pigeons
    if pigeons:
        print(f"\n   🐦 Registered Pigeons:")
        for pigeon in pigeons:
            print(f"      • {pigeon.get('ring_number', 'N/A')} - {pigeon.get('name', 'Unnamed')} ({pigeon.get('owner', 'No owner')})")
    
    # Show race results
    if race_results:
        print(f"\n   🏆 Race Results:")
        for result in race_results:
            race_name = result.get('race', {}).get('race_name', 'Unknown Race')
            print(f"      • {result.get('ring_number', 'N/A')} - {race_name} (Position: {result.get('position', 'N/A')})")
    
    # Analyze ring numbers in file
    print(f"\n2. ANALYZING USER'S RESULT FILE...")
    file_rings = analyze_ring_numbers_in_file()
    print(f"   📄 Ring numbers found in user_result.txt: {len(file_rings)}")
    if file_rings:
        print(f"      Sample rings from file: {file_rings[:10]}")
    
    # Compare registered vs file rings
    if pigeons and file_rings:
        registered_rings = set(p.get('ring_number', '') for p in pigeons)
        file_rings_set = set(file_rings)
        
        matches = registered_rings.intersection(file_rings_set)
        registered_only = registered_rings - file_rings_set
        file_only = file_rings_set - registered_rings
        
        print(f"\n3. RING NUMBER MATCHING ANALYSIS...")
        print(f"   🔗 Matching rings (registered AND in file): {len(matches)}")
        if matches:
            print(f"      Matches: {list(matches)}")
        
        print(f"   ⚠️  Registered but NOT in file: {len(registered_only)}")
        if registered_only:
            print(f"      Registered only: {list(registered_only)}")
        
        print(f"   📄 In file but NOT registered: {len(file_only)}")
        if file_only:
            print(f"      File only (first 10): {list(file_only)[:10]}")
    
    # Test frontend API
    print(f"\n4. TESTING FRONTEND API ACCESS...")
    test_frontend_api()
    
    # Final diagnosis
    print(f"\n" + "="*80)
    print("🎯 FINAL DIAGNOSIS")
    print("="*80)
    
    if len(pigeons) == 0:
        print("❌ ROOT CAUSE: NO PIGEONS REGISTERED")
        print("   The user has not registered any pigeons in the system.")
        print("   Results only appear for pigeons that are registered BEFORE uploading the file.")
        print("\n💡 SOLUTION:")
        print("   1. User must register their pigeons first using the 'Add Pigeon' feature")
        print("   2. Use ring numbers that match those in their result file")
        print("   3. Then upload the race result file")
        print("   4. Results will appear for registered pigeons only")
        
    elif len(race_results) == 0:
        print("❌ ROOT CAUSE: NO MATCHING RING NUMBERS")
        print("   Pigeons are registered but no race results were created.")
        print("   This means the ring numbers in the uploaded file don't match registered pigeons.")
        print("\n💡 SOLUTION:")
        print("   1. Check that registered pigeon ring numbers exactly match those in the result file")
        print("   2. Ring numbers must be in format: BE504574322 (no spaces)")
        print("   3. Register additional pigeons with ring numbers from the file")
        print("   4. Re-upload the result file")
        
    elif len(race_results) > 0:
        print("✅ SYSTEM IS WORKING CORRECTLY!")
        print(f"   Found {len(race_results)} race results for {len(pigeons)} registered pigeons.")
        print("   Results should be visible in the frontend.")
        print("\n🔍 IF USER STILL CAN'T SEE RESULTS:")
        print("   1. Check if frontend is displaying the race results correctly")
        print("   2. Verify browser is not caching old data (refresh/clear cache)")
        print("   3. Check browser console for JavaScript errors")
        print("   4. Verify frontend is calling the correct API endpoints")
        
        # Show specific results
        print(f"\n📋 CURRENT RESULTS THAT SHOULD BE VISIBLE:")
        for result in race_results:
            race_name = result.get('race', {}).get('race_name', 'Unknown')
            position = result.get('position', 'N/A')
            speed = result.get('speed', 'N/A')
            print(f"   • Ring {result.get('ring_number', 'N/A')}: Position {position} in {race_name} (Speed: {speed})")
    
    print(f"\n" + "="*80)
    print("📞 COMMUNICATION TO USER:")
    print("="*80)
    
    if len(race_results) > 0:
        print("✅ GOOD NEWS: Your race results ARE in the system!")
        print(f"   We found {len(race_results)} race results for your registered pigeons.")
        print("   If you can't see them in the interface, try:")
        print("   • Refresh your browser page")
        print("   • Clear your browser cache")
        print("   • Check if you're looking in the right section of the app")
    else:
        print("ℹ️  Your race results are not showing because:")
        if len(pigeons) == 0:
            print("   • You need to register your pigeons FIRST, then upload the file")
        else:
            print("   • The ring numbers in your file don't match your registered pigeons")
            print("   • Make sure to register pigeons with the exact ring numbers from your file")

if __name__ == "__main__":
    main()