import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from urllib.parse import unquote

def decode_image_url(srcset_or_src):
    """Extract and decode the actual image URL from Next.js srcset or src attribute."""
    if not srcset_or_src:
        return None
    
    # If it's a srcset, get the first/largest URL
    if srcset_or_src and ',' in srcset_or_src:
        parts = srcset_or_src.split(',')
        last_part = parts[-1].strip().split(' ')
        src_value = last_part[0] if last_part else srcset_or_src.split(' ')[0]
    else:
        src_value = srcset_or_src
    
    # Extract the encoded URL from the src pattern
    match = re.search(r'url=([^&]+)', src_value)
    if match:
        encoded = match.group(1)
        decoded = unquote(encoded)
        return decoded
    
    if src_value.startswith('http'):
        return src_value
    
    return None

def scrape_item_boxes():
    """Scrape item boxes from the Pokémon GO store."""
    print("🚀 Starting Item Box scraper...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    url = "https://store.pokemongo.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        bundle_section = soup.find('div', id='BUNDLE')
        if not bundle_section:
            print("❌ Could not find #BUNDLE section")
            return []
        
        box_buttons = bundle_section.find_all('button')
        print(f"📦 Found {len(box_buttons)} boxes")
        
        boxes = []
        
        for i, button in enumerate(box_buttons):
            try:
                # Extract box name
                title_elem = button.find('h6', class_='contentContainerTitle')
                if not title_elem:
                    continue
                box_name = title_elem.get_text().strip()
                
                # Extract price
                price_elem = button.find('div', class_='flex', recursive=True)
                if price_elem:
                    price_text = price_elem.get_text().strip()
                    price_match = re.search(r'[\d.]+', price_text)
                    if price_match:
                        in_store_price = float(price_match.group())
                    else:
                        continue
                else:
                    continue
                
                # ========== FIX: Extract box image (skip badge) ==========
                box_image = None
                
                # Method 1: Look for media-main-container
                media_container = button.find('div', {'data-testid': 'sku-card.media-main-container'})
                if media_container:
                    img = media_container.find('img')
                    if img:
                        srcset = img.get('srcset', '')
                        src = img.get('src', '')
                        box_image = decode_image_url(srcset) or decode_image_url(src)
                
                # Method 2: Fallback - get any img that's NOT a badge
                if not box_image:
                    for img in button.find_all('img'):
                        alt = img.get('alt', '').lower()
                        # Skip badge images
                        if 'badge' in alt or 'web only' in alt:
                            continue
                        srcset = img.get('srcset', '')
                        src = img.get('src', '')
                        box_image = decode_image_url(srcset) or decode_image_url(src)
                        if box_image:
                            break
                # =========================================================
                
                # Extract items and counts
                items = []
                item_list = button.find('ul')
                if item_list:
                    for li in item_list.find_all('li'):
                        img = li.find('img')
                        if not img:
                            continue
                        
                        item_name = img.get('alt', '').strip()
                        item_image = decode_image_url(img.get('srcset', '')) or decode_image_url(img.get('src', ''))
                        
                        count_elem = li.find('p')
                        item_count = 1
                        if count_elem:
                            count_text = count_elem.get_text().strip()
                            if count_text.isdigit():
                                item_count = int(count_text)
                        
                        if item_name or item_image:
                            items.append({
                                'name': item_name if item_name else f"Item {len(items) + 1}",
                                'count': item_count,
                                'image': item_image
                            })
                
                boxes.append({
                    'box_name': box_name,
                    'in_store_price': in_store_price,
                    'box_image': box_image,
                    'items': items
                })
                
                print(f"  ✅ {box_name} - ${in_store_price:.2f} ({len(items)} items)")
                
            except Exception as e:
                print(f"  ⚠️ Error parsing box {i+1}: {e}")
                continue
        
        return boxes
        
    except Exception as e:
        print(f"❌ Error scraping store: {e}")
        return []


def calculate_silphco_price(price):
    """Calculate SilphCo price with discount and rounding."""
    if price < 20:
        discounted = price * 0.6
    else:
        discounted = price * 0.5
    
    rounded = (discounted + 0.49) // 0.5 * 0.5
    return round(rounded, 2)


def main():
    print("=" * 60)
    print("🛒 POKEMON GO STORE - ITEM BOX SCRAPER")
    print("=" * 60)
    
    boxes = scrape_item_boxes()
    
    if not boxes:
        output = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": True,
            "message": "Failed to scrape store boxes. Please contact admin.",
            "boxes": []
        }
        with open('store_boxes.json', 'w') as f:
            json.dump(output, f, indent=2)
        print("💾 Saved store_boxes.json with error state")
        return
    
    for box in boxes:
        box['silphco_price'] = calculate_silphco_price(box['in_store_price'])
    
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": False,
        "total": len(boxes),
        "boxes": boxes
    }
    
    with open('store_boxes.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"  ✅ Total boxes: {len(boxes)}")
    print("\n  📦 Boxes:")
    for box in boxes:
        print(f"    - {box['box_name']}")
        print(f"      In-Store: ${box['in_store_price']:.2f}")
        print(f"      SilphCo: ${box['silphco_price']:.2f}")
        print(f"      Items: {len(box['items'])}")
    print("\n" + "=" * 60)
    
    print("\n💾 Saved store_boxes.json")


if __name__ == "__main__":
    main()
