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
        
        # Wait for the table or card elements to load
        await page.wait_for_timeout(5000)  # Wait 5 seconds for JS to render
        
        print("✅ Page loaded, extracting data...")
        
        # Get all text content for debugging
        page_text = await page.evaluate('() => document.body.innerText')
        print(f"Page text preview: {page_text[:500]}")
        
        # Extract Pokémon data using more reliable selectors
        pokemon_data = await page.evaluate('''
            () => {
                const items = [];
                
                // Look for any elements containing Pokémon names and percentages
                const allText = document.body.innerText;
                
                // Find all percentage matches in the page
                const percentRegex = /(\\d+\\.?\\d*)%/g;
                const lines = allText.split('\\n');
                
                let currentName = null;
                let currentRate = null;
                
                for (let i = 0; i < lines.length; i++) {
                    const line = lines[i].trim();
                    if (!line) continue;
                    
                    // Check if line contains a percentage
                    const percentMatch = line.match(/(\\d+\\.?\\d*)%/);
                    if (percentMatch) {
                        currentRate = parseFloat(percentMatch[1]);
                        // Look back for the name (previous line or earlier)
                        for (let j = i-1; j >= 0 && j >= i-5; j--) {
                            const prevLine = lines[j].trim();
                            if (prevLine && !prevLine.match(/\\d/) && prevLine.length > 2 && prevLine.length < 30) {
                                currentName = prevLine;
                                break;
                            }
                        }
                        
                        if (currentName && currentRate) {
                            items.push({
                                name: currentName,
                                rate: currentRate,
                                id: null
                            });
                            currentName = null;
                            currentRate = null;
                        }
                    }
                }
                
                // Try to get IDs from image URLs
                const images = document.querySelectorAll('img');
                for (const img of images) {
                    const src = img.src;
                    if (src && src.includes('/sprites/')) {
                        const idMatch = src.match(/\\/(\\d+)\\./);
                        if (idMatch) {
                            const id = parseInt(idMatch[1]);
                            // Find the closest text to this image
                            let parent = img.parentElement;
                            let text = '';
                            for (let k = 0; k < 5 && parent; k++) {
                                text = parent.innerText;
                                if (text && text.length > 2) break;
                                parent = parent.parentElement;
                            }
                            if (text) {
                                // Find which item this ID belongs to
                                for (const item of items) {
                                    if (text.includes(item.name)) {
                                        item.id = id;
                                        break;
                                    }
                                }
                            }
                        }
                    }
                }
                
                return items;
            }
        ''')
        
        await browser.close()
        
        # Clean up and group by ID and rate
        form_map = {}
        for item in pokemon_data:
            if not item['id'] or not item['rate'] or not item['name']:
                continue
            
            id = item['id']
            rate = round(item['rate'], 2)
            name = item['name']
            
            # Clean up name
            name = name.replace('Shiny', '').strip()
            
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
