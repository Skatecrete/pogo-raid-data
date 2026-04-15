import asyncio
import json
from playwright.async_api import async_playwright
from datetime import datetime

async def scrape_shungo_forms():
    print("🚀 Launching browser to scrape Shungo forms...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("📄 Loading page...")
        await page.goto("https://shungo.app/tools/wild")
        
        # Wait for initial content
        await page.wait_for_timeout(3000)
        
        # Scroll to bottom to load all Pokémon
        print("📜 Scrolling to load all Pokémon...")
        last_height = await page.evaluate('() => document.body.scrollHeight')
        
        while True:
            # Scroll down
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)
            
            # Check if we've reached the bottom
            new_height = await page.evaluate('() => document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height
        
        print("✅ Page fully loaded, extracting data...")
        
        # Get the text content of the body
        text = await page.evaluate('() => document.body.innerText')
        
        # Parse the text
        lines = text.split('\n')
        form_map = {}
        
        i = 0
        while i < len(lines) - 2:
            name = lines[i].strip()
            rate_line = lines[i + 1].strip()
            id_line = lines[i + 2].strip()
            
            # Check if this looks like a Pokémon entry
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
        
        await browser.close()
        
        # Save to JSON
        output = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "form_mappings": form_map
        }
        
        with open('shungo_forms.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Saved to shungo_forms.json")
        print(f"Total Pokémon with forms: {len(form_map)}")
        print(f"Sample: {dict(list(form_map.items())[:5])}")

if __name__ == "__main__":
    asyncio.run(scrape_shungo_forms())
