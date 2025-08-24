import { Router, Request, Response } from 'express';
import { v4 as uuidv4 } from 'uuid';
import database from '../utils/database';
import { Pigeon, PigeonCreate } from '../types';

const router = Router();

// Get all pigeons with optional search
router.get('/', async (req: Request, res: Response) => {
  try {
    const { search } = req.query;
    let query: any = {};
    
    if (search && typeof search === 'string') {
      query = {
        $or: [
          { name: { $regex: search, $options: 'i' } },
          { ring_number: { $regex: search, $options: 'i' } },
          { breeder: { $regex: search, $options: 'i' } },
          { color: { $regex: search, $options: 'i' } },
          { loft: { $regex: search, $options: 'i' } }
        ]
      };
    }
    
    const pigeons = await database.pigeons.find(query).toArray();
    const parsedPigeons = pigeons.map(p => database.parseFromMongo(p));
    
    res.json(parsedPigeons);
  } catch (error) {
    console.error('Error fetching pigeons:', error);
    res.status(500).json({ detail: 'Failed to fetch pigeons' });
  }
});

// Get pigeon by ID
router.get('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const pigeon = await database.pigeons.findOne({ id });
    
    if (!pigeon) {
      return res.status(404).json({ detail: 'Pigeon not found' });
    }
    
    res.json(database.parseFromMongo(pigeon));
  } catch (error) {
    console.error('Error fetching pigeon:', error);
    res.status(500).json({ detail: 'Failed to fetch pigeon' });
  }
});

// Create new pigeon
router.post('/', async (req: Request, res: Response) => {
  try {
    const pigeonData: PigeonCreate = req.body;
    
    // Validate required fields
    if (!pigeonData.ring_number || !pigeonData.country || !pigeonData.gender) {
      return res.status(400).json({ detail: 'Ring number, country, and gender are required' });
    }
    
    // Check if ring number already exists
    const existing = await database.pigeons.findOne({ ring_number: pigeonData.ring_number });
    if (existing) {
      return res.status(400).json({ detail: 'Pigeon with this ring number already exists' });
    }
    
    const newPigeon: Pigeon = {
      id: uuidv4(),
      ring_number: pigeonData.ring_number,
      name: pigeonData.name || '',
      country: pigeonData.country,
      gender: pigeonData.gender,
      color: pigeonData.color || '',
      breeder: pigeonData.breeder || '',
      loft: pigeonData.loft || '',
      sire_ring: pigeonData.sire_ring || '',
      dam_ring: pigeonData.dam_ring || '',
      created_at: new Date()
    };
    
    const pigeonForMongo = database.prepareForMongo(newPigeon);
    await database.pigeons.insertOne(pigeonForMongo);
    
    res.json(newPigeon);
  } catch (error) {
    console.error('Error creating pigeon:', error);
    res.status(500).json({ detail: 'Failed to create pigeon' });
  }
});

// Update pigeon
router.put('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const updateData: Partial<PigeonCreate> = req.body;
    
    const result = await database.pigeons.updateOne(
      { id },
      { $set: database.prepareForMongo(updateData) }
    );
    
    if (result.matchedCount === 0) {
      return res.status(404).json({ detail: 'Pigeon not found' });
    }
    
    const updatedPigeon = await database.pigeons.findOne({ id });
    res.json(database.parseFromMongo(updatedPigeon));
  } catch (error) {
    console.error('Error updating pigeon:', error);
    res.status(500).json({ detail: 'Failed to update pigeon' });
  }
});

// Delete pigeon (with cascade deletion of race results)
router.delete('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    
    // First, get the pigeon to verify it exists and get its ring number
    const pigeon = await database.pigeons.findOne({ id });
    if (!pigeon) {
      return res.status(404).json({ detail: 'Pigeon not found' });
    }
    
    // Delete all race results associated with this pigeon (cascade deletion)
    const raceResultsDeleted = await database.raceResults.deleteMany({
      $or: [
        { pigeon_id: id },
        { ring_number: pigeon.ring_number }
      ]
    });
    
    // Delete the pigeon
    const result = await database.pigeons.deleteOne({ id });
    
    res.json({
      message: 'Pigeon and associated race results deleted successfully',
      race_results_deleted: raceResultsDeleted.deletedCount
    });
  } catch (error) {
    console.error('Error deleting pigeon:', error);
    res.status(500).json({ detail: 'Failed to delete pigeon' });
  }
});

export default router;