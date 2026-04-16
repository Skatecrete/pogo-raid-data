import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def get_rotomlabs_slug(pokemon_name):
    """
    Converts a Pokemon name with form into a RotomLabs URL slug.
    (Same as spawns version)
    """
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
        "Castform Sunny": "castform-sunny",
        "Castform Rainy": "castform-rainy",
        "Castform Snowy": "castform-snowy",
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
        "Flabébé Red Flower": "flabebe-red",
        "Flabébé Blue Flower": "flabebe-blue",
        "Flabébé Yellow Flower": "flabebe-yellow",
        "Flabébé White Flower": "flabebe-white",
        "Flabébé Orange Flower": "flabebe-orange",
        "Furfrou Heart": "furfrou-heart",
        "Furfrou Star": "furfrou-star",
        "Aegislash Blade": "aegislash-blade",
        "Pumpkaboo Average": "pumpkaboo-average",
        "Pumpkaboo Large": "pumpkaboo-large",
        "Pumpkaboo Super": "pumpkaboo-super",
        "Gourgeist Average": "gourgeist-average",
        "Gourgeist Large": "gourgeist-large",
        "Gourgeist Super": "gourgeist-super",
        "Zygarde 10%": "zygarde-10",
        "Zygarde Complete": "zygarde-complete",
        "Oricorio Baile Style": "oricorio-baile",
        "Oricorio Pom-Pom Style": "oricorio-pompom",
        "Oricorio Pa'u Style": "oricorio-pau",
        "Oricorio Sensu Style": "oricorio-sensu",
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
        "Necrozma Ultra": "necrozma-ultra",
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
    
    if clean_name in special_mappings:
        clean_name = special_mappings[clean_name]
        slug = clean_name.lower().replace(" ", "-")
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')
        return slug
    
    clean_name = re.sub(r'\s+(Form|Forme|Style)$', '', clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\s+(Form|Forme|Style)\s+', ' ', clean_name, flags=re.IGNORECASE)
    clean_name = clean_name.replace("'", "")
    clean_name = clean_name.replace("♀", "-f").replace("♂", "-m")
    clean_name = clean_name.replace("é", "e").replace("è", "e").replace("ë", "e")
    clean_name = clean_name.replace("û", "u").replace("ü", "u")
    
    slug = clean_name.lower().replace(" ", "-")
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    
    return slug

def get_raid_image_url(pokemon_name, raid_tier):
    """
    Generate RotomLabs image URL for a raid Pokemon.
    """
    # Extract base Pokemon name (remove descriptors like "D-Max ", "Shiny ", etc.)
    base_name = pokemon_name
    base_name = re.sub(r'^D-Max\s+', '', base_name)
    base_name = re.sub(r'^Shiny\s+', '', base_name)
    base_name = re.sub(r'\s*\([^)]*\)$', '', base_name)  # Remove trailing parentheses
    base_name = base_name.strip()
    
    slug = get_rotomlabs_slug(base_name)
    
    # Map raid tiers to URL suffixes
    tier_lower = raid_tier.lower()
    
    if 'gigantamax' in tier_lower:
        return f"https://rotomlabs.net/dex/{slug}/gigantamax"
    elif 'mega' in tier_lower:
        # Check for Mega X/Y
        if 'mega x' in pokemon_name.lower() or 'charizard' in base_name.lower() and 'x' in pokemon_name.lower():
            return f"https://rotomlabs.net/dex/{slug}/mega-x"
        elif 'mega y' in pokemon_name.lower() or 'charizard' in base_name.lower() and 'y' in pokemon_name.lower():
            return f"https://rotomlabs.net/dex/{slug}/mega-y"
        else:
            return f"https://rotomlabs.net/dex/{slug}/mega"
    else:
        # Regular, Dynamax, Shadow raids use base form
        return f"https://rotomlabs.net/dex/{slug}"

def scrape_snacknap_raids():
    """Scrape Tier 1 and Tier 3 raids from snacknap.com/raids"""
    print("  📡 Fetching Tier 1 & 3 raids from SnackNap...")
    url = "https://snacknap.com/raids"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        raid_data = {
            "tier1": [],
            "tier3": []
        }
        
        main_container = soup.find('div', id='pokemon')
        if not main_container:
            print("    ❌ Could not find main container")
            return raid_data
        
        for h2 in main_container.find_all('h2'):
            tier_title = h2.get_text().strip()
            print(f"    Found header: {tier_title}")
            
            current_tier = None
            if tier_title == "Tier 1":
                current_tier = "tier1"
            elif tier_title == "Tier 3":
                current_tier = "tier3"
            else:
                continue
            
            tier_container = h2.find_next('div', class_=re.compile(r'row g-2'))
            if not tier_container:
                print(f"    Could not find container for {tier_title}")
                continue
            
            pokemon_cards = tier_container.find_all('a', href=re.compile(r'/pokedex/pokemon/'))
            
            for card in pokemon_cards:
                name_elem = card.find('p', class_='pkmn-title')
                if name_elem:
                    raw_name = name_elem.get_text().strip()
                    clean_name = re.sub(r'\s+', ' ', raw_name).strip()
                    
                    if clean_name and clean_name not in [r['name'] for r in raid_data[current_tier]]:
                        image_url = get_raid_image_url(clean_name, current_tier)
                        raid_data[current_tier].append({
                            "name": clean_name,
                            "imageUrl": image_url
                        })
                        print(f"      Added to {current_tier}: {clean_name} -> {image_url}")
        
        print(f"\n  📊 SNACKNAP RAID SUMMARY:")
        print(f"    Tier 1: {len(raid_data['tier1'])}")
        print(f"    Tier 3: {len(raid_data['tier3'])}")
        
        return raid_data
    except Exception as e:
        print(f"    ❌ Error scraping raids: {e}")
        import traceback
        traceback.print_exc()
        return {"tier1": [], "tier3": []}

def scrape_snacknap_maxbattles():
    """Scrape Dynamax Tier 1-5 and Gigantamax from snacknap.com/max-battles"""
    print("  📡 Fetching Dynamax & Gigantamax battles...")
    url = "https://www.snacknap.com/max-battles"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        raid_data = {
            "dynamax_tier1": [],
            "dynamax_tier2": [],
            "dynamax_tier3": [],
            "dynamax_tier4": [],
            "dynamax_tier5": [],
            "gigantamax": []
        }
        
        social_media = ['Telegram', 'Facebook', 'Instagram', 'Threads', 'Bluesky', 'X', 'Twitter', 'Discord', 'Patreon', 'YouTube', 'Twitch']
        type_words = ['fire', 'water', 'grass', 'electric', 'bug', 'ground', 'flying', 'ghost', 
                     'ice', 'psychic', 'dragon', 'dark', 'steel', 'fairy', 'rock', 'fighting', 
                     'poison', 'normal', 'shiny']
        
        current_tier = None
        tier_map = {
            'dynamax_tier1': ['Tier 1', 'TIER 1', 'tier 1'],
            'dynamax_tier2': ['Tier 2', 'TIER 2', 'tier 2'],
            'dynamax_tier3': ['Tier 3', 'TIER 3', 'tier 3'],
            'dynamax_tier4': ['Tier 4', 'TIER 4', 'tier 4'],
            'dynamax_tier5': ['Tier 5', 'TIER 5', 'tier 5'],
            'gigantamax': ['Gigantamax', 'GIGANTAMAX', 'gigantamax']
        }
        
        for element in soup.find_all(['h2', 'h3', 'div']):
            text = element.get_text().strip()
            
            for tier_key, tier_patterns in tier_map.items():
                if any(pattern in text for pattern in tier_patterns):
                    current_tier = tier_key
                    print(f"    Found {current_tier} section")
                    break
            
            if current_tier and current_tier in raid_data:
                imgs = element.find_all('img')
                for img in imgs:
                    alt = img.get('alt', '')
                    if alt and len(alt) > 2:
                        clean_name = alt.replace('D-Max', '').replace('Shiny', '').replace('ShinyD-Max', '').strip()
                        
                        if not clean_name or clean_name in social_media or clean_name.lower() in type_words:
                            continue
                        
                        existing_names = [r['name'] for r in raid_data[current_tier]]
                        if clean_name and clean_name not in existing_names:
                            image_url = get_raid_image_url(clean_name, current_tier)
                            raid_data[current_tier].append({
                                "name": clean_name,
                                "imageUrl": image_url
                            })
                            print(f"      Added to {current_tier}: {clean_name} -> {image_url}")
        
        for tier in raid_data:
            raid_data[tier] = sorted(raid_data[tier], key=lambda x: x['name'])
        
        print(f"\n  📊 MAX BATTLES SUMMARY:")
        print(f"    Dynamax Tier 1: {len(raid_data['dynamax_tier1'])}")
        print(f"    Dynamax Tier 2: {len(raid_data['dynamax_tier2'])}")
        print(f"    Dynamax Tier 3: {len(raid_data['dynamax_tier3'])}")
        print(f"    Dynamax Tier 4: {len(raid_data['dynamax_tier4'])}")
        print(f"    Dynamax Tier 5: {len(raid_data['dynamax_tier5'])}")
        print(f"    Gigantamax: {len(raid_data['gigantamax'])}")
        
        return raid_data
    except Exception as e:
        print(f"    ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🚀 Starting Snack Nap scraper...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    raids = scrape_snacknap_raids()
    max_battles = scrape_snacknap_maxbattles() or {}
    
    new_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "tier1": raids.get("tier1", []),
        "tier3": raids.get("tier3", []),
        "dynamax_tier1": max_battles.get("dynamax_tier1", []),
        "dynamax_tier2": max_battles.get("dynamax_tier2", []),
        "dynamax_tier3": max_battles.get("dynamax_tier3", []),
        "dynamax_tier4": max_battles.get("dynamax_tier4", []),
        "dynamax_tier5": max_battles.get("dynamax_tier5", []),
        "gigantamax": max_battles.get("gigantamax", [])
    }
    
    with open('current_raids.json', 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print("\n💾 Saved to current_raids.json")
    print("\n📸 Sample raid image URLs:")
    for tier in ['tier1', 'tier3', 'gigantamax']:
        if new_data.get(tier) and len(new_data[tier]) > 0:
            sample = new_data[tier][0]
            print(f"   {tier}: {sample['name']} -> {sample['imageUrl']}")

if __name__ == "__main__":
    main()
