import { Router, Request, Response } from 'express';
import { v4 as uuidv4 } from 'uuid';
import database from '../utils/database';
import { Pairing, PairingCreate, PairingResultCreate, Pigeon } from '../types';

const router = Router();

// Get all pairings
router.get('/', async (req: Request, res: Response) => {
  try {
    const pairings = await database.pairings.find({}).toArray();
    const parsedPairings = pairings.map(p => database.parseFromMongo(p));
    
    res.json(parsedPairings);
  } catch (error) {
    console.error('Error fetching pairings:', error);
    res.status(500).json({ detail: 'Failed to fetch pairings' });
  }
});

// Create new pairing
router.post('/', async (req: Request, res: Response) => {
  try {
    const pairingData: PairingCreate = req.body;
    
    // Validate that both pigeons exist
    const sire = await database.pigeons.findOne({ id: pairingData.sire_id });
    const dam = await database.pigeons.findOne({ id: pairingData.dam_id });
    
    if (!sire) {
      return res.status(404).json({ detail: 'Sire (father) pigeon not found' });
    }
    if (!dam) {
      return res.status(404).json({ detail: 'Dam (mother) pigeon not found' });
    }
    
    // Validate gender if available
    if (sire.gender && sire.gender !== 'Male') {
      return res.status(400).json({ detail: 'Sire must be male' });
    }
    if (dam.gender && dam.gender !== 'Female') {
      return res.status(400).json({ detail: 'Dam must be female' });
    }
    
    const newPairing: Pairing = {
      id: uuidv4(),
      sire_id: pairingData.sire_id,
      dam_id: pairingData.dam_id,
      expected_hatch_date: pairingData.expected_hatch_date,
      notes: pairingData.notes,
      status: 'active',
      created_at: new Date()
    };
    
    const pairingForMongo = database.prepareForMongo(newPairing);
    await database.pairings.insertOne(pairingForMongo);
    
    res.json(newPairing);
  } catch (error) {
    console.error('Error creating pairing:', error);
    res.status(500).json({ detail: 'Failed to create pairing' });
  }
});

// Create offspring from pairing
router.post('/:pairing_id/result', async (req: Request, res: Response) => {
  try {
    const { pairing_id } = req.params;
    const resultData: PairingResultCreate = req.body;
    
    // Validate pairing exists
    const pairing = await database.pairings.findOne({ id: pairing_id });
    if (!pairing) {
      return res.status(404).json({ detail: 'Pairing not found' });
    }
    
    // Create full ring number with country code
    const fullRingNumber = `${resultData.country}${resultData.ring_number}`;
    
    // Check if ring number already exists
    const existing = await database.pigeons.findOne({ ring_number: fullRingNumber });
    if (existing) {
      return res.status(400).json({ detail: 'Pigeon with this ring number already exists' });
    }
    
    // Get parent pigeons for pedigree information
    const sire = await database.pigeons.findOne({ id: pairing.sire_id });
    const dam = await database.pigeons.findOne({ id: pairing.dam_id });
    
    if (!sire || !dam) {
      return res.status(404).json({ detail: 'Parent pigeons not found' });
    }
    
    // Create new pigeon with parent information
    const newPigeon: Pigeon = {
      id: uuidv4(),
      ring_number: fullRingNumber,
      name: resultData.name || `Child of ${sire.name || sire.ring_number} x ${dam.name || dam.ring_number}`,
      country: resultData.country,
      gender: resultData.gender || 'Unknown',
      color: resultData.color || '',
      breeder: resultData.breeder || sire.breeder || '',
      loft: sire.loft || dam.loft || '', // Inherit loft from parents
      sire_ring: sire.ring_number,
      dam_ring: dam.ring_number,
      created_at: new Date()
    };
    
    const pigeonForMongo = database.prepareForMongo(newPigeon);
    await database.pigeons.insertOne(pigeonForMongo);
    
    // Store pairing result
    const pairingResult = {
      id: uuidv4(),
      pairing_id: pairing_id,
      ring_number: fullRingNumber,
      name: resultData.name,
      country: resultData.country,
      gender: resultData.gender,
      color: resultData.color,
      breeder: resultData.breeder,
      created_at: new Date()
    };
    
    const resultForMongo = database.prepareForMongo(pairingResult);
    await database.pairingResults.insertOne(resultForMongo);
    
    res.json({
      message: 'Pairing result created successfully',
      pigeon: newPigeon
    });
  } catch (error) {
    console.error('Error creating pairing result:', error);
    res.status(500).json({ detail: 'Failed to create pairing result' });
  }
});

export default router;