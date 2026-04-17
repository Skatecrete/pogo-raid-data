import requests
import json
import re
from datetime import datetime

def get_rotomlabs_slug(pokemon_name):
    """
    Converts a Pokemon name with form into a RotomLabs URL slug.
    """
    # Remove any parenthetical notes
    clean_name = re.sub(r'\([^)]*\)', '', pokemon_name).strip()
    
    # Special case mappings for known tricky names
    special_mappings = {
        "Nidoran\u2640": "nidoran-f",
        "Nidoran\u2642": "nidoran-m",
        "Farfetch'd": "farfetchd",
        "Mr. Mime": "mr-mime",
        "Type: Null": "type-null",
        "Flabébé": "flabebe",
        "Ho-Oh": "ho-oh",
        "Sirfetch'd": "sirfetchd",
        "Mr. Rime": "mr-rime",
        "Great Tusk": "great-tusk",
        "Scream Tail": "scream-tail",
        "Flutter Mane": "flutter-mane",
        "Slither Wing": "slither-wing",
        "Sandy Shocks": "sandy-shocks",
        "Iron Treads": "iron-treads",
        "Iron Bundle": "iron-bundle",
        "Iron Hands": "iron-hands",
        "Iron Jugulis": "iron-jugulis",
        "Iron Moth": "iron-moth",
        "Iron Thorns": "iron-thorns",
        "Roaring Moon": "roaring-moon",
        "Iron Valiant": "iron-valiant",
        "Walking Wake": "walking-wake",
        "Iron Leaves": "iron-leaves",
        "Gouging Fire": "gouging-fire",
        "Raging Bolt": "raging-bolt",
        "Iron Boulder": "iron-boulder",
        "Iron Crown": "iron-crown",
        "Deerling Spring Form": "deerling-spring",
        "Deerling Autumn Form": "deerling-autumn",
        "Castform Sunny": "castform-sunny",
        "Castform Rainy": "castform-rainy",
        "Castform Snowy": "castform-snowy",
    }
    
    # Check special mappings first
    if clean_name in special_mappings:
        return special_mappings[clean_name]
    
    # Handle "Form" patterns
    clean_name = re.sub(r'\s+(Form|Forme|Style)$', '', clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\s+(Form|Forme|Style)\s+', ' ', clean_name, flags=re.IGNORECASE)
    
    # Handle apostrophes
    clean_name = clean_name.replace("'", "")
    
    # Handle special characters
    clean_name = clean_name.replace("♀", "-f").replace("♂", "-m")
    clean_name = clean_name.replace("é", "e").replace("è", "e").replace("ë", "e")
    clean_name = clean_name.replace("û", "u").replace("ü", "u")
    
    # Convert to lowercase and replace spaces with hyphens
    slug = clean_name.lower().replace(" ", "-")
    
    # Remove any remaining non-alphanumeric characters (except hyphens)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    
    # Remove duplicate hyphens
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug

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
        
        # Generate local image URL (will be populated by the image scraper)
        slug = get_rotomlabs_slug(pokemon_name)
        local_image_url = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{pokemon_id}_{slug}.webp"
        
        spawns.append({
            "id": pokemon_id,
            "name": pokemon_name,
            "rate": round(rate, 2),
            "shiny": is_shiny,
            "image_url": local_image_url
        })
    
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