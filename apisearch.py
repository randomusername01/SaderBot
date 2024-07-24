import requests
import toml

config = toml.load("config.toml")

TOKEN = config["discord"]["bot_token"]
API_KEY = config["api"]["apikey"]

def get_character_id(character_name):
    api_url = f"https://api.dfoneople.com/df/servers/cain/characters?characterName={character_name}&wordType=match&apikey={API_KEY}"

    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()

        if "rows" in data and len(data["rows"]) > 0:
            character_id = data["rows"][0].get("characterId", "No characterId found")
            return character_id
        else:
            return "No character found"
    else:
        return f"Failed to fetch data from the API. Status code: {response.status_code}"

def get_character_status(character_id):
    api_url = f"https://api.dfoneople.com/df/servers/cain/characters/{character_id}/status?apikey={API_KEY}"

    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()

        character_stats = {
            "Buff Power": 0,
            "Strength": 0,
            "Intelligence": 0,
            "Vitality": 0,
            "Spirit": 0,
        }

        for stat in data.get("status", []):
            if stat["name"] == "Buff Power":
                character_stats["Buff Power"] = stat["value"]

        for stat in data.get("status", []):
            if stat["name"] in character_stats and stat["value"] > 0:
                character_stats[stat["name"]] = max(
                    character_stats[stat["name"]], stat["value"]
                )

        for buff in data.get("buff", []):
            for stat in buff.get("status", []):
                if stat["name"] in character_stats and stat["value"] > 0:
                    character_stats[stat["name"]] = max(
                        character_stats[stat["name"]], stat["value"]
                    )

        return character_stats
    else:
        return f"Failed to fetch data from the API. Status code: {response.status_code}"

def get_character_equipment(character_id):
    api_url = f"https://api.dfoneople.com/df/servers/cain/characters/{character_id}/equip/equipment?apikey={API_KEY}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        return data.get("equipment", [])
    else:
        raise Exception(
            f"Failed to fetch data from the API. Status code: {response.status_code}"
        )

def get_character_avatar(character_id):
    api_url = f"https://api.dfoneople.com/df/servers/cain/characters/{character_id}/equip/avatar?apikey={API_KEY}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("avatar", [])
    else:
        raise Exception(
            f"Failed to fetch data from the API. Status code: {response.status_code}"
        )

def get_buff_avatar(character_id):
    api_url = f"https://api.dfoneople.com/df/servers/cain/characters/{character_id}/skill/buff/equip/avatar?apikey={API_KEY}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        if "avatar" in data:
            return [avatar['slotId'] for avatar in data["avatar"]]
        return []
    else:
        raise Exception(
            f"Failed to fetch data from the API. Status code: {response.status_code}"
        )

def get_character_creature(character_id):
    api_url = f"https://api.dfoneople.com/df/servers/cain/characters/{character_id}/equip/creature?apikey={API_KEY}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        return data.get("creature", [])
    else:
        raise Exception(
            f"Failed to fetch data from the API. Status code: {response.status_code}"
        )

def get_buff_creature(character_id):
    api_url = f"https://api.dfoneople.com/df/servers/cain/characters/{character_id}/skill/buff/equip/creature?apikey={API_KEY}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        return data.get("itemId")
    else:
        raise Exception(
            f"Failed to fetch data from the API. Status code: {response.status_code}"
        )

def get_item_details(item_id):
    api_url = f"https://api.dfoneople.com/df/items/{item_id}?apikey={API_KEY}"
    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Failed to fetch data from the API. Status code: {response.status_code}"
        )

def normalize_string(s):
    return " ".join(s.lower().split())

