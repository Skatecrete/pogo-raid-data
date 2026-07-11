import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def scrape_snacknap_raids():
    """Scrape all raid tiers from snacknap.com/raids"""
    print("  📡 Fetching all raid tiers from SnackNap...")
    url = "https://snacknap.com/raids"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        raid_data = {
            "tier1": [],
            "tier3": [],
            "tier5": [],
            "mega": [],
            "primal": [],
            "ultra_beasts": [],
            "super_mega": []
        }
        
        tier_map = {
            't1': 'tier1',
            't3': 'tier3',
            't5': 'tier5',
            't6': 'mega',
            't8': 'ultra_beasts',
            't10': 'primal',
            't17': 'super_mega',
        }
        
        tier_cards = soup.find_all('div', class_='to-card')
        print(f"  Found {len(tier_cards)} tier cards")
        
        for card in tier_cards:
            data_tier = card.get('data-tier', '')
            current_tier = tier_map.get(data_tier)
            if not current_tier:
                continue
            
            pokemon_names = []
            
            # ========== ONLY USE TITLE ATTRIBUTE ==========
            for a in card.find_all('a'):
                title = a.get('title', '')
                if title and len(title) > 3:
                    pokemon_names.append(title)
            # =============================================
            
            pokemon_names = list(set(pokemon_names))
            
            # ========== SPECIAL HANDLING ==========
            if current_tier == 'ultra_beasts':
                print(f"  🔍 Ultra Beast raw: {pokemon_names}")
                known = ['nihilego', 'buzzwole', 'pheromosa', 'xurkitree', 'celesteela', 
                        'kartana', 'guzzlord', 'poipole', 'naganadel', 'stakataka', 
                        'blacephalon', 'necrozma']
                pokemon_names = [n for n in pokemon_names if n.lower() in known]
                print(f"  🔍 Ultra Beast final: {pokemon_names}")
            
            if current_tier == 'primal':
                print(f"  🔍 Primal raw: {pokemon_names}")
                pokemon_names = [f"Primal {n}" for n in pokemon_names if n and 'primal' not in n.lower()]
                print(f"  🔍 Primal final: {pokemon_names}")
            
            if current_tier == 'super_mega':
                print(f"  🔍 Super Mega raw: {pokemon_names}")
                pokemon_names = [f"Super Mega {n}" for n in pokemon_names if n and 'super mega' not in n.lower()]
                print(f"  🔍 Super Mega final: {pokemon_names}")
            
            for name in pokemon_names:
                if name and name not in raid_data[current_tier]:
                    raid_data[current_tier].append(name)
                    print(f"      Added to {current_tier}: {name}")
        
        print(f"\n  📊 FINAL RESULTS:")
        print(f"    Ultra Beasts: {len(raid_data['ultra_beasts'])} - {raid_data['ultra_beasts']}")
        print(f"    Primal: {len(raid_data['primal'])} - {raid_data['primal']}")
        print(f"    Super Mega: {len(raid_data['super_mega'])} - {raid_data['super_mega']}")
        
        return raid_data
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"tier1": [], "tier3": [], "tier5": [], "mega": [], "primal": [], "ultra_beasts": [], "super_mega": []}


def scrape_snacknap_maxbattles():
    """Scrape Dynamax tiers from snacknap.com/max-battles"""
    print("  📡 Fetching Dynamax battles...")
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
            "dynamax_tier5": []
        }
        
        invalid_names = ['Telegram', 'Facebook', 'Instagram', 'Threads', 'Bluesky', 'X', 'Twitter', 'Discord', 'Patreon', 'YouTube', 'Twitch', 'Search...', 'Snacknap']
        type_words = ['fire', 'water', 'grass', 'electric', 'bug', 'ground', 'flying', 'ghost', 
                     'ice', 'psychic', 'dragon', 'dark', 'steel', 'fairy', 'rock', 'fighting', 
                     'poison', 'normal', 'shiny']
        
        current_tier = None
        
        for element in soup.find_all(['h2', 'h3', 'div']):
            text = element.get_text().strip()
            
            if 'Tier 1' in text or 'Tier 1' in text.upper():
                current_tier = 'dynamax_tier1'
                print(f"    Found Dynamax Tier 1")
                continue
            elif 'Tier 2' in text or 'Tier 2' in text.upper():
                current_tier = 'dynamax_tier2'
                print(f"    Found Dynamax Tier 2")
                continue
            elif 'Tier 3' in text or 'Tier 3' in text.upper():
                current_tier = 'dynamax_tier3'
                print(f"    Found Dynamax Tier 3")
                continue
            elif 'Tier 5' in text or 'Tier 5' in text.upper():
                current_tier = 'dynamax_tier5'
                print(f"    Found Dynamax Tier 5")
                continue
            
            if current_tier and current_tier in raid_data:
                imgs = element.find_all('img')
                for img in imgs:
                    alt = img.get('alt', '')
                    if alt and len(alt) > 2:
                        clean_name = alt.replace('D-Max', '').replace('Shiny', '').replace('ShinyD-Max', '').strip()
                        if not clean_name:
                            continue
                        if clean_name in invalid_names:
                            continue
                        if clean_name.lower() in type_words:
                            continue
                        if 'G-Max' in clean_name or 'Gigantamax' in clean_name:
                            continue
                        if clean_name and clean_name not in raid_data[current_tier]:
                            raid_data[current_tier].append(clean_name)
                            print(f"      Added to {current_tier}: {clean_name}")
        
        for tier in raid_data:
            raid_data[tier] = sorted(list(set(raid_data[tier])))
        
        print(f"\n  📊 MAX BATTLES SUMMARY:")
        print(f"    Dynamax Tier 1: {len(raid_data['dynamax_tier1'])}")
        print(f"    Dynamax Tier 2: {len(raid_data['dynamax_tier2'])}")
        print(f"    Dynamax Tier 3: {len(raid_data['dynamax_tier3'])}")
        print(f"    Dynamax Tier 5: {len(raid_data['dynamax_tier5'])}")
        
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
        "tier5": raids.get("tier5", []),
        "mega": raids.get("mega", []),
        "primal": raids.get("primal", []),
        "ultra_beasts": raids.get("ultra_beasts", []),
        "super_mega": raids.get("super_mega", []),
        "dynamax_tier1": max_battles.get("dynamax_tier1", []),
        "dynamax_tier2": max_battles.get("dynamax_tier2", []),
        "dynamax_tier3": max_battles.get("dynamax_tier3", []),
        "dynamax_tier5": max_battles.get("dynamax_tier5", [])
    }
    
    with open('current_raids.json', 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print("\n💾 Saved to current_raids.json")
    print(json.dumps(new_data, indent=2))


if __name__ == "__main__":
    main()
