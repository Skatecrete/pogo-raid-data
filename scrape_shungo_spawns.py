import requests
import json
import re
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

# ============================================================================
# 1. SCRAPE FORMS DIRECTLY FROM SHUNGO WEBSITE (NO SEPARATE FILE NEEDED)
# ============================================================================

async def scrape_forms_from_website():
    """Scrape form names directly from Shungo website"""
    print("🌐 Scraping form data from Shungo website...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("📄 Loading page...")
        await page.goto("https://shungo.app/tools/wild")
        
        await page.wait_for_timeout(5000)
        
        print("📜 Scrolling to load all Pokémon...")
        last_height = await page.evaluate('() => document.body.scrollHeight')
        
        while True:
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)
            new_height = await page.evaluate('() => document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height
        
        print("✅ Page loaded, extracting data...")
        
        text = await page.evaluate('() => document.body.innerText')
        
        await browser.close()
        
        # Parse the text into form mappings
        lines = text.split('\n')
        form_map = {}
        
        i = 0
        while i < len(lines) - 2:
            name = lines[i].strip()
            rate_line = lines[i + 1].strip()
            id_line = lines[i + 2].strip()
            
            if name and rate_line.endswith('%') and id_line.isdigit():
                rate = float(rate_line.replace('%', ''))
                pokemon_id = int(id_line)
                rounded_rate = round(rate, 2)
                
                if pokemon_id not in form_map:
                    form_map[pokemon_id] = {}
                
                if rounded_rate in form_map[pokemon_id]:
                    existing = form_map[pokemon_id][rounded_rate]
                    if existing != name and name not in existing:
                        form_map[pokemon_id][rounded_rate] = f"{existing} or {name}"
                else:
                    form_map[pokemon_id][rounded_rate] = name
                
                i += 3
            else:
                i += 1
        
        print(f"📋 Found {len(form_map)} Pokémon with forms")
        return form_map


# ============================================================================
# 2. FETCH SPAWNS FROM API
# ============================================================================

def fetch_spawns_from_api():
    """Fetch raw spawn data from Shungo API"""
    print("📡 Fetching spawns from Shungo API...")
    api_url = "https://shungo.app/api/shungo/data/spawns"
    response = requests.get(api_url)
    data = response.json()
    result_array = data["result"]
    print(f"📊 Raw spawn entries: {len(result_array)}")
    return result_array


# ============================================================================
# 3. HELPER FUNCTIONS
# ============================================================================

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
    
    if clean_name in special_mappings:
        return special_mappings[clean_name]
    
    clean_name = clean_name.lower()
    clean_name = clean_name.replace("'", "")
    clean_name = clean_name.replace(" ", "-")
    clean_name = re.sub(r'[^a-z0-9-]', '', clean_name)
    clean_name = re.sub(r'-+', '-', clean_name)
    clean_name = clean_name.strip('-')
    
    return clean_name


def match_spawns_with_forms(spawns_array, form_map):
    """Match each spawn with its correct form name"""
    spawns = []
    matched = 0
    fallback = 0
    
    # Build a quick lookup by ID (for fallback)
    id_to_any_name = {}
    for pid, rates in form_map.items():
        for rate, name in rates.items():
            id_to_any_name[pid] = name
            break
    
    for item in spawns_array:
        pokemon_id = item[0]
        rate = item[2]
        is_shiny = item[3] == "true" or item[3] == True
        
        pokemon_name = None
        
        # Try to find exact or closest rate match
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
                matched += 1
        
        # Fallback: use any name for this ID
        if not pokemon_name and pokemon_id in id_to_any_name:
            pokemon_name = id_to_any_name[pokemon_id]
            fallback += 1
        
        # Last resort
        if not pokemon_name:
            pokemon_name = f"Pokemon #{pokemon_id}"
        
        slug = get_rotomlabs_slug(pokemon_name)
        image_url = f"https://rotomlabs.net/dex/{slug}"
        
        spawns.append({
            "id": pokemon_id,
            "name": pokemon_name,
            "rate": round(rate, 2),
            "shiny": is_shiny,
            "image_url": image_url
        })
    
    print(f"✅ Exact matches: {matched} | Fallback matches: {fallback}")
    return spawns


# ============================================================================
# 4. MAIN FUNCTION
# ============================================================================

async def main():
    print("="*60)
    print("🚀 POKESPAWN SPAWN SCRAPER (STANDALONE)")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Scrape form data directly from website
    form_map = await scrape_forms_from_website()
    
    # Step 2: Fetch spawns from API
    spawns_array = fetch_spawns_from_api()
    
    # Step 3: Match and generate spawns
    spawns = match_spawns_with_forms(spawns_array, form_map)
    
    # Step 4: Sort by spawn rate
    spawns.sort(key=lambda x: x['rate'], reverse=True)
    
    # Step 5: Save output
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


def run():
    """Entry point for the script"""
    asyncio.run(main())


if __name__ == "__main__":
    run()
