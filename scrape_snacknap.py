import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import re

def scrape_snacknap_raids():
    print("  📡 Fetching raids from Snack Nap...")
    url = "https://www.snacknap.com/raids"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the HTML to debug
        with open('debug_raids.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("    ✅ Saved HTML to debug_raids.html")
        
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
        
        # Print ALL headers to see what's on the page
        print("\n  📋 ALL HEADERS FOUND:")
        all_headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        for i, header in enumerate(all_headers):
            header_text = header.get_text().strip()
            if header_text:
                print(f"    {i}: {header_text}")
        
        # Now specifically look for Shadow sections by finding text containing "Shadow"
        print("\n  🔍 LOOKING FOR SHADOW SECTIONS:")
        shadow_elements = soup.find_all(string=re.compile('Shadow Tier|Shadow Legendary|Shadow', re.IGNORECASE))
        for elem in shadow_elements:
            print(f"    Found text: {elem.strip()}")
            # Find the parent header
            parent = elem.parent
            while parent and parent.name not in ['h2', 'h3', 'h4']:
                parent = parent.parent
            if parent:
                print(f"      Parent header: {parent.get_text().strip()}")
        
        # Now parse by looking for specific section markers
        print("\n  🃏 PARSING POKEMON BY SECTION:")
        
        # Find all section containers - look for divs that might contain the raid cards
        # Based on the HTML structure, raid cards are in rows
        rows = soup.find_all('div', class_=re.compile('row'))
        print(f"    Found {len(rows)} rows")
        
        current_section = None
        
        for row in rows:
            # Check if this row has a header
            header = row.find(['h2', 'h3'])
            if header:
                header_text = header.get_text().strip()
                print(f"    Row header: {header_text}")
                
                if 'Shadow' in header_text:
                    current_section = 'shadow'
                    print(f"      -> Setting section to SHADOW")
                elif 'Legendary' in header_text and 'Shadow' not in header_text:
                    current_section = 'tier5'
                elif 'Mega' in header_text:
                    current_section = 'mega'
                elif 'Tier 3' in header_text:
                    current_section = 'tier3'
                elif 'Tier 1' in header_text:
                    current_section = 'tier1'
                else:
                    current_section = None
            
            # If we have a current section, look for Pokemon in this row
            if current_section and current_section in raid_data:
                # Find all images in this row
                imgs = row.find_all('img')
                for img in imgs:
                    alt = img.get('alt', '')
                    if alt and len(alt) > 2:
                        # Skip type icons
                        type_words = ['fire', 'water', 'grass', 'electric', 'bug', 'ground', 'flying', 
                                     'ghost', 'ice', 'psychic', 'dragon', 'dark', 'steel', 'fairy', 
                                     'rock', 'fighting', 'poison', 'normal', 'shiny']
                        if alt.lower() not in type_words:
                            # Clean the name
                            clean_name = alt.replace('Shiny', '').replace('Shadow', '').strip()
                            if clean_name and clean_name not in raid_data[current_section]:
                                raid_data[current_section].append(clean_name)
                                print(f"      Added to {current_section}: {clean_name}")
        
        # Sort all lists
        for tier in raid_data:
            raid_data[tier] = sorted(list(set(raid_data[tier])))
        
        print(f"\n  📊 SHADOW RAID SUMMARY:")
        print(f"    Shadow Pokemon found: {len(raid_data['shadow'])}")
        if raid_data['shadow']:
            for pokemon in raid_data['shadow']:
                print(f"      - {pokemon}")
        
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
    for tier, pokemon in regular.items():
        if pokemon:
            print(f"  {tier}: {pokemon}")

if __name__ == "__main__":
    main()
