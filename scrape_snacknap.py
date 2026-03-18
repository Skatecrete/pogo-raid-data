import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def scrape_snacknap_maxbattles():
    """Scrape all Dynamax and Gigantamax raids from Snack Nap"""
    
    print("🚀 Starting Snack Nap Max Battles scraper...")
    
    url = "https://www.snacknap.com/max-battles"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Initialize data structure
        raid_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "dynamax_tier1": [],
            "dynamax_tier2": [],
            "dynamax_tier3": [],
            "gigantamax": []  # If any
        }
        
        # Find the main pokemon container
        pokemon_container = soup.find('div', id='pokemon')
        if not pokemon_container:
            print("❌ Could not find pokemon container")
            return None
        
        # Find all tier sections
        current_tier = None
        
        # Iterate through all elements in the container
        for element in pokemon_container.find_all(['div', 'h2'], recursive=True):
            # Check if this is a tier header
            if element.name == 'h2':
                header_text = element.get_text().strip()
                if 'Tier 1' in header_text:
                    current_tier = 'dynamax_tier1'
                    print(f"📋 Found {header_text}")
                elif 'Tier 2' in header_text:
                    current_tier = 'dynamax_tier2'
                    print(f"📋 Found {header_text}")
                elif 'Tier 3' in header_text:
                    current_tier = 'dynamax_tier3'
                    print(f"📋 Found {header_text}")
                elif 'Gigantamax' in header_text:
                    current_tier = 'gigantamax'
                    print(f"📋 Found {header_text}")
                continue
            
            # If we're in a tier and find a pokemon card
            if current_tier and element.name == 'div' and 'col-xl-2' in element.get('class', []):
                # Find the pokemon link
                link = element.find('a')
                if not link:
                    continue
                
                # Extract Pokemon name
                title = link.get('title', '')
                if not title:
                    continue
                
                # Get the full name with D-Max prefix
                pokemon_name = title.strip()
                
                # Check if it's shiny (has the shiny-dark image)
                shiny_img = element.find('img', class_='shiny')
                is_shiny = shiny_img is not None
                
                # Get Pokemon ID from URL
                href = link.get('href', '')
                pokemon_id = 0
                if '/pokedex/pokemon/' in href:
                    try:
                        pokemon_id = int(href.split('/')[-1])
                    except:
                        pass
                
                # Only add if we have a name
                if pokemon_name and pokemon_name not in raid_data[current_tier]:
                    raid_data[current_tier].append(pokemon_name)
                    shiny_mark = "✨" if is_shiny else "  "
                    print(f"  {shiny_mark} Added {pokemon_name} (ID: {pokemon_id}) to {current_tier}")
        
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

def save_raid_data(data, filename='current_raids.json'):
    """Save raid data to JSON file"""
    if data:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Saved to {filename}")
        return True
    return False

if __name__ == "__main__":
    print("=" * 50)
    data = scrape_snacknap_maxbattles()
    if data:
        save_raid_data(data)
        print("\n✅ Scrape complete!")
    else:
        print("\n❌ Scrape failed")
        exit(1)
