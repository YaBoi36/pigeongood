import { MongoClient, Db, Collection } from 'mongodb';
import { 
  Pigeon, 
  Race, 
  RaceResult, 
  Pairing, 
  PairingResult, 
  HealthLog, 
  LoftLog 
} from '../types';

class Database {
  private client: MongoClient;
  private db: Db;

  constructor() {
    const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017/pigeon_racing';
    this.client = new MongoClient(mongoUrl);
  }

  async connect(): Promise<void> {
    try {
      await this.client.connect();
      this.db = this.client.db();
      console.log('✅ Connected to MongoDB');
    } catch (error) {
      console.error('❌ MongoDB connection error:', error);
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    await this.client.close();
    console.log('🔌 Disconnected from MongoDB');
  }

  // Collections
  get pigeons(): Collection<Pigeon> {
    return this.db.collection<Pigeon>('pigeons');
  }

  get races(): Collection<Race> {
    return this.db.collection<Race>('races');
  }

  get raceResults(): Collection<RaceResult> {
    return this.db.collection<RaceResult>('race_results');
  }

  get pairings(): Collection<Pairing> {
    return this.db.collection<Pairing>('pairings');
  }

  get pairingResults(): Collection<PairingResult> {
    return this.db.collection<PairingResult>('pairing_results');
  }

  get healthLogs(): Collection<HealthLog> {
    return this.db.collection<HealthLog>('health_logs');
  }

  get loftLogs(): Collection<LoftLog> {
    return this.db.collection<LoftLog>('loft_logs');
  }

  // Utility methods for data preparation
  prepareForMongo(data: any): any {
    const prepared = { ...data };
    
    // Convert Date objects to ISO strings for MongoDB
    if (prepared.created_at && prepared.created_at instanceof Date) {
      prepared.created_at = prepared.created_at.toISOString();
    }
    
    return prepared;
  }

  parseFromMongo(data: any): any {
    const parsed = { ...data };
    
    // Remove MongoDB's _id field
    delete parsed._id;
    
    // Convert ISO strings back to Date objects if needed
    if (parsed.created_at && typeof parsed.created_at === 'string') {
      parsed.created_at = new Date(parsed.created_at);
    }
    
    return parsed;
  }
}

// Export singleton instance
export const database = new Database();
export default database;