import requests
import json
import re
from datetime import datetime

def get_rotomlabs_slug(pokemon_name):
    """Convert Pokemon name to RotomLabs URL slug."""
    clean_name = re.sub(r'\([^)]*\)', '', pokemon_name).strip()
    
    special_mappings = {
        "Nidoran\u2640": "nidoran-f",
        "Nidoran\u2642": "nidoran-m",
        "Farfetch'd": "farfetch-d",
        "Mr. Mime": "mr-mime",
        "Type: Null": "type-null",
        "Flabébé": "flabebe",
        "Nidoran♀": "nidoran-f",
        "Nidoran♂": "nidoran-m",
        "Porygon2": "porygon2",
        "Porygon-Z": "porygon-z",
        "Ho-Oh": "ho-oh",
        "Mime Jr.": "mime-jr",
        "Sirfetch'd": "sirfetchd",
        "Mr. Rime": "mr-rime",
        "Castform Rainy": "castform-rainy",
        "Castform Sunny": "castform-sunny",
        "Castform Snowy": "castform-snowy",
        "Castform": "castform",
        "Cherrim Overcast Form": "cherrim-overcast",
        "Cherrim Sunny": "cherrim-sunshine",
        "Deerling Spring Form": "deerling-spring",
        "Sawsbuck Spring Form": "sawsbuck-spring",
        "Darmanitan Standard": "darmanitan-standard-mode",
        "Farfetch'd Galarian": "farfetch-d-galarian",
    }
    
    if clean_name in special_mappings:
        return special_mappings[clean_name]
    
    clean_name = clean_name.lower()
    clean_name = clean_name.replace("'", "")
    clean_name = clean_name.replace(" ", "-")
    clean_name = re.sub(r'[^a-z0-9-]', '', clean_name)
    clean_name = re.sub(r'-+', '-', clean_name)
    clean_name = clean_name.strip('-')
    
    return clean_name

def is_form_pokemon(pokemon_name):
    """Check if a Pokemon has a special form that should use RotomLabs image."""
    name_lower = pokemon_name.lower()
    
    form_indicators = [
        'alola', 'alolan', 'galarian', 'hisuian', 'paldea', 'paldean',
        'rainy', 'sunny', 'snowy',
        'overcast', 'sunshine',
        'heat', 'wash', 'frost', 'fan', 'mow',
        'baile', 'pom-pom', 'pau', 'sensu',
        'super', 'large', 'small', 'average',
        'blue flower', 'red flower', 'yellow flower', 'white flower', 'orange flower',
        'standard', 'zen',
        'origin', 'sky', 'therian', 'resolute', 'pirouette',
        'plant cloak', 'sandy cloak', 'trash cloak',
        'spring', 'summer', 'autumn', 'winter',
        '♀', '♂', "'", '.', ':',
    ]
    
    for indicator in form_indicators:
        if indicator in name_lower:
            return True
    return False

def get_pokemon_name_from_api(pokemon_id):
    """Fallback to PokeAPI for unknown Pokémon"""
    try:
        url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}/"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for name_entry in data.get('names', []):
                if name_entry.get('language', {}).get('name') == 'en':
                    return name_entry.get('name')
    except:
        pass
    return None

def scrape_shungo_spawns():
    print("="*60)
    print("🚀 FETCHING SPAWNS FROM SHUNGO API")
    print("="*60)
    
    api_url = "https://shungo.app/api/shungo/data/spawns"
    response = requests.get(api_url)
    data = response.json()
    result_array = data["result"]
    
    print(f"📊 Raw spawn entries: {len(result_array)}")
    
    try:
        with open('shungo_forms.json', 'r') as f:
            forms_data = json.load(f)
            form_mappings = forms_data.get("form_mappings", {})
        print(f"📋 Loaded form mappings for {len(form_mappings)} Pokémon")
    except FileNotFoundError:
        print("⚠️ shungo_forms.json not found, run scrape_shungo_forms.py first")
        form_mappings = {}
    
    # Build form map for name lookup
    form_map = {}
    for id_str, rates in form_mappings.items():
        pokemon_id = int(id_str)
        form_map[pokemon_id] = {}
        for rate_str, name in rates.items():
            rate = float(rate_str)
            form_map[pokemon_id][rate] = name
    
    # Build ID to name map (for fallback)
    id_to_name = {}
    for pid, rates in form_map.items():
        for rate, name in rates.items():
            id_to_name[pid] = name
            break
    
    spawns = []
    form_count = 0
    regular_count = 0
    missing_ids = set()
    
    print("\n📝 Processing spawns...")
    
    for item in result_array:
        pokemon_id = item[0]
        rate = item[2]
        is_shiny = item[3] == "true" or item[3] == True
        
        # Get Pokémon name
        pokemon_name = None
        
        # Try rate match first
        if pokemon_id in form_map:
            closest_rate = None
            closest_diff = 1.0
            for map_rate in form_map[pokemon_id].keys():
                diff = abs(map_rate - rate)
                if diff < closest_diff:
                    closest_diff = diff
                    closest_rate = map_rate
            if closest_rate is not None:
                pokemon_name = form_map[pokemon_id][closest_rate]
        
        # Fallback to ID mapping
        if not pokemon_name and pokemon_id in id_to_name:
            pokemon_name = id_to_name[pokemon_id]
        
        # Last resort - PokeAPI
        if not pokemon_name:
            pokemon_name = get_pokemon_name_from_api(pokemon_id)
        
        if not pokemon_name:
            missing_ids.add(pokemon_id)
            pokemon_name = f"Pokemon #{pokemon_id}"
        
        # Determine image URL
        if is_form_pokemon(pokemon_name) and not pokemon_name.startswith('Pokemon #'):
            # Form Pokémon - use RotomLabs image
            slug = get_rotomlabs_slug(pokemon_name)
            image_url = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{pokemon_id}_{slug}.webp"
            form_count += 1
        else:
            # Regular Pokémon - use PokeAPI
            image_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
            regular_count += 1
        
        spawns.append({
            "id": pokemon_id,
            "name": pokemon_name,
            "rate": round(rate, 2),
            "shiny": is_shiny,
            "image_url": image_url
        })
    
    # Sort by spawn rate
    spawns.sort(key=lambda x: x['rate'], reverse=True)
    
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(spawns),
        "spawns": spawns
    }
    
    with open('spawns.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "="*60)
    print("💾 SAVED: spawns.json")
    print("="*60)
    print(f"   Total spawns: {len(spawns)}")
    print(f"   🔸 Form Pokémon (RotomLabs): {form_count}")
    print(f"   🔹 Regular Pokémon (PokeAPI): {regular_count}")
    
    if missing_ids:
        print(f"   ⚠️ Missing names for IDs: {sorted(missing_ids)[:20]}...")
    
    print("\n📊 Top 10 highest spawn rates:")
    for i, spawn in enumerate(spawns[:10]):
        source = "RotomLabs" if "rotomlabs" in spawn['image_url'] else "PokeAPI"
        print(f"   {i+1}. {spawn['name']}: {spawn['rate']}% [{source}]")
    
    print("\n✨ Done!")

if __name__ == "__main__":
    scrape_shungo_spawns()
