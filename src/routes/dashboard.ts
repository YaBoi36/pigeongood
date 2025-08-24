import { Router, Request, Response } from 'express';
import database from '../utils/database';
import { DashboardStats } from '../types';

const router = Router();

// Get dashboard statistics
router.get('/dashboard-stats', async (req: Request, res: Response) => {
  try {
    // Get total counts
    const totalPigeons = await database.pigeons.countDocuments({});
    const totalRaces = await database.races.countDocuments({});
    
    // Count only results that have matching pigeons
    const allResults = await database.raceResults.find({}).toArray();
    let totalResults = 0;
    const validResults = [];
    
    for (const result of allResults) {
      // Check if pigeon exists
      if (result.pigeon_id) {
        const pigeon = await database.pigeons.findOne({ id: result.pigeon_id });
        if (pigeon) {
          totalResults++;
          validResults.push(result);
        }
      }
    }
    
    // Calculate wins (position 1) from valid results
    const totalWins = validResults.filter(r => r.position === 1).length;
    
    // Get top performers (only for pigeons that exist in our database)
    const performersAgg = [
      { $match: { pigeon_id: { $ne: null } } },
      {
        $group: {
          _id: '$ring_number',
          avg_speed: { $avg: '$speed' },
          total_races: { $sum: 1 },
          best_position: { $min: '$position' }
        }
      },
      { $match: { total_races: { $gte: 1 } } },
      { $sort: { avg_speed: -1 } },
      { $limit: 3 }
    ];
    
    const topPerformersData = await database.raceResults.aggregate(performersAgg).toArray();
    
    // Enhance with pigeon details and filter for existing pigeons only
    const enhancedPerformers = [];
    for (const performer of topPerformersData) {
      const pigeon = await database.pigeons.findOne({ ring_number: performer._id });
      if (pigeon) {
        enhancedPerformers.push({
          ring_number: performer._id,
          name: pigeon.name || 'Unnamed',
          avg_speed: Math.round(performer.avg_speed * 100) / 100,
          total_races: performer.total_races,
          best_position: performer.best_position
        });
      }
    }
    
    const stats: DashboardStats = {
      total_pigeons: totalPigeons,
      total_races: totalRaces,
      total_results: totalResults,
      total_wins: totalWins,
      top_performers: enhancedPerformers
    };
    
    res.json(stats);
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    res.status(500).json({ detail: 'Failed to fetch dashboard statistics' });
  }
});

export default router;