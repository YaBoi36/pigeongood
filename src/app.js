const express = require('express');
const cors = require('cors');
const multer = require('multer');
const { MongoClient } = require('mongodb');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = process.env.PORT || 8001;
const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017/pigeon_racing';

// MongoDB client
let db;
const client = new MongoClient(MONGO_URL);

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Multer for file uploads
const upload = multer({ storage: multer.memoryStorage() });

// Connect to MongoDB
async function connectDB() {
  try {
    await client.connect();
    db = client.db();
    console.log('✅ Connected to MongoDB');
  } catch (error) {
    console.error('❌ MongoDB connection error:', error);
    process.exit(1);
  }
}

// Helper functions
function prepareForMongo(data) {
  const prepared = { ...data };
  if (prepared.created_at instanceof Date) {
    prepared.created_at = prepared.created_at.toISOString();  
  }
  return prepared;
}

function parseFromMongo(data) {
  const parsed = { ...data };
  delete parsed._id;
  if (parsed.created_at && typeof parsed.created_at === 'string') {
    parsed.created_at = new Date(parsed.created_at);
  }
  return parsed;
}

// File parser function
function parseRaceFile(content) {
  const lines = content.split('\n');
  const races = [];
  const results = [];
  
  let currentRace = null;
  let currentResults = [];
  let i = 0;
  
  while (i < lines.length) {
    const line = lines[i].trim();
    
    // Skip empty lines and separator lines
    if (!line || line.includes('---')) {
      i++;
      continue;
    }
    
    // Check for organization header (save previous race and reset)
    if (line.includes('Data Technology Deerlijk') || 
        (line.includes('LUMMEN') && line.includes('Data Technology'))) {
      // Save previous race if exists
      if (currentRace && currentResults.length > 0) {
        races.push(currentRace);
        results.push(...currentResults);
      }
      
      currentRace = null;
      currentResults = [];
      i++;
      continue;
    }
    
    // Check for race header (contains race name, date, pigeons count) - CASE INSENSITIVE
    if (/\d{2}-\d{2}-\d{2}/.test(line) && 
        (/jongen/i.test(line) || /oude/i.test(line) || /jaar/i.test(line))) {
      
      // Save previous race if exists
      if (currentRace && currentResults.length > 0) {
        races.push(currentRace);
        results.push(...currentResults);
      }
      
      currentRace = parseRaceHeader(line);
      currentResults = [];
      i++;
      continue;
    }
    
    // Skip column headers (but not result lines that start with numbers) - FIXED
    if ((line.toUpperCase().includes('NR') || 
         line.toUpperCase().includes('NAAM') || 
         line.toUpperCase().includes('RING') || 
         line.toUpperCase().includes('NOM') || 
         line.toUpperCase().includes('BAGUE') || 
         line.toUpperCase().includes('VITESSE') || 
         line.toUpperCase().includes('SNELH')) && 
        !/^\s*\d+/.test(line)) {
      i++;
      continue;
    }
    
    // Parse race result lines (starts with a number)
    if (line && currentRace && /^\s*\d+/.test(line)) {
      const result = parseResultLine(line, currentRace);
      if (result) {
        currentResults.push(result);
      }
    }
    
    i++;
  }
  
  // Add final race
  if (currentRace && currentResults.length > 0) {
    races.push(currentRace);
    results.push(...currentResults);
  }
  
  return { races, results };
}

