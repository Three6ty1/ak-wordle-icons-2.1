import json
from pprint import pprint 
from alias import aliases
import shutil
import sys

OPERATOR_PATH = "./operator_db/operator_db.json"
OLD_OPERATOR_DB_PATH = "./operator_db/old_operator_db.json"
HANDBOOK_INFO_TABLE_PATH = "./source_json/handbook_info_table.json"
CHARACTER_TABLE_PATH = "./source_json/character_table.json"

def get_profile_info(profile_data, id):
    # find entry in profile data
    # char id > story text audio > first > stories > story text > codename etc.
    # ['[Code Name] ', '[Gender] ', '[Combat Experience] ', '[Place of Birth] ', '[Date of Birth] ', '[Race] ', '[Height] '
    return profile_data[id]["storyTextAudio"][0]["stories"][0]["storyText"].split('\n')

def get_infected_status(profile_info, name):
    infected_msg = ' '.join(profile_info[8:]).strip().lower()

    if infected_msg == '':
        infected_msg = ' '.join(profile_info[7:]).strip().lower()

    if "no infection" in infected_msg or "uninfected" in infected_msg or "non-infected" in infected_msg:
        infected = "No"
    elif "infection confirmed" in infected_msg or "confirmed infected" in infected_msg:
        infected = "Yes"
    else:
        # Outliers
        # Weird wording for first few
        if name == "Fang" or name == "Ptilopsis" or name == "Schwarz" or name == "Specter":
            infected = "Yes"
        # Ch'en being infected is spoilers so its unknown in her entry
        elif name == "Nian" or name == "Ch'en":
            infected = "Undisclosed"
        else: # Robots
            infected = "N/A"

    return infected

def get_group(info):
    group = "None" if info["groupId"] == None else info["groupId"]
    team = "Ægir" if info["teamId"] == "egir" else ("None" if info["teamId"] == None else info["teamId"])

    if team == "Ægir":
        print(info["name"])

    # if group then no team. If team then no group.
    if group != "None":
        group = group
    elif team != "None":
        group = team
    else:
        return ''

    group = group.strip().lower()

    # Format
    if group == "student":
        group = "Ursus Student Self-Governing Group"
    elif group == "lee":
        group = "Lee's Detective Agency"
    elif group == "penguin":
        group = "Penguin Logistics"    
    elif group == "rainbow":
        group = "Team Rainbow" 
    elif group == "lgd":
        group = "LGD"
    elif group == "abyssal":
        group = "Abyssal Hunters"
    elif group == "rhine":
        group = "Rhine Lab"
    elif group == "elite":
        group = "Elite Operators"
    elif group == "action4":
        group = "Action 4"
    elif group == "karlan":
        group = "Karlan Trade"
    elif group == "chiave":
        group = "Chiave's Gang"
    elif group == "pinus":
        group = "Pinus Sylvestris"
    elif group == "sweep":
        group = "S.W.E.E.P."
    elif group == "blacksteel":
        group = "Blacksteel Worldwide"
    elif "reserve" in group:
        group = "Reserve " + group[-1]
    elif group == "laios":
        group = "Laios' Party"
    else:
        group = group.capitalize()

    return group

def get_nation(info):
    nation = info["nationId"]
    
    if nation == None:
        nation = "None"
    elif nation == "rhodes":
        nation = "Rhodes Island"
    elif nation == "rim":
        nation = "Rim Billiton"
    elif nation == "egir":
        nation = 'Ægir'
    elif nation == "bolivar":
        nation = "Bolívar"
    else:
        nation = nation.capitalize()

    return nation

def get_class(info):
    _class = info["profession"].lower()
    if _class == "pioneer":
        _class = "Vanguard"
    elif _class == "tank":
        _class = "Defender"
    elif _class == "warrior":
        _class = "Guard"
    elif _class == "special":
        _class = "Specialist"
    elif _class == "support":
        _class = "Supporter"
    else:
        _class = _class.lower().capitalize()

    return _class

def handle_race_cases(race: str):
    if "unknown" in race.lower() or "undisclosed" in race.lower(): # afaik, Ch'en and Nian special case
        race = "Unknown/Undisclosed"
    elif any(char.isdigit() for char in race): # Robots special case
        race = "Robot"
    elif race == 'Cautus/Chimera': # Amiya Special case
        race = 'Chimera'
    elif race == "Pythia": # Serpents diferent name case
        race = "Phidia"
    elif race == "Rebbah": # Hyena diferent name case
        race = "Reproba"
    elif "Self-declared" in race: # Danmeshi collab <3 example: "Half-foot (Self-declared)"
        race = race.replace(" (Self-declared)", "")

    return race