def search_in_json(data, TEXT_TO_SKILL_BONUS_MAPPING, counters, in_fixed_option=False):
    matches = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key == "fixedOption":
                matches.extend(
                    search_in_json(
                        value,
                        TEXT_TO_SKILL_BONUS_MAPPING,
                        counters,
                        in_fixed_option=True,
                    )
                )
            elif key == "enchant":
                for term in TEXT_TO_SKILL_BONUS_MAPPING:
                    if normalize_string(term) in normalize_string(str(value)):
                        matches.append((term, TEXT_TO_SKILL_BONUS_MAPPING[term]))
                        counters[term] += 1
            elif isinstance(value, (dict, list)):
                matches.extend(
                    search_in_json(
                        value, TEXT_TO_SKILL_BONUS_MAPPING, counters, in_fixed_option
                    )
                )
            elif in_fixed_option and key == "explainDetail":
                for term in TEXT_TO_SKILL_BONUS_MAPPING:
                    if normalize_string(term) in normalize_string(str(value)):
                        matches.append((term, TEXT_TO_SKILL_BONUS_MAPPING[term]))
                        counters[term] += 1
            elif not in_fixed_option:
                for term in TEXT_TO_SKILL_BONUS_MAPPING:
                    if normalize_string(term) in normalize_string(str(value)):
                        matches.append((term, TEXT_TO_SKILL_BONUS_MAPPING[term]))
                        counters[term] += 1
    elif isinstance(data, list):
        for item in data:
            matches.extend(
                search_in_json(
                    item, TEXT_TO_SKILL_BONUS_MAPPING, counters, in_fixed_option
                )
            )

    return matches

def search_items(character_id, TEXT_TO_SKILL_BONUS_MAPPING):
    equipment = get_character_equipment(character_id)
    avatar = get_character_avatar(character_id)
    buff_avatars = get_buff_avatar(character_id)
    matched_items = []
    counters = {term: 0 for term in TEXT_TO_SKILL_BONUS_MAPPING}
    
    for item in equipment:
        item_id = item.get('itemId')
        if item_id:
            if 'enchant' in item:
                search_in_json(item['enchant'], TEXT_TO_SKILL_BONUS_MAPPING, counters)
            item_details = get_item_details(item_id)
            matches = search_in_json(item_details, TEXT_TO_SKILL_BONUS_MAPPING, counters)
            if matches:
                matched_items.append({
                    'itemName': item.get('itemName'),
                    'itemDescription': item_details,
                    'matches': matches
                })
    
    for item in avatar:
        if item['slotId'] not in buff_avatars:
            if 'enchant' in item:
                search_in_json(item['enchant'], TEXT_TO_SKILL_BONUS_MAPPING, counters)
            matches = search_in_json(item, TEXT_TO_SKILL_BONUS_MAPPING, counters)
            if matches:
                matched_items.append({
                    'itemName': item.get('itemName'),
                    'itemDescription': item,
                    'matches': matches
                })
    
    return matched_items, counters


TEXT_TO_SKILL_BONUS_MAPPING = {
    "Lv. 30 Buff Skill Levels +1": [(30, 1, "both")],
    "Lv. 50 Active skill levels +1": [(50, 1, "both")],
    "Lv. 50 Active skill levels +2": [(50, 2, "both")],
    "Lv. 1 - 25 skill levels +2": [
        (1, 2, "both"),
        (5, 2, "both"),
        (10, 2, "both"),
        (15, 2, "both"),
        (20, 2, "both"),
        (25, 2, "both"),
    ],
    "Lv. 1 - 100 skill levels +2": [
        (1, 2, "both"),
        (5, 2, "both"),
        (10, 2, "both"),
        (15, 2, "both"),
        (20, 2, "both"),
        (25, 2, "both"),
        (30, 2, "both"),
        (35, 2, "both"),
        (40, 2, "both"),
        (45, 2, "both"),
        (48, 2, "both"),
        (50, 2, "both"),
        (60, 2, "both"),
        (70, 2, "both"),
        (75, 2, "both"),
        (80, 2, "both"),
        (85, 2, "both"),
        (95, 2, "both"),
        (100, 2, "both"),
    ],
    "Puppeteer": [(15, 3, "both")],
    "Divine Invocation": [(30, 1, "active")],
    "Forbidden Curse Skill Lv +1": [(30, 1, "active")],
    "Lovely Tempo Skill Lv +1": [(30, 1, "active")],
    "Valor Blessing Skill Lv +1": [(30, 1, "active")],
}

character_name = "DrProfessor"
character_id = get_character_id(character_name)
character_status = get_character_status(character_id)
equipment = get_character_equipment(character_id)
matched_items, counters = search_items(character_id, TEXT_TO_SKILL_BONUS_MAPPING)
item_detail = get_item_details("e32b3fff2b80149f792fc24a1b8d4fb4")

print(f"Character ID for {character_name}: {character_id}")

print("Occurrences:")
for term, count in counters.items():
    print(f"{term}: {count} times")
