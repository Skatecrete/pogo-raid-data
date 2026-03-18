import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def scrape_snacknap():
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
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        # Scrape regular raids
        print("📡 Fetching regular raids...")
        raids_url = "https://www.snacknap.com/raids"
        response = requests.get(raids_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all raid sections
        content = soup.get_text()
        
        # Simple extraction patterns (you can expand these)
        if "Zacian" in content:
            raid_data["tier5"] = ["Zacian", "Zamazenta"]
        if "Mega Steelix" in content:
            raid_data["mega"] = ["Mega Steelix", "Mega Slowbro"]
        if "Pinsir" in content:
            raid_data["tier3"] = ["Pinsir", "Scizor", "Kleavor"]
        if "Blipbug" in content:
            raid_data["tier1"] = ["Blipbug"]
        if "Shadow Latias" in content:
            raid_data["shadow"] = [
                "Shadow Latias", "Shadow Dratini", "Shadow Gligar",
                "Shadow Cacnea", "Shadow Joltik", "Shadow Alolan Marowak",
                "Shadow Lapras", "Shadow Stantler"
            ]
        
        # Scrape max battles
        print("📡 Fetching max battles...")
        max_url = "https://www.snacknap.com/max-battles"
        response = requests.get(max_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text()
        
        # Dynamax Tier 1
        dynamax_t1 = ["Bulbasaur", "Charmander", "Squirtle", "Pidove", "Woobat", 
                     "Drilbur", "Inkay", "Bounsweet", "Grookey", "Sobble", 
                     "Skwovet", "Wooloo", "Scorbunny", "Trubbish", "Rookidee",
                     "Spheal", "Roggenrola", "Gastly", "Caterpie", "Growlithe",
                     "Krabby", "Kabuto", "Omanyte", "Abra", "Ralts", "Hatenna"]
        raid_data["dynamax_tier1"] = [p for p in dynamax_t1 if p in content]
        
        # Dynamax Tier 2
        dynamax_t2 = ["Machop", "Darumaka", "Eevee", "Shuckle", "Wailmer"]
        raid_data["dynamax_tier2"] = [p for p in dynamax_t2 if p in content]
        
        # Dynamax Tier 3
        dynamax_t3 = ["Sableye", "Chansey", "Drampa", "Hitmonchan", "Hitmonlee",
                     "Cryogonal", "Passimian", "Beldum", "Falinks"]
        raid_data["dynamax_tier3"] = [p for p in dynamax_t3 if p in content]
        
        # Print summary
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
