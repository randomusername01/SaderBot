import requests
import toml

config = toml.load('config.toml')

TOKEN = config['discord']['bot_token']
API_KEY = config['api']['apikey']

def get_character_id(character_name):
    api_url = f'https://api.dfoneople.com/df/servers/cain/characters?characterName={character_name}&wordType=match&apikey={API_KEY}'
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'rows' in data and len(data['rows']) > 0:
            character_id = data['rows'][0].get('characterId', 'No characterId found')
            return character_id
        else:
            return 'No character found'
    else:
        return f'Failed to fetch data from the API. Status code: {response.status_code}'

def get_character_status(character_id):
    api_url = f'https://api.dfoneople.com/df/servers/cain/characters/{character_id}/status?apikey={API_KEY}'
    
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        
        character_stats = {
            "Buff Power": 0,
            "Strength": 0,
            "Intelligence": 0,
            "Vitality": 0,
            "Spirit": 0
        }

        for stat in data.get('status', []):
            if stat['name'] == 'Buff Power':
                character_stats['Buff Power'] = stat['value']

        for stat in data.get('status', []):
            if stat['name'] in character_stats and stat['value'] > 0:
                character_stats[stat['name']] = max(character_stats[stat['name']], stat['value'])

        for buff in data.get('buff', []):
            for stat in buff.get('status', []):
                if stat['name'] in character_stats and stat['value'] > 0:
                    character_stats[stat['name']] = max(character_stats[stat['name']], stat['value'])
        
        return character_stats
    else:
        return f'Failed to fetch data from the API. Status code: {response.status_code}'

character_name = 'CloudLight'
character_id = get_character_id(character_name)
character_status = get_character_status(character_id)
print(f'Character ID for {character_name}: {character_id}')
print(f'Character status: {character_status}')
