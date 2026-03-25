def scrape_snacknap_raids():
    print("  📡 Fetching regular raids...")
    url = "https://www.snacknap.com/raids"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
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
        
        # Find all sections with headers
        # Look for h2 or h3 elements that indicate raid tiers
        all_headers = soup.find_all(['h2', 'h3'])
        
        current_tier = None
        current_section = None
        
        for header in all_headers:
            header_text = header.get_text().strip()
            
            # Check for regular raid tiers
            if 'Tier 1' in header_text and 'Shadow' not in header_text:
                current_tier = 'tier1'
                current_section = header
            elif 'Tier 2' in header_text and 'Shadow' not in header_text:
                current_tier = 'tier2'
                current_section = header
            elif 'Tier 3' in header_text and 'Shadow' not in header_text:
                current_tier = 'tier3'
                current_section = header
            elif 'Tier 4' in header_text and 'Shadow' not in header_text:
                current_tier = 'tier4'
                current_section = header
            elif 'Tier 5' in header_text or 'Legendary' in header_text:
                if 'Shadow' not in header_text:
                    current_tier = 'tier5'
                    current_section = header
            elif 'Mega' in header_text:
                current_tier = 'mega'
                current_section = header
            # Check for Shadow tiers
            elif 'Shadow Tier 1' in header_text or ('Shadow' in header_text and 'Tier 1' in header_text):
                current_tier = 'shadow'
                current_section = header
                print(f"    Found Shadow Tier 1 section")
            elif 'Shadow Tier 3' in header_text or ('Shadow' in header_text and 'Tier 3' in header_text):
                current_tier = 'shadow'
                current_section = header
                print(f"    Found Shadow Tier 3 section")
            elif 'Shadow Legendary' in header_text or ('Shadow' in header_text and 'Legendary' in header_text):
                current_tier = 'shadow'
                current_section = header
                print(f"    Found Shadow Legendary section")
            elif '6-Star' in header_text or 'Elite' in header_text:
                current_tier = 'six_star'
                current_section = header
            
            if current_tier and current_section:
                # Now find all Pokemon cards after this header until the next header
                next_elements = []
                next_element = current_section.find_next_sibling()
                
                while next_element and next_element.name not in ['h2', 'h3']:
                    next_elements.append(next_element)
                    next_element = next_element.find_next_sibling()
                
                # Look for Pokemon in the cards
                for element in next_elements:
                    # Find all cards or links containing Pokemon info
                    pokemon_cards = element.find_all(['div', 'a'], class_=re.compile('card|col-xl-2|col-md-4|raid-card'))
                    if not pokemon_cards:
                        pokemon_cards = [element]
                    
                    for card in pokemon_cards:
                        # Try to find Pokemon name
                        title = None
                        
                        # Look for img alt text (often has the Pokemon name)
                        img = card.find('img')
                        if img and img.get('alt'):
                            title = img.get('alt')
                        
                        # Look for link title
                        if not title:
                            link = card.find('a')
                            if link and link.get('title'):
                                title = link.get('title')
                        
                        # Look for any text that might be a Pokemon name
                        if not title:
                            text = card.get_text().strip()
                            # Filter out non-Pokemon text
                            lines = text.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line and not any(x in line for x in ['CP', 'cp', 'Shadow', 'Shiny', 'Normal', 'Dragon', 'Fire', 'Water', 'Grass', 'Electric', 'Bug', 'Ground', 'Flying', 'Ghost', 'Ice', 'Psychic']):
                                    if len(line) < 30 and not line.isdigit():
                                        title = line
                                        break
                        
                        if title:
                            # Clean the title
                            clean_title = title.replace('Shadow', '').replace('Shiny', '').strip()
                            # Remove Pokemon types if they appear
                            for type_word in ['Normal', 'Fire', 'Water', 'Grass', 'Electric', 'Bug', 'Ground', 'Flying', 'Ghost', 'Ice', 'Psychic', 'Dragon', 'Dark', 'Steel', 'Fairy', 'Rock', 'Fighting', 'Poison']:
                                clean_title = clean_title.replace(type_word, '').strip()
                            
                            if clean_title and clean_title not in raid_data[current_tier]:
                                raid_data[current_tier].append(clean_title)
                                if current_tier == 'shadow':
                                    print(f"      Added Shadow: {clean_title}")
        
        # Also check for any direct links that might contain Pokemon
        all_links = soup.find_all('a', href=re.compile('/raids/'))
        for link in all_links:
            title = link.get('title')
            if title and not any(title in tier_list for tier_list in raid_data.values()):
                # Try to determine tier from parent
                parent = link.parent
                parent_text = parent.get_text() if parent else ""
                
                if 'Shadow' in parent_text or 'Shadow' in title:
                    if title not in raid_data['shadow']:
                        raid_data['shadow'].append(title)
                elif 'Tier 5' in parent_text or 'Legendary' in parent_text:
                    if title not in raid_data['tier5']:
                        raid_data['tier5'].append(title)
                elif 'Mega' in parent_text:
                    if title not in raid_data['mega']:
                        raid_data['mega'].append(title)
        
        # Remove duplicates and clean
        for tier in raid_data:
            raid_data[tier] = list(set(raid_data[tier]))
        
        print(f"    Found {sum(len(v) for v in raid_data.values())} total raids")
        print(f"    Shadow raids found: {len(raid_data['shadow'])}")
        if raid_data['shadow']:
            print(f"    Shadow: {raid_data['shadow']}")
        
        return raid_data
    except Exception as e:
        print(f"    ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
