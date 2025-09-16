# Add all avatars into list

# Go through all ops and remove from db

# Make sure no one is left

import json
import os
import pprint

OPERATOR_PATH = "./operator_db/operator_db.json"
AVATAR_PATH = "./assets/dyn/arts/charavatars/"
E2_AVATAR_PATH = "./assets/dyn/arts/charavatars/elite/"

with open(OPERATOR_PATH, 'r', encoding="utf-8") as f:
    char_data = json.load(f)

    existing = []
    icons = 0

    for info in char_data.values():
        existing.append(info['charId'])
    
    total_op_db = len(existing)

    print(str(len(existing)) + " Operators in operator_db.json")

    for file in os.listdir(os.fsencode(AVATAR_PATH)) + os.listdir(os.fsencode(E2_AVATAR_PATH)):
        filename = os.fsdecode(file)
        if filename.endswith(".webp"):
            # 5 or 6 star with E2 art
            if filename.endswith("_2.webp"):
                filename = filename.replace("_2.webp", "")
            else:
                filename = filename.replace(".webp", "")
            icons += 1
        else:
            continue

        try:
            existing.remove(filename)
        except:
            print("Operator in avatar does not exist in database: " + filename)
    
    print("\n"+str(len(existing)) + " Operators exist in database without an avatar (total " + str(total_op_db) + ")")
    print(str(icons) + " Icons in avatars")
    print(str(abs(total_op_db - icons)) + " discrepancy (2 is due to guardmiya and then healermiya)")
    pprint.pp(existing)
