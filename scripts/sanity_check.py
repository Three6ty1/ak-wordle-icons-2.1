# Add all avatars into list

# Go through all ops and remove from db

# Make sure no one is left

import json
import os
import pprint

OPERATOR_PATH = "./operator_db/operator_db.json"
AVATAR_PATH = "./assets/dyn/arts/charavatars/"
E2_AVATAR_PATH = "./assets/dyn/arts/charavatars/elite/"

def try_removing_from_existing_set(charId):
    try:
        existing.remove(charId)
    except:
        print("Operator in avatar does not exist in database: " + charId)

def try_removing_from_png_set(charId):
    try:
        existing_png.remove(charId)
    except:
        print("Operator png in avatar does not exist in database: " + charId)

with open(OPERATOR_PATH, 'r', encoding="utf-8") as f:
    char_data = json.load(f)

    existing = []
    icons = 0
    existing_png = []
    icons_png = 0

    out_of_place = []
    e2_out_of_place = []

    for info in char_data.values():
        existing.append(info['charId'])
        existing_png.append(info['charId'])
    
    total_op_db = len(existing)

    for file in os.listdir(os.fsencode(AVATAR_PATH)):
        filename = os.fsdecode(file)

        if not os.path.isfile(AVATAR_PATH + filename):
            continue

        if filename.endswith(".png"):
            charId = filename.replace(".png", "")
            icons_png += 1
            try_removing_from_png_set(charId)
            continue

        charId = filename.replace(".webp", "")

        if filename.endswith("_2.webp"):
            e2_out_of_place.append(charId)
            # 5 or 6 star with E2 art

        icons += 1
        try_removing_from_existing_set(charId)

    for file in os.listdir(os.fsencode(E2_AVATAR_PATH)):
        filename = os.fsdecode(file)

        if not os.path.isfile(E2_AVATAR_PATH + filename):
            continue

        if filename.endswith(".png"):
            charId = filename.replace("_2.png", "")
            icons_png += 1
            try_removing_from_png_set(charId)
            continue

        charId = filename.replace("_2.webp", "")

        if not filename.endswith("_2.webp"):
            out_of_place.append(charId)

        icons += 1
        try_removing_from_existing_set(charId)
    
    print("\n"+str(len(existing)) + " Operators exist in database without an avatar (total " + str(total_op_db) + ")")
    print(str(icons) + " Icons in avatars")
    print(str(abs(total_op_db - icons)) + " discrepancy")
    pprint.pp(existing)

    print(str(icons_png) + " PNG Icons in avatars")
    print(str(total_op_db - icons_png) + " PNG discrepancy")
    pprint.pp(existing_png)

    print(f"E2 operators that are in the non-e2 directory {len(e2_out_of_place)}")
    pprint.pp(e2_out_of_place)
    print(f"Non e2 operators that are in the e2 directory {len(out_of_place)}")
    pprint.pp(out_of_place)

    assert len(existing) == 0, "There is a discrepancy between the operators in the DB and the converted icons"
    assert len(out_of_place) == 0 and len(e2_out_of_place) == 0, "There are misplaced icons in the wrong directory for certain e2 operators"
