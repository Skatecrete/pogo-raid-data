import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os

def scrape_pokemongohub():
    """Scrape current raid data from Pokémon GO Hub"""
    
    url = "https://pokemongohub.net/post/guide/current-go-raids/"
    print(f"🌐 Fetching {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Initialize raid data structure
        raid_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "tier5": [],
            "mega": [],
            "tier3": [],
            "tier1": [],
            "shadow": []
        }
        
        # Get the main content text
        content = soup.get_text()
        
        # Extract 5-Star raids
        tier5_match = re.search(r'5-Star Raids:?\s*([^<\n]+)', content, re.IGNORECASE)
        if tier5_match:
            tier5_text = tier5_match.group(1)
            # Clean up the text
            tier5_text = re.sub(r'\([^)]*\)', '', tier5_text)  # Remove parentheses
            raid_data["tier5"] = [name.strip() for name in tier5_text.split(',') if name.strip()]
            print(f"✅ Found 5-Star: {raid_data['tier5']}")
        
        # Extract Mega raids
        mega_match = re.search(r'Mega Raids:?\s*([^<\n]+)', content, re.IGNORECASE)
        if mega_match:
            mega_text = mega_match.group(1)
            raid_data["mega"] = [name.strip() for name in mega_text.split(',') if name.strip()]
            print(f"✅ Found Mega: {raid_data['mega']}")
        
        # Extract 3-Star raids
        tier3_match = re.search(r'3-Star Raids:?\s*([^<\n]+)', content, re.IGNORECASE)
        if tier3_match:
            tier3_text = tier3_match.group(1)
            raid_data["tier3"] = [name.strip() for name in tier3_text.split(',') if name.strip()]
            print(f"✅ Found 3-Star: {raid_data['tier3']}")
        
        # Extract 1-Star raids
        tier1_match = re.search(r'1-Star Raids:?\s*([^<\n]+)', content, re.IGNORECASE)
        if tier1_match:
            tier1_text = tier1_match.group(1)
            raid_data["tier1"] = [name.strip() for name in tier1_text.split(',') if name.strip()]
            print(f"✅ Found 1-Star: {raid_data['tier1']}")
        
        # Extract Shadow raids
        shadow_match = re.search(r'5-Star Shadow Raid:?\s*([^<\n]+)', content, re.IGNORECASE)
        if shadow_match:
            shadow_text = shadow_match.group(1)
            raid_data["shadow"] = [name.strip() for name in shadow_text.split(',') if name.strip()]
            print(f"✅ Found Shadow: {raid_data['shadow']}")
        
        return raid_data
        
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Parsing error: {e}")
        return None

def load_current_data():
    """Load existing JSON file if it exists"""
    try:
        if os.path.exists('current_raids.json'):
            with open('current_raids.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def save_raid_data(data):
    """Save raid data to JSON file"""
    with open('current_raids.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"💾 Saved to current_raids.json")

def has_data_changed(old_data, new_data):
    """Check if raid data has actually changed"""
    if not old_data or not new_data:
        return True
    
    # Compare each tier (ignore last_updated)
    for tier in ['tier5', 'mega', 'tier3', 'tier1', 'shadow']:
        if old_data.get(tier, []) != new_data.get(tier, []):
            return True
    return False

if __name__ == "__main__":
    print("🚀 Starting raid data update...")
    
    # Load existing data
    old_data = load_current_data()
    
    # Scrape new data
    new_data = scrape_pokemongohub()
    
    if new_data:
        if has_data_changed(old_data, new_data):
            print("📊 Data has changed! Updating...")
            save_raid_data(new_data)
            print("✅ Update complete!")
        else:
            print("📊 No changes detected. Keeping existing data.")
    else:
        print("❌ Failed to fetch data. Exiting.")
        exit(1)