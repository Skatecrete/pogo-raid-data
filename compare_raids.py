import json
import requests

def fetch_scrapedduck_raids():
    """Fetch current raids from ScrapedDuck API"""
    try:
        url = "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/data/raids.min.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"ScrapedDuck API returned {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching ScrapedDuck: {e}")
        return []

def get_raid_key(raid):
    """Create a unique key for a raid"""
    name = raid.get('name', '').strip()
    tier = raid.get('tier', '').strip()
    return f"{name}|{tier}"

def main():
    # Load old SnackNap data
    try:
        with open('current_raids_old.json', 'r') as f:
            old_snacknap = json.load(f)
    except:
        old_snacknap = {"last_updated": "", "tier1": [], "tier3": [], "dynamax_tier1": [], "dynamax_tier2": [], "dynamax_tier3": [], "gigantamax": []}
    
    # Load new SnackNap data
    with open('current_raids.json', 'r') as f:
        new_snacknap = json.load(f)
    
    # Load old ScrapedDuck data if exists
    try:
        with open('scrapedduck_old.json', 'r') as f:
            old_scrapedduck_data = json.load(f)
    except:
        old_scrapedduck_data = []
    
    # Fetch current ScrapedDuck raids
    current_scrapedduck = fetch_scrapedduck_raids()
    
    # Build sets for comparison
    old_scrapedduck_set = set()
    for raid in old_scrapedduck_data:
        old_scrapedduck_set.add(get_raid_key(raid))
    
    new_scrapedduck_set = set()
    for raid in current_scrapedduck:
        new_scrapedduck_set.add(get_raid_key(raid))
    
    # Find added and removed ScrapedDuck raids
    scrapedduck_added = new_scrapedduck_set - old_scrapedduck_set
    scrapedduck_removed = old_scrapedduck_set - new_scrapedduck_set
    
    # Save current ScrapedDuck for next comparison
    with open('scrapedduck_old.json', 'w') as f:
        json.dump(current_scrapedduck, f)
    
    # SnackNap categories
    categories = ['tier1', 'tier3', 'dynamax_tier1', 'dynamax_tier2', 'dynamax_tier3', 'gigantamax']
    display_names = {
        'tier1': '⭐ 1-Star Raids',
        'tier3': '⭐⭐⭐ 3-Star Raids',
        'dynamax_tier1': '⚡ Dynamax Tier 1',
        'dynamax_tier2': '⚡⚡ Dynamax Tier 2',
        'dynamax_tier3': '⚡⚡⚡ Dynamax Tier 3',
        'gigantamax': '💥 Gigantamax'
    }
    
    changes = []
    
    # Check SnackNap changes
    for category in categories:
        old_set = set(old_snacknap.get(category, []))
        new_set = set(new_snacknap.get(category, []))
        
        added = new_set - old_set
        removed = old_set - new_set
        
        if added or removed:
            changes.append(f"\n**{display_names[category]}:**")
            if added:
                changes.append(f"  ✅ Added: {', '.join(sorted(added))}")
            if removed:
                changes.append(f"  ❌ Removed: {', '.join(sorted(removed))}")
    
    # Check ScrapedDuck changes
    if scrapedduck_added or scrapedduck_removed:
        # Parse added raids by tier
        added_by_tier = {}
        for key in scrapedduck_added:
            name, tier = key.rsplit('|', 1)
            # Clean up tier name for display
            display_tier = tier
            if 'Shadow' in tier:
                if '5-Star' in tier or 'Legendary' in tier:
                    display_tier = '🌑 Shadow Legendary'
                elif '3-Star' in tier:
                    display_tier = '🌑 Shadow 3-Star'
                elif '1-Star' in tier:
                    display_tier = '🌑 Shadow 1-Star'
                else:
                    display_tier = '🌑 Shadow'
            elif 'Mega' in tier:
                display_tier = '🔴 Mega'
            else:
                display_tier = tier
            
            if display_tier not in added_by_tier:
                added_by_tier[display_tier] = []
            added_by_tier[display_tier].append(name)
        
        removed_by_tier = {}
        for key in scrapedduck_removed:
            name, tier = key.rsplit('|', 1)
            display_tier = tier
            if 'Shadow' in tier:
                if '5-Star' in tier or 'Legendary' in tier:
                    display_tier = '🌑 Shadow Legendary'
                elif '3-Star' in tier:
                    display_tier = '🌑 Shadow 3-Star'
                elif '1-Star' in tier:
                    display_tier = '🌑 Shadow 1-Star'
                else:
                    display_tier = '🌑 Shadow'
            elif 'Mega' in tier:
                display_tier = '🔴 Mega'
            else:
                display_tier = tier
            
            if display_tier not in removed_by_tier:
                removed_by_tier[display_tier] = []
            removed_by_tier[display_tier].append(name)
        
        if added_by_tier or removed_by_tier:
            changes.append(f"\n**🔥 OTHER RAIDS (5-Star, Mega, Shadow):**")
            
            for tier, names in added_by_tier.items():
                changes.append(f"  ✅ Added {tier}: {', '.join(sorted(names))}")
            
            for tier, names in removed_by_tier.items():
                changes.append(f"  ❌ Removed {tier}: {', '.join(sorted(names))}")
    
    # Save changes to file
    with open('raid_changes.txt', 'w') as f:
        if changes:
            f.write('\n'.join(changes))
            print("changes=true")
        else:
            f.write("No changes detected")
            print("changes=false")

if __name__ == "__main__":
    main()
