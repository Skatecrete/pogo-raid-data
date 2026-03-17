import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os
import time

def scrape_pokemongohub():
    """Scrape current raid data from Pokémon GO Hub with browser-like headers"""
    
    url = "https://pokemongohub.net/post/guide/current-go-raids/"
    print(f"🌐 Fetching {url}")
    
    # These headers make the request look like a real Chrome browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        # Add a small delay to be respectful
        time.sleep(2)
        
        response = requests.get(url, headers=headers, timeout=15)
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
        
        # Debug: print first 500 chars to see what we got
        print(f"📄 Page content preview: {content[:500]}...")
        
        # Extract 5-Star raids - updated patterns based on current page
        tier5_match = re.search(r'5-Star Raids?:?\s*([^<\n]+)', content, re.IGNORECASE)
        if tier5_match:
            tier5_text = tier5_match.group(1)
            # Clean up the text
            tier5_text = re.sub(r'\([^)]*\)', '', tier5_text)  # Remove parentheses
            # Handle various formats
            if ',' in tier5_text:
                raid_data["tier5"] = [name.strip() for name in tier5_text.split(',') if name.strip()]
            else:
                raid_data["tier5"] = [tier5_text.strip()]
            print(f"✅ Found 5-Star: {raid_data['tier5']}")
        
        # Extract Mega raids
        mega_match = re.search(r'Mega Raids?:?\s*([^<\n]+)', content, re.IGNORECASE)
        if mega_match:
            mega_text = mega_match.group(1)
            if ',' in mega_text:
                raid_data["mega"] = [name.strip() for name in mega_text.split(',') if name.strip()]
            else:
                raid_data["mega"] = [mega_text.strip()]
            print(f"✅ Found Mega: {raid_data['mega']}")
        
        # Extract 3-Star raids
        tier3_match = re.search(r'3-Star Raids?:?\s*([^<\n]+)', content, re.IGNORECASE)
        if tier3_match:
            tier3_text = tier3_match.group(1)
            if ',' in tier3_text:
                raid_data["tier3"] = [name.strip() for name in tier3_text.split(',') if name.strip()]
            else:
                raid_data["tier3"] = [tier3_text.strip()]
            print(f"✅ Found 3-Star: {raid_data['tier3']}")
        
        # Extract 1-Star raids
        tier1_match = re.search(r'1-Star Raids?:?\s*([^<\n]+)', content, re.IGNORECASE)
        if tier1_match:
            tier1_text = tier1_match.group(1)
            if ',' in tier1_text:
                raid_data["tier1"] = [name.strip() for name in tier1_text.split(',') if name.strip()]
            else:
                raid_data["tier1"] = [tier1_text.strip()]
            print(f"✅ Found 1-Star: {raid_data['tier1']}")
        
        # Extract Shadow raids
        shadow_match = re.search(r'Shadow Raid:?\s*([^<\n]+)|Shadow\s+([^<\n]+)', content, re.IGNORECASE)
        if shadow_match:
            shadow_text = shadow_match.group(1) or shadow_match.group(2)
            if shadow_text:
                if ',' in shadow_text:
                    raid_data["shadow"] = [name.strip() for name in shadow_text.split(',') if name.strip()]
                else:
                    raid_data["shadow"] = [shadow_text.strip()]
                print(f"✅ Found Shadow: {raid_data['shadow']}")
        
        return raid_data
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if response.status_code == 403:
            print("   Site is blocking automated requests. This is common.")
            print("   Try running this script from a different location or use a VPN.")
        return None
    except requests.exceptions.RequestException as e:
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
    
    for tier in ['tier5', 'mega', 'tier3', 'tier1', 'shadow']:
        if old_data.get(tier, []) != new_data.get(tier, []):
            return True
    return False

if __name__ == "__main__":
    print("🚀 Starting raid data update...")
    
    old_data = load_current_data()
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
