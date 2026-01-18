
import requests
from bs4 import BeautifulSoup
import re


URLS = [
    "https://mirrors.kodi.tv/releases/windows/win64/test-builds/",
    "https://mirrors.kodi.tv/test-builds/windows/win64/",
    "https://mirrors.kodi.tv/nightlies/windows/win64/master/"
]

def debug_links():
    for url in URLS:
        try:
            print(f"Fetching {url}...")
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"Links found in {url}:")
            found = False
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and "exe" in href:
                    print(f" - {href}")
                    found = True
            if not found:
                print("  No .exe files found.")
                
        except Exception as e:
            print(f"Error fetching {url}: {e}")


if __name__ == "__main__":
    debug_links()
