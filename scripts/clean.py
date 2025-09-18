import json
import os
import pprint
import shutil

OPERATOR_PATH = "./operator_db/operator_db.json"
AVATAR_PATH = "./assets/dyn/arts/charavatars/"
E2_AVATAR_PATH = "./assets/dyn/arts/charavatars/elite/"

existing_set = []

def removeFromExisting(charId):
    try:
        existing_set.remove(charId)
    except:
        print(f"Could not remove {charId} from existing operator set")

# Check if the charId is an existing operator in the set
def validateExisitingOp(charId):
    return charId in existing_set

def moveOperators():
    directory = os.fsencode(AVATAR_PATH)
    
    print(f"//////////////////// Moving operators in {AVATAR_PATH} ////////////////////")

    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        if not os.path.isfile(AVATAR_PATH + filename):
            continue

        # Skip the essential files we need to run this script
        if not filename.endswith(".png"):
            continue

        if not filename.endswith("_2.png"):
            continue

        # This means the e2 icon is in the wrong directory, we should move it to the correct one.
        print(f"Moving e2 art {filename} to the elite directory")
        shutil.copy(AVATAR_PATH + filename, E2_AVATAR_PATH)

with open(OPERATOR_PATH, 'r', encoding="utf-8") as f:
    char_data = json.load(f)

    existing = {}

    for info in char_data.values():
        existing[info['charId']] = info['rarity']
        existing_set.append(info['charId'])

    found_ops = 0
    threestars = 0
    twostars = 0
    onestars = 0

    moveOperators()

    directory = os.fsencode(AVATAR_PATH)
    
    print(f"//////////////////// Parsing {AVATAR_PATH} ////////////////////")

    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        if not os.path.isfile(AVATAR_PATH + filename):
            continue

        # Skip the essential files we need to run this script
        if not filename.endswith(".png"):
            continue

        # Not a character so we skip
        if not filename.startswith("char"):
            os.remove(AVATAR_PATH + filename)
            continue

        # Check if the operator is a 3, 2 or 1 star operator.
        if not filename.endswith('_2.png'):
            charId = filename.replace('.png', '')

            # If the character exists and they are not a 3, 2 or 1 star then delete their non-e2 art
            if charId in existing:
                if existing[charId] == 3:
                    threestars += 1
                    removeFromExisting(charId)
                elif existing[charId] == 2:
                    twostars += 1
                    removeFromExisting(charId)
                elif existing[charId] == 1:
                    onestars += 1
                    removeFromExisting(charId)
                else:
                    print(f'deleting non e2 art {filename}')
                    os.remove(AVATAR_PATH + filename)
            else:
                print(f'deleting operator not in db {filename}')
                os.remove(AVATAR_PATH + filename)

            continue

        # Icon is an e2 icon
        charId = filename.replace('_2.png', '')

        # IS borrow operators are "elite" but arent "real" characters
        if not validateExisitingOp(charId):
            print(f'deleting IS operator {filename}')
            os.remove(AVATAR_PATH + filename)

            continue

        raise ValueError("Operators should be in the correct directory")
        

    print(f"//////////////////// Parsing {E2_AVATAR_PATH} ////////////////////")

    eliteDirectory = os.fsencode(E2_AVATAR_PATH)

    for file in os.listdir(eliteDirectory):
        filename = os.fsdecode(file)

        # If file doesnt exist
        if not os.path.isfile(E2_AVATAR_PATH + filename):
            continue

        # If file is not a png
        if not filename.endswith(".png"):
            continue 

        # If the file is not a character
        if not filename.startswith("char"):
            os.remove(E2_AVATAR_PATH + filename)
            continue

        # If the image file is not an elite operator (they should be because its in the elite folder)
        if not filename.endswith('_2.png'):
            print(f'deleting operator in e2 directory {filename}')
            os.remove(E2_AVATAR_PATH + filename)
            continue
        
        charId = filename.replace('_2.png', '')

        # Check if the character is an existing operator
        if not validateExisitingOp(charId):
            try:
                print(f'deleting other op {filename}')
                os.remove(E2_AVATAR_PATH + filename)
            except:
                # Special case where we have a bunch of amiya versions but they arent different units
                print(f'Could not remove op {filename}')

            continue

        found_ops += 1
        removeFromExisting(charId)

    print(f'{found_ops + threestars + twostars + onestars} total operator avatars found vs {len(existing)} operators in db')
    print(f'{threestars} three stars {twostars} two stars {onestars} one stars')
    pprint.pp(existing_set)
    