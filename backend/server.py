from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import re
import io

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Pydantic Models
class Pigeon(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ring_number: str
    name: str
    country: str = "NL"
    gender: str  # "Male" or "Female"
    color: str
    breeder: str
    sire_ring: Optional[str] = None
    dam_ring: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PigeonCreate(BaseModel):
    ring_number: str
    name: str
    country: str = "NL"
    gender: str
    color: str
    breeder: str
    sire_ring: Optional[str] = None
    dam_ring: Optional[str] = None

class Race(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization: str
    race_name: str
    date: str
    total_pigeons: int
    participants: int
    unloading_time: str
    category: str  # "Jongen" or "oude & jaar"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RaceResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    race_id: str
    pigeon_id: Optional[str] = None
    ring_number: str
    owner_name: str
    city: str
    position: int
    distance: int  # in meters
    time: str
    speed: float
    coefficient: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RaceResultWithDetails(BaseModel):
    id: str
    race_id: str
    ring_number: str
    owner_name: str
    city: str
    position: int
    distance: int
    time: str
    speed: float
    coefficient: float
    pigeon: Optional[Pigeon] = None
    race: Optional[Race] = None

class Pairing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sire_id: str  # Father pigeon ID
    dam_id: str   # Mother pigeon ID
    expected_hatch_date: Optional[str] = None
    notes: Optional[str] = None
    status: str = "active"  # active, completed, cancelled
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PairingCreate(BaseModel):
    sire_id: str
    dam_id: str
    expected_hatch_date: Optional[str] = None
    notes: Optional[str] = None

class PairingResultCreate(BaseModel):
    ring_number: str
    name: Optional[str] = None
    country: str = "NL"
    gender: Optional[str] = None
    color: Optional[str] = None
    breeder: Optional[str] = None

class PairingResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pairing_id: str
    ring_number: str
    name: Optional[str] = None
    country: str = "NL"
    gender: Optional[str] = None
    color: Optional[str] = None
    breeder: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PairingResultCreate(BaseModel):
    ring_number: str
    name: Optional[str] = None
    country: str = "NL"
    gender: Optional[str] = None
    color: Optional[str] = None
    breeder: Optional[str] = None

class HealthLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pigeon_id: str
    type: str  # health, training, diet
    title: str
    description: Optional[str] = None
    date: str
    reminder_date: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LoftLogCreate(BaseModel):
    loft_name: str  # Breeder/Loft name
    type: str  # health, training, diet
    title: str
    description: Optional[str] = None
    date: str
    reminder_date: Optional[str] = None

class LoftLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    loft_name: str
    type: str
    title: str
    description: Optional[str] = None
    date: str
    reminder_date: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PigeonStats(BaseModel):
    total_races: int
    total_wins: int
    win_rate: float
    best_speed: float
    avg_placement: float
    total_distance: int

# Helper functions
def parse_race_file(content: str) -> Dict[str, Any]:
    """Parse the race results TXT file"""
    lines = content.strip().split('\n')
    races = []
    current_race = None
    current_results = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and separator lines
        if not line or line.startswith('------') or line.startswith('==='):
            i += 1
            continue
            
        # Check for organization header (more specific to avoid matching city names)
        if 'Data Technology Deerlijk' in line or ('LUMMEN' in line and 'Data Technology' in line):
            # Save previous race if exists
            if current_race and current_results:
                races.append({
                    'race': current_race,
                    'results': current_results
                })
            
            current_race = None
            current_results = []
            i += 1
            continue
            
        # Check for race header (contains race name, date, pigeons count)
        if re.search(r'\d{2}-\d{2}-\d{2}', line) and ('Jongen' in line or 'oude' in line or 'jaar' in line):
            parts = line.split()
            race_name = parts[0] if parts else "Unknown"
            date = None
            total_pigeons = 0
            participants = 0
            unloading_time = ""
            category = "Jongen"
            
            # Parse line to extract race information
            for j, part in enumerate(parts):
                # Date pattern
                if re.match(r'\d{2}-\d{2}-\d{2}', part):
                    date = part
                
                # Total pigeons (number before Jongen/oude)
                if part.isdigit() and int(part) > 10:  # Reasonable threshold for pigeon count
                    total_pigeons = int(part)
                
                # Category
                if 'Jongen' in part:
                    category = "Jongen"
                elif 'oude' in part and 'jaar' in part:
                    category = "oude & jaar"
                
                # Participants
                if 'Deelnemers:' in part:
                    try:
                        participants = int(part.split(':')[1])
                    except (ValueError, IndexError):
                        participants = 0
                
                # Unloading time
                if 'LOSTIJD:' in part:
                    try:
                        time_parts = part.split(':')
                        if len(time_parts) >= 3:
                            unloading_time = f"{time_parts[1]}:{time_parts[2]}"
                        else:
                            unloading_time = "13:00"
                    except (ValueError, IndexError):
                        unloading_time = "13:00"
            
            current_race = {
                'organization': 'De Witpen LUMMEN',
                'race_name': race_name,
                'date': date or "2025-01-01",
                'total_pigeons': total_pigeons,
                'participants': participants,
                'unloading_time': unloading_time,
                'category': category
            }
            i += 1
            continue
            
        # Skip column headers
        if any(header in line.upper() for header in ['NR', 'NAAM', 'RING', 'NOM', 'BAGUE', 'VITESSE', 'SNELH']):
            i += 1
            continue
            
        # Parse race result lines (starts with a number)
        if line and current_race and re.match(r'^\s*\d+', line):
            parts = line.split()
            if len(parts) >= 7:  # Minimum required fields
                try:
                    position = int(parts[0])
                    
                    # Extract owner name (typically parts 2-3 or 2-4)
                    owner_name = ""
                    city = ""
                    ring_number = ""
                    distance = 0
                    time = ""
                    speed = 0.0
                    
                    # Find ring number pattern (country code + number) and normalize it
                    ring_idx = -1
                    for j, part in enumerate(parts):
                        if re.match(r'^[A-Z]{2}\s*\d{6,9}', part) or (len(part) == 2 and part.isupper() and j + 1 < len(parts) and parts[j + 1].isdigit()):
                            ring_idx = j
                            if j + 1 < len(parts) and parts[j + 1].isdigit():
                                ring_number = f"{part}{parts[j + 1]}"  # No space between country and number
                            else:
                                ring_number = part
                            break
                    
                    # Clean and normalize ring number
                    ring_number = ring_number.replace(' ', '').strip()
                    
                    if not ring_number:
                        logger.warning(f"Could not extract ring number from line: {line[:100]}")
                        continue
                    
                    if ring_idx > 1:
                        # Owner name is before ring number
                        owner_name = ' '.join(parts[1:ring_idx]).replace('-', ' ')
                        # City might be right after owner name
                        if ring_idx > 2:
                            city = parts[ring_idx - 1]
                    
                    # Extract distance, time, and speed from remaining parts
                    for part in parts[ring_idx + 2:]:  # Skip ring number parts
                        if part.isdigit() and len(part) >= 4:  # Distance (meters)
                            distance = int(part)
                        elif re.match(r'\d{2}\.\d{4,5}', part):  # Time format
                            time = part
                        elif re.match(r'\d+\.\d+', part):  # Speed (decimal)
                            try:
                                speed_val = float(part)
                                if speed_val > 100:  # Reasonable speed threshold
                                    speed = speed_val
                            except ValueError:
                                pass
                    
                    # Calculate coefficient: (position * 100) / total_pigeons_in_race
                    # Note: We limit the max pigeons in race to 5000, not the coefficient itself
                    actual_total_pigeons = min(current_race['total_pigeons'], 5000) if current_race['total_pigeons'] > 0 else position * 10
                    coefficient = (position * 100) / actual_total_pigeons
                    
                    if ring_number and owner_name:  # Only add if we have essential data
                        result = {
                            'ring_number': ring_number.replace(' ', ''),
                            'owner_name': owner_name.strip(),
                            'city': city.strip(),
                            'position': position,
                            'distance': distance if distance > 0 else 85000,  # Default distance
                            'time': time or "14:00:00",
                            'speed': speed if speed > 0 else 1000.0,  # Default speed
                            'coefficient': coefficient
                        }
                        current_results.append(result)
                        
                except (ValueError, IndexError) as e:
                    # Log parsing errors but continue
                    logger.warning(f"Error parsing line: {line[:50]}... - {str(e)}")
                    pass
        
        i += 1
    
    # Add the last race
    if current_race and current_results:
        races.append({
            'race': current_race,
            'results': current_results
        })
    
    return {'races': races}

def prepare_for_mongo(data):
    """Prepare data for MongoDB storage"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    """Parse data from MongoDB"""
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, str) and 'T' in value:
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    pass
    return item

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Pigeon Racing Dashboard API"}

@api_router.post("/pigeons", response_model=Pigeon)
async def create_pigeon(pigeon: PigeonCreate):
    # Check if ring number already exists
    existing = await db.pigeons.find_one({"ring_number": pigeon.ring_number})
    if existing:
        raise HTTPException(status_code=400, detail="Pigeon with this ring number already exists")
    
    pigeon_dict = pigeon.dict()
    pigeon_obj = Pigeon(**pigeon_dict)
    pigeon_data = prepare_for_mongo(pigeon_obj.dict())
    await db.pigeons.insert_one(pigeon_data)
    return pigeon_obj

@api_router.get("/pigeons", response_model=List[Pigeon])
async def get_pigeons(search: Optional[str] = None):
    query = {}
    if search:
        query = {
            "$or": [
                {"name": {"$regex": search, "$options": "i"}},
                {"ring_number": {"$regex": search, "$options": "i"}},
                {"breeder": {"$regex": search, "$options": "i"}},
                {"color": {"$regex": search, "$options": "i"}}
            ]
        }
    
    pigeons = await db.pigeons.find(query).to_list(1000)
    return [Pigeon(**parse_from_mongo(pigeon)) for pigeon in pigeons]

@api_router.get("/pigeons/{pigeon_id}", response_model=Pigeon)
async def get_pigeon(pigeon_id: str):
    pigeon = await db.pigeons.find_one({"id": pigeon_id})
    if not pigeon:
        raise HTTPException(status_code=404, detail="Pigeon not found")
    return Pigeon(**parse_from_mongo(pigeon))

@api_router.put("/pigeons/{pigeon_id}", response_model=Pigeon)
async def update_pigeon(pigeon_id: str, pigeon_update: PigeonCreate):
    existing = await db.pigeons.find_one({"id": pigeon_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Pigeon not found")
    
    # Check if new ring number conflicts with another pigeon
    ring_conflict = await db.pigeons.find_one({
        "ring_number": pigeon_update.ring_number,
        "id": {"$ne": pigeon_id}
    })
    if ring_conflict:
        raise HTTPException(status_code=400, detail="Ring number already exists for another pigeon")
    
    update_data = prepare_for_mongo(pigeon_update.dict())
    await db.pigeons.update_one({"id": pigeon_id}, {"$set": update_data})
    updated_pigeon = await db.pigeons.find_one({"id": pigeon_id})
    return Pigeon(**parse_from_mongo(updated_pigeon))

@api_router.delete("/pigeons/{pigeon_id}")
async def delete_pigeon(pigeon_id: str):
    # First, get the pigeon to verify it exists and get its ring number
    pigeon = await db.pigeons.find_one({"id": pigeon_id})
    if not pigeon:
        raise HTTPException(status_code=404, detail="Pigeon not found")
    
    # Delete all race results associated with this pigeon (cascade deletion)
    race_results_deleted = await db.race_results.delete_many({
        "$or": [
            {"pigeon_id": pigeon_id},  # Delete by pigeon_id
            {"ring_number": pigeon["ring_number"]}  # Delete by ring number (for safety)
        ]
    })
    
    # Delete the pigeon
    result = await db.pigeons.delete_one({"id": pigeon_id})
    
    return {
        "message": "Pigeon and associated race results deleted successfully",
        "race_results_deleted": race_results_deleted.deleted_count
    }

class RaceUploadRequest(BaseModel):
    total_pigeons_override: Optional[int] = None

@api_router.post("/upload-race-results")
async def upload_race_results(file: UploadFile = File(...), total_pigeons_override: Optional[int] = None):
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only TXT files are allowed")
    
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        logger.info(f"Processing file with content length: {len(content_str)}")
        parsed_data = parse_race_file(content_str)
        
        processed_races = []
        processed_results = []
        
        for race_data in parsed_data['races']:
            race_info = race_data['race']
            results = race_data['results']
            
            # Use override if provided, otherwise use parsed value
            if total_pigeons_override:
                race_info['total_pigeons'] = total_pigeons_override
            
            logger.info(f"Processing race: {race_info}")
            
            # Check if this race already exists to prevent duplicate races
            existing_race = await db.races.find_one({
                "race_name": race_info['race_name'],
                "date": race_info['date'],
                "organization": race_info['organization'],
                "category": race_info['category']
            })
            
            if existing_race:
                logger.info(f"Race already exists: {existing_race['id']}")
                race_obj = Race(**parse_from_mongo(existing_race))
                processed_races.append(race_obj)
            else:
                # Create new race
                race_obj = Race(**race_info)
                race_dict = prepare_for_mongo(race_obj.dict())
                await db.races.insert_one(race_dict)
                processed_races.append(race_obj)
                logger.info(f"Created new race: {race_obj.id}")
            
            # Create race results with robust duplicate prevention
            for result in results:
                logger.info(f"Processing result: {result}")
                
                ring_number = result['ring_number'].strip()
                
                # Check if this pigeon already has a result for this race (using race_id)
                existing_result = await db.race_results.find_one({
                    "race_id": race_obj.id,
                    "ring_number": ring_number
                })
                
                if existing_result:
                    logger.warning(f"Skipping duplicate result for ring {ring_number} in race {race_obj.id}")
                    continue
                
                # Recalculate coefficient with correct formula using the confirmed total (not parsed total)
                # Use the race's total_pigeons which should be the confirmed count if overridden
                actual_total_pigeons = min(race_obj.total_pigeons, 5000)  # Use race object's total, max 5000 pigeons in race
                if actual_total_pigeons > 0:
                    coefficient = (result['position'] * 100) / actual_total_pigeons
                else:
                    coefficient = result['position'] * 100  # If no total, just use position * 100
                
                # Try to find matching pigeon in our database
                pigeon = await db.pigeons.find_one({"ring_number": ring_number})
                pigeon_id = pigeon['id'] if pigeon else None
                
                # Only create result if pigeon exists in our database
                if pigeon_id:
                    result_obj = RaceResult(
                        race_id=race_obj.id,
                        pigeon_id=pigeon_id,
                        ring_number=ring_number,  # Use cleaned ring number
                        coefficient=coefficient,  # Use recalculated coefficient
                        **{k: v for k, v in result.items() if k not in ['coefficient', 'ring_number']}
                    )
                    result_dict = prepare_for_mongo(result_obj.dict())
                    await db.race_results.insert_one(result_dict)
                    processed_results.append(result_obj)
                    logger.info(f"Created result for registered pigeon {ring_number}")
                else:
                    logger.info(f"Skipping result for unregistered pigeon {ring_number}")
        
        return {
            "message": f"Successfully processed {len(processed_races)} races with {len(processed_results)} results",
            "races": len(processed_races),
            "results": len(processed_results),
            "needs_pigeon_count_confirmation": total_pigeons_override is None,
            "parsed_pigeon_counts": [race_data['race']['total_pigeons'] for race_data in parsed_data['races']]
        }
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@api_router.post("/confirm-race-upload")
async def confirm_race_upload(file: UploadFile = File(...), confirmed_pigeon_count: int = 0):
    """Confirm race upload with specified pigeon count"""
    return await upload_race_results(file, confirmed_pigeon_count)

@api_router.get("/race-results", response_model=List[RaceResultWithDetails])
async def get_race_results(limit: int = 50):
    # Get all results and then filter for ones with matching pigeons
    results = await db.race_results.find().sort("created_at", -1).limit(limit).to_list(limit)
    
    detailed_results = []
    for result in results:
        result_obj = RaceResult(**parse_from_mongo(result))
        
        # Get associated pigeon and race
        pigeon = None
        race = None
        
        if result_obj.pigeon_id:
            pigeon_data = await db.pigeons.find_one({"id": result_obj.pigeon_id})
            if pigeon_data:
                pigeon = Pigeon(**parse_from_mongo(pigeon_data))
        
        race_data = await db.races.find_one({"id": result_obj.race_id})
        if race_data:
            race = Race(**parse_from_mongo(race_data))
        
        # Only include results that have matching pigeons in our database
        if pigeon and race:
            detailed_result = RaceResultWithDetails(
                **result_obj.dict(),
                pigeon=pigeon,
                race=race
            )
            detailed_results.append(detailed_result)
    
    return detailed_results

@api_router.get("/pigeon-stats/{ring_number}", response_model=PigeonStats)
async def get_pigeon_stats(ring_number: str):
    results = await db.race_results.find({"ring_number": ring_number}).to_list(1000)
    
    if not results:
        return PigeonStats(
            total_races=0,
            total_wins=0,
            win_rate=0.0,
            best_speed=0.0,
            avg_placement=0.0,
            total_distance=0
        )
    
    total_races = len(results)
    total_wins = len([r for r in results if r.get('position', 0) == 1])
    win_rate = (total_wins / total_races) * 100 if total_races > 0 else 0.0
    speeds = [r.get('speed', 0) for r in results if r.get('speed', 0) > 0]
    best_speed = max(speeds) if speeds else 0.0
    positions = [r.get('position', 0) for r in results if r.get('position', 0) > 0]
    avg_placement = sum(positions) / len(positions) if positions else 0.0
    total_distance = sum([r.get('distance', 0) for r in results])
    
    return PigeonStats(
        total_races=total_races,
        total_wins=total_wins,
        win_rate=win_rate,
        best_speed=best_speed,
        avg_placement=avg_placement,
        total_distance=total_distance
    )

@api_router.delete("/race-results/{result_id}")
async def delete_race_result(result_id: str):
    result = await db.race_results.delete_one({"id": result_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Race result not found")
    return {"message": "Race result deleted successfully"}

@api_router.delete("/races/{race_id}")
async def delete_race(race_id: str):
    # Delete all race results for this race first
    await db.race_results.delete_many({"race_id": race_id})
    
    # Delete the race
    result = await db.races.delete_one({"id": race_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Race not found")
    return {"message": "Race and all its results deleted successfully"}

@api_router.post("/remove-duplicate-results")
async def remove_duplicate_results():
    """Remove duplicate race results for the same pigeon in the same race"""
    # Find all race results grouped by race_id and ring_number
    pipeline = [
        {"$group": {
            "_id": {"race_id": "$race_id", "ring_number": "$ring_number"},
            "ids": {"$push": "$id"},
            "count": {"$sum": 1}
        }},
        {"$match": {"count": {"$gt": 1}}}
    ]
    
    duplicates = await db.race_results.aggregate(pipeline).to_list(1000)
    removed_count = 0
    
    for duplicate in duplicates:
        # Keep the first result, remove the rest
        ids_to_remove = duplicate["ids"][1:]  # Skip first ID
        for result_id in ids_to_remove:
            await db.race_results.delete_one({"id": result_id})
            removed_count += 1
    
    return {
        "message": f"Removed {removed_count} duplicate race results",
        "duplicates_found": len(duplicates),
        "results_removed": removed_count
    }

@api_router.post("/clear-test-data")
async def clear_test_data():
    """Clear all test data from database"""
    races_deleted = await db.races.delete_many({})
    results_deleted = await db.race_results.delete_many({})
    pigeons_deleted = await db.pigeons.delete_many({})
    
    return {
        "message": "Test data cleared successfully",
        "races_deleted": races_deleted.deleted_count,
        "results_deleted": results_deleted.deleted_count,
        "pigeons_deleted": pigeons_deleted.deleted_count
    }

@api_router.get("/dashboard-stats")
async def get_dashboard_stats():
    # Get total counts
    total_pigeons = await db.pigeons.count_documents({})
    total_races = await db.races.count_documents({})
    
    # Count only results that have matching pigeons
    all_results = await db.race_results.find().to_list(1000)
    total_results = 0
    valid_results = []
    
    for result in all_results:
        # Check if pigeon exists
        if result.get('pigeon_id'):
            pigeon = await db.pigeons.find_one({"id": result['pigeon_id']})
            if pigeon:
                total_results += 1
                valid_results.append(result)
    
    # Calculate wins (position 1) from valid results
    total_wins = len([r for r in valid_results if r.get('position', 0) == 1])
    
    # Get top performers (only for pigeons that exist in our database)
    pipeline = [
        {"$match": {"pigeon_id": {"$ne": None}}},  # Only results with pigeons
        {"$group": {
            "_id": "$ring_number",
            "avg_speed": {"$avg": "$speed"},
            "total_races": {"$sum": 1},
            "best_position": {"$min": "$position"}
        }},
        {"$match": {"total_races": {"$gte": 1}}},
        {"$sort": {"avg_speed": -1}},
        {"$limit": 3}
    ]
    
    top_performers = await db.race_results.aggregate(pipeline).to_list(3)
    
    # Enhance with pigeon details and filter for existing pigeons only
    enhanced_performers = []
    for performer in top_performers:
        pigeon = await db.pigeons.find_one({"ring_number": performer["_id"]})
        if pigeon:  # Only include if pigeon still exists
            enhanced_performers.append({
                "ring_number": performer["_id"],
                "name": pigeon["name"],
                "avg_speed": round(performer["avg_speed"], 2),
                "total_races": performer["total_races"],
                "best_position": performer["best_position"]
            })
    
    return {
        "total_pigeons": total_pigeons,
        "total_races": total_races,
        "total_results": total_results,
        "total_wins": total_wins,
        "top_performers": enhanced_performers
    }

# Pairing endpoints
@api_router.post("/pairings", response_model=Pairing)
async def create_pairing(pairing: PairingCreate):
    # Validate that both pigeons exist
    sire = await db.pigeons.find_one({"id": pairing.sire_id})
    dam = await db.pigeons.find_one({"id": pairing.dam_id})
    
    if not sire:
        raise HTTPException(status_code=404, detail="Sire (father) pigeon not found")
    if not dam:
        raise HTTPException(status_code=404, detail="Dam (mother) pigeon not found")
    
    # Validate gender if available
    if sire.get('gender') and sire['gender'] != 'Male':
        raise HTTPException(status_code=400, detail="Sire must be male")
    if dam.get('gender') and dam['gender'] != 'Female':
        raise HTTPException(status_code=400, detail="Dam must be female")
    
    pairing_dict = pairing.dict()
    pairing_obj = Pairing(**pairing_dict)
    pairing_data = prepare_for_mongo(pairing_obj.dict())
    await db.pairings.insert_one(pairing_data)
    return pairing_obj

@api_router.get("/pairings", response_model=List[Pairing])
async def get_pairings():
    pairings = await db.pairings.find().to_list(1000)
    return [Pairing(**parse_from_mongo(pairing)) for pairing in pairings]

@api_router.post("/pairings/{pairing_id}/result")
async def create_pairing_result(pairing_id: str, result: PairingResultCreate):
    # Validate pairing exists
    pairing = await db.pairings.find_one({"id": pairing_id})
    if not pairing:
        raise HTTPException(status_code=404, detail="Pairing not found")
    
    # Create full ring number with country code
    full_ring_number = f"{result.country}{result.ring_number}"
    
    # Check if ring number already exists
    existing = await db.pigeons.find_one({"ring_number": full_ring_number})
    if existing:
        raise HTTPException(status_code=400, detail="Pigeon with this ring number already exists")
    
    # Get parent pigeons for pedigree information
    sire = await db.pigeons.find_one({"id": pairing["sire_id"]})
    dam = await db.pigeons.find_one({"id": pairing["dam_id"]})
    
    # Create new pigeon with parent information
    new_pigeon = Pigeon(
        ring_number=full_ring_number,  # Use full ring number
        name=result.name or f"Child of {sire['name'] if sire.get('name') else sire['ring_number']} x {dam['name'] if dam.get('name') else dam['ring_number']}",
        country=result.country,
        gender=result.gender or "Unknown",
        color=result.color or "",
        breeder=result.breeder or sire.get('breeder', ''),
        sire_ring=sire['ring_number'],
        dam_ring=dam['ring_number']
    )
    
    pigeon_data = prepare_for_mongo(new_pigeon.dict())
    await db.pigeons.insert_one(pigeon_data)
    
    # Store pairing result
    result_dict = result.dict()
    result_dict['pairing_id'] = pairing_id
    result_dict['ring_number'] = full_ring_number  # Store full ring number
    result_obj = PairingResult(**result_dict)
    result_data = prepare_for_mongo(result_obj.dict())
    await db.pairing_results.insert_one(result_data)
    
    return {"message": "Pairing result created successfully", "pigeon": new_pigeon}

# Loft log endpoints
@api_router.post("/loft-logs", response_model=LoftLog)
async def create_loft_log(log: LoftLogCreate):
    # No validation needed for loft_name as it's just a string identifier
    
    log_dict = log.dict()
    log_obj = LoftLog(**log_dict)
    log_data = prepare_for_mongo(log_obj.dict())
    await db.loft_logs.insert_one(log_data)
    return log_obj

@api_router.get("/loft-logs", response_model=List[LoftLog])
async def get_loft_logs(loft_name: Optional[str] = None, type: Optional[str] = None):
    query = {}
    if loft_name:
        query["loft_name"] = loft_name
    if type:
        query["type"] = type
    
    logs = await db.loft_logs.find(query).sort("date", -1).to_list(1000)
    return [LoftLog(**parse_from_mongo(log)) for log in logs]

@api_router.delete("/loft-logs/{log_id}")
async def delete_loft_log(log_id: str):
    result = await db.loft_logs.delete_one({"id": log_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Loft log not found")
    return {"message": "Loft log deleted successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()