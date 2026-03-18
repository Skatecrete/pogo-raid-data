import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def clean_pokemon_name(text):
    """Extract clean Pokemon name from link text"""
    # Remove common prefixes
    text = text.replace('Shiny', '').replace('D-Max', '').replace('G-Max', '')
    # Take first word and clean it
    return text.strip().split()[0]

def scrape_snacknap():
    """Scrape all raid data from Snack Nap"""
    
    print("🚀 Starting Snack Nap scraper...")
    
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
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        # Scrape regular raids
        print("📡 Fetching regular raids...")
        raids_url = "https://www.snacknap.com/raids"
        response = requests.get(raids_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all Pokemon links
        for link in soup.find_all('a', href=True):
            if '/pokemon/' in link['href']:
                text = link.get_text()
                pokemon = clean_pokemon_name(text)
                
                # Categorize based on context (you'll need to expand this)
                if 'Zacian' in text or 'Zamazenta' in text:
                    if pokemon not in raid_data['tier5']:
                        raid_data['tier5'].append(pokemon)
                elif 'Mega' in text:
                    if pokemon not in raid_data['mega']:
                        raid_data['mega'].append(pokemon)
                elif 'Shadow' in text:
                    # Add D-Max prefix for shadow Pokemon
                    full_name = f"Shadow {pokemon}"
                    if full_name not in raid_data['shadow']:
                        raid_data['shadow'].append(full_name)
        
        # Scrape max battles
        print("📡 Fetching max battles...")
        max_url = "https://www.snacknap.com/max-battles"
        response = requests.get(max_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        current_tier = None
        
        for element in soup.find_all(['h2', 'h3', 'ul']):
            if element.name in ['h2', 'h3']:
                heading = element.get_text()
                if 'Tier 1' in heading:
                    current_tier = 'dynamax_tier1'
                    print("📋 Found Dynamax Tier 1")
                elif 'Tier 2' in heading:
                    current_tier = 'dynamax_tier2'
                    print("📋 Found Dynamax Tier 2")
                elif 'Tier 3' in heading:
                    current_tier = 'dynamax_tier3'
                    print("📋 Found Dynamax Tier 3")
                elif 'Gigantamax' in heading:
                    current_tier = 'gigantamax'
                    print("📋 Found Gigantamax")
                else:
                    current_tier = None
            
            elif element.name == 'ul' and current_tier:
                for item in element.find_all('li'):
                    link = item.find('a')
                    if link:
                        text = link.get_text()
                        # Keep the D-Max prefix in the JSON
                        pokemon = text.strip()
                        if pokemon and pokemon not in raid_data[current_tier]:
                            raid_data[current_tier].append(pokemon)
                            print(f"  ✅ Added {pokemon}")
        
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
    data = scrape_snacknap()
    if data:
        save_raid_data(data)
        print("\n✅ Scrape complete!")
    else:
        print("\n❌ Scrape failed")
        exit(1)