# Need this to stop them from getting built into the DB since they are operators with profiles
def ignore_is_ops(name):
    if name == "Pith" or name == "Sharp" or name == "Stormeye" or name == "Touch" or name == "Tulip":
        return True

    return False

def update_previous_old_db():
    print("Attempting to overwrite old db file")
    try: 
        shutil.copyfile(OPERATOR_PATH, OLD_OPERATOR_DB_PATH)
        print("Successfully rewrote old file")
    except Exception as e:
        print(f"Old file doesn't exist/Unexpected error : {e}")

def get_old_info(oldOperators):
    info = {
        "nations": set(),
        "races": set(),
        "groups": set(),
    }

    for operator in oldOperators.values():
        info["nations"].add(operator["nation"])
        info["races"].add(operator["race"])
        info["groups"].add(operator["group"])

    res = {
        "nations": sorted(list(info["nations"])),
        "races": sorted(list(info["races"])),
        "groups": sorted(list(info["groups"]))
    }

    print(res)

    return res

def print_result(ignored, nations, old_info, races, groups, new, old_operators, operators, missing_alias):
    print("//////////////////////////////////////////////////")
    print("Ignored operators: " + str(len(ignored)))
    print(ignored)
    print("//////////////////////////////////////////////////")
    print(str(len(nations)) + ' unique nations')
    print(sorted(nations))
    print(f"Compared to {len(old_info['nations'])} old nations")
    print(old_info["nations"])
    print("//////////////////////////////////////////////////")
    print(str(len(races)) + ' unique races')
    print(sorted(races))
    print(f"Compared to {len(old_info["races"])} old races")
    print(old_info["races"])
    print("//////////////////////////////////////////////////")
    print(str(len(groups)) + ' unique groups')
    print(sorted(groups))
    print(f"Compared to {len(old_info['groups'])} old groups")
    print(old_info["groups"])
    print("//////////////////////////////////////////////////")
    print(str(len(new)) + ' new operators')
    print(sorted(new, key=lambda x: (x[1], x[0])))
    print("//////////////////////////////////////////////////")
    print(str(len(old_operators)) + ' old operators vs ' + str(len(operators)) + ' new operators')
    print(str(len(aliases) - len(missing_alias)) + ' aliases added, missing ' + str(len(missing_alias)))
    pprint(sorted(missing_alias))

def main():
    if sys.argv[0] == "true":
        print("Replacing old version flag set to true, updating old file")
        update_previous_old_db()
    else:
        print("Replacing old version flag is empty/false, skipping old file update")

    ignored = []
    nations = set()
    races = set()
    groups = set()
    new = []

    with open(CHARACTER_TABLE_PATH, 'r', encoding="utf-8") as f:
        char_data = json.load(f)

        with open(HANDBOOK_INFO_TABLE_PATH, 'r', encoding="utf-8") as ff:
            profile_data = json.load(ff)["handbookDict"]

            with open(OLD_OPERATOR_DB_PATH, 'r', encoding="utf-8") as fff:
                old_operators = json.load(fff)

    operators = {}

    for id, info in char_data.items():
        name = info["name"]

        if not id.startswith('char'):
            continue
        
        try:
            profile_info = get_profile_info(profile_data, id)
        except:
            ignored.append(name)
            continue

        if ignore_is_ops(name):
            ignored.append(name)
            continue
        
        infected = get_infected_status(profile_info, name)
        gender = profile_info[1].split(']')[1].strip()
        race = handle_race_cases(profile_info[5].split(']')[1].strip())
        group = get_group(info)
        nation = get_nation(info)
        position = info["position"].lower().capitalize()

        profession = get_class(info)
        archetype = info["subProfessionId"].capitalize()
        rarity = int(info["rarity"][-1])
        e0_cost = info["phases"][0]["attributesKeyFrames"][0]["data"]["cost"]
        e2_cost = info["phases"][-1]["attributesKeyFrames"][0]["data"]["cost"]

        operators[name] = {
            "charId": id,
            "alias": [],
            "gender": gender,
            "race": race,
            "group": group,
            "nation": nation,
            "position": position,
            "profession": profession,
            "archetype": archetype,
            "rarity": rarity,
            "cost": (e0_cost, e2_cost),
            "infected": infected,
        }

        if not name in old_operators:
            print("New operator: " + name)
            new.append([id, rarity])

        races.add(race)
        groups.add(group)
        nations.add(nation)

    old_info = get_old_info(old_operators)

    missing_alias = []
    for alias in aliases:
        try:
            operators[alias]["alias"] = aliases[alias]
        except:
            missing_alias.append(alias)
    
    print_result(ignored, nations, old_info, races, groups, new, old_operators, operators, missing_alias)

    with open(OPERATOR_PATH, 'w', encoding='utf-8') as f:
        json.dump(operators, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
