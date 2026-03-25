import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import re

def scrape_snacknap_raids():
    print("  📡 Fetching regular raids...")
    url = "https://www.snacknap.com/raids"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # DEBUG: Save HTML for inspection
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("    ✅ Saved page HTML to debug_page.html")
        
        raid_data = {
            "tier5": [],
            "mega": [],
            "tier4": [],
            "tier3": [],
            "tier2": [],
            "tier1": [],
            "six_star": [],
            "shadow": []
        }
        
        # Find all images with alt text
        all_imgs = soup.find_all('img')
        print(f"    Found {len(all_imgs)} images total")
        
        shadow_count = 0
        regular_count = 0
        
        for img in all_imgs:
            alt = img.get('alt', '')
            if alt:
                print(f"      Image alt: {alt}")
                
                # Check for Shadow Pokemon (alt contains "Shadow")
                if 'Shadow' in alt:
                    shadow_count += 1
                    # Clean the name
                    clean_name = alt.replace('Shadow', '').replace('Shiny', '').strip()
                    # Also remove type words if they appear
                    for type_word in ['Normal', 'Fire', 'Water', 'Grass', 'Electric', 'Bug', 'Ground', 
                                     'Flying', 'Ghost', 'Ice', 'Psychic', 'Dragon', 'Dark', 'Steel', 
                                     'Fairy', 'Rock', 'Fighting', 'Poison']:
                        clean_name = clean_name.replace(type_word, '').strip()
                    
                    if clean_name and clean_name not in raid_data['shadow']:
                        raid_data['shadow'].append(clean_name)
                        print(f"        -> Added to shadow: {clean_name}")
                
                # Check for regular Pokemon (no Shadow)
                elif alt and len(alt) > 2 and alt not in ['Search...', 'Logo', 'Snack Nap']:
                    regular_count += 1
                    # Determine tier by looking at parent elements
                    parent = img.parent
                    tier = None
                    for _ in range(5):
                        if parent:
                            parent_text = parent.get_text()
                            if 'Tier 1' in parent_text and 'Shadow' not in parent_text:
                                tier = 'tier1'
                                break
                            elif 'Tier 3' in parent_text and 'Shadow' not in parent_text:
                                tier = 'tier3'
                                break
                            elif 'Legendary' in parent_text and 'Shadow' not in parent_text:
                                tier = 'tier5'
                                break
                            elif 'Mega' in parent_text:
                                tier = 'mega'
                                break
                        parent = parent.parent if parent else None
                    
                    if tier and tier in raid_data:
                        clean_name = alt.replace('Mega', '').replace('Shiny', '').strip()
                        if clean_name and clean_name not in raid_data[tier]:
                            raid_data[tier].append(clean_name)
                            print(f"        -> Added to {tier}: {clean_name}")
        
        print(f"\n    Found {shadow_count} Shadow images, {regular_count} regular images")
        print(f"    Shadow Pokemon: {raid_data['shadow']}")
        
        return raid_data
    except Exception as e:
        print(f"    ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🚀 Starting Snack Nap scraper...")
    regular = scrape_snacknap_raids() or {}
    print(f"\n📊 FINAL RESULTS:")
    if regular:
        for tier, pokemon in regular.items():
            if pokemon:
                print(f"  {tier}: {pokemon}")
    else:
        print("  No data scraped!")

if __name__ == "__main__":
    main()
