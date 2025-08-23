#!/usr/bin/env python3

import re

# Test the parsing logic on our specific lines
test_lines = [
    "   1 290908-05 LARBIE - LUYTEN       HEUSDEN 27  5   89037 BE 501516325 14.14470 1190.5995    1",
    "   2 290908-05 LARBIE - LUYTEN       HEUSDEN 27 16       2 BE 501516025 14.14480 1190.3342    2", 
    "   3 193824-18 DAS JOS               LUMMEN  15 13   85202 BE 501120725 14.12040 1182.2664    3"
]

for i, line in enumerate(test_lines, 1):
    print(f"\n=== Processing Line {i} ===")
    print(f"Line: {line}")
    
    parts = line.split()
    print(f"Parts ({len(parts)}): {parts}")
    
    if len(parts) >= 7:
        position = int(parts[0])
        print(f"Position: {position}")
        
        # Find ring number pattern
        ring_idx = -1
        ring_number = ""
        
        for j, part in enumerate(parts):
            print(f"  Part {j}: '{part}'")
            if re.match(r'^[A-Z]{2}\s*\d{6,9}', part):
                print(f"    Matches pattern 1: [A-Z]{{2}}\\s*\\d{{6,9}}")
                ring_idx = j
                ring_number = part
                break
            elif len(part) == 2 and part.isupper() and j + 1 < len(parts) and parts[j + 1].isdigit():
                print(f"    Matches pattern 2: 2-letter country code + next part is digit")
                ring_idx = j
                ring_number = f"{part}{parts[j + 1]}"
                break
        
        # Clean and normalize ring number
        ring_number = ring_number.replace(' ', '').strip()
        print(f"Ring number found: '{ring_number}' at index {ring_idx}")
        
        if ring_idx > 1:
            owner_name = ' '.join(parts[1:ring_idx]).replace('-', ' ')
            print(f"Owner name: '{owner_name}'")
        
        # Extract other fields
        for k, part in enumerate(parts[ring_idx + 2:], ring_idx + 2):
            print(f"  After ring part {k}: '{part}'")
            if part.isdigit() and len(part) >= 4:
                print(f"    Could be distance: {part}")
            elif re.match(r'\d{2}\.\d{4,5}', part):
                print(f"    Could be time: {part}")
            elif re.match(r'\d+\.\d+', part):
                try:
                    speed_val = float(part)
                    if speed_val > 100:
                        print(f"    Could be speed: {speed_val}")
                except ValueError:
                    pass
    else:
        print(f"Not enough parts: {len(parts)} < 7")