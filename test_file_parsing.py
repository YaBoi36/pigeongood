#!/usr/bin/env python3

import re

def parse_race_file(content: str):
    """Parse the race results TXT file - simplified version for debugging"""
    lines = content.strip().split('\n')
    races = []
    current_race = None
    current_results = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        print(f"Line {i}: '{line}'")
        
        # Skip empty lines and separator lines
        if not line or line.startswith('------') or line.startswith('==='):
            print(f"  -> Skipping empty/separator line")
            i += 1
            continue
            
        # Check for organization header
        if 'Data Technology Deerlijk' in line or 'LUMMEN' in line:
            print(f"  -> Organization header found")
            # Save previous race if exists
            if current_race and current_results:
                races.append({
                    'race': current_race,
                    'results': current_results
                })
            
            current_race = None
            current_results = []
            i += 1
            continue
            
        # Check for race header (contains race name, date, pigeons count)
        if re.search(r'\d{2}-\d{2}-\d{2}', line) and ('Jongen' in line or 'oude' in line or 'jaar' in line):
            print(f"  -> Race header found")
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
                if 'Jongen' in part:
                    category = "Jongen"
                elif 'oude' in part and 'jaar' in part:
                    category = "oude & jaar"
                
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
            print(f"  -> Created race: {current_race}")
            i += 1
            continue
            
        # Skip column headers
        if any(header in line.upper() for header in ['NR', 'NAAM', 'RING', 'NOM', 'BAGUE', 'VITESSE', 'SNELH']):
            print(f"  -> Skipping column header")
            i += 1
            continue
            
        # Parse race result lines (starts with a number)
        if line and current_race and re.match(r'^\s*\d+', line):
            print(f"  -> Processing race result line")
            parts = line.split()
            print(f"     Parts: {parts}")
            if len(parts) >= 7:  # Minimum required fields
                try:
                    position = int(parts[0])
                    print(f"     Position: {position}")
                    
                    # Find ring number pattern
                    ring_idx = -1
                    ring_number = ""
                    
                    for j, part in enumerate(parts):
                        if re.match(r'^[A-Z]{2}\s*\d{6,9}', part) or (len(part) == 2 and part.isupper() and j + 1 < len(parts) and parts[j + 1].isdigit()):
                            ring_idx = j
                            if j + 1 < len(parts) and parts[j + 1].isdigit():
                                ring_number = f"{part}{parts[j + 1]}"
                            else:
                                ring_number = part
                            break
                    
                    ring_number = ring_number.replace(' ', '').strip()
                    print(f"     Ring number: '{ring_number}' at index {ring_idx}")
                    
                    if not ring_number:
                        print(f"     WARNING: Could not extract ring number")
                        i += 1
                        continue
                    
                    owner_name = ""
                    if ring_idx > 1:
                        owner_name = ' '.join(parts[1:ring_idx]).replace('-', ' ')
                    
                    print(f"     Owner: '{owner_name}'")
                    
                    if ring_number and owner_name:
                        result = {
                            'ring_number': ring_number,
                            'owner_name': owner_name.strip(),
                            'position': position,
                        }
                        current_results.append(result)
                        print(f"     ✅ ADDED RESULT: {result}")
                    else:
                        print(f"     ❌ SKIPPED - missing ring_number or owner_name")
                        
                except (ValueError, IndexError) as e:
                    print(f"     ERROR: {str(e)}")
            else:
                print(f"     Not enough parts: {len(parts)} < 7")
        else:
            print(f"  -> Not a race result line (no race or doesn't start with number)")
        
        i += 1
    
    # Add the last race
    if current_race and current_results:
        races.append({
            'race': current_race,
            'results': current_results
        })
    
    return {'races': races}

# Test with the actual file
with open('/app/test_race_results.txt', 'r') as f:
    content = f.read()

print("=== PARSING TEST FILE ===")
result = parse_race_file(content)

print(f"\n=== FINAL RESULTS ===")
print(f"Found {len(result['races'])} races")
for i, race_data in enumerate(result['races']):
    race = race_data['race']
    results = race_data['results']
    print(f"Race {i+1}: {race['race_name']} - {len(results)} results")
    for j, res in enumerate(results):
        print(f"  {j+1}. Ring: {res['ring_number']}, Owner: {res['owner_name']}, Position: {res['position']}")