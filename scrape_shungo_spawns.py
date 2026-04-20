import requests
import json
import re
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

# ============================================================================
# 1. SCRAPE FORMS DIRECTLY FROM SHUNGO WEBSITE (NO SEPARATE FILE NEEDED)
# ============================================================================

async def scrape_forms_from_website():
    """Scrape form names directly from Shungo website"""
    print("🌐 Scraping form data from Shungo website...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("📄 Loading page...")
        await page.goto("https://shungo.app/tools/wild")
        
        await page.wait_for_timeout(5000)
        
        print("📜 Scrolling to load all Pokémon...")
        last_height = await page.evaluate('() => document.body.scrollHeight')
        
        while True:
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)
            new_height = await page.evaluate('() => document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height
        
        print("✅ Page loaded, extracting data...")
        
        text = await page.evaluate('() => document.body.innerText')
        
        await browser.close()
        
        # Parse the text into form mappings
        lines = text.split('\n')
        form_map = {}
        
        i = 0
        while i < len(lines) - 2:
            name = lines[i].strip()
            rate_line = lines[i + 1].strip()
            id_line = lines[i + 2].strip()
            
            if name and rate_line.endswith('%') and id_line.isdigit():
                rate = float(rate_line.replace('%', ''))
                pokemon_id = int(id_line)
                rounded_rate = round(rate, 2)
                
                if pokemon_id not in form_map:
                    form_map[pokemon_id] = {}
                
                if rounded_rate in form_map[pokemon_id]:
                    existing = form_map[pokemon_id][rounded_rate]
                    if existing != name and name not in existing:
                        form_map[pokemon_id][rounded_rate] = f"{existing} or {name}"
                else:
                    form_map[pokemon_id][rounded_rate] = name
                
                i += 3
            else:
                i += 1
        
        print(f"📋 Found {len(form_map)} Pokémon with forms")
        return form_map


# ============================================================================
# 2. FETCH SPAWNS FROM API
# ============================================================================

def fetch_spawns_from_api():
    """Fetch raw spawn data from Shungo API"""
    print("📡 Fetching spawns from Shungo API...")
    api_url = "https://shungo.app/api/shungo/data/spawns"
    response = requests.get(api_url)
    data = response.json()
    result_array = data["result"]
    print(f"📊 Raw spawn entries: {len(result_array)}")
    return result_array


# ============================================================================
# 3. HELPER FUNCTIONS
# ============================================================================

def get_rotomlabs_slug(pokemon_name):
    """Convert Pokemon name to RotomLabs URL slug."""
    clean_name = re.sub(r'\([^)]*\)', '', pokemon_name).strip()
    
    special_mappings = {
        "Nidoran\u2640": "nidoran-f",
        "Nidoran\u2642": "nidoran-m",
        "Farfetch'd": "farfetch-d",
        "Mr. Mime": "mr-mime",
        "Type: Null": "type-null",
        "Flabébé": "flabebe",
        "Ho-Oh": "ho-oh",
        "Sirfetch'd": "sirfetchd",
        "Mr. Rime": "mr-rime",
        "Pumpkaboo": "pumpkaboo",
        "Darmanitan": "darmanitan",
        "Rapidash": "rapidash",
        "Pikachu": "pikachu",
        "Geodude": "geodude",
        "Grimer": "grimer",
        "Meowth": "meowth",
        "Vulpix": "vulpix",
        "Rattata": "rattata",
        "Diglett": "diglett",
        "Sandshrew": "sandshrew",
        "Dugtrio": "dugtrio",
        "Graveler": "graveler",
        "Persian": "persian",
        "Raticate": "raticate",
        "Muk": "muk",
        "Ninetales": "ninetales",
        "Oinkologne": "oinkologne",
        "Flabébé": "flabebe",
        "Floette": "floette",
        "Cherrim": "cherrim",
        "Burmy": "burmy",
        "Sandslash": "sandslash",
    }
    
    if clean_name in special_mappings:
        return special_mappings[clean_name]
    
    clean_name = clean_name.lower()
    clean_name = clean_name.replace("'", "")
    clean_name = clean_name.replace(" ", "-")
    clean_name = re.sub(r'[^a-z0-9-]', '', clean_name)
    clean_name = re.sub(r'-+', '-', clean_name)
    clean_name = clean_name.strip('-')
    
    return clean_name


def match_spawns_with_forms(spawns_array, form_map):
    """Match each spawn with its correct form name"""
    spawns = []
    matched = 0
    fallback = 0
    
    # Build a quick lookup by ID (for fallback)
    id_to_any_name = {}
    for pid, rates in form_map.items():
        for rate, name in rates.items():
            id_to_any_name[pid] = name
            break
    
    for item in spawns_array:
        pokemon_id = item[0]
        rate = item[2]
        is_shiny = item[3] == "true" or item[3] == True
        
        pokemon_name = None
        
        # Try to find exact or closest rate match
        if pokemon_id in form_map:
            closest_rate = None
            closest_diff = 1.0
            for map_rate in form_map[pokemon_id].keys():
                diff = abs(map_rate - rate)
                if diff < closest_diff:
                    closest_diff = diff
                    closest_rate = map_rate
            
            if closest_rate is not None:
                pokemon_name = form_map[pokemon_id][closest_rate]
                matched += 1
        
        # Fallback: use any name for this ID
        if not pokemon_name and pokemon_id in id_to_any_name:
            pokemon_name = id_to_any_name[pokemon_id]
            fallback += 1
        
        # Last resort
        if not pokemon_name:
            pokemon_name = f"Pokemon #{pokemon_id}"
        
        slug = get_rotomlabs_slug(pokemon_name)
        image_url = f"https://rotomlabs.net/dex/{slug}"
        
        spawns.append({
            "id": pokemon_id,
            "name": pokemon_name,
            "rate": round(rate, 2),
            "shiny": is_shiny,
            "image_url": image_url
        })
    
    print(f"✅ Exact matches: {matched} | Fallback matches: {fallback}")
    return spawns


# ============================================================================
# 4. MAIN FUNCTION
# ============================================================================

async def main():
    print("="*60)
    print("🚀 POKESPAWN SPAWN SCRAPER (STANDALONE)")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Scrape form data directly from website
    form_map = await scrape_forms_from_website()
    
    # Step 2: Fetch spawns from API
    spawns_array = fetch_spawns_from_api()
    
    # Step 3: Match and generate spawns
    spawns = match_spawns_with_forms(spawns_array, form_map)
    
    # Step 4: Sort by spawn rate
    spawns.sort(key=lambda x: x['rate'], reverse=True)
    
    # Step 5: Save output
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(spawns),
        "spawns": spawns
    }
    
    with open('spawns.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Saved to spawns.json")
    print(f"   Total spawns: {len(spawns)}")
    print(f"\n📊 Top 10 highest spawn rates:")
    for i, spawn in enumerate(spawns[:10]):
        print(f"   {i+1}. {spawn['name']}: {spawn['rate']}%")
    
    print("\n✨ Done!")


def run():
    """Entry point for the script"""
    asyncio.run(main())


if __name__ == "__main__":
    run()
