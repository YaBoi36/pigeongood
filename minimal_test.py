#!/usr/bin/env python3
"""
Minimal test to isolate the duplicate prevention issue
"""
import asyncio
import motor.motor_asyncio
import os
from datetime import datetime
import uuid

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/pigeon_racing')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.get_default_database()

async def test_duplicate_prevention():
    print("🧪 Testing duplicate prevention logic...")
    
    # Clear test data
    await db.pigeons.delete_many({})
    await db.races.delete_many({})
    await db.race_results.delete_many({})
    print("✅ Cleared test data")
    
    # Create test pigeon
    pigeon = {
        'id': str(uuid.uuid4()),
        'ring_number': 'BE505078525',
        'name': 'Test Pigeon',
        'country': 'BE',
        'gender': 'Male',
        'color': 'Blue',
        'breeder': 'Test Breeder',
        'created_at': datetime.utcnow().isoformat()
    }
    await db.pigeons.insert_one(pigeon)
    print(f"✅ Created pigeon: {pigeon['ring_number']}")
    
    # Create test race
    race_data = {
        'id': str(uuid.uuid4()),
        'organization': 'De Witpen LUMMEN',
        'race_name': 'CHIMAY',
        'date': '09-08-25',
        'total_pigeons': 462,
        'participants': 25,
        'unloading_time': '08:20',
        'category': 'Jongen',
        'created_at': datetime.utcnow().isoformat()
    }
    await db.races.insert_one(race_data)
    print(f"✅ Created race: {race_data['race_name']}")
    
    # Try to create first result
    result1 = {
        'id': str(uuid.uuid4()),
        'race_id': race_data['id'],
        'pigeon_id': pigeon['id'],
        'ring_number': 'BE505078525',
        'owner_name': 'VANGEEL JO',
        'city': 'KURINGE',
        'position': 1,
        'distance': 123355,
        'time': '09.42260',
        'speed': 1496.4214,
        'coefficient': (1 * 100) / 462,
        'created_at': datetime.utcnow().isoformat()
    }
    
    # Check for existing result (duplicate prevention logic)
    existing_results_for_pigeon = await db.race_results.find({
        "ring_number": result1['ring_number']
    }).to_list(1000)
    
    has_result_for_date = False
    for existing_result in existing_results_for_pigeon:
        existing_race = await db.races.find_one({"id": existing_result["race_id"]})
        if existing_race and existing_race["date"] == race_data["date"]:
            has_result_for_date = True
            print(f"⚠️  Found existing result for {result1['ring_number']} on date {race_data['date']}")
            break
    
    if not has_result_for_date:
        await db.race_results.insert_one(result1)
        print(f"✅ Created first result for {result1['ring_number']}")
    else:
        print(f"❌ Skipped first result due to existing result")
    
    # Try to create second result (should be prevented)
    result2 = {
        'id': str(uuid.uuid4()),
        'race_id': race_data['id'],  # Same race
        'pigeon_id': pigeon['id'],
        'ring_number': 'BE505078525',  # Same pigeon
        'owner_name': 'VANGEEL JO',
        'city': 'KURINGE', 
        'position': 2,  # Different position
        'distance': 123355,
        'time': '09.43000',  # Different time
        'speed': 1490.0,  # Different speed
        'coefficient': (2 * 100) / 462,
        'created_at': datetime.utcnow().isoformat()
    }
    
    # Check for existing result (duplicate prevention logic)
    existing_results_for_pigeon = await db.race_results.find({
        "ring_number": result2['ring_number']
    }).to_list(1000)
    
    has_result_for_date = False
    for existing_result in existing_results_for_pigeon:
        existing_race = await db.races.find_one({"id": existing_result["race_id"]})
        if existing_race and existing_race["date"] == race_data["date"]:
            has_result_for_date = True
            print(f"✅ DUPLICATE PREVENTION WORKING - Found existing result for {result2['ring_number']} on date {race_data['date']}")
            break
    
    if not has_result_for_date:
        await db.race_results.insert_one(result2)
        print(f"❌ DUPLICATE PREVENTION FAILED - Created second result")
    else:
        print(f"✅ DUPLICATE PREVENTION WORKING - Skipped second result")
    
    # Check final state
    all_results = await db.race_results.find({}).to_list(1000)
    pigeon_results = [r for r in all_results if r['ring_number'] == 'BE505078525']
    
    print(f"\n📊 Final Results:")
    print(f"  Total results in database: {len(all_results)}")
    print(f"  Results for test pigeon: {len(pigeon_results)}")
    
    if len(pigeon_results) == 1:
        print("✅ SUCCESS - Duplicate prevention is working correctly!")
        return True
    else:
        print("❌ FAILURE - Duplicate prevention is not working!")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_duplicate_prevention())
    exit(0 if result else 1)