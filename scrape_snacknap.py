import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def fetch_scrapedduck_raids():
    """Fetch current raids from ScrapedDuck API"""
    try:
        url = "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/data/raids.min.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  ScrapedDuck API returned {response.status_code}")
            return []
    except Exception as e:
        print(f"  Error fetching ScrapedDuck: {e}")
        return []

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
            if "Tier 1" in tier_title:
                current_tier = "tier1"
            elif "Tier 3" in tier_title:
                current_tier = "tier3"
            else:
                continue
            
            tier_container = h2.find_next('div', class_=re.compile(r'row g-2'))
            if not tier_container:
                continue
            
            pokemon_cards = tier_container.find_all('a', href=re.compile(r'/pokedex/pokemon/'))
            
            for card in pokemon_cards:
                name_elem = card.find('p', class_='pkmn-title')
                if name_elem:
                    raw_name = name_elem.get_text().strip()
                    clean_name = re.sub(r'\s+', ' ', raw_name).strip()
                    
                    if clean_name and clean_name not in raid_data[current_tier]:
                        raid_data[current_tier].append(clean_name)
                        print(f"      Added to {current_tier}: {clean_name}")
        
        return raid_data
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return {"tier1": [], "tier3": []}

def scrape_snacknap_maxbattles():
    """Scrape Dynamax and Gigantamax battles"""
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
        
        # Filter out invalid names
        invalid_names = ['bug', 'dark', 'dragon', 'electric', 'fairy', 'fighting', 'fire', 
                         'flying', 'ghost', 'grass', 'ground', 'ice', 'normal', 'poison', 
                         'psychic', 'rock', 'steel', 'water', 'Search...', 'Telegram', 
                         'Facebook', 'Instagram', 'Discord', 'Threads', 'Bluesky']
        
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
                        
                        if not clean_name or clean_name in invalid_names or clean_name.lower() in invalid_names:
                            continue
                        
                        if clean_name and clean_name not in raid_data[current_tier]:
                            raid_data[current_tier].append(clean_name)
                            print(f"      Added to {current_tier}: {clean_name}")
        
        return raid_data
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

def main():
    print("🚀 Starting Snack Nap scraper...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get SnackNap data
    raids = scrape_snacknap_raids()
    max_battles = scrape_snacknap_maxbattles() or {}
    
    # Get ScrapedDuck data (5-Star, Mega, Shadow)
    scrapedduck_raids = fetch_scrapedduck_raids()
    print(f"  📡 ScrapedDuck: {len(scrapedduck_raids)} raids found")
    
    # Filter ScrapedDuck raids by tier for the JSON output
    filtered_scrapedduck = []
    for raid in scrapedduck_raids:
        tier = raid.get('tier', '')
        name = raid.get('name', '')
        # Keep 5-Star, Mega, and ALL Shadow raids (including 1-star and 3-star Shadow)
        if ('5-Star' in tier or 
            'Mega' in tier or 
            'Shadow' in name or 
            'Shadow' in tier):
            filtered_scrapedduck.append(raid)
            print(f"      Kept ScrapedDuck: {name} ({tier})")
    
    # Combine all data
    new_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "tier1": raids.get("tier1", []),
        "tier3": raids.get("tier3", []),
        "dynamax_tier1": max_battles.get("dynamax_tier1", []),
        "dynamax_tier2": max_battles.get("dynamax_tier2", []),
        "dynamax_tier3": max_battles.get("dynamax_tier3", []),
        "dynamax_tier4": max_battles.get("dynamax_tier4", []),
        "dynamax_tier5": max_battles.get("dynamax_tier5", []),
        "gigantamax": max_battles.get("gigantamax", []),
        "scrapedduck_raids": filtered_scrapedduck  # ADD THIS - contains 5-Star, Mega, Shadow
    }
    
    with open('current_raids.json', 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print("\n💾 Saved to current_raids.json")
    print(f"   SnackNap Tier 1: {len(new_data['tier1'])}")
    print(f"   SnackNap Tier 3: {len(new_data['tier3'])}")
    print(f"   Dynamax/Gmax: {len(new_data['dynamax_tier1']) + len(new_data['dynamax_tier2']) + len(new_data['dynamax_tier3']) + len(new_data['gigantamax'])}")
    print(f"   ScrapedDuck (5-Star/Mega/Shadow): {len(filtered_scrapedduck)}")

if __name__ == "__main__":
    main()