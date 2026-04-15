import asyncio
import json
from playwright.async_api import async_playwright
import re

async def scrape_shungo_forms():
    print("🚀 Launching browser to scrape Shungo forms...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("📄 Loading page...")
        await page.goto("https://shungo.app/tools/wild")
        
        # Wait for the Pokémon list to load
        await page.wait_for_selector(".pkmn-list-img", timeout=30000)
        
        print("✅ Page loaded, extracting data...")
        
        # Extract all Pokémon entries from the rendered page
        pokemon_data = await page.evaluate('''
            () => {
                const items = [];
                const cards = document.querySelectorAll('.pkmn-list-img');
                
                for (const card of cards) {
                    // Get the parent container
                    const container = card.closest('.col-xl-2, .col-4');
                    if (!container) continue;
                    
                    // Get Pokémon name
                    const nameElement = container.querySelector('.pkmn-title');
                    let name = nameElement ? nameElement.innerText.trim() : '';
                    
                    // Get spawn rate
                    const cpText = container.querySelector('.pkmn-cp')?.innerText || '';
                    const rateMatch = cpText.match(/CP\\s+\\d+\\s*-\\s*\\d+\\s*\\n\\s*CP\\s+\\d+\\s*-\\s*\\d+/);
                    // Alternative: find the percentage in the text
                    let rate = null;
                    const allText = container.innerText;
                    const percentMatch = allText.match(/(\\d+\\.?\\d*)%/);
                    if (percentMatch) {
                        rate = parseFloat(percentMatch[1]);
                    }
                    
                    // Get Pokémon ID from image src
                    const img = card.querySelector('img.sprite, img:not(.shiny):not(.overlay)');
                    let id = null;
                    if (img && img.src) {
                        const idMatch = img.src.match(/\\/(\\d+)[_.]/);
                        if (idMatch) {
                            id = parseInt(idMatch[1]);
                        }
                    }
                    
                    if (name && rate && id) {
                        items.push({ id, rate, name });
                    }
                }
                
                return items;
            }
        ''')
        
        await browser.close()
        
        # Group by ID and rate
        form_map = {}
        for item in pokemon_data:
            id = item['id']
            rate = item['rate']
            name = item['name']
            
            if id not in form_map:
                form_map[id] = {}
            
            rounded_rate = round(rate, 2)
            if rounded_rate in form_map[id]:
                # Same rate, combine names
                existing = form_map[id][rounded_rate]
                if existing != name and name not in existing:
                    form_map[id][rounded_rate] = f"{existing} or {name}"
            else:
                form_map[id][rounded_rate] = name
        
        # Save to JSON
        output = {
            "last_updated": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "form_mappings": form_map
        }
        
        with open('shungo_forms.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Saved to shungo_forms.json")
        print(json.dumps(output, indent=2))
        
        return form_map

if __name__ == "__main__":
    asyncio.run(scrape_shungo_forms())