function parseRaceHeader(line) {
  const parts = line.split(/\s+/);
  
  // Extract basic info
  let raceName = 'Unknown Race';
  let date = '01-01-25';
  let totalPigeons = 0;
  let participants = 0;
  let unloadingTime = '08:00';
  let category = 'Unknown';
  
  // Parse each part
  for (let j = 0; j < parts.length; j++) {
    const part = parts[j];
    
    // Race name (first non-empty part)
    if (j === 0 && part) {
      raceName = part;
    }
    
    // Date (DD-MM-YY format)
    if (/\d{2}-\d{2}-\d{2}/.test(part)) {
      date = part;
    }
    
    // Total pigeons (number followed by category)
    if (/^\d+$/.test(part) && j + 1 < parts.length) {
      const nextPart = parts[j + 1];
      if (/jongen|oude|jaar/i.test(nextPart)) {
        totalPigeons = parseInt(part);
      }
    }
    
    // Category - CASE INSENSITIVE FIX
    if (/jongen/i.test(part)) {
      category = 'Jongen';
    } else if (/oude/i.test(part) && /jaar/i.test(part)) {
      category = 'oude & jaar';
    } else if (/oude/i.test(part)) {
      category = 'Oude';
    } else if (/jaar/i.test(part)) {
      category = 'Jaarduiven';
    }
    
    // Participants
    if (part.includes('Deelnemers:')) {
      const match = part.match(/Deelnemers:(\d+)/);
      if (match) {
        participants = parseInt(match[1]);
      }
    }
    
    // Unloading time
    if (part.includes('LOSTIJD:')) {
      const match = part.match(/LOSTIJD:(\d{2}):?(\d{2})?/);
      if (match) {
        unloadingTime = match[2] ? `${match[1]}:${match[2]}` : '08:00';
      }
    }
  }
  
  // Construct full race name including category - RACE NAME FIX
  const fullRaceName = raceName !== 'Unknown Race' ? `${raceName} ${category}` : `Unknown Race ${category}`;
  
  return {
    id: uuidv4(),
    race_name: fullRaceName,
    date: date,
    organisation: 'De Witpen LUMMEN',
    total_pigeons: totalPigeons,
    participants: participants,
    unloading_time: unloadingTime,
    created_at: new Date()
  };
}

function parseResultLine(line, race) {
  try {
    const parts = line.trim().split(/\s+/);
    
    if (parts.length < 8) {
      return null;
    }
    
    const position = parseInt(parts[0]);
    if (isNaN(position)) {
      return null;
    }
    
    // Find ring number (BE followed by digits, with or without space)
    let ringNumber = '';
    let ringIdx = -1;
    
    for (let j = 1; j < parts.length; j++) {
      const part = parts[j];
      
      // Check for country code + number pattern
      if (/^[A-Z]{2}\s*\d{6,9}/.test(part) || 
          (part.length === 2 && /^[A-Z]{2}$/.test(part) && 
           j + 1 < parts.length && /^\d{6,9}$/.test(parts[j + 1]))) {
        
        ringIdx = j;
        if (j + 1 < parts.length && /^\d{6,9}$/.test(parts[j + 1])) {
          // Country and number are separate parts
          ringNumber = `${part}${parts[j + 1]}`;
        } else {
          // Country and number in one part
          ringNumber = part;
        }
        break;
      }
    }
    
    if (!ringNumber || ringIdx === -1) {
      return null;
    }
    
    // Clean and normalize ring number
    ringNumber = ringNumber.replace(/\s+/g, '').trim();
    
    // Extract other fields
    const ownerName = parts.slice(1, ringIdx).join(' ');
    const timeIdx = ringIdx + (parts[ringIdx + 1] && /^\d{6,9}$/.test(parts[ringIdx + 1]) ? 2 : 1);
    const speedIdx = timeIdx + 1;
    
    const distance = 85000; // Default distance
    const time = parts[timeIdx] || '00.00000';
    const speed = parseFloat(parts[speedIdx] || '0');
    
    // Calculate coefficient (position * 100) / total_pigeons
    const coefficient = race.total_pigeons > 0 ? (position * 100) / race.total_pigeons : 0;
    
    return {
      id: uuidv4(),
      race_id: race.id,
      ring_number: ringNumber,
      owner_name: ownerName,
      city: ownerName.split(' ').pop() || '',
      position: position,
      distance: distance,
      time: time,
      speed: speed,
      coefficient: coefficient,
      created_at: new Date()
    };
    
  } catch (error) {
    console.error('Error parsing result line:', line, error);
    return null;
  }
}

// Routes

