"""
Patent Watchlist Manager
Allows users to create and manage their own curated patent lists
"""

import json
import os
from typing import List, Dict
from datetime import datetime


class WatchlistManager:
    """Manages user's patent watchlists"""
    
    def __init__(self, watchlist_file: str = "my_watchlist.json"):
        self.watchlist_file = watchlist_file
        self.watchlists = self.load_watchlists()
    
    def load_watchlists(self) -> Dict:
        """Load watchlists from JSON file"""
        if os.path.exists(self.watchlist_file):
            try:
                with open(self.watchlist_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading watchlist: {e}")
                return self._get_default_watchlists()
        else:
            return self._get_default_watchlists()
    
    def _get_default_watchlists(self) -> Dict:
        """Return default/example watchlists"""
        return {
            "C07": [
                {
                    "id": "WO2024033280",
                    "title": "Furopyridin and furopyrimidin inhibitors of PI4K",
                    "notes": "",
                    "added_date": datetime.now().strftime("%Y-%m-%d")
                },
                {
                    "id": "WO2024033281",
                    "title": "Furo pyrimidine derivatives",
                    "notes": "",
                    "added_date": datetime.now().strftime("%Y-%m-%d")
                }
            ],
            "A61": [
                {
                    "id": "WO2025128873",
                    "title": "Heterocyclic pyridinone compounds as TREM2 agonists",
                    "notes": "",
                    "added_date": datetime.now().strftime("%Y-%m-%d")
                }
            ]
        }
    
    def save_watchlists(self):
        """Save watchlists to JSON file"""
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump(self.watchlists, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving watchlist: {e}")
            return False
    
    def add_patent(self, class_code: str, patent_id: str, title: str = None, notes: str = ""):
        """Add a patent to watchlist"""
        
        # Initialize class if not exists
        if class_code not in self.watchlists:
            self.watchlists[class_code] = []
        
        # Check if already exists
        if any(p['id'] == patent_id for p in self.watchlists[class_code]):
            return False, "Patent already in watchlist"
        
        # If no title provided, try to fetch from Google Patents
        if not title:
            from google_patents_fetcher import fetch_patent_from_google
            patent_data = fetch_patent_from_google(patent_id)
            title = patent_data.get('title', 'Patent filing') if patent_data else 'Patent filing'
        
        # Add patent
        patent_entry = {
            "id": patent_id,
            "title": title[:100],  # Truncate long titles
            "notes": notes,
            "added_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.watchlists[class_code].append(patent_entry)
        self.save_watchlists()
        
        return True, "Patent added successfully"
    
    def remove_patent(self, class_code: str, patent_id: str):
        """Remove a patent from watchlist"""
        
        if class_code not in self.watchlists:
            return False, "Class not found"
        
        # Find and remove
        original_length = len(self.watchlists[class_code])
        self.watchlists[class_code] = [
            p for p in self.watchlists[class_code] 
            if p['id'] != patent_id
        ]
        
        if len(self.watchlists[class_code]) < original_length:
            self.save_watchlists()
            return True, "Patent removed"
        else:
            return False, "Patent not found"
    
    def get_watchlist(self, class_code: str) -> List[Dict]:
        """Get watchlist for a specific class"""
        return self.watchlists.get(class_code, [])
    
    def add_patents_from_csv(self, class_code: str, csv_content: str):
        """
        Add multiple patents from CSV content
        
        CSV format:
        WO2024033280,Optional note
        WO2025128873,Check this one
        WO2026001234
        """
        
        added = 0
        failed = 0
        
        lines = csv_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(',')
            patent_id = parts[0].strip()
            notes = parts[1].strip() if len(parts) > 1 else ""
            
            # Validate patent ID
            if not patent_id.startswith('WO'):
                failed += 1
                continue
            
            success, _ = self.add_patent(class_code, patent_id, notes=notes)
            if success:
                added += 1
            else:
                failed += 1
        
        return added, failed


# ==============================================================================
# TEST CODE
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("WATCHLIST MANAGER - TEST MODE")
    print("="*70)
    
    # Create manager
    wm = WatchlistManager("test_watchlist.json")
    
    # Test adding patent
    print("\nAdding patent to C07 watchlist...")
    success, msg = wm.add_patent("C07", "WO2023219591", "Novel kinase inhibitor compounds")
    print(f"  Result: {msg}")
    
    # Test getting watchlist
    print("\nC07 Watchlist:")
    for patent in wm.get_watchlist("C07"):
        print(f"  - {patent['id']}: {patent['title'][:50]}...")
    
    # Test CSV upload
    print("\nTesting CSV upload...")
    csv_data = """
WO2026001234,Competitor filing - priority
WO2026001235,Interesting scaffold
"""
    added, failed = wm.add_patents_from_csv("C07", csv_data)
    print(f"  Added: {added}, Failed: {failed}")
    
    # Show updated list
    print("\nUpdated C07 Watchlist:")
    for patent in wm.get_watchlist("C07"):
        print(f"  - {patent['id']}: {patent['title'][:50]}...")
    
    # Test removal
    print("\nRemoving WO2026001234...")
    success, msg = wm.remove_patent("C07", "WO2026001234")
    print(f"  Result: {msg}")
    
    print("\n" + "="*70)
    print("✓ Test complete!")
    print("="*70)
