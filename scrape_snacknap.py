import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import re

def scrape_snacknap_maxbattles():
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
        
        # Filter out social media and type names
        social_media = ['Telegram', 'Facebook', 'Instagram', 'Threads', 'Bluesky', 'X', 'Twitter', 'Discord', 'Patreon', 'YouTube', 'Twitch']
        type_words = ['fire', 'water', 'grass', 'electric', 'bug', 'ground', 'flying', 'ghost', 
                     'ice', 'psychic', 'dragon', 'dark', 'steel', 'fairy', 'rock', 'fighting', 
                     'poison', 'normal', 'shiny']
        
        rows = soup.find_all('div', class_=re.compile('row'))
        current_tier = None
        
        for row in rows:
            header = row.find(['h2', 'h3'])
            if header:
                header_text = header.get_text().strip()
                if 'Tier 1' in header_text:
                    current_tier = 'dynamax_tier1'
                elif 'Tier 2' in header_text:
                    current_tier = 'dynamax_tier2'
                elif 'Tier 3' in header_text:
                    current_tier = 'dynamax_tier3'
                elif 'Tier 4' in header_text:
                    current_tier = 'dynamax_tier4'
                elif 'Tier 5' in header_text:
                    current_tier = 'dynamax_tier5'
                elif 'Gigantamax' in header_text:
                    current_tier = 'gigantamax'
                else:
                    current_tier = None
            
            if current_tier and current_tier in raid_data:
                imgs = row.find_all('img')
                for img in imgs:
                    alt = img.get('alt', '')
                    if alt and len(alt) > 2:
                        # Skip social media and type words
                        if alt in social_media:
                            continue
                        if alt.lower() in type_words:
                            continue
                        
                        clean_name = alt.replace('D-Max', '').replace('Shiny', '').strip()
                        
                        if clean_name and clean_name not in raid_data[current_tier]:
                            raid_data[current_tier].append(clean_name)
                            print(f"      Added to {current_tier}: {clean_name}")
        
        # Remove duplicates and sort
        for tier in raid_data:
            raid_data[tier] = sorted(list(set(raid_data[tier])))
        
        print(f"\n  📊 MAX BATTLES SUMMARY:")
        print(f"    Dynamax Tier 1: {len(raid_data['dynamax_tier1'])}")
        print(f"    Dynamax Tier 2: {len(raid_data['dynamax_tier2'])}")
        print(f"    Dynamax Tier 3: {len(raid_data['dynamax_tier3'])}")
        print(f"    Dynamax Tier 4: {len(raid_data['dynamax_tier4'])}")
        print(f"    Dynamax Tier 5: {len(raid_data['dynamax_tier5'])}")
        print(f"    Gigantamax: {len(raid_data['gigantamax'])}")
        
        return raid_data
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

def main():
    print("🚀 Starting Snack Nap scraper (Dynamax & Gigantamax only)...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Only get Dynamax and Gigantamax
    max_battles = scrape_snacknap_maxbattles() or {}
    
    # Only include Dynamax and Gigantamax in the output
    new_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "dynamax_tier1": max_battles.get("dynamax_tier1", []),
        "dynamax_tier2": max_battles.get("dynamax_tier2", []),
        "dynamax_tier3": max_battles.get("dynamax_tier3", []),
        "dynamax_tier4": max_battles.get("dynamax_tier4", []),
        "dynamax_tier5": max_battles.get("dynamax_tier5", []),
        "gigantamax": max_battles.get("gigantamax", [])
    }
    
    with open('current_raids.json', 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print("\n💾 Saved to current_raids.json (Dynamax & Gigantamax only)")

if __name__ == "__main__":
    main()
