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
        "Farfetch'd": "farfetchd",
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
        "Deerling Spring Form": "deerling-spring",
        "Deerling Autumn Form": "deerling-autumn",
        "Deerling Summer Form": "deerling-summer",
        "Deerling Winter Form": "deerling-winter",
        "Sawsbuck Spring Form": "sawsbuck-spring",
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

def scrape_shungo_spawns():
    print("🚀 Fetching spawns from Shungo API...")
    
    api_url = "https://shungo.app/api/shungo/data/spawns"
    response = requests.get(api_url)
    data = response.json()
    result_array = data["result"]
    
    print(f"📊 Raw spawns: {len(result_array)} entries")
    
    try:
        with open('shungo_forms.json', 'r') as f:
            forms_data = json.load(f)
            form_mappings = forms_data.get("form_mappings", {})
        print(f"📋 Loaded form mappings for {len(form_mappings)} Pokémon")
    except FileNotFoundError:
        print("⚠️ shungo_forms.json not found, run scrape_shungo_forms.py first")
        form_mappings = {}
    
    form_map = {}
    for id_str, rates in form_mappings.items():
        pokemon_id = int(id_str)
        form_map[pokemon_id] = {}
        for rate_str, name in rates.items():
            rate = float(rate_str)
            form_map[pokemon_id][rate] = name
    
    spawns = []
    for item in result_array:
        pokemon_id = item[0]
        rate = item[2]
        is_shiny = item[3] == "true" or item[3] == True
        
        pokemon_name = None
        if pokemon_id in form_map:
            closest_rate = None
            closest_diff = 1.0
            for map_rate in form_map[pokemon_id].keys():
                diff = abs(map_rate - rate)
                if diff < closest_diff:
                    closest_diff = diff
                    closest_rate = map_rate
            if closest_rate and closest_diff < 0.05:
                pokemon_name = form_map[pokemon_id][closest_rate]
        
        if not pokemon_name:
            pokemon_name = f"Pokemon #{pokemon_id}"
        
        # Generate image URL using RotomLabs pattern (but app will use whatever)
        slug = get_rotomlabs_slug(pokemon_name)
        image_url = f"https://rotomlabs.net/dex/{slug}"
        
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
    
    print(f"\n💾 Saved to spawns.json")
    print(f"   Total spawns: {len(spawns)}")
    print(f"\n📊 Top 10 highest spawn rates:")
    for i, spawn in enumerate(spawns[:10]):
        print(f"   {i+1}. {spawn['name']}: {spawn['rate']}%")
    
    print("\n✨ Done!")

if __name__ == "__main__":
    scrape_shungo_spawns()
