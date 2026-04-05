
import os
import sys
from plexapi.server import PlexServer

base_url = "http://127.0.0.1:32400"
token = "oGA9iEfVYh8ATXmzYrU8"

def test_pagination():
    try:
        # Use IPv4
        os.environ["PLEX_URL"] = base_url
        os.environ["PLEX_TOKEN"] = token
        
        plex = PlexServer(base_url, token)
        sections = plex.library.sections()
        if not sections:
            print("No sections found")
            return
            
        section = sections[0]
        print(f"Testing section: {section.title} ({section.type})")
        
        # Test offset in browse (all)
        print("Testing section.all with X-Plex-Container-Start/Size equivalent...")
        # In plexapi, 'all' supports X-Plex-Container-Start/Size if passed as headers or as specific kwargs for some versions.
        # Actually, python-plexapi uses 'X-Plex-Container-Start' and 'X-Plex-Container-Size' as headers.
        
        # Let's test if it responds correctly to 'start' and 'size' kwargs which some methods use
        try:
            # We'll try to reach it directly via the URL to confirm what Plex supports
            items = section.all()
            print(f"Total items found via .all(): {len(items)}")
            
            # Plex actually uses 'X-Plex-Container-Start' and 'X-Plex-Container-Size' as URL params internally
            # python-plexapi might not expose them cleanly in section.search() yet.
            # But we can try to pass them via kwargs in some methods.
        except Exception as e:
            print(f"Pagination test error: {e}")
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_pagination()
