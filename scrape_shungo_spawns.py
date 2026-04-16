import requests
import json
import re
from datetime import datetime

def get_rotomlabs_slug(pokemon_name):
    """
    Converts a Pokemon name with form into a RotomLabs URL slug.
    e.g., "Oricorio Pom-Pom Style" -> "oricorio-pom-pom-style"
    """
    # Remove any parenthetical notes (like "(Sunglasses)") that might be in the name
    clean_name = re.sub(r'\([^)]*\)', '', pokemon_name).strip()
    
    # Special case mappings for known tricky names
    special_mappings = {
        "Nidoran\u2640": "nidoran-f",      # Female symbol
        "Nidoran\u2642": "nidoran-m",      # Male symbol
        "Farfetch'd": "farfetchd",         # Remove apostrophe
        "Mr. Mime": "mr-mime",             # Handle punctuation
        "Type: Null": "type-null",
        "Flabébé": "flabebe",              # Remove accent
        "Nidoran♀": "nidoran-f",           # Female symbol (literal)
        "Nidoran♂": "nidoran-m",           # Male symbol (literal)
        "Porygon2": "porygon2",            # Keep as is
        "Porygon-Z": "porygon-z",          # Hyphenated
        "Ho-Oh": "ho-oh",                  # Hyphenated
        "Mime Jr.": "mime-jr",             # Punctuation
        "Sirfetch'd": "sirfetchd",         # Remove apostrophe
        "Mr. Rime": "mr-rime",             # Handle punctuation
        "Great Tusk": "great-tusk",
        "Scream Tail": "scream-tail",
        "Brute Bonnet": "brute-bonnet",
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
        "Ogerpon": "ogerpon",
        "Terapagos": "terapagos",
        "Pecharunt": "pecharunt",
        "Deerling Spring Form": "deerling-spring",
        "Deerling Autumn Form": "deerling-autumn",
        "Deerling Summer Form": "deerling-summer",
        "Deerling Winter Form": "deerling-winter",
        "Sawsbuck Spring Form": "sawsbuck-spring",
        "Sawsbuck Summer Form": "sawsbuck-summer",
        "Sawsbuck Autumn Form": "sawsbuck-autumn",
        "Sawsbuck Winter Form": "sawsbuck-winter",
        "Castform": "castform",
        "Castform Sunny": "castform-sunny",
        "Castform Rainy": "castform-rainy",
        "Castform Snowy": "castform-snowy",
        "Cherrim Overcast Form": "cherrim",
        "Cherrim Sunny": "cherrim-sunshine",
        "Shellos West Sea": "shellos-west",
        "Shellos East Sea": "shellos-east",
        "Gastrodon West Sea": "gastrodon-west",
        "Gastrodon East Sea": "gastrodon-east",
        "Burmy Plant Cloak": "burmy-plant",
        "Burmy Sandy Cloak": "burmy-sandy",
        "Burmy Trash Cloak": "burmy-trash",
        "Wormadam Plant Cloak": "wormadam-plant",
        "Wormadam Sandy Cloak": "wormadam-sandy",
        "Wormadam Trash Cloak": "wormadam-trash",
        "Rotom": "rotom",
        "Rotom Heat": "rotom-heat",
        "Rotom Wash": "rotom-wash",
        "Rotom Frost": "rotom-frost",
        "Rotom Fan": "rotom-fan",
        "Rotom Mow": "rotom-mow",
        "Giratina Altered": "giratina",
        "Giratina Origin": "giratina-origin",
        "Shaymin Land": "shaymin",
        "Shaymin Sky": "shaymin-sky",
        "Basculin Red-Striped": "basculin",
        "Basculin Blue-Striped": "basculin-blue-striped",
        "Darmanitan Standard": "darmanitan",
        "Darmanitan Zen": "darmanitan-zen",
        "Tornadus Incarnate": "tornadus",
        "Tornadus Therian": "tornadus-therian",
        "Thundurus Incarnate": "thundurus",
        "Thundurus Therian": "thundurus-therian",
        "Landorus Incarnate": "landorus",
        "Landorus Therian": "landorus-therian",
        "Keldeo Ordinary": "keldeo",
        "Keldeo Resolute": "keldeo-resolute",
        "Meloetta Aria": "meloetta",
        "Meloetta Pirouette": "meloetta-pirouette",
        "Genesect": "genesect",
        "Genesect Burn": "genesect-burn",
        "Genesect Chill": "genesect-chill",
        "Genesect Douse": "genesect-douse",
        "Genesect Shock": "genesect-shock",
        "Greninja": "greninja",
        "Greninja Ash": "greninja-ash",
        "Vivillon Meadow": "vivillon",
        "Vivillon Polar": "vivillon-polar",
        "Vivillon Tundra": "vivillon-tundra",
        "Vivillon Continental": "vivillon-continental",
        "Vivillon Garden": "vivillon-garden",
        "Vivillon Elegant": "vivillon-elegant",
        "Vivillon Modern": "vivillon-modern",
        "Vivillon Marine": "vivillon-marine",
        "Vivillon Archipelago": "vivillon-archipelago",
        "Vivillon High Plains": "vivillon-high-plains",
        "Vivillon Sandstorm": "vivillon-sandstorm",
        "Vivillon River": "vivillon-river",
        "Vivillon Monsoon": "vivillon-monsoon",
        "Vivillon Savanna": "vivillon-savanna",
        "Vivillon Sun": "vivillon-sun",
        "Vivillon Ocean": "vivillon-ocean",
        "Vivillon Jungle": "vivillon-jungle",
        "Vivillon Fancy": "vivillon-fancy",
        "Vivillon Pokeball": "vivillon-pokeball",
        "Flabébé Red Flower": "flabebe-red",
        "Flabébé Blue Flower": "flabebe-blue",
        "Flabébé Yellow Flower": "flabebe-yellow",
        "Flabébé White Flower": "flabebe-white",
        "Flabébé Orange Flower": "flabebe-orange",
        "Floette Red Flower": "floette-red",
        "Floette Blue Flower": "floette-blue",
        "Floette Yellow Flower": "floette-yellow",
        "Floette White Flower": "floette-white",
        "Floette Orange Flower": "floette-orange",
        "Furfrou Natural": "furfrou",
        "Furfrou Heart": "furfrou-heart",
        "Furfrou Star": "furfrou-star",
        "Furfrou Diamond": "furfrou-diamond",
        "Furfrou Debutante": "furfrou-debutante",
        "Furfrou Matron": "furfrou-matron",
        "Furfrou Dandy": "furfrou-dandy",
        "Furfrou La Reine": "furfrou-la-reine",
        "Furfrou Kabuki": "furfrou-kabuki",
        "Furfrou Pharaoh": "furfrou-pharaoh",
        "Aegislash Shield": "aegislash-shield",
        "Aegislash Blade": "aegislash-blade",
        "Pumpkaboo Small": "pumpkaboo",
        "Pumpkaboo Average": "pumpkaboo-average",
        "Pumpkaboo Large": "pumpkaboo-large",
        "Pumpkaboo Super": "pumpkaboo-super",
        "Gourgeist Small": "gourgeist",
        "Gourgeist Average": "gourgeist-average",
        "Gourgeist Large": "gourgeist-large",
        "Gourgeist Super": "gourgeist-super",
        "Zygarde 10%": "zygarde-10",
        "Zygarde 50%": "zygarde",
        "Zygarde Complete": "zygarde-complete",
        "Oricorio Baile Style": "oricorio-baile",
        "Oricorio Pom-Pom Style": "oricorio-pompom",
        "Oricorio Pa'u Style": "oricorio-pau",
        "Oricorio Sensu Style": "oricorio-sensu",
        "Rockruff": "rockruff",
        "Lycanroc Midday": "lycanroc",
        "Lycanroc Midnight": "lycanroc-midnight",
        "Lycanroc Dusk": "lycanroc-dusk",
        "Wishiwashi Solo": "wishiwashi",
        "Wishiwashi School": "wishiwashi-school",
        "Minior Red": "minior-red",
        "Minior Orange": "minior-orange",
        "Minior Yellow": "minior-yellow",
        "Minior Green": "minior-green",
        "Minior Blue": "minior-blue",
        "Minior Indigo": "minior-indigo",
        "Minior Violet": "minior-violet",
        "Mimikyu Disguised": "mimikyu",
        "Mimikyu Busted": "mimikyu-busted",
        "Necrozma": "necrozma",
        "Necrozma Dusk Mane": "necrozma-dusk",
        "Necrozma Dawn Wings": "necrozma-dawn",
        "Necrozma Ultra": "necrozma-ultra",
        "Toxtricity Amped": "toxtricity",
        "Toxtricity Low Key": "toxtricity-low-key",
        "Eiscue Ice": "eiscue",
        "Eiscue Noice": "eiscue-noice",
        "Indeedee Male": "indeedee",
        "Indeedee Female": "indeedee-female",
        "Morpeko Full Belly": "morpeko",
        "Morpeko Hangry": "morpeko-hangry",
        "Zacian Hero": "zacian",
        "Zacian Crowned": "zacian-crowned",
        "Zamazenta Hero": "zamazenta",
        "Zamazenta Crowned": "zamazenta-crowned",
        "Urshifu Single Strike": "urshifu",
        "Urshifu Rapid Strike": "urshifu-rapid",
        "Calyrex": "calyrex",
        "Calyrex Ice Rider": "calyrex-ice",
        "Calyrex Shadow Rider": "calyrex-shadow",
        "Basculegion Male": "basculegion",
        "Basculegion Female": "basculegion-female",
        "Enamorus Incarnate": "enamorus",
        "Enamorus Therian": "enamorus-therian",
        "Koraidon": "koraidon",
        "Koraidon Battle": "koraidon-battle",
        "Koraidon Sprint": "koraidon-sprint",
        "Koraidon Swim": "koraidon-swim",
        "Koraidon Glide": "koraidon-glide",
        "Miraidon": "miraidon",
        "Miraidon Battle": "miraidon-battle",
        "Miraidon Sprint": "miraidon-sprint",
        "Miraidon Swim": "miraidon-swim",
        "Miraidon Glide": "miraidon-glide",
        "Wooper Paldea": "wooper-paldea",
        "Tauros Paldean Blaze Breed": "tauros-paldea-blaze",
        "Tauros Paldean Aqua Breed": "tauros-paldea-aqua",
        "Tauros Paldean Combat Breed": "tauros-paldea-combat",
    }
    
    # Check for special mapping first
    if clean_name in special_mappings:
        clean_name = special_mappings[clean_name]
    else:
        # Handle "Form" patterns (e.g., "Deoxys Attack Forme" -> "deoxys-attack")
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
    
    # For special mappings, convert to lowercase and ensure hyphens
    slug = clean_name.lower().replace(" ", "-")
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    
    return slug

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
    
    # 4. Build spawns list with image URLs
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
            # Fallback: Use default name from ID if no form mapping found
            pokemon_name = f"Pokemon #{pokemon_id}"
        
        # Generate RotomLabs image URL based on the form name
        slug = get_rotomlabs_slug(pokemon_name)
        image_url = f"https://rotomlabs.net/dex/{slug}"
        
        spawns.append({
            "id": pokemon_id,
            "name": pokemon_name,
            "rate": round(rate, 2),
            "shiny": is_shiny,
            "image_url": image_url  # ADDED: RotomLabs image URL
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
    
    # Print a few examples to verify
    print("\n📸 Sample image URLs generated:")
    for spawn in spawns[:10]:
        print(f"   {spawn['name']}: {spawn['image_url']}")

if __name__ == "__main__":
    scrape_shungo_spawns()
