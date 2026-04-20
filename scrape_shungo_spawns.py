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
        "Cherrim Overcast Form": "cherrim-overcast",
        "Cherrim Sunny": "cherrim-sunshine",
        "Deerling Spring Form": "deerling-spring",
        "Sawsbuck Spring Form": "sawsbuck-spring",
        "Darmanitan Standard": "darmanitan-standard-mode",
        "Farfetch'd Galarian": "farfetch-d-galarian",
        "Pumpkaboo Small": "pumpkaboo-small",
        "Pumpkaboo Large": "pumpkaboo-large",
        "Pumpkaboo Super": "pumpkaboo-super",
        "Pumpkaboo Average": "pumpkaboo-average",
        "Flabébé Blue Flower": "flabebe-blue-flower",
        "Flabébé Red Flower": "flabebe-red-flower",
        "Flabébé Yellow Flower": "flabebe-yellow-flower",
        "Flabébé White Flower": "flabebe-white-flower",
        "Flabébé Orange Flower": "flabebe-orange-flower",
        "Floette Blue Flower": "floette-blue-flower",
        "Floette Red Flower": "floette-red-flower",
        "Floette Yellow Flower": "floette-yellow-flower",
        "Burmy Plant Cloak": "burmy-plant-cloak",
        "Burmy Sandy Cloak": "burmy-sandy-cloak",
        "Burmy Trash Cloak": "burmy-trash-cloak",
        "Oricorio Baile Style": "oricorio-baile-style",
        "Oricorio Pom-Pom Style": "oricorio-pom-pom-style",
        "Oricorio Sensu Style": "oricorio-sensu-style",
        "Geodude Alola": "geodude-alolan",
        "Graveler Alola": "graveler-alolan",
        "Grimer Alola": "grimer-alolan",
        "Muk Alola": "muk-alolan",
        "Rattata Alola": "rattata-alolan",
        "Raticate Alola": "raticate-alolan",
        "Meowth Alola": "meowth-alolan",
        "Persian Alola": "persian-alolan",
        "Sandshrew Alola": "sandshrew-alolan",
        "Vulpix Alola": "vulpix-alolan",
        "Diglett Alola": "diglett-alolan",
        "Dugtrio Alola": "dugtrio-alolan",
    }
    
    if clean_name in special_mappings:
        return special_mappings[clean_name]
    
    # Handle "Alola" in name
    if 'alola' in clean_name.lower():
        base = clean_name.lower().replace(' alola', '').replace(' alolan', '')
        return f"{base}-alolan"
    
    clean_name = clean_name.lower()
    clean_name = clean_name.replace("'", "")
    clean_name = clean_name.replace(" ", "-")
    clean_name = re.sub(r'[^a-z0-9-]', '', clean_name)
    clean_name = re.sub(r'-+', '-', clean_name)
    clean_name = clean_name.strip('-')
    
    return clean_name

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
    
    spawns = []
    form_count = 0
    regular_count = 0
    
    print("\n📝 Processing spawns...")
    
    for item in result_array:
        pokemon_id = item[0]
        rate = item[2]
        is_shiny = item[3] == "true" or item[3] == True
        
        # Get the form name from mappings
        pokemon_name = None
        
        if pokemon_id in form_map:
            # Find closest rate match
            closest_rate = None
            closest_diff = 1.0
            for map_rate in form_map[pokemon_id].keys():
                diff = abs(map_rate - rate)
                if diff < closest_diff:
                    closest_diff = diff
                    closest_rate = map_rate
            if closest_rate is not None:
                pokemon_name = form_map[pokemon_id][closest_rate]
        
        # If no name found, use ID
        if not pokemon_name:
            pokemon_name = f"Pokemon #{pokemon_id}"
            regular_count += 1
        else:
            # Check if this is a form (name has indicators like Rainy, Alola, etc.)
            name_lower = pokemon_name.lower()
            is_form = any(x in name_lower for x in [
                'rainy', 'sunny', 'snowy', 'alola', 'alolan', 'galarian', 
                'hisuian', 'paldea', 'heat', 'wash', 'frost', 'fan', 'mow',
                'baile', 'pom-pom', 'pau', 'sensu', 'overcast', 'sunshine',
                'blue flower', 'red flower', 'yellow flower', 'white flower', 'orange flower',
                'plant cloak', 'sandy cloak', 'trash cloak', 'spring', 'autumn',
                'small', 'large', 'super', 'average', 'standard', 'zen'
            ])
            
            if is_form:
                form_count += 1
            else:
                regular_count += 1
        
        # Generate image URL - ALWAYS use the form name for the slug
        slug = get_rotomlabs_slug(pokemon_name)
        
        # Check if this should use RotomLabs (forms) or PokeAPI (regular)
        name_lower = pokemon_name.lower()
        use_rotomlabs = any(x in name_lower for x in [
            'rainy', 'sunny', 'snowy', 'alola', 'alolan', 'galarian', 
            'hisuian', 'paldea', 'heat', 'wash', 'frost', 'fan', 'mow',
            'baile', 'pom-pom', 'pau', 'sensu', 'overcast', 'sunshine',
            'blue flower', 'red flower', 'yellow flower', 'white flower', 'orange flower',
            'plant cloak', 'sandy cloak', 'trash cloak', 'spring', 'autumn',
            'small', 'large', 'super', 'average', 'standard', 'zen'
        ])
        
        if use_rotomlabs and not pokemon_name.startswith('Pokemon #'):
            image_url = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{pokemon_id}_{slug}.webp"
        else:
            image_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
        
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
    
    # Show sample of form Pokémon
    form_spawns = [s for s in spawns if 'rotomlabs' in s['image_url']]
    if form_spawns:
        print(f"\n📸 Sample form Pokémon (using RotomLabs):")
        for s in form_spawns[:5]:
            print(f"   - {s['name']}: {s['image_url']}")
    
    print("\n✨ Done!")

if __name__ == "__main__":
    scrape_shungo_spawns()
