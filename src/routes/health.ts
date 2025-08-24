import { Router, Request, Response } from 'express';
import { v4 as uuidv4 } from 'uuid';
import database from '../utils/database';
import { HealthLog, HealthLogCreate, LoftLog, LoftLogCreate } from '../types';

const router = Router();

// Individual Health Logs

// Create health log
router.post('/health-logs', async (req: Request, res: Response) => {
  try {
    const logData: HealthLogCreate = req.body;
    
    // Validate that pigeon exists
    const pigeon = await database.pigeons.findOne({ id: logData.pigeon_id });
    if (!pigeon) {
      return res.status(404).json({ detail: 'Pigeon not found' });
    }
    
    const newLog: HealthLog = {
      id: uuidv4(),
      pigeon_id: logData.pigeon_id,
      type: logData.type,
      title: logData.title,
      description: logData.description,
      date: logData.date,
      reminder_date: logData.reminder_date,
      created_at: new Date()
    };
    
    const logForMongo = database.prepareForMongo(newLog);
    await database.healthLogs.insertOne(logForMongo);
    
    res.json(newLog);
  } catch (error) {
    console.error('Error creating health log:', error);
    res.status(500).json({ detail: 'Failed to create health log' });
  }
});

// Get health logs
router.get('/health-logs', async (req: Request, res: Response) => {
  try {
    const { pigeon_id, type } = req.query;
    let query: any = {};
    
    if (pigeon_id && typeof pigeon_id === 'string') {
      query.pigeon_id = pigeon_id;
    }
    if (type && typeof type === 'string') {
      query.type = type;
    }
    
    const logs = await database.healthLogs.find(query).sort({ date: -1 }).toArray();
    const parsedLogs = logs.map(log => database.parseFromMongo(log));
    
    res.json(parsedLogs);
  } catch (error) {
    console.error('Error fetching health logs:', error);
    res.status(500).json({ detail: 'Failed to fetch health logs' });
  }
});

// Delete health log
router.delete('/health-logs/:log_id', async (req: Request, res: Response) => {
  try {
    const { log_id } = req.params;
    
    const result = await database.healthLogs.deleteOne({ id: log_id });
    if (result.deletedCount === 0) {
      return res.status(404).json({ detail: 'Health log not found' });
    }
    
    res.json({ message: 'Health log deleted successfully' });
  } catch (error) {
    console.error('Error deleting health log:', error);
    res.status(500).json({ detail: 'Failed to delete health log' });
  }
});

// Loft Logs

// Create loft log
router.post('/loft-logs', async (req: Request, res: Response) => {
  try {
    const logData: LoftLogCreate = req.body;
    
    const newLog: LoftLog = {
      id: uuidv4(),
      loft_name: logData.loft_name,
      type: logData.type,
      title: logData.title,
      description: logData.description,
      date: logData.date,
      reminder_date: logData.reminder_date,
      created_at: new Date()
    };
    
    const logForMongo = database.prepareForMongo(newLog);
    await database.loftLogs.insertOne(logForMongo);
    
    res.json(newLog);
  } catch (error) {
    console.error('Error creating loft log:', error);
    res.status(500).json({ detail: 'Failed to create loft log' });
  }
});

// Get loft logs
router.get('/loft-logs', async (req: Request, res: Response) => {
  try {
    const { loft_name, type } = req.query;
    let query: any = {};
    
    if (loft_name && typeof loft_name === 'string') {
      query.loft_name = loft_name;
    }
    if (type && typeof type === 'string') {
      query.type = type;
    }
    
    const logs = await database.loftLogs.find(query).sort({ date: -1 }).toArray();
    const parsedLogs = logs.map(log => database.parseFromMongo(log));
    
    res.json(parsedLogs);
  } catch (error) {
    console.error('Error fetching loft logs:', error);
    res.status(500).json({ detail: 'Failed to fetch loft logs' });
  }
});

// Delete loft log
router.delete('/loft-logs/:log_id', async (req: Request, res: Response) => {
  try {
    const { log_id } = req.params;
    
    const result = await database.loftLogs.deleteOne({ id: log_id });
    if (result.deletedCount === 0) {
      return res.status(404).json({ detail: 'Loft log not found' });
    }
    
    res.json({ message: 'Loft log deleted successfully' });
  } catch (error) {
    console.error('Error deleting loft log:', error);
    res.status(500).json({ detail: 'Failed to delete loft log' });
  }
});

export default router;