// Health check
app.get('/', (req, res) => {
  res.json({
    message: 'Pigeon Racing Management System API',
    version: '2.0.0-js',
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
});

// Get pigeons
app.get('/api/pigeons', async (req, res) => {
  try {
    const pigeons = await db.collection('pigeons').find({}).toArray();
    const parsedPigeons = pigeons.map(parseFromMongo);
    res.json(parsedPigeons);
  } catch (error) {
    console.error('Error fetching pigeons:', error);
    res.status(500).json({ detail: 'Failed to fetch pigeons' });
  }
});

// Create pigeon
app.post('/api/pigeons', async (req, res) => {
  try {
    // Check for duplicate ring number
    const { ring_number } = req.body;
    if (ring_number) {
      const existingPigeon = await db.collection('pigeons').findOne({ ring_number: ring_number });
      if (existingPigeon) {
        return res.status(400).json({ 
          detail: `A pigeon with ring number ${ring_number} already exists` 
        });
      }
    }

    const pigeonData = {
      id: uuidv4(),
      ...req.body,
      created_at: new Date()
    };
    
    const pigeonForMongo = prepareForMongo(pigeonData);
    await db.collection('pigeons').insertOne(pigeonForMongo);
    
    res.json(parseFromMongo(pigeonData));
  } catch (error) {
    console.error('Error creating pigeon:', error);
    res.status(500).json({ detail: 'Failed to create pigeon' });
  }
});

// Get race results 
app.get('/api/race-results', async (req, res) => {
  try {
    const results = await db.collection('race_results').find({}).sort({ created_at: -1 }).toArray();
    const detailedResults = [];
    
    for (const result of results) {
      const pigeon = await db.collection('pigeons').findOne({ ring_number: result.ring_number });
      const race = await db.collection('races').findOne({ id: result.race_id });
      
      // Include ALL results, but mark which ones have matching pigeons
      detailedResults.push({
        ...parseFromMongo(result),
        pigeon: pigeon ? parseFromMongo(pigeon) : null,
        race: race ? parseFromMongo(race) : null
      });
    }
    
    res.json(detailedResults);
  } catch (error) {
    console.error('Error fetching race results:', error);
    res.status(500).json({ detail: 'Failed to fetch race results' });
  }
});

// Upload race results file (initial upload)
app.post('/api/upload-race-results', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ detail: 'No file uploaded' });
    }
    
    const fileContent = req.file.buffer.toString('utf-8');
    const { races, results } = parseRaceFile(fileContent);
    
    // Return parsing results for confirmation
    const parsedPigeonCounts = races.map(race => race.total_pigeons);
    
    res.json({
      message: 'File parsed successfully',
      races: races.length,
      results: results.length,
      needs_pigeon_count_confirmation: parsedPigeonCounts.length > 1,
      parsed_pigeon_counts: parsedPigeonCounts
    });
  } catch (error) {
    console.error('Error parsing race file:', error);
    res.status(500).json({ detail: 'Failed to parse race file' });
  }
});

// Confirm and process race results file upload  
app.post('/api/confirm-race-upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ detail: 'No file uploaded' });
    }
    
    const fileContent = req.file.buffer.toString('utf-8');
    const { races, results } = parseRaceFile(fileContent);
    
    // Get all registered pigeons
    const registeredPigeons = await db.collection('pigeons').find({}).toArray();
    const registeredRingNumbers = new Set(registeredPigeons.map(p => p.ring_number));
    
    let racesInserted = 0;
    let resultsInserted = 0;
    const parsedPigeonCounts = [];
    
    // Insert races first
    for (const race of races) {
      try {
        const raceForMongo = prepareForMongo(race);
        await db.collection('races').insertOne(raceForMongo);
        racesInserted++;
        parsedPigeonCounts.push(race.total_pigeons);
        console.log(`Processing race: ${JSON.stringify({
          organization: race.organisation,
          race_name: race.race_name,
          date: race.date,
          total_pigeons: race.total_pigeons,
          participants: race.participants,
          unloading_time: race.unloading_time
        })}`);
      } catch (error) {
        console.error('Error inserting race:', error);
      }
    }
    
    // Insert results (only for registered pigeons and prevent duplicates)
    for (const result of results) {
      try {
        // Only process results for registered pigeons
        if (!registeredRingNumbers.has(result.ring_number)) {
          console.log(`Skipping result for unregistered pigeon ${result.ring_number}`);
          continue;
        }
        
        // Find the pigeon and set pigeon_id
        const pigeon = registeredPigeons.find(p => p.ring_number === result.ring_number);
        if (pigeon) {
          result.pigeon_id = pigeon.id;
        }
        
        console.log(`Processing result: ${JSON.stringify({
          ring_number: result.ring_number,
          owner_name: result.owner_name,
          city: result.city,
          position: result.position,
          distance: result.distance,
          time: result.time,
          speed: result.speed,
          coefficient: result.coefficient
        })}`);
        
        // DUPLICATE PREVENTION: Check if this pigeon already has a result in this specific race AND date
        const currentRace = races.find(r => r.id === result.race_id);
        if (currentRace) {
          const existingResultsForPigeon = await db.collection('race_results').find({
            ring_number: result.ring_number
          }).toArray();
          
          let hasResultForDate = false;
          for (const existingResult of existingResultsForPigeon) {
            const existingRace = await db.collection('races').findOne({ id: existingResult.race_id });
            if (existingRace && existingRace.date === currentRace.date) {
              hasResultForDate = true;
              console.log(`Skipping duplicate result for ring ${result.ring_number} on date ${currentRace.date} - pigeon already has result for this date (existing race: "${existingRace.race_name}", current race: "${currentRace.race_name}")`);
              break;
            }
          }
          
          if (hasResultForDate) {
            continue;
          }
        }
        
        const resultForMongo = prepareForMongo(result);
        await db.collection('race_results').insertOne(resultForMongo);
        resultsInserted++;
        console.log(`Created result for ${result.ring_number}`);
      } catch (error) {
        console.error('Error inserting result:', error);
      }
    }
    
    res.json({
      message: `Successfully processed ${racesInserted} races with ${resultsInserted} results`,
      races: racesInserted,
      results: resultsInserted,
      needs_pigeon_count_confirmation: false,
      parsed_pigeon_counts: parsedPigeonCounts
    });
  } catch (error) {
    console.error('Error processing race file:', error);
    res.status(500).json({ detail: 'Failed to process race file' });
  }
});

