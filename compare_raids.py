import json
import requests
import os
import sys
from datetime import datetime

# Configuration
CONFIRMATION_COUNT = 2
TRACKER_FILE = 'pending_removals.json'

def fetch_scrapedduck_raids():
    """Fetch current raids from ScrapedDuck API"""
    try:
        url = "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/data/raids.min.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"ScrapedDuck API returned {response.status_code}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Error fetching ScrapedDuck: {e}", file=sys.stderr)
        return []

def get_raid_key(raid):
    """Create a unique key for a raid with normalization"""
    name = raid.get('name', '').strip().lower()
    name = name.replace('d-max ', '').replace('dynamax ', '').replace('g-max ', '')
    name = name.strip()
    tier = raid.get('tier', '').strip().lower()
    return f"{name}|{tier}"

def extract_name_from_raid_obj(raid_obj):
    if isinstance(raid_obj, dict):
        return raid_obj.get('name', '')
    return str(raid_obj)

def load_removal_tracker():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_removal_tracker(tracker):
    with open(TRACKER_FILE, 'w') as f:
        json.dump(tracker, f, indent=2)

def get_confirmed_removals(removed_set, tracker):
    now = datetime.now().isoformat()
    new_tracker = {}
    confirmed = set()
    
    for raid in removed_set:
        if raid in tracker:
            count = tracker[raid]['count'] + 1
            if count >= CONFIRMATION_COUNT:
                confirmed.add(raid)
            new_tracker[raid] = {
                'first_seen': tracker[raid]['first_seen'],
                'count': count
            }
        else:
            new_tracker[raid] = {
                'first_seen': now,
                'count': 1
            }
    
    return confirmed, new_tracker

def main():
    print("compare_raids.py running...", file=sys.stderr)
    
    tracker = load_removal_tracker()
    
    try:
        with open('current_raids_old.json', 'r') as f:
            old_snacknap = json.load(f)
    except:
        old_snacknap = {"last_updated": "", "tier1": [], "tier3": [], "tier5": [], "mega": [], "dynamax_tier1": [], "dynamax_tier2": [], "dynamax_tier3": [], "dynamax_tier5": [], "gigantamax": []}
    
    with open('current_raids.json', 'r') as f:
        new_snacknap = json.load(f)
    
    # DEBUG: Check Cottonee
    for category in ['dynamax_tier1', 'tier1', 'tier3']:
        old_list = old_snacknap.get(category, [])
        new_list = new_snacknap.get(category, [])
        
        old_names = [extract_name_from_raid_obj(r) for r in old_list]
        new_names = [extract_name_from_raid_obj(r) for r in new_list]
        
        old_cottonee = [n for n in old_names if 'cottonee' in n.lower()]
        new_cottonee = [n for n in new_names if 'cottonee' in n.lower()]
        
        if old_cottonee or new_cottonee:
            print(f"Cottonee in {category}: old={old_cottonee} new={new_cottonee}", file=sys.stderr)
            for c in old_cottonee:
                print(f"  Old repr: {repr(c)}", file=sys.stderr)
            for c in new_cottonee:
                print(f"  New repr: {repr(c)}", file=sys.stderr)
    
    try:
        with open('scrapedduck_old.json', 'r') as f:
            old_scrapedduck_data = json.load(f)
    except:
        old_scrapedduck_data = []
    
    current_scrapedduck = fetch_scrapedduck_raids()
    
    old_scrapedduck_set = set()
    for raid in old_scrapedduck_data:
        old_scrapedduck_set.add(get_raid_key(raid))
    
    new_scrapedduck_set = set()
    for raid in current_scrapedduck:
        new_scrapedduck_set.add(get_raid_key(raid))
    
    scrapedduck_added = new_scrapedduck_set - old_scrapedduck_set
    scrapedduck_removed = old_scrapedduck_set - new_scrapedduck_set
    
    for added in scrapedduck_added:
        if 'cottonee' in added.lower():
            print(f"COTTONEE ADDED in ScrapedDuck: {added}", file=sys.stderr)
    for removed in scrapedduck_removed:
        if 'cottonee' in removed.lower():
            print(f"COTTONEE REMOVED in ScrapedDuck: {removed}", file=sys.stderr)
    
    confirmed_removals, updated_tracker = get_confirmed_removals(scrapedduck_removed, tracker)
    
    for raid in list(updated_tracker.keys()):
        if raid not in scrapedduck_removed:
            del updated_tracker[raid]
    
    save_removal_tracker(updated_tracker)
    
    with open('scrapedduck_old.json', 'w') as f:
        json.dump(current_scrapedduck, f, indent=2)
    
    categories = ['tier1', 'tier3', 'tier5', 'mega', 'dynamax_tier1', 'dynamax_tier2', 'dynamax_tier3', 'dynamax_tier5', 'gigantamax']
    display_names = {
        'tier1': '⭐ 1-Star Raids',
        'tier3': '⭐⭐⭐ 3-Star Raids',
        'tier5': '⭐⭐⭐⭐⭐ 5-Star Raids',
        'mega': '🔴 Mega Raids',
        'dynamax_tier1': '⚡ Dynamax Tier 1',
        'dynamax_tier2': '⚡⚡ Dynamax Tier 2',
        'dynamax_tier3': '⚡⚡⚡ Dynamax Tier 3',
        'dynamax_tier5': '⚡⚡⚡⚡⚡ Dynamax Tier 5',
        'gigantamax': '💥 Gigantamax'
    }
    
    changes = []
    
    for category in categories:
        old_list = old_snacknap.get(category, [])
        new_list = new_snacknap.get(category, [])
        
        old_names = set(extract_name_from_raid_obj(r) for r in old_list)
        new_names = set(extract_name_from_raid_obj(r) for r in new_list)
        
        added = new_names - old_names
        removed = old_names - new_names
        
        if added or removed:
            changes.append(f"\n**{display_names[category]}:**")
            if added:
                changes.append(f"  ✅ Added: {', '.join(sorted(added))}")
            if removed:
                confirmed_removed_names = [r for r in removed if r in confirmed_removals]
                if confirmed_removed_names:
                    changes.append(f"  ❌ Removed: {', '.join(sorted(confirmed_removed_names))}")
    
    if scrapedduck_added or confirmed_removals:
        added_by_tier = {}
        for key in scrapedduck_added:
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
            
            if display_tier not in added_by_tier:
                added_by_tier[display_tier] = []
            added_by_tier[display_tier].append(name)
        
        removed_by_tier = {}
        for key in confirmed_removals:
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
    
    with open('raid_changes.txt', 'w') as f:
        if changes:
            f.write('\n'.join(changes))
            print("true")
        else:
            f.write("No changes detected")
            print("false")

if __name__ == "__main__":
    main()
