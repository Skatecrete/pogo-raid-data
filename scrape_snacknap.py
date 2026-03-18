import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_snacknap_raids():
    """Scrape regular raids from Snack Nap"""
    print("  📡 Fetching regular raids...")
    url = "https://www.snacknap.com/raids"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        raid_data = {
            "tier5": [], "mega": [], "tier3": [], "tier1": [], "shadow": []
        }
        
        pokemon_container = soup.find('div', id='pokemon')
        if not pokemon_container:
            return raid_data
        
        current_tier = None
        for element in pokemon_container.find_all(['div', 'h2'], recursive=True):
            if element.name == 'h2':
                header = element.get_text().strip()
                if 'Tier 1' in header:
                    current_tier = 'tier1'
                elif 'Tier 3' in header:
                    current_tier = 'tier3'
                elif 'Legendary' in header or 'Tier 5' in header:
                    current_tier = 'tier5'
                elif 'Mega' in header:
                    current_tier = 'mega'
                elif 'Shadow' in header:
                    current_tier = 'shadow'
                continue
            
            if current_tier and element.name == 'div' and 'col-xl-2' in element.get('class', []):
                link = element.find('a')
                if link:
                    title = link.get('title', '')
                    if title and title not in raid_data[current_tier]:
                        raid_data[current_tier].append(title.strip())
                        print(f"    ✅ Added {title} to {current_tier}")
        
        return raid_data
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

def scrape_snacknap_maxbattles():
    """Scrape Dynamax/Gigantamax raids from Snack Nap"""
    print("  📡 Fetching max battles...")
    url = "https://www.snacknap.com/max-battles"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        raid_data = {
            "dynamax_tier1": [], "dynamax_tier2": [], "dynamax_tier3": [], "gigantamax": []
        }
        
        pokemon_container = soup.find('div', id='pokemon')
        if not pokemon_container:
            return raid_data
        
        current_tier = None
        for element in pokemon_container.find_all(['div', 'h2'], recursive=True):
            if element.name == 'h2':
                header = element.get_text().strip()
                if 'Tier 1' in header:
                    current_tier = 'dynamax_tier1'
                elif 'Tier 2' in header:
                    current_tier = 'dynamax_tier2'
                elif 'Tier 3' in header:
                    current_tier = 'dynamax_tier3'
                elif 'Gigantamax' in header:
                    current_tier = 'gigantamax'
                continue
            
            if current_tier and element.name == 'div' and 'col-xl-2' in element.get('class', []):
                link = element.find('a')
                if link:
                    title = link.get('title', '')
                    if title and title not in raid_data[current_tier]:
                        raid_data[current_tier].append(title.strip())
                        print(f"    ✅ Added {title} to {current_tier}")
        
        return raid_data
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

def main():
    print("🚀 Starting Snack Nap scraper...")
    
    # Scrape both
    regular = scrape_snacknap_raids() or {}
    max_battles = scrape_snacknap_maxbattles() or {}
    
    # Combine data
    combined = {
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        **regular,
        **max_battles
    }
    
    # Save to file
    with open('current_raids.json', 'w') as f:
        json.dump(combined, f, indent=2)
    
    # Print summary
    print("\n📊 TOTAL SUMMARY:")
    total = 0
    for tier, pokemon in combined.items():
        if tier != 'last_updated':
            print(f"  {tier}: {len(pokemon)} Pokemon")
            total += len(pokemon)
    print(f"  TOTAL: {total} Pokemon")
    print(f"\n💾 Saved to current_raids.json")

if __name__ == "__main__":
    main()