// Delete pigeon (with cascade deletion of race results)
app.delete('/api/pigeons/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Find the pigeon first to get its ring number
    const pigeon = await db.collection('pigeons').findOne({ id });
    if (!pigeon) {
      return res.status(404).json({ detail: 'Pigeon not found' });
    }
    
    // Delete associated race results (cascade deletion)
    const raceResultsDeleted = await db.collection('race_results').deleteMany({ 
      ring_number: pigeon.ring_number 
    });
    
    // Delete the pigeon
    const result = await db.collection('pigeons').deleteOne({ id });
    if (result.deletedCount === 0) {
      return res.status(404).json({ detail: 'Pigeon not found' });
    }
    
    console.log(`Deleted pigeon ${pigeon.ring_number} and ${raceResultsDeleted.deletedCount} associated race results`);
    
    res.json({ 
      message: 'Pigeon deleted successfully',
      race_results_deleted: raceResultsDeleted.deletedCount
    });
  } catch (error) {
    console.error('Error deleting pigeon:', error);
    res.status(500).json({ detail: 'Failed to delete pigeon' });
  }
});

// Delete race result
app.delete('/api/race-results/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await db.collection('race_results').deleteOne({ id });
    if (result.deletedCount === 0) {
      return res.status(404).json({ detail: 'Race result not found' });
    }
    
    console.log(`Deleted race result ${id}`);
    
    res.json({ message: 'Race result deleted successfully' });
  } catch (error) {
    console.error('Error deleting race result:', error);
    res.status(500).json({ detail: 'Failed to delete race result' });
  }
});

// Get dashboard statistics
app.get('/api/dashboard-stats', async (req, res) => {
  try {
    const totalPigeons = await db.collection('pigeons').countDocuments();
    const totalRaces = await db.collection('races').countDocuments();
    const totalResults = await db.collection('race_results').countDocuments();
    
    // Calculate wins (position 1)
    const totalWins = await db.collection('race_results').countDocuments({ position: 1 });
    
    res.json({
      total_pigeons: totalPigeons,
      total_races: totalRaces,
      total_results: totalResults,
      total_wins: totalWins
    });
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    res.status(500).json({ detail: 'Failed to fetch dashboard statistics' });
  }
});

// Clear test data
app.delete('/api/clear-test-data', async (req, res) => {
  try {
    const raceResult = await db.collection('race_results').deleteMany({});
    const raceDeleteResult = await db.collection('races').deleteMany({});
    
    res.json({
      message: 'Test data cleared successfully',
      races_deleted: raceDeleteResult.deletedCount,
      results_deleted: raceResult.deletedCount
    });
  } catch (error) {
    console.error('Error clearing test data:', error);
    res.status(500).json({ detail: 'Failed to clear test data' });
  }
});

