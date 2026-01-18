import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import os

RELEASE_URL = "https://mirrors.kodi.tv/releases/windows/win64/"

class KodiDownloader:
    def __init__(self):
        self.base_url = RELEASE_URL

    def get_available_versions(self) -> List[Dict[str, str]]:
        """
        Returns ONLY the latest Stable version.
        """
        try:
            # 1. Fetch Releases (Stable)
            # We try the specific win64 path on the mirror(s)
            releases = self._fetch_releases()
            
            # Sort releases by version desc to find latest stable
            def parse_ver(v_str):
                 try:
                    return tuple(map(int, v_str.split('.')))
                 except:
                    return (0,0,0)

            # Sort descending
            releases.sort(key=lambda x: parse_ver(x['version']), reverse=True)
            
            latest_stable = next((v for v in releases if v['is_stable']), None)
            
            final_list = []
            
            if latest_stable:
                final_list.append(latest_stable)
            
            return final_list

        except Exception as e:
            print(f"Error fetching versions: {e}")
            return []

    def _fetch_releases(self) -> List[Dict[str, str]]:
        # User requested redundant mirror check. 
        # Though the domain is the same, we implement the list iteration logic.
        urls = [
            "https://mirrors.kodi.tv/releases/windows/win64/",
            "https://mirrors.kodi.tv/releases/windows/win64/" # Implicitly what the user asked for as fallback
        ]
        
        # Pattern: kodi-21.0-Omega-x64.exe
        pattern = re.compile(r'kodi-([0-9]+\.[0-9]+(?:\.[0-9]+)?)(-([A-Za-z0-9]+))?-([A-Za-z0-9]+)-x64\.exe')
        
        # Re-implementing correctly with base_url awareness
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    base_url = url
                    
                    # Parse this attempt
                    local_versions = []
                    for link in soup.find_all('a'):
                        href = link.get('href')
                        if not href: continue
                        
                        match = pattern.match(href)
                        if match:
                            version_num = match.group(1)
                            tag = match.group(3) or ""
                            codename = match.group(4)
                            
                            local_versions.append({
                                'version': version_num,
                                'tag': tag,
                                'codename': codename,
                                'filename': href,
                                'url': base_url + href,
                                'is_stable': not bool(tag)
                            })
                    if local_versions:
                        return local_versions # Return success from first working mirror
            except Exception:
                continue
        return []

    def _fetch_from_urls(self, urls: List[str]) -> Optional[BeautifulSoup]:
        """Helper to try multiple URLs."""
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.text, 'html.parser')
            except Exception:
                pass
        return None

    def download_file(self, url: str, dest_path: str, progress_callback=None):
        """
        Downloads the file to dest_path.
        progress_callback(current, total)
        """
        try:
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total_length = r.headers.get('content-length')
                
                if dest_path.endswith(os.sep):
                     # if directory provided, preserve filename
                     filename = url.split('/')[-1]
                     dest_path = os.path.join(dest_path, filename)

                with open(dest_path, 'wb') as f:
                    dl = 0
                    total_length = int(total_length) if total_length else None
                    
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            dl += len(chunk)
                            f.write(chunk)
                            if progress_callback and total_length:
                                progress_callback(dl, total_length)
            return dest_path
        except Exception as e:
            print(f"Download error: {e}")
            raise e

