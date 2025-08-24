import { Router, Request, Response } from 'express';
import multer, { MulterError } from 'multer';
import database from '../utils/database';
import { parseRaceFile } from '../utils/file-parser';
import { RaceResultWithDetails } from '../types';

const router = Router();
const upload = multer({ storage: multer.memoryStorage() });

// Get all race results with pigeon and race details
router.get('/race-results', async (req: Request, res: Response): Promise<void> => {
  try {
    const results = await database.raceResults.find({}).sort({ created_at: -1 }).toArray();
    const detailedResults: RaceResultWithDetails[] = [];
    
    for (const result of results) {
      const pigeon = await database.pigeons.findOne({ ring_number: result.ring_number });
      const race = await database.races.findOne({ id: result.race_id });
      
      // Only include results that have matching pigeons
      if (pigeon) {
        detailedResults.push({
          ...database.parseFromMongo(result),
          pigeon: database.parseFromMongo(pigeon),
          race: race ? database.parseFromMongo(race) : undefined
        });
      }
    }
    
    res.json(detailedResults);
  } catch (error) {
    console.error('Error fetching race results:', error);
    res.status(500).json({ detail: 'Failed to fetch race results' });
  }
});

// Delete race result
router.delete('/race-results/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    
    const result = await database.raceResults.deleteOne({ id });
    if (result.deletedCount === 0) {
      return res.status(404).json({ detail: 'Race result not found' });
    }
    
    res.json({ message: 'Race result deleted successfully' });
  } catch (error) {
    console.error('Error deleting race result:', error);
    res.status(500).json({ detail: 'Failed to delete race result' });
  }
});

// Upload and process race results file
router.post('/upload-race-results', upload.single('file'), async (req: Request, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ detail: 'No file uploaded' });
    }
    
    const fileContent = req.file.buffer.toString('utf-8');
    const { races, results } = RaceFileParser.parseRaceFile(fileContent);
    
    // Get all registered pigeons
    const registeredPigeons = await database.pigeons.find({}).toArray();
    const registeredRingNumbers = new Set(registeredPigeons.map(p => p.ring_number));
    
    let racesInserted = 0;
    let resultsInserted = 0;
    
    // Insert races
    for (const race of races) {
      try {
        const raceForMongo = database.prepareForMongo(race);
        await database.races.insertOne(raceForMongo);
        racesInserted++;
      } catch (error) {
        console.error('Error inserting race:', error);
      }
    }
    
    // Insert results (only for registered pigeons and prevent duplicates)
    const processedPigeonsToday = new Set<string>(); // Track pigeons we've already processed for today
    const raceDate = races.length > 0 ? races[0].date : null; // All races in file should be same date
    
    for (const result of results) {
      try {
        // Only process results for registered pigeons
        if (!registeredRingNumbers.has(result.ring_number)) {
          continue;
        }
        
        // Find the pigeon and set pigeon_id
        const pigeon = registeredPigeons.find(p => p.ring_number === result.ring_number);
        if (pigeon) {
          result.pigeon_id = pigeon.id;
        }
        
        // Check for duplicates within current processing batch
        if (processedPigeonsToday.has(result.ring_number)) {
          console.log(`Duplicate result in current batch for ${result.ring_number} - skipping additional results`);
          continue;
        }
        
        // Check for duplicates against existing database results (same pigeon, same date)
        if (raceDate) {
          const existingResultsForPigeon = await database.raceResults.find({
            ring_number: result.ring_number
          }).toArray();
          
          let hasResultForDate = false;
          for (const existingResult of existingResultsForPigeon) {
            const existingRace = await database.races.findOne({ id: existingResult.race_id });
            if (existingRace && existingRace.date === raceDate) {
              hasResultForDate = true;
              break;
            }
          }
          
          if (hasResultForDate) {
            console.log(`Duplicate result found for ${result.ring_number} on date ${raceDate} - skipping`);
            continue;
          }
        }
        
        // Mark this pigeon as processed for today
        processedPigeonsToday.add(result.ring_number);
        
        const resultForMongo = database.prepareForMongo(result);
        await database.raceResults.insertOne(resultForMongo);
        resultsInserted++;
      } catch (error) {
        console.error('Error inserting result:', error);
      }
    }
    
    res.json({
      races: racesInserted,
      results: resultsInserted,
      message: `Processed ${racesInserted} races and ${resultsInserted} results`
    });
  } catch (error) {
    console.error('Error processing race file:', error);
    res.status(500).json({ detail: 'Failed to process race file' });
  }
});

// Clear test data
router.delete('/clear-test-data', async (req: Request, res: Response) => {
  try {
    const raceResult = await database.raceResults.deleteMany({});
    const raceDeleteResult = await database.races.deleteMany({});
    
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

export default router;