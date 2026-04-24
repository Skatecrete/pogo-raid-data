import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

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
                    
                    if clean_name and clean_name not in raid_data[current_tier]:
                        raid_data[current_tier].append(clean_name)
                        print(f"      Added to {current_tier}: {clean_name}")
        
        print(f"\n  📊 SNACKNAP RAID SUMMARY:")
        print(f"    Tier 1: {len(raid_data['tier1'])} - {raid_data['tier1']}")
        print(f"    Tier 3: {len(raid_data['tier3'])} - {raid_data['tier3']}")
        
        return raid_data
    except Exception as e:
        print(f"    ❌ Error scraping raids: {e}")
        import traceback
        traceback.print_exc()
        return {"tier1": [], "tier3": []}

def scrape_snacknap_mega_raids():
    """Scrape Mega raids from snacknap.com/raids"""
    print("  📡 Fetching Mega Raids from SnackNap...")
    url = "https://snacknap.com/raids"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        mega_raids = []
        
        # Find Mega Raids section
        for h2 in soup.find_all('h2'):
            if 'Mega' in h2.get_text():
                print(f"    Found Mega Raids section")
                tier_container = h2.find_next('div', class_=re.compile(r'row g-2'))
                if tier_container:
                    pokemon_cards = tier_container.find_all('a', href=re.compile(r'/pokedex/pokemon/'))
                    for card in pokemon_cards:
                        name_elem = card.find('p', class_='pkmn-title')
                        if name_elem:
                            raw_name = name_elem.get_text().strip()
                            clean_name = re.sub(r'\s+', ' ', raw_name).strip()
                            if clean_name and clean_name not in mega_raids:
                                mega_raids.append(clean_name)
                                print(f"      Added Mega: {clean_name}")
        
        print(f"    Mega Raids: {len(mega_raids)} - {mega_raids}")
        return mega_raids
    except Exception as e:
        print(f"    ❌ Error scraping Mega raids: {e}")
        return []

def scrape_snacknap_maxbattles():
    """Scrape Dynamax Tier 1,2,3 and Gigantamax from snacknap.com/max-battles"""
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
            "gigantamax": []
        }
        
        # ADD 'Search...' to this list
        invalid_names = ['Telegram', 'Facebook', 'Instagram', 'Threads', 'Bluesky', 'X', 'Twitter', 'Discord', 'Patreon', 'YouTube', 'Twitch', 'Search...']
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
            elif 'Gigantamax' in text:
                current_tier = 'gigantamax'
                print(f"    Found Gigantamax section")
                continue
            
            if current_tier and current_tier in raid_data:
                imgs = element.find_all('img')
                for img in imgs:
                    alt = img.get('alt', '')
                    if alt and len(alt) > 2:
                        clean_name = alt.replace('D-Max', '').replace('Shiny', '').replace('ShinyD-Max', '').strip()
                        
                        if not clean_name:
                            continue
                        # Check against invalid_names (now includes 'Search...')
                        if clean_name in invalid_names:
                            continue
                        if clean_name.lower() in type_words:
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
        "gigantamax": max_battles.get("gigantamax", [])
    }
    
    with open('current_raids.json', 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print("\n💾 Saved to current_raids.json")
    print(json.dumps(new_data, indent=2))

if __name__ == "__main__":
    main()
