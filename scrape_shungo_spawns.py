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
        "Cherrim Overcast Form": "cherrim-overcast",
        "Cherrim Sunshine Form": "cherrim-sunshine",
        "Cherrim Sunny": "cherrim-sunshine",
        "Floette Blue Flower": "floette-blue-flower",
        "Floette Red Flower": "floette-red-flower",
        "Floette Yellow Flower": "floette-yellow-flower",
        "Floette White Flower": "floette-white-flower",
        "Floette Orange Flower": "floette-orange-flower",
        "Flabébé Blue Flower": "flabebe-blue-flower",
        "Flabébé Red Flower": "flabebe-red-flower",
        "Flabébé Yellow Flower": "flabebe-yellow-flower",
        "Flabébé White Flower": "flabebe-white-flower",
        "Flabébé Orange Flower": "flabebe-orange-flower",
        "Oricorio Baile Style": "oricorio-baile",
        "Oricorio Pom-Pom Style": "oricorio-pompom",
        "Oricorio Pa'u Style": "oricorio-pau",
        "Oricorio Sensu Style": "oricorio-sensu",
        "Rotom Heat": "rotom-heat",
        "Rotom Wash": "rotom-wash",
        "Rotom Frost": "rotom-frost",
        "Rotom Fan": "rotom-fan",
        "Rotom Mow": "rotom-mow",
        "Giratina Origin": "giratina-origin",
        "Shaymin Sky": "shaymin-sky",
        "Basculin Blue-Striped": "basculin-blue-striped",
        "Darmanitan Zen": "darmanitan-zen",
        "Tornadus Therian": "tornadus-therian",
        "Thundurus Therian": "thundurus-therian",
        "Landorus Therian": "landorus-therian",
        "Keldeo Resolute": "keldeo-resolute",
        "Meloetta Pirouette": "meloetta-pirouette",
        "Genesect Burn": "genesect-burn",
        "Genesect Chill": "genesect-chill",
        "Genesect Douse": "genesect-douse",
        "Genesect Shock": "genesect-shock",
        "Greninja Ash": "greninja-ash",
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
        "Furfrou Heart": "furfrou-heart",
        "Furfrou Star": "furfrou-star",
        "Furfrou Diamond": "furfrou-diamond",
        "Furfrou Debutante": "furfrou-debutante",
        "Furfrou Matron": "furfrou-matron",
        "Furfrou Dandy": "furfrou-dandy",
        "Furfrou La Reine": "furfrou-la-reine",
        "Furfrou Kabuki": "furfrou-kabuki",
        "Furfrou Pharaoh": "furfrou-pharaoh",
        "Aegislash Blade": "aegislash-blade",
        "Pumpkaboo Average": "pumpkaboo-average",
        "Pumpkaboo Large": "pumpkaboo-large",
        "Pumpkaboo Super": "pumpkaboo-super",
        "Gourgeist Average": "gourgeist-average",
        "Gourgeist Large": "gourgeist-large",
        "Gourgeist Super": "gourgeist-super",
        "Zygarde 10%": "zygarde-10",
        "Zygarde Complete": "zygarde-complete",
        "Lycanroc Midnight": "lycanroc-midnight",
        "Lycanroc Dusk": "lycanroc-dusk",
        "Wishiwashi School": "wishiwashi-school",
        "Minior Orange": "minior-orange",
        "Minior Yellow": "minior-yellow",
        "Minior Green": "minior-green",
        "Minior Blue": "minior-blue",
        "Minior Indigo": "minior-indigo",
        "Minior Violet": "minior-violet",
        "Mimikyu Busted": "mimikyu-busted",
        "Necrozma Dusk Mane": "necrozma-dusk",
        "Necrozma Dawn Wings": "necrozma-dawn",
        "Toxtricity Low Key": "toxtricity-low-key",
        "Eiscue Noice": "eiscue-noice",
        "Indeedee Female": "indeedee-female",
        "Morpeko Hangry": "morpeko-hangry",
        "Zacian Crowned": "zacian-crowned",
        "Zamazenta Crowned": "zamazenta-crowned",
        "Urshifu Rapid Strike": "urshifu-rapid",
        "Calyrex Ice Rider": "calyrex-ice",
        "Calyrex Shadow Rider": "calyrex-shadow",
        "Basculegion Female": "basculegion-female",
        "Enamorus Therian": "enamorus-therian",
        "Wooper Paldea": "wooper-paldea",
        "Tauros Paldean Blaze Breed": "tauros-paldea-blaze",
        "Tauros Paldean Aqua Breed": "tauros-paldea-aqua",
        "Tauros Paldean Combat Breed": "tauros-paldea-combat",
    }
    
    # Check special mappings first
    if clean_name in special_mappings:
        return special_mappings[clean_name]
    
    clean_name = clean_name.lower()
    clean_name = clean_name.replace("'", "")
    clean_name = clean_name.replace(" ", "-")
    clean_name = re.sub(r'[^a-z0-9-]', '', clean_name)
    clean_name = re.sub(r'-+', '-', clean_name)
    clean_name = clean_name.strip('-')
    
    return clean_name

