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
        
        # ========== UPDATED TIER MAPPING ==========
        # t1 = 1-Star, t3 = 3-Star, t5 = 5-Star
        # t6 = Mega, t10 = Primal, t11 = Ultra Beasts, t12 = Super Mega
        tier_map = {
            't1': 'tier1',
            't3': 'tier3',
            't5': 'tier5',
            't6': 'mega',
            't10': 'primal',
            't11': 'ultra_beasts',
            't12': 'super_mega'
        }
        # ========================================
        
        # Find all tier cards - try multiple class patterns
        tier_cards = soup.find_all('div', class_='to-card')
        
        # If no cards found, try alternative class names
        if not tier_cards:
            tier_cards = soup.find_all('div', class_=re.compile(r'card|tier|raid', re.I))
        
        for card in tier_cards:
            data_tier = card.get('data-tier', '')
            
            # Try to get tier from class if data-tier is missing
            if not data_tier:
                for class_name in card.get('class', []):
                    if class_name.startswith('t'):
                        data_tier = class_name
                        break
            
            current_tier = tier_map.get(data_tier)
            if not current_tier:
                continue
            
            # Try multiple ways to find Pokémon names
            pokemon_names = []
            
            # Method 1: snk-tile with a/p
            for tile in card.find_all('div', class_='snk-tile'):
                link = tile.find('a')
                if link:
                    name = link.get('title', '') or link.get_text().strip()
                    if name:
                        pokemon_names.append(name)
            
            # Method 2: direct a/p tags (fallback)
            if not pokemon_names:
                for p in card.find_all('p'):
                    text = p.get_text().strip()
                    if text and len(text) > 2 and not text.startswith('Tier'):
                        # Check if this is a Pokémon name (not a label)
                        if not any(word in text.lower() for word in ['tier', 'star', 'mega', 'primal', 'ultra']):
                            pokemon_names.append(text)
            
            # Method 3: any link with title
            if not pokemon_names:
                for a in card.find_all('a'):
                    title = a.get('title', '')
                    if title and len(title) > 2:
                        pokemon_names.append(title)
            
            # Add unique names to raid_data
            for name in pokemon_names:
                if name and name not in raid_data[current_tier]:
                    # For Mega raids, KEEP the "Mega " prefix
                    # For others, keep as-is
                    raid_data[current_tier].append(name)
                    print(f"      Added to {current_tier}: {name}")
        
        print(f"\n  📊 SNACKNAP RAID SUMMARY:")
        print(f"    Tier 1: {len(raid_data['tier1'])}")
        print(f"    Tier 3: {len(raid_data['tier3'])}")
        print(f"    Tier 5: {len(raid_data['tier5'])}")
        print(f"    Mega: {len(raid_data['mega'])}")
        print(f"    Primal: {len(raid_data['primal'])}")
        print(f"    Ultra Beasts: {len(raid_data['ultra_beasts'])}")
        print(f"    Super Mega: {len(raid_data['super_mega'])}")
        
        return raid_data
        
    except Exception as e:
        print(f"    ❌ Error scraping raids: {e}")
        import traceback
        traceback.print_exc()
        return {"tier1": [], "tier3": [], "tier5": [], "mega": [], "primal": [], "ultra_beasts": [], "super_mega": []}


def scrape_snacknap_maxbattles():
    """Scrape Dynamax Tier 1,2,3,5 from snacknap.com/max-battles (NO GIGANTAMAX)"""
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
                print(f"    Found Dynamax Tier 1 section")
                continue
            elif 'Tier 2' in text or 'Tier 2' in text.upper():
                current_tier = 'dynamax_tier2'
                print(f"    Found Dynamax Tier 2 section")
                continue
            elif 'Tier 3' in text or 'Tier 3' in text.upper():
                current_tier = 'dynamax_tier3'
                print(f"    Found Dynamax Tier 3 section")
                continue
            elif 'Tier 5' in text or 'Tier 5' in text.upper():
                current_tier = 'dynamax_tier5'
                print(f"    Found Dynamax Tier 5 section")
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