// Start server
async function startServer() {
  try {
    await connectDB();
    
    app.listen(PORT, '0.0.0.0', () => {
      console.log(`🚀 Server running on http://0.0.0.0:${PORT}`);
      console.log(`📊 API Documentation available at http://0.0.0.0:${PORT}/api`);
      console.log(`🐦 Pigeon Racing Management System v2.0.0-js`);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Shutting down server...');
  await client.close();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Shutting down server...');
  await client.close();
  process.exit(0);
});

startServer();

// Pairing Endpoints

// Get all pairings
app.get('/api/pairings', async (req, res) => {
  try {
    const pairings = await db.collection('pairings').find({}).toArray();
    const parsedPairings = pairings.map(parseFromMongo);
    
    res.json(parsedPairings);
  } catch (error) {
    console.error('Error fetching pairings:', error);
    res.status(500).json({ detail: 'Failed to fetch pairings' });
  }
});

// Create new pairing
app.post('/api/pairings', async (req, res) => {
  try {
    const pairingData = req.body;
    
    // Validate that both pigeons exist
    const sire = await db.collection('pigeons').findOne({ id: pairingData.sire_id });
    const dam = await db.collection('pigeons').findOne({ id: pairingData.dam_id });
    
    if (!sire) {
      return res.status(404).json({ detail: 'Sire (father) pigeon not found' });
    }
    if (!dam) {
      return res.status(404).json({ detail: 'Dam (mother) pigeon not found' });
    }
    
    // Validate gender if available
    if (sire.gender && sire.gender.toLowerCase() !== 'male') {
      return res.status(400).json({ detail: 'Sire must be male' });
    }
    if (dam.gender && dam.gender.toLowerCase() !== 'female') {
      return res.status(400).json({ detail: 'Dam must be female' });
    }
    
    const newPairing = {
      id: uuidv4(),
      sire_id: pairingData.sire_id,
      dam_id: pairingData.dam_id,
      expected_hatch_date: pairingData.expected_hatch_date,
      notes: pairingData.notes || '',
      status: 'active',
      created_at: new Date()
    };
    
    const pairingForMongo = prepareForMongo(newPairing);
    await db.collection('pairings').insertOne(pairingForMongo);
    
    res.json(parseFromMongo(newPairing));
  } catch (error) {
    console.error('Error creating pairing:', error);
    res.status(500).json({ detail: 'Failed to create pairing' });
  }
});

// Create offspring from pairing
app.post('/api/pairings/:pairing_id/result', async (req, res) => {
  try {
    const { pairing_id } = req.params;
    const resultData = req.body;
    
    // Validate pairing exists
    const pairing = await db.collection('pairings').findOne({ id: pairing_id });
    if (!pairing) {
      return res.status(404).json({ detail: 'Pairing not found' });
    }
    
    // Get parent pigeons for pedigree info
    const sire = await db.collection('pigeons').findOne({ id: pairing.sire_id });
    const dam = await db.collection('pigeons').findOne({ id: pairing.dam_id });
    
    // Create full ring number
    const fullRingNumber = `${resultData.country}${resultData.ring_number}`;
    
    // Check for duplicate ring number
    const existingPigeon = await db.collection('pigeons').findOne({ ring_number: fullRingNumber });
    if (existingPigeon) {
      return res.status(400).json({ 
        detail: `A pigeon with ring number ${fullRingNumber} already exists` 
      });
    }
    
    // Create new pigeon (offspring)
    const newPigeon = {
      id: uuidv4(),
      ring_number: fullRingNumber,
      name: resultData.name || '',
      gender: resultData.gender,
      birth_year: parseInt(resultData.birth_year) || new Date().getFullYear(),
      color: resultData.color || '',
      country: resultData.country,
      breeder: resultData.breeder || '',
      loft: resultData.loft || '',
      sire_ring: sire?.ring_number || '',
      dam_ring: dam?.ring_number || '',
      created_at: new Date()
    };
    
    const pigeonForMongo = prepareForMongo(newPigeon);
    await db.collection('pigeons').insertOne(pigeonForMongo);
    
    // Create pairing result record
    const pairingResult = {
      id: uuidv4(),
      pairing_id: pairing_id,
      pigeon_id: newPigeon.id,
      ring_number: fullRingNumber,
      birth_date: resultData.birth_date,
      notes: resultData.notes || '',
      created_at: new Date()
    };
    
    const resultForMongo = prepareForMongo(pairingResult);
    await db.collection('pairing_results').insertOne(resultForMongo);
    
    res.json({
      pigeon: parseFromMongo(newPigeon),
      pairing_result: parseFromMongo(pairingResult)
    });
  } catch (error) {
    console.error('Error creating pairing result:', error);
    res.status(500).json({ detail: 'Failed to create pairing result' });
  }
});

module.exports = app;