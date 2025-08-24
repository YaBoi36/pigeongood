import { Race, RaceResult } from '../types';
import { v4 as uuidv4 } from 'uuid';

export class RaceFileParser {
  static parseRaceFile(content: string): { races: Race[], results: RaceResult[] } {
    const lines = content.split('\n').map(line => line.trim());
    const races: Race[] = [];
    const results: RaceResult[] = [];
    
    let currentRace: Race | null = null;
    let inResultsSection = false;
    let raceHeaderFound = false;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      if (!line || line.length < 3) continue;
      
      // Look for race header patterns - be more specific
      if (!raceHeaderFound && this.isRaceHeaderLine(line, lines, i)) {
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
          raceHeaderFound = true;
          inResultsSection = false;
          console.log('Found race:', currentRace.race_name);
        }
      }
      
      // Check if we're entering the results section
      if (line.toLowerCase().includes('nr') && 
          (line.toLowerCase().includes('naam') || line.toLowerCase().includes('name')) && 
          (line.toLowerCase().includes('ring') || line.toLowerCase().includes('bague'))) {
        inResultsSection = true;
        console.log('Found results header:', line);
        continue;
      }
      
      // Parse result lines - only when we have a current race and are in results section
      if (inResultsSection && currentRace && this.isResultLine(line)) {
        const result = this.parseResultLine(line, currentRace.id);
        if (result) {
          // Calculate coefficient with max 5000 pigeons as specified
          const maxPigeons = Math.min(currentRace.total_pigeons, 5000);
          result.coefficient = (result.position * 100) / maxPigeons;
          results.push(result);
        }
      }
    }
    
    console.log(`Parsed ${races.length} races and ${results.length} results`);
    return { races, results };
  }
  
  private static isRaceHeaderLine(line: string, lines: string[], index: number): boolean {
    // More specific race header detection
    const raceIndicators = [
      /UITSLAGEN/i,
      /RESULTATEN/i,
      /RESULTS/i,
      /CLASSEMENT/i
    ];
    
    // Check if this line contains race indicators
    for (const indicator of raceIndicators) {
      if (indicator.test(line)) {
        return true;
      }
    }
    
    // Check for race info pattern: "Location Date PigeonCount Type"
    // Example: "Mettet 20-08-25 357 Jongen"
    const raceInfoPattern = /^[A-Za-z\s]+\s+\d{2}-\d{2}-\d{2}\s+\d{2,4}\s+[A-Za-z]+/;
    if (raceInfoPattern.test(line)) {
      console.log('Found race info line:', line);
      return true;
    }
    
    // Check if this looks like a race title with date nearby
    if (line.length > 10 && line.includes(' ') && !line.includes('---') && !/^NR/.test(line)) {
      for (let j = Math.max(0, index - 2); j <= Math.min(lines.length - 1, index + 2); j++) {
        if (this.containsDate(lines[j])) {
          console.log('Found race with nearby date:', line);
          return true;
        }
      }
    }
    
    return false;
  }
  
  private static isResultLine(line: string): boolean {
    // A result line should start with a number (position) and have multiple parts
    const parts = line.trim().split(/\s+/);
    
    // Must start with a number (position)
    if (!/^\d+$/.test(parts[0])) {
      return false;
    }
    
    // Must have at least 6 parts: position, name, ring, distance, time, speed
    if (parts.length < 6) {
      return false;
    }
    
    // Check if it has a ring number pattern (letters and numbers)
    const hasRingPattern = parts.some(part => /^[A-Z]{1,3}\s*\d{6,9}$/i.test(part.replace(/\s+/g, '')));
    
    return hasRingPattern;
  }
  
  private static containsDate(line: string): boolean {
    // Look for date patterns
    const datePatterns = [
      /\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}/,
      /\d{4}[-/.]\d{1,2}[-/.]\d{1,2}/,
      /\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i
    ];
    
    return datePatterns.some(pattern => pattern.test(line));
  }
  
  private static extractRaceInfo(line: string, lines: string[], index: number): any {
    // Look for race information in surrounding lines
    const raceName = this.extractRaceName(line, lines, index);
    const date = this.extractDate(line, lines, index);
    const organisation = this.extractOrganisation(line, lines, index);
    const totalPigeons = this.extractTotalPigeons(lines, index);
    
    // Only create race if we have at least name and date
    if (raceName && date && raceName !== 'Unknown Race') {
      return {
        raceName,
        date,
        organisation: organisation || 'Racing Federation',
        totalPigeons: totalPigeons || 357,
        participants: totalPigeons || 357,
        unloadingTime: '06:00:00'
      };
    }
    
    return null;
  }
  
  private static extractRaceName(line: string, lines: string[], index: number): string {
    // Try to extract race name from current line
    if (line.includes('UITSLAGEN') || line.includes('RESULTATEN') || line.includes('RESULTS')) {
      // Look in nearby lines for the actual race name
      for (let i = Math.max(0, index - 3); i <= Math.min(lines.length - 1, index + 3); i++) {
        const checkLine = lines[i].trim();
        if (checkLine && 
            !checkLine.includes('UITSLAGEN') && 
            !checkLine.includes('RESULTATEN') &&
            !checkLine.includes('RESULTS') &&
            !checkLine.startsWith('NR') &&
            checkLine.length > 5 &&
            checkLine.length < 50) {
          return checkLine;
        }
      }
    }
    
    // If current line looks like a race name (not too long, has spaces, no numbers at start)
    if (line.length > 5 && line.length < 50 && line.includes(' ') && !/^\d/.test(line)) {
      return line.trim();
    }
    
    return 'Unknown Race';
  }
  
  private static extractDate(line: string, lines: string[], index: number): string {
    // Look for date patterns in current and nearby lines
    const datePattern = /(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})/;
    
    for (let i = Math.max(0, index - 5); i <= Math.min(lines.length - 1, index + 5); i++) {
      const match = lines[i].match(datePattern);
      if (match) {
        const dateStr = match[1];
        // Convert to ISO format
        const parts = dateStr.split(/[-/.]/);
        if (parts.length === 3) {
          let [day, month, year] = parts;
          
          // Handle different date formats
          if (year.length === 2) {
            year = `20${year}`;
          }
          
          // Ensure month and day are 2 digits
          month = month.padStart(2, '0');
          day = day.padStart(2, '0');
          
          return `${year}-${month}-${day}`;
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
      /UNION/i,
      /FEDERATION/i
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
    for (let i = Math.max(0, index - 10); i <= Math.min(lines.length - 1, index + 15); i++) {
      const line = lines[i];
      
      // Look for patterns like "357 duiven", "Total: 357", etc.
      const patterns = [
        /(\d{2,4})\s*duiven/i,
        /(\d{2,4})\s*pigeons/i,
        /Total:\s*(\d{2,4})/i,
        /(\d{2,4})\s*deelnemers/i,
        /(\d{2,4})\s*participants/i
      ];
      
      for (const pattern of patterns) {
        const match = line.match(pattern);
        if (match) {
          const count = parseInt(match[1], 10);
          if (count >= 10 && count <= 5000) {  // Reasonable pigeon count range
            return count;
          }
        }
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