import json
import requests
import os
import sys
from datetime import datetime

# Configuration
CONFIRMATION_COUNT = 2
TRACKER_FILE = 'pending_removals.json'
LAST_SENT_FILE = 'current_raids_last_sent.json'

# Ultra Beast names to filter out of ScrapedDuck notifications
ULTRA_BEAST_NAMES = ['nihilego', 'buzzwole', 'pheromosa', 'xurkitree', 'celesteela', 
                     'kartana', 'guzzlord', 'poipole', 'naganadel', 'stakataka', 'blacephalon']

def is_ultra_beast(name):
    """Check if a raid name is an Ultra Beast"""
    return name.lower() in ULTRA_BEAST_NAMES

def safe_json_save(data, filepath):
    """Safely save JSON data, ensuring it's valid"""
    try:
        json_str = json.dumps(data, indent=2)
        json.loads(json_str)
        with open(filepath, 'w') as f:
            f.write(json_str)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}", file=sys.stderr)
        return False

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
    """Extract name from raid object"""
    if isinstance(raid_obj, dict):
        return raid_obj.get('name', '')
    return str(raid_obj)

def normalize_raid_name(name):
    """Normalize raid name for comparison"""
    name = str(name).strip().lower()
    name = name.replace('d-max ', '').replace('dynamax ', '').replace('g-max ', '')
    name = name.replace('mega ', '')
    return name.strip()

def load_removal_tracker():
    """Load the tracking file for pending removals"""
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {TRACKER_FILE} is corrupted. Creating new file.", file=sys.stderr)
            return {}
    return {}

def save_removal_tracker(tracker):
    """Save the tracking file"""
    safe_json_save(tracker, TRACKER_FILE)

def load_last_sent():
    """Load the last state that was successfully sent as notification"""
    empty_structure = {
        "last_updated": "",
        "tier1": [],
        "tier3": [],
        "tier5": [],
        "mega": [],
        "ultra_beasts": [],
        "dynamax_tier1": [],
        "dynamax_tier2": [],
        "dynamax_tier3": [],
        "dynamax_tier5": [],
        "gigantamax": [],
        "scrapedduck_raids": []
    }
    
    if os.path.exists(LAST_SENT_FILE):
        try:
            with open(LAST_SENT_FILE, 'r') as f:
                data = json.load(f)
                for key in empty_structure:
                    if key not in data:
                        data[key] = empty_structure[key]
                return data
        except json.JSONDecodeError:
            print(f"Warning: {LAST_SENT_FILE} is corrupted. Creating new file.", file=sys.stderr)
            return empty_structure
    return empty_structure

def save_last_sent(snacknap_data, scrapedduck_data):
    """Save the current state as last sent"""
    data = snacknap_data.copy()
    data['scrapedduck_raids'] = [get_raid_key(r) for r in scrapedduck_data]
    data['last_sent_time'] = datetime.now().isoformat()
    safe_json_save(data, LAST_SENT_FILE)

def get_confirmed_removals(removed_set, tracker):
    """Return raids that have been removed for CONFIRMATION_COUNT consecutive scans"""
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

def normalize_raid_list(raid_list):
    """Normalize a list of raid names for comparison"""
    normalized = set()
    for r in raid_list:
        name = normalize_raid_name(extract_name_from_raid_obj(r))
        if name:
            normalized.add(name)
    return normalized

def get_tier_display(tier, name):
    """Convert tier string to display format with emoji"""
    tier_lower = tier.lower()
    name_lower = name.lower()

    if 'shadow' in name_lower or 'shadow' in tier_lower:
        if '5-star' in tier_lower or 'legendary' in tier_lower:
            return '🌑 Shadow Legendary'
        elif '3-star' in tier_lower:
            return '🌑 Shadow 3-Star'
        elif '1-star' in tier_lower:
            return '🌑 Shadow 1-Star'
        else:
            return '🌑 Shadow'

    if 'ultra beast' in tier_lower or 'ultra beast' in name_lower:
        return '🌀 Ultra Beast'

    if 'mega' in tier_lower or 'mega' in name_lower:
        return '🔴 Mega'

    if 'dynamax' in tier_lower:
        if 'tier 5' in tier_lower:
            return '⚡⚡⚡⚡⚡ Dynamax Tier 5'
        elif 'tier 4' in tier_lower:
            return '⚡⚡⚡⚡ Dynamax Tier 4'
        elif 'tier 3' in tier_lower:
            return '⚡⚡⚡ Dynamax Tier 3'
        elif 'tier 2' in tier_lower:
            return '⚡⚡ Dynamax Tier 2'
        elif 'tier 1' in tier_lower:
            return '⚡ Dynamax Tier 1'
        else:
            return '⚡ Dynamax'

    if 'gigantamax' in tier_lower or 'gigantamax' in name_lower:
        return '💥 Gigantamax'

    if '5-star' in tier_lower:
        return '⭐⭐⭐⭐⭐ 5-Star Raids'
    if '4-star' in tier_lower:
        return '⭐⭐⭐⭐ 4-Star Raids'
    if '3-star' in tier_lower:
        return '⭐⭐⭐ 3-Star Raids'
    if '2-star' in tier_lower:
        return '⭐⭐ 2-Star Raids'
    if '1-star' in tier_lower:
        return '⭐ 1-Star Raids'

    return None

