// Type definitions for the Pigeon Racing Management System

export interface Pigeon {
  id: string;
  ring_number: string;
  name?: string;
  country: string;
  gender: string;
  color?: string;
  breeder?: string;
  loft?: string;
  sire_ring?: string;
  dam_ring?: string;
  created_at: Date;
}

export interface PigeonCreate {
  ring_number: string;
  name?: string;
  country: string;
  gender: string;
  color?: string;
  breeder?: string;
  loft?: string;
  sire_ring?: string;
  dam_ring?: string;
}

export interface Race {
  id: string;
  race_name: string;
  date: string;
  organisation: string;
  total_pigeons: number;
  participants: number;
  unloading_time: string;
  created_at: Date;
}

export interface RaceResult {
  id: string;
  race_id: string;
  ring_number: string;
  owner_name: string;
  city: string;
  position: number;
  distance: number;
  time: string;
  speed: number;
  coefficient: number;
  pigeon_id?: string;
  created_at: Date;
}

export interface RaceResultWithDetails extends RaceResult {
  pigeon?: Pigeon;
  race?: Race;
}

export interface Pairing {
  id: string;
  sire_id: string;
  dam_id: string;
  expected_hatch_date?: string;
  notes?: string;
  status: string;
  created_at: Date;
}

export interface PairingCreate {
  sire_id: string;
  dam_id: string;
  expected_hatch_date?: string;
  notes?: string;
}

export interface PairingResult {
  id: string;
  pairing_id: string;
  ring_number: string;
  name?: string;
  country: string;
  gender?: string;
  color?: string;
  breeder?: string;
  created_at: Date;
}

export interface PairingResultCreate {
  ring_number: string;
  name?: string;
  country: string;
  gender?: string;
  color?: string;
  breeder?: string;
}

export interface HealthLog {
  id: string;
  pigeon_id: string;
  type: string;
  title: string;
  description?: string;
  date: string;
  reminder_date?: string;
  created_at: Date;
}

export interface HealthLogCreate {
  pigeon_id: string;
  type: string;
  title: string;
  description?: string;
  date: string;
  reminder_date?: string;
}

export interface LoftLog {
  id: string;
  loft_name: string;
  type: string;
  title: string;
  description?: string;
  date: string;
  reminder_date?: string;
  created_at: Date;
}

export interface LoftLogCreate {
  loft_name: string;
  type: string;
  title: string;
  description?: string;
  date: string;
  reminder_date?: string;
}

export interface PigeonStats {
  total_races: number;
  best_position: number;
  avg_speed: number;
  total_wins: number;
}

export interface DashboardStats {
  total_pigeons: number;
  total_races: number;
  total_results: number;
  total_wins: number;
  top_performers: Array<{
    ring_number: string;
    name: string;
    avg_speed: number;
    total_races: number;
    best_position: number;
  }>;
}

export interface RaceFileData {
  races: number;
  results: number;
}