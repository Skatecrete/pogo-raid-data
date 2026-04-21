import json
import re
import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

async def fetch_current_spawns():
    """Fetch current spawn data from Shungo website using Playwright"""
    print("📡 Fetching current spawns from Shungo website...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://shungo.app/tools/wild")
        
        # Wait for content to load
        await page.wait_for_timeout(5000)
        
        # Scroll to load all
        last_height = await page.evaluate('() => document.body.scrollHeight')
        while True:
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)
            new_height = await page.evaluate('() => document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height
        
        # Get the text content (this works because Playwright sees the rendered page)
        text = await page.evaluate('() => document.body.innerText')
        await browser.close()
        
        # Parse the text - each Pokémon is 3 lines: name, rate%, id
        lines = text.split('\n')
        spawns = []
        
        i = 0
        while i < len(lines) - 2:
            name = lines[i].strip()
            rate_line = lines[i + 1].strip()
            id_line = lines[i + 2].strip()
            
            # Check if this looks like a Pokémon entry
            if name and rate_line.endswith('%') and id_line.isdigit():
                rate = float(rate_line.replace('%', ''))
                pokemon_id = int(id_line)
                is_shiny = 'shiny' in name.lower()
                
                spawns.append({
                    "id": pokemon_id,
                    "name": name,
                    "rate": round(rate, 2),
                    "shiny": is_shiny,
                    "image_url": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
                })
                i += 3
            else:
                i += 1
        
        print(f"✅ Fetched {len(spawns)} spawns from website")
        
        # Print top 10 for debugging
        print("\n📊 Top 10 spawns from website:")
        for idx, s in enumerate(spawns[:10]):
            print(f"   {idx+1}. {s['name']}: {s['rate']}%")
        
        return spawns

def fix_image_urls():
    """Fix image URLs in spawns.json to match existing files in images folder"""
    
    print("="*60)
    print("🖼️ FIXING IMAGE URLS FOR ALL FORMS")
    print("="*60)
    
    with open('spawns.json', 'r') as f:
        data = json.load(f)
    
    spawns = data.get('spawns', [])
    print(f"📊 Loaded {len(spawns)} spawns")
    
    images_folder = 'images'
    existing_images = set()
    if os.path.exists(images_folder):
        existing_images = set(os.listdir(images_folder))
        print(f"📁 Found {len(existing_images)} images in {images_folder}/")
    else:
        print(f"⚠️ Images folder '{images_folder}' not found!")
        return
    
    # ===== COMPLETE FORM MAPPINGS =====
    form_mappings = {
        # Castform
        "Castform Rainy": "351_castform-rainy.webp",
        "Castform Sunny": "351_castform-sunny.webp",
        "Castform": "351_castformwebp",
        
        # Pumpkaboo
        "Pumpkaboo Small": "710_pumpkaboo-small.webp",
        "Pumpkaboo Average": "710_pumpkaboo-average.webp",
        "Pumpkaboo Large": "710_pumpkaboo-large.webp",
        "Pumpkaboo Super": "710_pumpkaboo-super.webp",
        
        # Deerling
        "Deerling Spring Form": "585_deerling-spring.webp",
        "Deerling Summer Form": "585-deerling-summer.webp",
        "Deerling Autumn Form": "585-deerling-autumn.webp",
        "Deerling Winter Form": "585-deerling-winter.webp",
        
        # Sawsbuck
        "Sawsbuck Spring Form": "586_sawsbuck-spring.webp",
        "Sawsbuck Summer Form": "586-sawsbuck-summer.webp",
        "Sawsbuck Autumn Form": "586-sawsbuck-autumn.webp",
        "Sawsbuck Winter Form": "586-sawsbuck-winter.webp",
        
        # Oricorio
        "Oricorio Baile Style": "741_oricorio-baile-style.webp",
        "Oricorio Pom-Pom Style": "741-oricorio-pom-pom-style.webp",
        "Oricorio Sensu Style": "741_oricorio-sensu-style.webp",
        
        # Cherrim
        "Cherrim Overcast Form": "421-cherrim-overcast.webp",
        "Cherrim Sunny": "421_cherrim-sunshine.webp",
        
        # Burmy
        "Burmy Plant Cloak": "412_burmy-plant-cloak.webp",
        "Burmy Sandy Cloak": "412_burmy-sandy-cloak.webp",
        "Burmy Trash Cloak": "412_burmy-trash-cloak.webp",
        
        # Flabébé
        "Flabébé Blue Flower": "669_flab-b--blue-flower.webp",
        "Flabébé Red Flower": "669_flab-b--red-flower.webp",
        "Flabébé Yellow Flower": "669_flab-b--yellow-flower.webp",
        "Flabébé White Flower": "669_flab-b--white-flower.webp",
        "Flabébé Orange Flower": "669_flab-b--orange-flower.webp",
        
        # Floette
        "Floette Blue Flower": "670_floette-blue-flower.webp",
        "Floette Red Flower": "670_floette-red-flower.webp",
        "Floette Yellow Flower": "670-floette-yellow-flower.webp",
        
        # Shellos/Gastrodon
        "Shellos East Sea": "422_shellos-east-seawebp",
        "Shellos West Sea": "422_shellos-west-seawebp",
        "Gastrodon East Sea": "423_gastrodon-east-seawebp",
        "Gastrodon West Sea": "423_gastrodon-west-seawebp",
        
        # Nidoran
        "Nidoran♀": "29_nidoran-f.webp",
        "Nidoran♂": "32_nidoran-m.webp",
        
        # Frillish
        "Frillish Female": "592_frillish-female.webp",
        "Frillish Male": "592_frillishwebp",
        
        # Oinkologne
        "Oinkologne Female": "916_oinkologne-female.webp",
        
        # Alolan
        "Rattata Alola": "19_rattata-alola.webp",
        "Sandshrew Alola": "27_sandshrew-alola.webp",
        "Vulpix Alola": "37_vulpix-alola.webp",
        "Diglett Alola": "50_diglett-alola.webp",
        "Meowth Alola": "52_meowth-alola.webp",
        "Geodude Alola": "74_geodude-alola.webp",
        "Grimer Alola": "88_grimer-alola.webp",
        
        # Galarian
        "Meowth Galarian": "52_meowth-galarian.webp",
        "Ponyta Galarian": "77_ponyta-galarian.webp",
        "Slowpoke Galarian": "79_slowpoke-galarian.webp",
        "Zigzagoon Galarian": "263_zigzagoon-galarian.webp",
        
        # Hisuian
        "Growlithe Hisuian": "58_growlithe-hisuian.webp",
        "Voltorb Hisuian": "100_voltorb-hisuian.webp",
        "Sneasel Hisuian": "215_sneasel-hisuian.webp",
        
        # Paldean
        "Wooper Paldea": "194_wooper-paldea.webp",
        "Clodsire": "980_clodsirewebp",
        
        # Rotom
        "Rotom Heat": "479_rotom-heat.webp",
        "Rotom Wash": "479_rotom-wash.webp",
        
        # Other
        "Farfetch'd": "83_farfetch-d.webp",
        "Mr. Mime": "122_mr-mime.webp",
        "Porygon": "137_porygonwebp",
        "Porygon2": "233_porygon2webp",
        "Porygon-Z": "474_porygon-zwebp",
        "Ho-Oh": "250_ho-ohwebp",
        "Mime Jr.": "439_mime-jrwebp",
        "Sirfetch'd": "865_sirfetchdwebp",
        "Mr. Rime": "866_mr-rimewebp",
    }
    
    updated_count = 0
    
    for spawn in spawns:
        name = spawn['name']
        pokemon_id = spawn['id']
        
        if name in form_mappings:
            filename = form_mappings[name]
            if filename in existing_images:
                spawn['image_url'] = f"https://raw.githubusercontent.com/Skatecrete/pogo-raid-data/main/images/{filename}"
                updated_count += 1
                print(f"✅ {name} -> {filename}")
            else:
                spawn['image_url'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
        else:
            spawn['image_url'] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{pokemon_id}.png"
    
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(spawns),
        "spawns": spawns
    }
    
    with open('spawns.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Updated spawns.json")
    print(f"   ✅ Fixed {updated_count} image URLs")
    print("="*60)

async def main():
    print("="*60)
    print("🚀 POKESPAWN SPAWN SCRAPER")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Fetch current spawns using Playwright
    current_spawns = await fetch_current_spawns()
    
    if current_spawns:
        output = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(current_spawns),
            "spawns": current_spawns
        }
        with open('spawns.json', 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\n✅ Saved {len(current_spawns)} spawns to spawns.json")
    
    # Step 2: Fix image URLs
    fix_image_urls()
    
    print("\n✨ Done!")

if __name__ == "__main__":
    asyncio.run(main())
