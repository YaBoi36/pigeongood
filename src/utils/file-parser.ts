import { Race, RaceResult } from '../types';
import { v4 as uuidv4 } from 'uuid';

interface ParsedRaceData {
  races: Race[];
  results: RaceResult[];
}

export function parseRaceFile(content: string): ParsedRaceData {
  const lines = content.split('\n');
  const races: Race[] = [];
  const results: RaceResult[] = [];
  
  let currentRace: Race | null = null;
  let currentResults: RaceResult[] = [];
  let i = 0;
  
  while (i < lines.length) {
    const line = lines[i].trim();
    
    // Skip empty lines and separator lines
    if (!line || line.includes('---')) {
      i++;
      continue;
    }
    
    // Check for organization header (save previous race and reset)
    if (line.includes('Data Technology Deerlijk') || 
        (line.includes('LUMMEN') && line.includes('Data Technology'))) {
      // Save previous race if exists
      if (currentRace && currentResults.length > 0) {
        races.push(currentRace);
        results.push(...currentResults);
      }
      
      currentRace = null;
      currentResults = [];
      i++;
      continue;
    }
    
    // Check for race header (contains race name, date, pigeons count) - CASE INSENSITIVE
    if (/\d{2}-\d{2}-\d{2}/.test(line) && 
        (/jongen/i.test(line) || /oude/i.test(line) || /jaar/i.test(line))) {
      
      // Save previous race if exists
      if (currentRace && currentResults.length > 0) {
        races.push(currentRace);
        results.push(...currentResults);
      }
      
      currentRace = parseRaceHeader(line);
      currentResults = [];
      i++;
      continue;
    }
    
    // Skip column headers (but not result lines that start with numbers) - FIXED
    if ((line.toUpperCase().includes('NR') || 
         line.toUpperCase().includes('NAAM') || 
         line.toUpperCase().includes('RING') || 
         line.toUpperCase().includes('NOM') || 
         line.toUpperCase().includes('BAGUE') || 
         line.toUpperCase().includes('VITESSE') || 
         line.toUpperCase().includes('SNELH')) && 
        !/^\s*\d+/.test(line)) {
      i++;
      continue;
    }
    
    // Parse race result lines (starts with a number)
    if (line && currentRace && /^\s*\d+/.test(line)) {
      const result = parseResultLine(line, currentRace);
      if (result) {
        currentResults.push(result);
      }
    }
    
    i++;
  }
  
  // Add final race
  if (currentRace && currentResults.length > 0) {
    races.push(currentRace);
    results.push(...currentResults);
  }
  
  return { races, results };
}

function parseRaceHeader(line: string): Race {
  const parts = line.split(/\s+/);
  
  // Extract basic info
  let raceName = 'Unknown Race';
  let date = '01-01-25';
  let totalPigeons = 0;
  let participants = 0;
  let unloadingTime = '08:00';
  let category = 'Unknown';
  
  // Parse each part
  for (let j = 0; j < parts.length; j++) {
    const part = parts[j];
    
    // Race name (first non-empty part)
    if (j === 0 && part) {
      raceName = part;
    }
    
    // Date (DD-MM-YY format)
    if (/\d{2}-\d{2}-\d{2}/.test(part)) {
      date = part;
    }
    
    // Total pigeons (number followed by category)
    if (/^\d+$/.test(part) && j + 1 < parts.length) {
      const nextPart = parts[j + 1];
      if (/jongen|oude|jaar/i.test(nextPart)) {
        totalPigeons = parseInt(part);
      }
    }
    
    // Category - CASE INSENSITIVE FIX
    if (/jongen/i.test(part)) {
      category = 'Jongen';
    } else if (/oude/i.test(part) && /jaar/i.test(part)) {
      category = 'oude & jaar';
    } else if (/oude/i.test(part)) {
      category = 'Oude';
    } else if (/jaar/i.test(part)) {
      category = 'Jaarduiven';
    }
    
    // Participants
    if (part.includes('Deelnemers:')) {
      const match = part.match(/Deelnemers:(\d+)/);
      if (match) {
        participants = parseInt(match[1]);
      }
    }
    
    // Unloading time
    if (part.includes('LOSTIJD:')) {
      const match = part.match(/LOSTIJD:(\d{2}):?(\d{2})?/);
      if (match) {
        unloadingTime = match[2] ? `${match[1]}:${match[2]}` : '08:00';
      }
    }
  }
  
  // Construct full race name including category - RACE NAME FIX
  const fullRaceName = raceName !== 'Unknown Race' ? `${raceName} ${category}` : `Unknown Race ${category}`;
  
  return {
    id: uuidv4(),
    race_name: fullRaceName,
    date: date,
    organisation: 'De Witpen LUMMEN',
    total_pigeons: totalPigeons,
    participants: participants,
    unloading_time: unloadingTime,
    created_at: new Date()
  };
}

function parseResultLine(line: string, race: Race): RaceResult | null {
  try {
    const parts = line.trim().split(/\s+/);
    
    if (parts.length < 8) {
      return null;
    }
    
    const position = parseInt(parts[0]);
    if (isNaN(position)) {
      return null;
    }
    
    // Find ring number (BE followed by digits, with or without space)
    let ringNumber = '';
    let ringIdx = -1;
    
    for (let j = 1; j < parts.length; j++) {
      const part = parts[j];
      
      // Check for country code + number pattern
      if (/^[A-Z]{2}\s*\d{6,9}/.test(part) || 
          (part.length === 2 && /^[A-Z]{2}$/.test(part) && 
           j + 1 < parts.length && /^\d{6,9}$/.test(parts[j + 1]))) {
        
        ringIdx = j;
        if (j + 1 < parts.length && /^\d{6,9}$/.test(parts[j + 1])) {
          // Country and number are separate parts
          ringNumber = `${part}${parts[j + 1]}`;
        } else {
          // Country and number in one part
          ringNumber = part;
        }
        break;
      }
    }
    
    if (!ringNumber || ringIdx === -1) {
      return null;
    }
    
    // Clean and normalize ring number
    ringNumber = ringNumber.replace(/\s+/g, '').trim();
    
    // Extract other fields
    const ownerName = parts.slice(1, ringIdx).join(' ');
    const timeIdx = ringIdx + (parts[ringIdx + 1] && /^\d{6,9}$/.test(parts[ringIdx + 1]) ? 2 : 1);
    const speedIdx = timeIdx + 1;
    
    const distance = 85000; // Default distance
    const time = parts[timeIdx] || '00.00000';
    const speed = parseFloat(parts[speedIdx] || '0');
    
    // Calculate coefficient (position * 100) / total_pigeons
    const coefficient = race.total_pigeons > 0 ? (position * 100) / race.total_pigeons : 0;
    
    return {
      id: uuidv4(),
      race_id: race.id,
      ring_number: ringNumber,
      owner_name: ownerName,
      city: ownerName.split(' ').pop() || '',
      position: position,
      distance: distance,
      time: time,
      speed: speed,
      coefficient: coefficient,
      created_at: new Date()
    };
    
  } catch (error) {
    console.error('Error parsing result line:', line, error);
    return null;
  }
}