import { Race, RaceResult } from '../types';
import { v4 as uuidv4 } from 'uuid';

export class RaceFileParser {
  static parseRaceFile(content: string): { races: Race[], results: RaceResult[] } {
    const lines = content.split('\n').map(line => line.trim());
    const races: Race[] = [];
    const results: RaceResult[] = [];
    
    let currentRace: Race | null = null;
    let inResultsSection = false;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      if (!line) continue;
      
      // Check if this is a race header line
      if (line.includes('UITSLAGEN') || line.includes('RESULTATEN') || 
          (line.includes(' ') && line.split(' ').length >= 3 && !line.startsWith('NR'))) {
        
        // Extract race information from the line
        const raceInfo = this.extractRaceInfo(line, lines, i);
        if (raceInfo) {
          currentRace = {
            id: uuidv4(),
            race_name: raceInfo.raceName,
            date: raceInfo.date,
            organisation: raceInfo.organisation,
            total_pigeons: raceInfo.totalPigeons,
            participants: raceInfo.participants,
            unloading_time: raceInfo.unloadingTime,
            created_at: new Date()
          };
          races.push(currentRace);
          inResultsSection = false;
        }
      }
      
      // Check if we're entering the results section
      if (line.startsWith('NR') && line.includes('Naam') && line.includes('Ring')) {
        inResultsSection = true;
        continue;
      }
      
      // Parse result lines
      if (inResultsSection && currentRace && line.match(/^\d+/)) {
        const result = this.parseResultLine(line, currentRace.id);
        if (result) {
          // Calculate coefficient
          result.coefficient = Math.min((result.position * 100) / currentRace.total_pigeons, 100);
          results.push(result);
        }
      }
    }
    
    return { races, results };
  }
  
  private static extractRaceInfo(line: string, lines: string[], index: number): any {
    // Look for race information in surrounding lines
    const raceName = this.extractRaceName(line, lines, index);
    const date = this.extractDate(line, lines, index);
    const organisation = this.extractOrganisation(line, lines, index);
    const totalPigeons = this.extractTotalPigeons(lines, index);
    
    if (raceName && date) {
      return {
        raceName,
        date,
        organisation: organisation || 'Unknown',
        totalPigeons: totalPigeons || 100,
        participants: totalPigeons || 100,
        unloadingTime: '06:00:00'
      };
    }
    
    return null;
  }
  
  private static extractRaceName(line: string, lines: string[], index: number): string {
    // Try to extract race name from current line or nearby lines
    const racePattern = /([A-Z][a-zA-Z\s]+)/;
    const match = line.match(racePattern);
    if (match) {
      return match[1].trim();
    }
    
    // Look in previous lines for race name
    for (let i = Math.max(0, index - 5); i < index; i++) {
      const prevLine = lines[i];
      const prevMatch = prevLine.match(racePattern);
      if (prevMatch && prevMatch[1].length > 3) {
        return prevMatch[1].trim();
      }
    }
    
    return 'Unknown Race';
  }
  
  private static extractDate(line: string, lines: string[], index: number): string {
    // Look for date patterns in current and nearby lines
    const datePattern = /(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})/;
    
    for (let i = Math.max(0, index - 3); i <= Math.min(lines.length - 1, index + 3); i++) {
      const match = lines[i].match(datePattern);
      if (match) {
        const dateStr = match[1];
        // Convert to ISO format
        const parts = dateStr.split(/[-/.]/);
        if (parts.length === 3) {
          const [day, month, year] = parts;
          const fullYear = year.length === 2 ? `20${year}` : year;
          return `${fullYear}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        }
      }
    }
    
    return new Date().toISOString().split('T')[0];
  }
  
  private static extractOrganisation(line: string, lines: string[], index: number): string {
    // Look for organisation names in nearby lines
    const orgPatterns = [
      /FEDERATIE/i,
      /BOND/i,
      /CLUB/i,
      /VERENIGING/i,
      /UNION/i
    ];
    
    for (let i = Math.max(0, index - 5); i <= Math.min(lines.length - 1, index + 2); i++) {
      const checkLine = lines[i];
      for (const pattern of orgPatterns) {
        if (pattern.test(checkLine)) {
          return checkLine.trim();
        }
      }
    }
    
    return 'Racing Federation';
  }
  
  private static extractTotalPigeons(lines: string[], index: number): number {
    // Look for total pigeon count in nearby lines
    for (let i = Math.max(0, index - 5); i <= Math.min(lines.length - 1, index + 10); i++) {
      const line = lines[i];
      const match = line.match(/(\d{2,4})\s*duiven/i) || line.match(/Total:\s*(\d{2,4})/i);
      if (match) {
        return parseInt(match[1], 10);
      }
    }
    
    return 357; // Default fallback
  }
  
  private static parseResultLine(line: string, raceId: string): RaceResult | null {
    // Parse a result line with format: NR Naam Ring Afstand Tijd Snelheid
    const parts = line.trim().split(/\s+/);
    
    if (parts.length < 6) return null;
    
    try {
      const position = parseInt(parts[0], 10);
      const name = parts[1];
      const ringNumber = this.normalizeRingNumber(parts[2]);
      const distance = this.parseDistance(parts[3]);
      const time = parts[4];
      const speed = this.parseSpeed(parts[5]);
      
      if (isNaN(position) || isNaN(distance) || isNaN(speed)) {
        return null;
      }
      
      return {
        id: uuidv4(),
        race_id: raceId,
        ring_number: ringNumber,
        owner_name: name,
        city: 'Unknown',
        position,
        distance,
        time,
        speed,
        coefficient: 0, // Will be calculated later
        created_at: new Date()
      };
    } catch (error) {
      console.error('Error parsing result line:', line, error);
      return null;
    }
  }
  
  private static normalizeRingNumber(ringStr: string): string {
    // Remove spaces and normalize
    return ringStr.replace(/\s+/g, '').toUpperCase();
  }
  
  private static parseDistance(distStr: string): number {
    // Parse distance (assume in meters)
    const cleaned = distStr.replace(/[^\d.]/g, '');
    const distance = parseFloat(cleaned);
    
    // If distance seems to be in km, convert to meters
    if (distance < 1000) {
      return distance * 1000;
    }
    
    return distance;
  }
  
  private static parseSpeed(speedStr: string): number {
    // Parse speed (in m/min)
    const cleaned = speedStr.replace(/[^\d.]/g, '');
    return parseFloat(cleaned);
  }
}