def main():
    print("compare_raids.py running...", file=sys.stderr)

    removal_tracker = load_removal_tracker()
    last_sent = load_last_sent()

    # Check if this is first run
    is_first_run = last_sent.get('last_updated') == "" or len(last_sent.get('tier1', [])) == 0
    print(f"DEBUG: is_first_run = {is_first_run}", file=sys.stderr)

    with open('current_raids.json', 'r') as f:
        new_snacknap = json.load(f)

    current_scrapedduck = fetch_scrapedduck_raids()
    current_scrapedduck_keys = set(get_raid_key(r) for r in current_scrapedduck)
    last_scrapedduck_keys = set(last_sent.get('scrapedduck_raids', []))

    # If first run, save baseline and exit WITHOUT sending notification
    if is_first_run:
        print("First run - saving baseline, no notification", file=sys.stderr)
        save_last_sent(new_snacknap, current_scrapedduck)
        with open('raid_changes.txt', 'w') as f:
            f.write("No changes detected")
            print("false")
        return

    categories = ['tier1', 'tier3', 'tier5', 'mega', 'ultra_beasts', 'dynamax_tier1', 'dynamax_tier2', 'dynamax_tier3', 'dynamax_tier5', 'gigantamax']
    display_names = {
        'tier1': '⭐ 1-Star Raids',
        'tier3': '⭐⭐⭐ 3-Star Raids',
        'tier5': '⭐⭐⭐⭐⭐ 5-Star Raids',
        'mega': '🔴 Mega Raids',
        'ultra_beasts': '🌀 Ultra Beasts',
        'dynamax_tier1': '⚡ Dynamax Tier 1',
        'dynamax_tier2': '⚡⚡ Dynamax Tier 2',
        'dynamax_tier3': '⚡⚡⚡ Dynamax Tier 3',
        'dynamax_tier5': '⚡⚡⚡⚡⚡ Dynamax Tier 5',
        'gigantamax': '💥 Gigantamax'
    }

    changes = []
    should_send = False

    for category in categories:
        new_list = new_snacknap.get(category, [])
        last_list = last_sent.get(category, [])

        new_names = normalize_raid_list(new_list)
        last_names = normalize_raid_list(last_list)

        added = new_names - last_names
        removed = last_names - new_names

        category_lines = []
        has_visible = False

        if added:
            category_lines.append(f"  ✅ Added: {', '.join(sorted(added))}")
            should_send = True
            has_visible = True

        if removed:
            confirmed_removals, removal_tracker = get_confirmed_removals(removed, removal_tracker)
            if confirmed_removals:
                category_lines.append(f"  ❌ Removed: {', '.join(sorted(confirmed_removals))}")
                should_send = True
                has_visible = True

        if has_visible:
            changes.append(f"\n**{display_names[category]}:**")
            changes.extend(category_lines)

    scrapedduck_added = current_scrapedduck_keys - last_scrapedduck_keys
    scrapedduck_removed = last_scrapedduck_keys - current_scrapedduck_keys

    confirmed_scrapedduck_removals, removal_tracker = get_confirmed_removals(scrapedduck_removed, removal_tracker)

    added_by_tier = {}
    removed_by_tier = {}
    uncategorized_added = []
    uncategorized_removed = []

    # Process ScrapedDuck additions - SKIP ULTRA BEASTS
    for key in scrapedduck_added:
        name, tier = key.rsplit('|', 1)
        
        # Skip Ultra Beasts - they come from SnackNap's ultra_beasts array
        if is_ultra_beast(name):
            print(f"DEBUG: Skipping Ultra Beast from ScrapedDuck: {name}", file=sys.stderr)
            continue
            
        display_tier = get_tier_display(tier, name)

        if display_tier:
            if display_tier not in added_by_tier:
                added_by_tier[display_tier] = []
            added_by_tier[display_tier].append(name)
            should_send = True
        else:
            uncategorized_added.append(f"{name} ({tier})")
            should_send = True

    # Process ScrapedDuck removals - SKIP ULTRA BEASTS
    for key in confirmed_scrapedduck_removals:
        name, tier = key.rsplit('|', 1)
        
        # Skip Ultra Beasts
        if is_ultra_beast(name):
            continue
            
        display_tier = get_tier_display(tier, name)

        if display_tier:
            if display_tier not in removed_by_tier:
                removed_by_tier[display_tier] = []
            removed_by_tier[display_tier].append(name)
            should_send = True
        else:
            uncategorized_removed.append(f"{name} ({tier})")
            should_send = True

    for tier, names in sorted(added_by_tier.items()):
        changes.append(f"\n**{tier}:**")
        changes.append(f"  ✅ Added: {', '.join(sorted(names))}")

    for tier, names in sorted(removed_by_tier.items()):
        tier_exists = any(tier in str(c) for c in changes)
        if not tier_exists:
            changes.append(f"\n**{tier}:**")
        changes.append(f"  ❌ Removed: {', '.join(sorted(names))}")

    if uncategorized_added or uncategorized_removed:
        changes.append(f"\n**⚠️ OTHER RAIDS (Uncategorized):**")
        if uncategorized_added:
            changes.append(f"  ✅ Added: {', '.join(sorted(uncategorized_added))}")
        if uncategorized_removed:
            changes.append(f"  ❌ Removed: {', '.join(sorted(uncategorized_removed))}")

    for raid in list(removal_tracker.keys()):
        if raid not in scrapedduck_removed:
            del removal_tracker[raid]

    save_removal_tracker(removal_tracker)

    # Only save last_sent if there are actual changes
    if changes:
        save_last_sent(new_snacknap, current_scrapedduck)
        print("Updated last_sent file", file=sys.stderr)

    with open('raid_changes.txt', 'w') as f:
        if changes:
            f.write('\n'.join(changes))
            print("true")
            print("Changes detected, notification will be sent", file=sys.stderr)
        else:
            f.write("No changes detected")
            print("false")
            print("No changes detected", file=sys.stderr)

if __name__ == "__main__":
    main()
