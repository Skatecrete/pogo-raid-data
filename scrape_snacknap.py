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
        
        # Find all tier sections
        # Look for elements containing "Tier 1", "Tier 2", "Tier 3", etc.
        all_text = soup.get_text()
        
        # Find all Pokemon cards - they are in divs with specific structure
        # Each Pokemon card has an image with alt text containing the Pokemon name
        
        current_tier = None
        
        # Find all elements that might contain tier headers
        for element in soup.find_all(['h2', 'h3', 'div']):
            text = element.get_text().strip()
            
            # Check for tier headers
            if 'Tier 1' in text or 'Tier 1' in text.upper():
                current_tier = 'dynamax_tier1'
                print(f"    Found Tier 1 section")
                continue
            elif 'Tier 2' in text or 'Tier 2' in text.upper():
                current_tier = 'dynamax_tier2'
                print(f"    Found Tier 2 section")
                continue
            elif 'Tier 3' in text or 'Tier 3' in text.upper():
                current_tier = 'dynamax_tier3'
                print(f"    Found Tier 3 section")
                continue
            elif 'Tier 4' in text or 'Tier 4' in text.upper():
                current_tier = 'dynamax_tier4'
                continue
            elif 'Tier 5' in text or 'Tier 5' in text.upper():
                current_tier = 'dynamax_tier5'
                continue
            elif 'Gigantamax' in text:
                current_tier = 'gigantamax'
                print(f"    Found Gigantamax section")
                continue
            
            # If we're in a tier section, look for Pokemon images
            if current_tier and current_tier in raid_data:
                # Find all images in this element or its children
                imgs = element.find_all('img')
                for img in imgs:
                    alt = img.get('alt', '')
                    if alt and len(alt) > 2:
                        # Clean the name
                        clean_name = alt.replace('D-Max', '').replace('Shiny', '').replace('ShinyD-Max', '').strip()
                        
                        # Skip if empty or in filter lists
                        if not clean_name:
                            continue
                        if clean_name in social_media:
                            continue
                        if clean_name.lower() in type_words:
                            continue
                        
                        # Add to current tier if not already there
                        if clean_name and clean_name not in raid_data[current_tier]:
                            raid_data[current_tier].append(clean_name)
                            print(f"      Added to {current_tier}: {clean_name}")
        
        # Also try a more direct approach - find all Pokemon cards
        # Look for elements with class containing 'card' or 'pokemon'
        pokemon_cards = soup.find_all(class_=re.compile(r'card|pokemon|max-battle', re.I))
        
        for card in pokemon_cards:
            # Try to find tier from nearby heading
            prev = card.find_previous(['h2', 'h3'])
            if prev:
                prev_text = prev.get_text().strip()
                if 'Tier 1' in prev_text:
                    current_tier = 'dynamax_tier1'
                elif 'Tier 2' in prev_text:
                    current_tier = 'dynamax_tier2'
                elif 'Tier 3' in prev_text:
                    current_tier = 'dynamax_tier3'
                elif 'Tier 4' in prev_text:
                    current_tier = 'dynamax_tier4'
                elif 'Tier 5' in prev_text:
                    current_tier = 'dynamax_tier5'
                elif 'Gigantamax' in prev_text:
                    current_tier = 'gigantamax'
            
            if current_tier and current_tier in raid_data:
                img = card.find('img')
                if img:
                    alt = img.get('alt', '')
                    if alt:
                        clean_name = alt.replace('D-Max', '').replace('Shiny', '').replace('ShinyD-Max', '').strip()
                        if clean_name and len(clean_name) > 2:
                            if clean_name not in social_media and clean_name.lower() not in type_words:
                                if clean_name not in raid_data[current_tier]:
                                    raid_data[current_tier].append(clean_name)
        
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
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🚀 Starting Snack Nap scraper (Dynamax & Gigantamax only)...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    max_battles = scrape_snacknap_maxbattles() or {}
    
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
    
    print("\n💾 Saved to current_raids.json")

if __name__ == "__main__":
    main()
