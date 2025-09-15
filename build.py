import json
from pprint import pprint 
from alias import aliases
import os
import shutil

INFECTED_INDEX = 8
OPERATOR_PATH = os.environ.get("OPERATOR_DB_JSON_PATH")
OLD_OPERATOR_PATH = os.environ.get("OLD_OPERATOR_DB_JSON_PATH")
RAW_DATA_PATH = os.environ.get("RAW_DATA_PATH")

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

def handleRaceCases(race):
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

    return race

def ignoreISOps(name):
    if name == "Pith" or name == "Sharp" or name == "Stormeye" or name == "Touch" or name == "Tulip":
        return True

    return False

def updatePreviousOldVersion():
    print("Attempting to overwrite old db file")
    try: 
        shutil.copyfile(OPERATOR_PATH, OLD_OPERATOR_PATH)
        print("Successfully rewrote old file")
    except Exception as e:
        print(f"Unexpected error : {e}")

# From AI search results
def find_first_matching_file_os(directory_path, start_string):
    print(f"Attempting to find first matching file for {directory_path} file name {start_string}")
    try:
        for filename in os.listdir(directory_path):
            if filename.startswith(start_string):
                print(f"Found matching file {filename}")
                return os.path.join(directory_path, filename)
        return None
    except FileNotFoundError:
        print(f"Error: Directory '{directory_path}' not found.")
        return None

# From AI search results
def read_bytes_file_to_json(file_path):
    print(f"Attempting to read file bytes to json {file_path}")
    try:
        with open(file_path, 'rb') as f:  # Open in binary read mode ('rb')
            byte_data = f.read()
        
        # Decode the bytes into a UTF-8 string
        decoded_string = byte_data.decode('utf-8')
        
        # Parse the JSON string into a Python dictionary
        json_data = json.loads(decoded_string)
        
        print("Successfully decoded file")
        return json_data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file: {e}")
        return None
    except UnicodeDecodeError as e:
        print(f"Error decoding bytes to string: {e}. Ensure the correct encoding is used.")
        return None

def main():
    print(f"Environment variables: RAW_DATA_PATH {RAW_DATA_PATH} OLD_OPERATOR_PATH {OLD_OPERATOR_PATH} OPERATOR_PATH {OPERATOR_PATH}")
    
    updatePreviousOldVersion()

    ignored = []
    nations = set()
    races = set()
    groups = set()
    new = []

    char_data = read_bytes_file_to_json(find_first_matching_file_os(RAW_DATA_PATH, 'character_table'))
    profile_data = read_bytes_file_to_json(find_first_matching_file_os(RAW_DATA_PATH, 'handbook_info_tables'))

    with open(OLD_OPERATOR_PATH, 'r', encoding="utf-8") as f:
        old_operators = json.load(f)

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

        if ignoreISOps(name):
            ignored.append(name)
            continue
        
        infected = get_infected_status(profile_info, name)
        gender = profile_info[1].split(']')[1].strip()
        race = handleRaceCases(profile_info[5].split(']')[1].strip())
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
            new.append(id)

        races.add(race)
        groups.add(group)
        nations.add(nation)

    # pprint(operators)
    # Shalem has 2 entries
    print("Ignored operators: " + str(len(ignored)))
    print(ignored)
    print(str(len(nations)) + ' unique nations')
    print(sorted(nations))
    print(str(len(races)) + ' unique races')
    print(sorted(races))
    print(str(len(groups)) + ' unique groups')
    print(sorted(groups))
    print(str(len(new)) + ' new operators')
    print(sorted(new))
    print(str(len(old_operators)) + ' old operators vs ' + str(len(operators)) + ' new operators')

    missing_alias = []
    for alias in aliases:
        try:
            operators[alias]["alias"] = aliases[alias]
        except:
            missing_alias.append(alias)
    
    print(str(len(aliases) - len(missing_alias)) + ' aliases added, missing ' + str(len(missing_alias)))
    pprint(sorted(missing_alias))

    with open(OPERATOR_PATH, 'w', encoding='utf-8') as f:
        json.dump(operators, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
