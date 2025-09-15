import json
import os

OPERATOR_PATH = os.environ.get("OPERATOR_DB_JSON_PATH")
AVATAR_PATH = os.environ.get("AVATAR_PATH")
E2_AVATAR_PATH = os.environ.get("AVATAR_E2_PATH")

with open(OPERATOR_PATH, 'r', encoding="utf-8") as f:
    char_data = json.load(f)

    existing = {}

    for info in char_data.values():
        existing[info['charId']] = info['rarity']

    found_ops = 0
    threestars = 0
    twostars = 0
    onestars = 0

    directory = os.fsencode(AVATAR_PATH)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        if not os.path.isfile(AVATAR_PATH + filename):
            continue

        # If webp we've converted it already
        if filename.endswith(".webp"):
            charId = filename.replace('.webp', '')
            if charId in existing:
                if existing[charId] == 3:
                    threestars += 1
                elif existing[charId] == 2:
                    twostars += 1
                elif existing[charId] == 1:
                    onestars += 1

            found_ops += 1
            continue

        # Skip the essential files we need to run this script
        if filename.endswith(".exe") or filename.endswith(".sh"):
            continue

        # not a character so we skip
        if not filename.startswith("char"):
            os.remove(AVATAR_PATH + filename)
        elif not filename.endswith('_2.png'):
            charId = filename.replace('.webp', '')
            if charId in existing:
                if existing[charId] == 3:
                    threestars += 1
                elif existing[charId] == 2:
                    twostars += 1
                elif existing[charId] == 1:
                    onestars += 1
                else:
                    print('deleting non e2 art ' + filename)
                    os.remove(AVATAR_PATH + filename)
            else:
                print('deleting operator skin' + filename)
                os.remove(AVATAR_PATH + filename)
        else:
            found_ops += 1

    print("Into elite 2 ##################################")

    eliteDirectory = os.fsencode(E2_AVATAR_PATH)

    for file in os.listdir(eliteDirectory):
        filename = os.fsdecode(file)

        if not os.path.isfile(E2_AVATAR_PATH + filename):
            continue

        if filename.endswith(".webp"):
            found_ops += 1
            continue
        if filename.endswith(".exe") or filename.endswith(".sh"):
            continue
        if not filename.startswith("char"):
            os.remove(E2_AVATAR_PATH + filename)
        elif not filename.endswith('_2.png'):
            print('deleting operator skin' + filename)
            os.remove(E2_AVATAR_PATH + filename)
        else:
            found_ops += 1

    print(str(found_ops) + ' total operator avatars found vs ' + str(len(existing)) + ' operators in db')
    print(str(threestars) + ' three stars ' + str(twostars) + ' two stars ' + str(onestars) + ' one stars')
    