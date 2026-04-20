import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time
from datetime import datetime

def debug_page_structure():
    """Debug function to examine the actual page structure"""
    print("\n🔍 DEBUGGING PAGE STRUCTURE")
    print("="*50)
    
    url = "https://leekduck.com/raid-bosses/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the HTML for inspection
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("  ✓ Saved page HTML to debug_page.html")
        
        # Look for any elements that might contain shadow raid info
        print("\n  Looking for 'shadow' in text...")
        shadow_texts = soup.find_all(string=re.compile(r'Shadow', re.IGNORECASE))
        print(f"  Found {len(shadow_texts)} text elements containing 'Shadow'")
        
        # Look for cards
        print("\n  Looking for card elements...")
        cards = soup.find_all('div', class_=re.compile(r'card', re.IGNORECASE))
        print(f"  Found {len(cards)} divs with 'card' in class")
        
        # Look for boss-img elements
        print("\n  Looking for boss-img elements...")
        boss_imgs = soup.find_all('div', class_=re.compile(r'boss', re.IGNORECASE))
        print(f"  Found {len(boss_imgs)} divs with 'boss' in class")
        
        # Look for any images that might be shadow-related
        print("\n  Looking for images...")
        images = soup.find_all('img')
        shadow_images = []
        for img in images:
            src = img.get('src', '')
            if 'pm' in src and 'icon' in src:
                shadow_images.append(src)
                print(f"    Found icon: {src}")
        
        # Check the structure around the first shadow text
        if shadow_texts:
            print("\n  First 'Shadow' text element:")
            first_shadow = shadow_texts[0]
            print(f"    Text: {first_shadow}")
            parent = first_shadow.parent
            print(f"    Parent tag: {parent.name if parent else 'None'}")
            if parent:
                print(f"    Parent classes: {parent.get('class', [])}")
                # Go up a few levels
                for i in range(3):
                    if parent:
                        print(f"    Level {i+1} up: {parent.name} - classes: {parent.get('class', [])}")
                        parent = parent.parent
        
        # Check for any div with style attribute containing url
        print("\n  Looking for divs with style containing url...")
        styled_divs = soup.find_all('div', style=re.compile(r'url', re.IGNORECASE))
        print(f"  Found {len(styled_divs)} divs with 'url' in style")
        for div in styled_divs[:3]:  # Show first 3
            style = div.get('style', '')
            print(f"    Style: {style[:100]}...")
        
        # Look for the specific structure you showed
        print("\n  Looking for '-shadow' class...")
        shadow_class_divs = soup.find_all('div', class_=re.compile(r'-shadow'))
        print(f"  Found {len(shadow_class_divs)} divs with '-shadow' in class")
        for div in shadow_class_divs[:3]:
            print(f"    Classes: {div.get('class', [])}")
        
    except Exception as e:
        print(f"❌ Error debugging: {e}")
        import traceback
        traceback.print_exc()

def main():
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # First, debug the page structure
    debug_page_structure()
    
    # Then try to scrape
    print("\n" + "="*50)
    print("Now attempting to scrape with adjusted selectors...")
    
    url = "https://leekduck.com/raid-bosses/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try multiple selectors to find shadow Pokémon
        shadow_pokemon = []
        
        # Selector 1: Look for any element with text containing "Shadow" and find nearby images
        shadow_texts = soup.find_all(string=re.compile(r'Shadow (?:Dratini|Gligar|Cacnea|Joltik|Marowak|Lapras|Stantler|Latios|Latias)'))
        
        for text_elem in shadow_texts:
            shadow_name = text_elem.strip()
            print(f"  Found shadow text: {shadow_name}")
            
            # Look for nearby image
            parent = text_elem.parent
            for _ in range(5):  # Go up 5 levels
                if parent:
                    # Look for images in this parent
                    img = parent.find('img')
                    if img and img.get('src'):
                        img_url = img.get('src')
                        if 'pm' in img_url and 'icon' in img_url:
                            pokemon_id = re.search(r'pm(\d+)\.icon', img_url)
                            if pokemon_id:
                                pokemon_id = int(pokemon_id.group(1))
                                # Get Pokémon name from ID
                                try:
                                    name_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}/"
                                    name_response = requests.get(name_url, timeout=10)
                                    if name_response.status_code == 200:
                                        name_data = name_response.json()
                                        for name_entry in name_data['names']:
                                            if name_entry['language']['name'] == 'en':
                                                base_name = name_entry['name']
                                                break
                                    else:
                                        base_name = f"Pokemon_{pokemon_id}"
                                except:
                                    base_name = f"Pokemon_{pokemon_id}"
                                
                                shadow_pokemon.append({
                                    'name': shadow_name,
                                    'base_name': base_name,
                                    'id': pokemon_id,
                                    'slug': base_name.lower().replace(' ', '-'),
                                    'icon_url': img_url
                                })
                                print(f"    Found image: {img_url} (ID: {pokemon_id})")
                                break
                    parent = parent.parent
        
        # Remove duplicates
        seen_ids = set()
        unique_pokemon = []
        for p in shadow_pokemon:
            if p['id'] not in seen_ids:
                seen_ids.add(p['id'])
                unique_pokemon.append(p)
        
        print(f"\n  Found {len(unique_pokemon)} unique shadow Pokémon")
        
        if unique_pokemon:
            # Download images
            os.makedirs('shadow_images', exist_ok=True)
            successful = 0
            
            for pokemon in unique_pokemon:
                filename = f"{pokemon['id']}_{pokemon['slug']}_shadow.webp"
                local_path = f"shadow_images/{filename}"
                
                print(f"\n  Downloading: {pokemon['name']}")
                print(f"    URL: {pokemon['icon_url']}")
                
                img_response = requests.get(pokemon['icon_url'], headers=headers, timeout=30)
                if img_response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"    ✓ Saved to {filename}")
                    successful += 1
                else:
                    print(f"    ❌ Failed to download")
                
                time.sleep(0.3)
            
            print(f"\n✅ Successfully downloaded {successful} shadow images")
        else:
            print("\n⚠️ Could not find shadow Pokémon with text search")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
