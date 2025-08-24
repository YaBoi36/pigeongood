#!/usr/bin/env python3
"""
Debug script to analyze the race file parsing logic
"""

import re
from typing import Dict, Any

def debug_parse_race_file(content: str) -> Dict[str, Any]:
    """Debug version of parse_race_file with detailed logging"""
    lines = content.strip().split('\n')
    races = []
    current_race = None
    current_results = []
    
    print(f"📄 Total lines in file: {len(lines)}")
    print("="*80)
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        print(f"Line {i+1:3d}: {line[:80]}{'...' if len(line) > 80 else ''}")
        
        # Skip empty lines and separator lines
        if not line or line.startswith('------') or line.startswith('==='):
            print(f"         → SKIP: Empty or separator line")
            i += 1
            continue
            
        # Check for organization header
        if 'Data Technology Deerlijk' in line or ('LUMMEN' in line and 'Data Technology' in line):
            print(f"         → ORGANIZATION HEADER detected")
            # Save previous race if exists
            if current_race and current_results:
                print(f"         → SAVING RACE: {current_race['race_name']} {current_race['category']} with {len(current_results)} results")
                races.append({
                    'race': current_race,
                    'results': current_results
                })
            
            current_race = None
            current_results = []
            i += 1
            continue
            
        # Check for race header (contains race name, date, pigeons count)
        date_match = re.search(r'\d{2}-\d{2}-\d{2}', line)
        category_match = ('jongen' in line.lower() or 'oude' in line.lower() or 'jaar' in line.lower())
        
        if date_match and category_match:
            print(f"         → RACE HEADER detected")
            print(f"           Date match: {date_match.group()}")
            print(f"           Category keywords found: {[word for word in ['jongen', 'oude', 'jaar'] if word in line.lower()]}")
            
            parts = line.split()
            race_name = parts[0] if parts else "Unknown"
            date = None
            total_pigeons = 0
            participants = 0
            unloading_time = ""
            category = "Jongen"
            
            # Parse line to extract race information
            for j, part in enumerate(parts):
                # Date pattern
                if re.match(r'\d{2}-\d{2}-\d{2}', part):
                    date = part
                
                # Total pigeons (number before Jongen/oude)
                if part.isdigit() and int(part) > 10:  # Reasonable threshold for pigeon count
                    total_pigeons = int(part)
                
                # Category
                if 'jongen' in part.lower():
                    category = "Jongen"
                elif 'oude' in part.lower() and 'jaar' in part.lower():
                    category = "oude & jaar"
                elif 'oude' in part.lower():
                    category = "Oude"
                elif 'jaar' in part.lower():
                    category = "Jaarduiven"
                
                # Participants
                if 'Deelnemers:' in part:
                    try:
                        participants = int(part.split(':')[1])
                    except (ValueError, IndexError):
                        participants = 0
                
                # Unloading time
                if 'LOSTIJD:' in part:
                    try:
                        time_parts = part.split(':')
                        if len(time_parts) >= 3:
                            unloading_time = f"{time_parts[1]}:{time_parts[2]}"
                        else:
                            unloading_time = "13:00"
                    except (ValueError, IndexError):
                        unloading_time = "13:00"
            
            current_race = {
                'organization': 'De Witpen LUMMEN',
                'race_name': race_name,
                'date': date or "2025-01-01",
                'total_pigeons': total_pigeons,
                'participants': participants,
                'unloading_time': unloading_time,
                'category': category
            }
            
            print(f"           → RACE CREATED: {current_race}")
            i += 1
            continue
            
        # Skip column headers
        if any(header in line.upper() for header in ['NR', 'NAAM', 'RING', 'NOM', 'BAGUE', 'VITESSE', 'SNELH']):
            print(f"         → SKIP: Column header")
            i += 1
            continue
            
        # Parse race result lines (starts with a number)
        if line and current_race and re.match(r'^\s*\d+', line):
            print(f"         → RESULT LINE detected")
            parts = line.split()
            if len(parts) >= 7:  # Minimum required fields
                try:
                    position = int(parts[0])
                    
                    # Find ring number pattern (country code + number) and normalize it
                    ring_idx = -1
                    ring_number = ""
                    for j, part in enumerate(parts):
                        if re.match(r'^[A-Z]{2}\s*\d{6,9}', part) or (len(part) == 2 and part.isupper() and j + 1 < len(parts) and parts[j + 1].isdigit()):
                            ring_idx = j
                            if j + 1 < len(parts) and parts[j + 1].isdigit():
                                ring_number = f"{part}{parts[j + 1]}"  # No space between country and number
                            else:
                                ring_number = part
                            break
                    
                    # Clean and normalize ring number
                    ring_number = ring_number.replace(' ', '').strip()
                    
                    if ring_number:
                        print(f"           → Ring number found: '{ring_number}' (position {position})")
                        
                        # Extract owner name
                        owner_name = ""
                        if ring_idx > 1:
                            owner_name = ' '.join(parts[1:ring_idx]).replace('-', ' ')
                        
                        result = {
                            'ring_number': ring_number,
                            'owner_name': owner_name.strip(),
                            'position': position,
                        }
                        current_results.append(result)
                        print(f"           → RESULT ADDED: {result}")
                    else:
                        print(f"           → NO RING NUMBER found in: {parts}")
                        
                except (ValueError, IndexError) as e:
                    print(f"           → ERROR parsing result: {str(e)}")
        else:
            if line and current_race:
                print(f"         → SKIP: Not a result line (no number start)")
            elif line:
                print(f"         → SKIP: No current race context")
        
        i += 1
    
    # Add the last race
    if current_race and current_results:
        print(f"\n🏁 SAVING FINAL RACE: {current_race['race_name']} {current_race['category']} with {len(current_results)} results")
        races.append({
            'race': current_race,
            'results': current_results
        })
    
    print("\n" + "="*80)
    print(f"📊 FINAL SUMMARY:")
    print(f"   Total races parsed: {len(races)}")
    for i, race_data in enumerate(races, 1):
        race = race_data['race']
        results = race_data['results']
        print(f"   Race {i}: {race['race_name']} {race['category']} - {len(results)} results")
        for result in results[:3]:  # Show first 3 results
            print(f"     - {result['ring_number']} (pos {result['position']})")
        if len(results) > 3:
            print(f"     - ... and {len(results) - 3} more")
    
    return {'races': races}

def main():
    print("🔍 Debug Race File Parser")
    print("Analyzing result_1.txt parsing step by step")
    
    try:
        with open('/app/result_1.txt', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ result_1.txt file not found")
        return
    
    debug_parse_race_file(content)

if __name__ == "__main__":
    main()