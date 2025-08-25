#!/usr/bin/env python3
"""
Final API Verification Test
Verifies that the race results are accessible via the exact API endpoints the frontend uses
"""

import requests
import json

# Backend URL
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

def test_api_endpoints():
    """Test all API endpoints that frontend uses"""
    print("=" * 80)
    print("FINAL API VERIFICATION - FRONTEND PERSPECTIVE")
    print("=" * 80)
    
    # Test race results endpoint (main endpoint frontend uses)
    try:
        print("🔍 Testing GET /api/race-results (main frontend endpoint)...")
        response = requests.get(f"{API_BASE}/race-results", timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ SUCCESS: {len(results)} race results returned")
            
            if results:
                print("\n📊 RACE RESULTS ANALYSIS:")
                
                # Check for user's specific ring number
                user_results = [r for r in results if r.get('ring_number') == 'BE504813624']
                if user_results:
                    print(f"✅ USER'S PIGEON FOUND: {len(user_results)} results for BE504813624")
                    for i, result in enumerate(user_results, 1):
                        race_name = result.get('race', {}).get('race_name', 'Unknown')
                        position = result.get('position', 'Unknown')
                        speed = result.get('speed', 'Unknown')
                        print(f"   Result {i}: {race_name}, Position: {position}, Speed: {speed}")
                else:
                    print("❌ USER'S PIGEON NOT FOUND: No results for BE504813624")
                
                # Show sample of all results
                print(f"\n📋 SAMPLE RESULTS (first 5 of {len(results)}):")
                for i, result in enumerate(results[:5], 1):
                    ring = result.get('ring_number', 'Unknown')
                    race_name = result.get('race', {}).get('race_name', 'Unknown') if result.get('race') else 'No Race'
                    position = result.get('position', 'Unknown')
                    print(f"   {i}. Ring: {ring}, Race: {race_name}, Position: {position}")
                    
                # Check data structure
                print(f"\n🔧 DATA STRUCTURE VERIFICATION:")
                sample_result = results[0]
                required_fields = ['id', 'ring_number', 'position', 'speed', 'race']
                for field in required_fields:
                    if field in sample_result:
                        print(f"   ✅ {field}: Present")
                    else:
                        print(f"   ❌ {field}: Missing")
                        
                # Check race data structure
                if sample_result.get('race'):
                    race_fields = ['id', 'race_name', 'date', 'organisation']
                    print(f"   Race object fields:")
                    for field in race_fields:
                        if field in sample_result['race']:
                            print(f"     ✅ race.{field}: Present")
                        else:
                            print(f"     ❌ race.{field}: Missing")
            else:
                print("❌ NO RESULTS: Empty array returned")
                
        else:
            print(f"❌ FAILED: Status code {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        
    # Test pigeons endpoint
    try:
        print(f"\n🔍 Testing GET /api/pigeons...")
        response = requests.get(f"{API_BASE}/pigeons", timeout=10)
        
        if response.status_code == 200:
            pigeons = response.json()
            print(f"✅ SUCCESS: {len(pigeons)} pigeons returned")
            
            # Check for user's pigeon
            user_pigeon = None
            for pigeon in pigeons:
                if pigeon.get('ring_number') == 'BE504813624':
                    user_pigeon = pigeon
                    break
                    
            if user_pigeon:
                print(f"✅ USER'S PIGEON FOUND: {user_pigeon.get('name', 'Unknown')} - {user_pigeon.get('ring_number')}")
            else:
                print("❌ USER'S PIGEON NOT FOUND in registered pigeons")
                
        else:
            print(f"❌ FAILED: Status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        
    # Test external URL (what frontend actually uses)
    try:
        print(f"\n🔍 Testing external URL (frontend configuration)...")
        
        # Read frontend .env
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
            
        external_url = None
        for line in env_content.split('\n'):
            if line.startswith('REACT_APP_BACKEND_URL='):
                external_url = line.split('=', 1)[1].strip()
                break
                
        if external_url:
            print(f"   Frontend configured URL: {external_url}")
            
            # Test external URL
            response = requests.get(f"{external_url}/api/race-results", timeout=10)
            if response.status_code == 200:
                results = response.json()
                print(f"✅ EXTERNAL API SUCCESS: {len(results)} results")
                
                # Check for user's results via external API
                user_results = [r for r in results if r.get('ring_number') == 'BE504813624']
                if user_results:
                    print(f"✅ USER'S RESULTS ACCESSIBLE VIA EXTERNAL API: {len(user_results)} results")
                else:
                    print("❌ USER'S RESULTS NOT ACCESSIBLE VIA EXTERNAL API")
                    
            else:
                print(f"❌ EXTERNAL API FAILED: Status code {response.status_code}")
        else:
            print("❌ REACT_APP_BACKEND_URL not configured")
            
    except Exception as e:
        print(f"❌ ERROR testing external URL: {str(e)}")
        
    print("\n" + "=" * 80)
    print("FINAL DIAGNOSIS")
    print("=" * 80)
    
    # Make final API call to confirm current state
    try:
        response = requests.get(f"{API_BASE}/race-results", timeout=10)
        if response.status_code == 200:
            results = response.json()
            user_results = [r for r in results if r.get('ring_number') == 'BE504813624']
            
            if user_results:
                print("🎯 CONCLUSION: BACKEND IS WORKING CORRECTLY")
                print(f"   ✅ User's pigeon BE504813624 has {len(user_results)} race results")
                print(f"   ✅ Results are accessible via API endpoints")
                print(f"   ✅ Data structure is correct")
                print()
                print("🔍 IF USER CAN'T SEE RESULTS, CHECK:")
                print("   1. Frontend display logic")
                print("   2. Browser console for JavaScript errors")
                print("   3. Network tab to see if API calls are being made")
                print("   4. Browser cache (try hard refresh)")
                print("   5. User looking in correct section of the app")
                print()
                print("📋 USER'S RACE RESULTS:")
                for i, result in enumerate(user_results, 1):
                    race_name = result.get('race', {}).get('race_name', 'Unknown')
                    position = result.get('position', 'Unknown')
                    speed = result.get('speed', 'Unknown')
                    date = result.get('race', {}).get('date', 'Unknown')
                    print(f"   {i}. Race: {race_name}, Date: {date}, Position: {position}, Speed: {speed}")
            else:
                print("❌ ISSUE CONFIRMED: No results found for user's pigeon")
                print("   This indicates a backend issue with ring number matching")
        else:
            print("❌ API ERROR: Cannot access race results")
            
    except Exception as e:
        print(f"❌ FINAL CHECK ERROR: {str(e)}")

if __name__ == "__main__":
    test_api_endpoints()