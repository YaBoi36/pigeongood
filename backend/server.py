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
            
        # Check for organization header
        if 'Data Technology Deerlijk' in line or 'LUMMEN' in line:
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
                    
                    # Find ring number pattern (country code + number)
                    ring_idx = -1
                    for j, part in enumerate(parts):
                        if re.match(r'^[A-Z]{2}\s*\d{6,9}', part) or (len(part) == 2 and part.isupper() and j + 1 < len(parts) and parts[j + 1].isdigit()):
                            ring_idx = j
                            if j + 1 < len(parts) and parts[j + 1].isdigit():
                                ring_number = f"{part} {parts[j + 1]}"
                            else:
                                ring_number = part
                            break
                    
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
    result = await db.pigeons.delete_one({"id": pigeon_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pigeon not found")
    return {"message": "Pigeon deleted successfully"}

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
            
            # Create race
            race_obj = Race(**race_info)
            race_dict = prepare_for_mongo(race_obj.dict())
            await db.races.insert_one(race_dict)
            processed_races.append(race_obj)
            
            # Create race results with corrected coefficient calculation and duplicate prevention
            processed_ring_numbers = set()  # Track processed ring numbers for this race
            
            for result in results:
                logger.info(f"Processing result: {result}")
                
                # Skip if we already processed this ring number for this race
                ring_number = result['ring_number'].strip()
                if ring_number in processed_ring_numbers:
                    logger.warning(f"Skipping duplicate ring number {ring_number} for race {race_obj.id}")
                    continue
                
                processed_ring_numbers.add(ring_number)
                
                # Recalculate coefficient with correct formula: (place * 100) / total_pigeons_in_race
                # Maximum 5000 pigeons in race, not maximum coefficient of 5000
                actual_total_pigeons = min(race_info['total_pigeons'], 5000)  # Max 5000 pigeons in race
                if actual_total_pigeons > 0:
                    coefficient = (result['position'] * 100) / actual_total_pigeons
                else:
                    coefficient = result['position'] * 100  # If no total, just use position * 100
                
                # Try to find matching pigeon
                pigeon = await db.pigeons.find_one({"ring_number": ring_number})
                pigeon_id = pigeon['id'] if pigeon else None
                
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

@api_router.get("/race-results")
async def get_race_results(limit: int = 50):
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
    total_results = await db.race_results.count_documents({})
    
    # Get top performers (best average speed)
    pipeline = [
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
    
    # Enhance with pigeon details
    enhanced_performers = []
    for performer in top_performers:
        pigeon = await db.pigeons.find_one({"ring_number": performer["_id"]})
        enhanced_performers.append({
            "ring_number": performer["_id"],
            "name": pigeon["name"] if pigeon else "Unknown",
            "avg_speed": round(performer["avg_speed"], 2),
            "total_races": performer["total_races"],
            "best_position": performer["best_position"]
        })
    
    return {
        "total_pigeons": total_pigeons,
        "total_races": total_races,
        "total_results": total_results,
        "top_performers": enhanced_performers
    }

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