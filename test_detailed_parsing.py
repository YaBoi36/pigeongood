#!/usr/bin/env python3

import re

def test_parsing_logic():
    # Simulate the exact parsing logic from the backend
    test_lines = [
        "   1 290908-05 LARBIE - LUYTEN       HEUSDEN 27  5   89037 BE 501516325 14.14470 1190.5995    1",
        "   2 290908-05 LARBIE - LUYTEN       HEUSDEN 27 16       2 BE 501516025 14.14480 1190.3342    2", 
        "   3 193824-18 DAS JOS               LUMMEN  15 13   85202 BE 501120725 14.12040 1182.2664    3"
    ]
    
    current_results = []
    
    for line in test_lines:
        line = line.strip()
        print(f"\n=== Processing: {line} ===")
        
        if line and re.match(r'^\s*\d+', line):
            parts = line.split()
            print(f"Parts: {parts}")
            
            if len(parts) >= 7:
                try:
                    position = int(parts[0])
                    print(f"Position: {position}")
                    
                    # Extract owner name (typically parts 2-3 or 2-4)
                    owner_name = ""
                    city = ""
                    ring_number = ""
                    distance = 0
                    time = ""
                    speed = 0.0
                    
                    # Find ring number pattern (country code + number) and normalize it
                    ring_idx = -1
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
                    print(f"Ring number: '{ring_number}' at index {ring_idx}")
                    
                    if not ring_number:
                        print(f"WARNING: Could not extract ring number from line: {line[:100]}")
                        continue
                    
                    if ring_idx > 1:
                        # Owner name is before ring number
                        owner_name = ' '.join(parts[1:ring_idx]).replace('-', ' ')
                        # City might be right after owner name
                        if ring_idx > 2:
                            city = parts[ring_idx - 1]
                    
                    print(f"Owner name: '{owner_name}'")
                    print(f"City: '{city}'")
                    
                    # Extract distance, time, and speed from remaining parts
                    for part in parts[ring_idx + 2:]:  # Skip ring number parts
                        if part.isdigit() and len(part) >= 4:  # Distance (meters)
                            distance = int(part)
                        elif re.match(r'\d{2}\.\d{4,5}', part):  # Time format
                            time = part
                        elif re.match(r'\d+\.\d+', part):  # Speed (decimal)
                            try:
                                speed_val = float(part)
                                if speed_val > 100:  # Reasonable speed threshold
                                    speed = speed_val
                            except ValueError:
                                pass
                    
                    print(f"Distance: {distance}, Time: {time}, Speed: {speed}")
                    
                    # Calculate coefficient
                    total_pigeons = 357  # From the race header
                    actual_total_pigeons = min(total_pigeons, 5000)
                    coefficient = (position * 100) / actual_total_pigeons
                    
                    print(f"Coefficient: {coefficient}")
                    
                    if ring_number and owner_name:  # Only add if we have essential data
                        result = {
                            'ring_number': ring_number.replace(' ', ''),
                            'owner_name': owner_name.strip(),
                            'city': city.strip(),
                            'position': position,
                            'distance': distance if distance > 0 else 85000,  # Default distance
                            'time': time or "14:00:00",
                            'speed': speed if speed > 0 else 1000.0,  # Default speed
                            'coefficient': coefficient
                        }
                        current_results.append(result)
                        print(f"✅ ADDED RESULT: {result}")
                    else:
                        print(f"❌ SKIPPED - ring_number: '{ring_number}', owner_name: '{owner_name}'")
                        
                except (ValueError, IndexError) as e:
                    print(f"ERROR parsing line: {line[:50]}... - {str(e)}")
                    pass
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Total results: {len(current_results)}")
    for i, result in enumerate(current_results):
        print(f"{i+1}. Ring: {result['ring_number']}, Owner: {result['owner_name']}")

if __name__ == "__main__":
    test_parsing_logic()