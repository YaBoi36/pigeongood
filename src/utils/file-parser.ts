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
    const trimmedLine = line.trim();
    
    // Must start with a number (position)
    if (!/^\s*\d+/.test(trimmedLine)) {
      return false;
    }
    
    // Skip lines that are separators
    if (trimmedLine.includes('---')) {
      return false;
    }
    
    // Must have reasonable length
    if (trimmedLine.length < 20) {
      return false;
    }
    
    // Check if it has a ring number pattern (BE followed by numbers)
    const hasRingPattern = /BE\s+\d{6,9}/.test(line);
    
    // Check if it has a speed pattern (decimal number near the end)
    const hasSpeedPattern = /\d+\.\d+/.test(line);
    
    console.log(`Checking result line: "${trimmedLine}" - Ring: ${hasRingPattern}, Speed: ${hasSpeedPattern}`);
    
    return hasRingPattern || hasSpeedPattern;
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
    // Check if current line has race info pattern "Location Date Count Type"
    const raceInfoPattern = /^([A-Za-z\s]+)\s+\d{2}-\d{2}-\d{2}\s+\d{2,4}\s+([A-Za-z]+)/;
    const match = line.match(raceInfoPattern);
    if (match) {
      const location = match[1].trim();
      const category = match[2];
      console.log('Extracted race name:', `${location} ${category}`);
      return `${location} ${category}`;
    }
    
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
            !checkLine.includes('---') &&
            checkLine.length > 5 &&
            checkLine.length < 50) {
          return checkLine;
        }
      }
    }
    
    // If current line looks like a race name (not too long, has spaces, no numbers at start)
    if (line.length > 5 && line.length < 50 && line.includes(' ') && !/^\d/.test(line) && !line.includes('---')) {
      return line.trim();
    }
    
    return 'Unknown Race';
  }
  
  private static extractDate(line: string, lines: string[], index: number): string {
    // Check current line first for pattern like "Mettet 20-08-25 357 Jongen"
    const currentLineDate = line.match(/\b(\d{2}-\d{2}-\d{2})\b/);
    if (currentLineDate) {
      const dateStr = currentLineDate[1];
      const [day, month, year] = dateStr.split('-');
      const fullYear = `20${year}`;
      console.log('Extracted date from current line:', `${fullYear}-${month}-${day}`);
      return `${fullYear}-${month}-${day}`;
    }
    
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
    // First check current line for race info pattern
    const currentLine = lines[index];
    if (currentLine) {
      const raceInfoMatch = currentLine.match(/\b(\d{2,4})\s+[A-Za-z]+$/);
      if (raceInfoMatch) {
        const count = parseInt(raceInfoMatch[1], 10);
        console.log('Extracted pigeon count from current line:', count);
        if (count >= 10 && count <= 5000) {
          return count;
        }
      }
    }
    
    // Look for total pigeon count in nearby lines
    for (let i = Math.max(0, index - 10); i <= Math.min(lines.length - 1, index + 15); i++) {
      const line = lines[i];
      
      // Look for patterns like "357 duiven", "Total: 357", etc.
      const patterns = [
        /(\d{2,4})\s*duiven/i,
        /(\d{2,4})\s*pigeons/i,
        /Total:\s*(\d{2,4})/i,
        /(\d{2,4})\s*deelnemers/i,
        /(\d{2,4})\s*participants/i,
        /(\d{2,4})\s*Jongen/i,
        /(\d{2,4})\s*Young/i
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
    // Parse a complex result line
    const trimmedLine = line.trim();
    console.log('Parsing result line:', trimmedLine);
    
    try {
      // Extract position (first number)
      const positionMatch = trimmedLine.match(/^\s*(\d+)/);
      if (!positionMatch) {
        return null;
      }
      const position = parseInt(positionMatch[1], 10);
      
      // Extract ring number (BE + digits, may have spaces)
      const ringMatch = line.match(/BE\s+(\d{6,9})/);
      if (!ringMatch) {
        console.log('No ring number found in line');
        return null;
      }
      const ringNumber = `BE${ringMatch[1]}`;  // Combine BE with digits (no spaces)
      
      // Extract speed (decimal number, usually near the end)
      const speedMatches = line.match(/(\d+\.\d+)/g);
      if (!speedMatches || speedMatches.length === 0) {
        console.log('No speed found in line');
        return null;
      }
      const speed = parseFloat(speedMatches[speedMatches.length - 1]);  // Take the last decimal number
      
      // Extract owner name (more complex parsing needed)
      let name = 'Unknown';
      const parts = trimmedLine.split(/\s+/);
      if (parts.length >= 4) {
        // Try to extract name from the middle parts
        const nameStart = 2;  // Skip position and first identifier
        const nameEnd = Math.max(nameStart + 1, parts.length - 8);  // Leave room for other data
        name = parts.slice(nameStart, nameEnd).join(' ');
        if (name.length > 30) {
          name = name.substring(0, 30);  // Limit name length
        }
      }
      
      // Extract distance (try to find a reasonable distance value)
      let distance = 85000;  // Default distance in meters
      const distanceMatches = line.match(/\b(\d{4,6})\b/g);
      if (distanceMatches) {
        for (const match of distanceMatches) {
          const d = parseInt(match, 10);
          if (d >= 10000 && d <= 1000000) {  // Reasonable distance range
            distance = d;
            break;
          }
        }
      }
      
      // Extract time (look for HH.MMSS pattern)
      let time = '14:00:00';
      const timeMatch = line.match(/(\d{2}\.\d{4,5})/);
      if (timeMatch) {
        const timeStr = timeMatch[1];
        const [hours, minutesSeconds] = timeStr.split('.');
        const minutes = minutesSeconds.substring(0, 2);
        const seconds = minutesSeconds.substring(2);
        time = `${hours}:${minutes}:${seconds}`;
      }
      
      console.log(`Parsed: Position=${position}, Ring=${ringNumber}, Speed=${speed}, Name=${name}`);
      
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
      console.error('Error parsing result line:', trimmedLine, error);
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