def get_form_name(pokemon_name):
    """Extract just the form part for display in duplicate summary"""
    # Common form indicators
    forms = [
        'Alola', 'Alolan', 'Galarian', 'Hisuian', 'Paldea', 'Paldean',
        'Rainy', 'Sunny', 'Snowy', 'Heat', 'Wash', 'Frost', 'Fan', 'Mow',
        'Overcast', 'Sunshine', 'Blue Flower', 'Red Flower', 'Yellow Flower',
        'White Flower', 'Orange Flower', 'Baile Style', 'Pom-Pom Style',
        "Pa'u Style", 'Sensu Style', 'Origin', 'Sky', 'Therian', 'Resolute',
        'Pirouette', 'Burn', 'Chill', 'Douse', 'Shock', 'Ash', 'Zen',
        'Crowned', 'Hero', 'Single Strike', 'Rapid Strike', 'Ice Rider',
        'Shadow Rider', 'Midnight', 'Dusk', 'School', 'Busted', 'Dusk Mane',
        'Dawn Wings', 'Ultra', 'Low Key', 'Noice', 'Female', 'Hangry',
        'Blaze Breed', 'Aqua Breed', 'Combat Breed', 'Small', 'Average',
        'Large', 'Super', 'Standard', 'Trash Cloak', 'Plant Cloak', 'Sandy Cloak'
    ]
    
    for form in forms:
        if form.lower() in pokemon_name.lower():
            return form
    return "Base Form"

def scrape_shungo_spawns():
    print("🚀 Fetching spawns from Shungo API...")
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
    
    form_map = {}
    for id_str, rates in form_mappings.items():
        pokemon_id = int(id_str)
        form_map[pokemon_id] = {}
        for rate_str, name in rates.items():
            rate = float(rate_str)
            form_map[pokemon_id][rate] = name
    
    # Track duplicates for reporting
    duplicate_log = []
    unique_spawns = {}
    
    # First pass: collect all entries and identify duplicates
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
        
        # Create a unique key for this Pokémon + form
        key = f"{pokemon_id}_{pokemon_name}"
        
        # Keep the HIGHEST spawn rate for each unique Pokémon/form
        if key not in unique_spawns:
            unique_spawns[key] = {
                "id": pokemon_id,
                "name": pokemon_name,
                "rate": rate,
                "shiny": is_shiny
            }
        else:
            # This is a duplicate - log it
            duplicate_log.append({
                "name": pokemon_name,
                "rate": rate,
                "kept_rate": unique_spawns[key]['rate'],
                "id": pokemon_id
            })
            # Update if this rate is higher
            if rate > unique_spawns[key]['rate']:
                unique_spawns[key]['rate'] = rate
                unique_spawns[key]['shiny'] = is_shiny
    
    # ============================================================
    # METHOD 5: DETAILED DUPLICATE SUMMARY
    # ============================================================
    print("\n" + "="*60)
    print("📋 DUPLICATE SUMMARY")
    print("="*60)
    
    if duplicate_log:
        # Group duplicates by Pokémon name
        grouped_dupes = defaultdict(list)
        for dup in duplicate_log:
            grouped_dupes[dup['name']].append(dup)
        
        print(f"\nFound {len(duplicate_log)} duplicate entries for {len(grouped_dupes)} Pokémon:\n")
        
        for name, dups in sorted(grouped_dupes.items()):
            form_type = get_form_name(name)
            print(f"  🔄 {name} [{form_type}]")
            for dup in dups:
                print(f"       - {dup['rate']}% (discarded, kept {dup['kept_rate']}%)")
        print("\n" + "-"*60)
        print(f"✅ Kept highest spawn rate for each unique Pokémon/form")
    else:
        print("\n  ✨ No duplicates found! All entries are unique.")
    
    print("="*60)
    
    # Convert back to list
    spawns = []
    for item in unique_spawns.values():
        slug = get_rotomlabs_slug(item['name'])
        local_image_url = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{item['id']}_{slug}.webp"
        spawns.append({
            "id": item['id'],
            "name": item['name'],
            "rate": round(item['rate'], 2),
            "shiny": item['shiny'],
            "image_url": local_image_url
        })
    
    # Sort by spawn rate (highest first)
    spawns.sort(key=lambda x: x['rate'], reverse=True)
    
    # Calculate statistics
    total_original = len(result_array)
    total_unique = len(spawns)
    duplicates_removed = total_original - total_unique
    
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(spawns),
        "spawns": spawns
    }
    
    with open('spawns.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 SAVED: spawns.json")
    print(f"   Original entries: {total_original}")
    print(f"   Unique entries:   {total_unique}")
    print(f"   Duplicates removed: {duplicates_removed}")
    print(f"\n📊 Top 10 highest spawn rates:")
    for i, spawn in enumerate(spawns[:10]):
        print(f"   {i+1}. {spawn['name']}: {spawn['rate']}%")
    
    print("\n✨ Done!")

if __name__ == "__main__":
    scrape_shungo_spawns()
