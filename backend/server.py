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
        
        # Skip separator lines
        if line.startswith('------'):
            i += 1
            continue
            
        # Check for organization header
        if 'Data Technology Deerlijk' in line:
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
        if re.search(r'\d{2}-\d{2}-\d{2}', line) and ('Jongen' in line or 'oude & jaar' in line):
            parts = line.split()
            race_name = parts[0]
            date = None
            total_pigeons = 0
            participants = 0
            unloading_time = ""
            category = ""
            
            for j, part in enumerate(parts):
                if re.match(r'\d{2}-\d{2}-\d{2}', part):
                    date = part
                if part.isdigit():
                    total_pigeons = int(part)
                if 'Jongen' in part:
                    category = "Jongen"
                elif 'oude' in part:
                    category = "oude & jaar"
                if 'Deelnemers:' in part:
                    participants = int(part.split(':')[1])
                if 'LOSTIJD:' in part:
                    unloading_time = part.split(':')[1] + ":" + part.split(':')[2]
            
            current_race = {
                'organization': 'De Witpen LUMMEN',
                'race_name': race_name,
                'date': date,
                'total_pigeons': total_pigeons,
                'participants': participants,
                'unloading_time': unloading_time,
                'category': category
            }
            i += 1
            continue
            
        # Skip column headers
        if 'NR' in line and 'Naam' in line and 'Ring' in line:
            i += 1
            continue
            
        # Parse race result lines
        if line and current_race and re.match(r'^\s*\d+', line):
            parts = line.split()
            if len(parts) >= 8:
                try:
                    position = int(parts[0])
                    owner_name = ' '.join(parts[2:4]) if len(parts) > 3 else parts[2]
                    city = parts[4] if len(parts) > 4 else ""
                    
                    # Find ring number (format: BE/DV/etc + digits)
                    ring_number = ""
                    distance = 0
                    time = ""
                    speed = 0.0
                    
                    for j, part in enumerate(parts):
                        if re.match(r'^[A-Z]{2}\s*\d+', part):
                            if j + 1 < len(parts):
                                ring_number = part + parts[j + 1]
                            else:
                                ring_number = part
                        elif part.isdigit() and len(part) == 5:
                            distance = int(part)
                        elif re.match(r'\d+\.\d+', part) and float(part) > 100:
                            speed = float(part)
                        elif re.match(r'\d{2}\.\d{4,5}', part):
                            time = part
                    
                    # Calculate coefficient: (position * 100) / total_pigeons, max 5000
                    coefficient = min((position * 100) / current_race['total_pigeons'], 5000)
                    
                    result = {
                        'ring_number': ring_number.replace(' ', ''),
                        'owner_name': owner_name,
                        'city': city,
                        'position': position,
                        'distance': distance,
                        'time': time,
                        'speed': speed,
                        'coefficient': coefficient
                    }
                    current_results.append(result)
                except (ValueError, IndexError):
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

@api_router.post("/upload-race-results")
async def upload_race_results(file: UploadFile = File(...)):
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only TXT files are allowed")
    
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        parsed_data = parse_race_file(content_str)
        
        processed_races = []
        processed_results = []
        
        for race_data in parsed_data['races']:
            race_info = race_data['race']
            results = race_data['results']
            
            # Create race
            race_obj = Race(**race_info)
            race_dict = prepare_for_mongo(race_obj.dict())
            await db.races.insert_one(race_dict)
            processed_races.append(race_obj)
            
            # Create race results
            for result in results:
                # Try to find matching pigeon
                pigeon = await db.pigeons.find_one({"ring_number": result['ring_number']})
                pigeon_id = pigeon['id'] if pigeon else None
                
                result_obj = RaceResult(
                    race_id=race_obj.id,
                    pigeon_id=pigeon_id,
                    **result
                )
                result_dict = prepare_for_mongo(result_obj.dict())
                await db.race_results.insert_one(result_dict)
                processed_results.append(result_obj)
        
        return {
            "message": f"Successfully processed {len(processed_races)} races with {len(processed_results)} results",
            "races": len(processed_races),
            "results": len(processed_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@api_router.get("/race-results", response_model=List[RaceResultWithDetails])
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