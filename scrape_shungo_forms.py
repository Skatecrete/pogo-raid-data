import requests
import re
import json
from datetime import datetime

def scrape_shungo_forms():
    print("🚀 Scraping Shungo forms from webpage...")
    
    url = "https://shungo.app/tools/wild"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    html = response.text
    
    print(f"HTML length: {len(html)}")
    print(f"First 500 chars: {html[:500]}")
    
    # Look for patterns
    pattern = r'([A-Za-z\s\-\(\)]+)\n(\d+\.?\d*)%\n(\d+)'
    matches = re.findall(pattern, html)
    
    print(f"Found {len(matches)} matches via regex")
    
    form_map = {}
    
    for match in matches:
        name = match[0].strip()
        rate = float(match[1])
        pokemon_id = int(match[2])
        
        rounded_rate = round(rate, 2)
        
        if pokemon_id not in form_map:
            form_map[pokemon_id] = {}
        
        if rounded_rate in form_map[pokemon_id]:
            existing = form_map[pokemon_id][rounded_rate]
            if existing != name:
                form_map[pokemon_id][rounded_rate] = f"{existing} or {name}"
        else:
            form_map[pokemon_id][rounded_rate] = name
        
        print(f"Found: ID {pokemon_id}, Rate {rounded_rate}%, Name: {name}")
    
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "form_mappings": form_map
    }
    
    with open('shungo_forms.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Saved to shungo_forms.json")

if __name__ == "__main__":
    scrape_shungo_forms()
