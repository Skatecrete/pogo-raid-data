import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def scrape_snacknap_raids():
    """Scrape all raid data from Snack Nap"""
    
    print("🚀 Starting Snack Nap scraper...")
    
    # Initialize data structure
    raid_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "tier5": [],
        "mega": [],
        "tier3": [],
        "tier1": [],
        "shadow": [],
        "dynamax_tier1": [],
        "dynamax_tier2": [],
        "dynamax_tier3": [],
        "gigantamax": []
    }
    
    # Headers to look like a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # Scrape regular raids
        print("📡 Fetching regular raids...")
        raids_url = "https://www.snacknap.com/raids"
        response = requests.get(raids_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all raid sections
        current_tier = None
        
        for element in soup.find_all(['h2', 'h3', 'ul']):
            if element.name in ['h2', 'h3']:
                heading = element.get_text()
                if 'Tier 1' in heading:
                    current_tier = 'tier1'
                    print("📋 Found Tier 1 section")
                elif 'Tier 3' in heading:
                    current_tier = 'tier3'
                    print("📋 Found Tier 3 section")
                elif 'Tier 5' in heading or 'Legendary' in heading:
                    current_tier = 'tier5'
                    print("📋 Found Tier 5 section")
                elif 'Mega' in heading:
                    current_tier = 'mega'
                    print("📋 Found Mega section")
                elif 'Shadow' in heading:
                    current_tier = 'shadow'
                    print("📋 Found Shadow section")
                else:
                    current_tier = None
            
            # If this is a list and we're in a tier, extract Pokemon
            elif element.name == 'ul' and current_tier:
                for item in element.find_all('li'):
                    link = item.find('a')
                    if link:
                        text = link.get_text()
                        # Extract just the Pokemon name (first word usually)
                        pokemon = text.split()[0]
                        # Clean up
                        pokemon = pokemon.strip()
                        
                        if pokemon and pokemon not in raid_data[current_tier]:
                            raid_data[current_tier].append(pokemon)
                            print(f"  ✅ Added {pokemon} to {current_tier}")
        
        # Scrape max battles
        print("\n📡 Fetching max battles...")
        max_url = "https://www.snacknap.com/max-battles"
        response = requests.get(max_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        current_tier = None
        
        for element in soup.find_all(['h2', 'h3', 'ul']):
            if element.name in ['h2', 'h3']:
                heading = element.get_text()
                if 'Dynamax 1-Star' in heading or 'Dynamax Tier 1' in heading:
                    current_tier = 'dynamax_tier1'
                    print("📋 Found Dynamax Tier 1 section")
                elif 'Dynamax 2-Star' in heading or 'Dynamax Tier 2' in heading:
                    current_tier = 'dynamax_tier2'
                    print("📋 Found Dynamax Tier 2 section")
                elif 'Dynamax 3-Star' in heading or 'Dynamax Tier 3' in heading:
                    current_tier = 'dynamax_tier3'
                    print("📋 Found Dynamax Tier 3 section")
                elif 'Gigantamax' in heading:
                    current_tier = 'gigantamax'
                    print("📋 Found Gigantamax section")
                else:
                    current_tier = None
            
            elif element.name == 'ul' and current_tier:
                for item in element.find_all('li'):
                    link = item.find('a')
                    if link:
                        text = link.get_text()
                        # Extract Pokemon name (clean up "D-max" prefixes if present)
                        pokemon = text.replace('D-max', '').replace('G-max', '').strip().split()[0]
                        
                        if pokemon and pokemon not in raid_data[current_tier]:
                            raid_data[current_tier].append(pokemon)
                            print(f"  ✅ Added {pokemon} to {current_tier}")
        
        # Print summary
        print("\n📊 SCRAPE SUMMARY:")
        total = 0
        for tier, pokemon in raid_data.items():
            if tier != 'last_updated':
                print(f"  {tier}: {len(pokemon)} Pokemon")
                total += len(pokemon)
        print(f"  TOTAL: {total} Pokemon")
        
        return raid_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def save_raid_data(data):
    """Save raid data to JSON file"""
    if data:
        with open('current_raids.json', 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Saved to current_raids.json")
        return True
    return False

if __name__ == "__main__":
    print("=" * 50)
    data = scrape_snacknap_raids()
    if data:
        save_raid_data(data)
        print("\n✅ Scrape complete!")
    else:
        print("\n❌ Scrape failed")
        exit(1)
