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
        
        # Wait for page to fully load (5 seconds)
        await page.wait_for_timeout(5000)
        
        print("✅ Page loaded, extracting data...")
        
        # Get all text content for debugging
        page_text = await page.evaluate('() => document.body.innerText')
        print(f"Page text preview: {page_text[:500]}")
        
        # Extract Pokémon data using the actual page structure
        pokemon_data = await page.evaluate('''
            () => {
                const items = [];
                
                // Find all card elements
                const cards = document.querySelectorAll('.card');
                
                for (const card of cards) {
                    // Get the text content
                    const text = card.innerText;
                    if (!text) continue;
                    
                    // Look for percentage
                    const percentMatch = text.match(/(\\d+\\.?\\d*)%/);
                    if (!percentMatch) continue;
                    
                    const rate = parseFloat(percentMatch[1]);
                    
                    // Get name (usually first line of text)
                    const lines = text.split('\\n');
                    let name = lines[0].trim();
                    
                    // Skip if name is empty or looks like CP
                    if (!name || name.includes('CP')) {
                        // Try the second line
                        name = lines[1]?.trim() || '';
                    }
                    
                    // Clean up name
                    name = name.replace(/\\n/g, '').trim();
                    
                    // Get ID from image src
                    const img = card.querySelector('img');
                    let id = null;
                    if (img && img.src) {
                        const idMatch = img.src.match(/\\/(\\d+)[_.]/);
                        if (idMatch) {
                            id = parseInt(idMatch[1]);
                        }
                    }
                    
                    if (name && rate && name.length > 2 && name.length < 40) {
                        items.push({
                            name: name,
                            rate: rate,
                            id: id
                        });
                        console.log(`Found: ${name} - ${rate}% - ID: ${id}`);
                    }
                }
                
                return items;
            }
        ''')
        
        await browser.close()
        
        # Group by ID and rate
        form_map = {}
        for item in pokemon_data:
            if not item['id']:
                continue
            
            id = item['id']
            rate = round(item['rate'], 2)
            name = item['name']
            
            if id not in form_map:
                form_map[id] = {}
            
            if rate in form_map[id]:
                existing = form_map[id][rate]
                if existing != name and name not in existing:
                    form_map[id][rate] = f"{existing} or {name}"
            else:
                form_map[id][rate] = name
        
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
