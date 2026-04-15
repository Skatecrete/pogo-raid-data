import requests
import json
from datetime import datetime

def scrape_shungo_spawns():
    print("🚀 Fetching spawns from Shungo API...")
    
    # 1. Get raw spawn data
    api_url = "https://shungo.app/api/shungo/data/spawns"
    response = requests.get(api_url)
    data = response.json()
    result_array = data["result"]
    
    print(f"📊 Raw spawns: {len(result_array)} entries")
    
    # 2. Load form mappings
    try:
        with open('shungo_forms.json', 'r') as f:
            forms_data = json.load(f)
            form_mappings = forms_data.get("form_mappings", {})
        print(f"📋 Loaded form mappings for {len(form_mappings)} Pokémon")
    except FileNotFoundError:
        print("⚠️ shungo_forms.json not found, run scrape_shungo_forms.py first")
        form_mappings = {}
    
    # 3. Convert to usable format
    form_map = {}
    for id_str, rates in form_mappings.items():
        pokemon_id = int(id_str)
        form_map[pokemon_id] = {}
        for rate_str, name in rates.items():
            rate = float(rate_str)
            form_map[pokemon_id][rate] = name
    
    # 4. Build spawns list
    spawns = []
    for item in result_array:
        pokemon_id = item[0]
        rate = item[2]
        is_shiny = item[3] == "true" or item[3] == True
        
        # Find form name
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
        
        spawns.append({
            "id": pokemon_id,
            "name": pokemon_name,
            "rate": round(rate, 2),
            "shiny": is_shiny
        })
    
    # 5. Save to JSON
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(spawns),
        "spawns": spawns
    }
    
    with open('spawns.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Saved to spawns.json")
    print(f"   Total spawns: {len(spawns)}")

if __name__ == "__main__":
    scrape_shungo_spawns()
