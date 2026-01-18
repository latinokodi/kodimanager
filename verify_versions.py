
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from kodimanager.core.downloader import KodiDownloader

def verify():
    downloader = KodiDownloader()
    print("Fetching versions...")
    versions = downloader.get_available_versions()
    
    print(f"Total versions found: {len(versions)}")
    
    if len(versions) < 3:
        print("Warning: Too few versions found. Might indicate filtering issue or network issue.")
        
    print("\nTop 10 Versions:")
    for v in versions[:10]:
        tag = v.get('tag', '')
        display = f"{v['version']}"
        if tag:
            display += f" {tag}"
        display += f" - {v['codename']}"
        print(f"  {display}")
        
    # Check if we have any unstable
    unstable_count = sum(1 for v in versions if not v['is_stable'])
    print(f"\nUnstable versions found: {unstable_count}")
    
    if unstable_count > 0:
        print("SUCCESS: Unstable versions detected.")
    else:
        print("FAILURE: No unstable versions found (and we expect some normally).")

if __name__ == "__main__":
    verify()
