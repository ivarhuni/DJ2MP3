import os
import sys
import argparse
import subprocess
import re
import requests
from bs4 import BeautifulSoup
import shutil
import time

def sanitize_filename(name):
    # Replace all problematic characters (including slashes, backslashes, and whitespace at ends) with underscores
    return re.sub(r'[\\/:*?"<>|\s]+', '_', name).strip('_')

def extract_tracklist_title(soup):
    """Extract the tracklist title from the page."""
    # Look for the main title - typically in h1 tag or title
    title_tag = soup.find('h1')
    if title_tag:
        return title_tag.get_text(strip=True)
    
    # Fallback to page title
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text(strip=True)
        # Remove " | 1001Tracklists" suffix if present
        if " | 1001Tracklists" in title:
            title = title.replace(" | 1001Tracklists", "")
        return title
    
    return "Unknown Tracklist"

def fetch_1001tracklists_tracks(url):
    """
    Scrape tracks from a 1001tracklists URL.
    Returns a list of "Artist Track" strings.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tracks = []
        
        # Extract tracklist title
        tracklist_title = extract_tracklist_title(soup)
        
        print(f"Page title: {tracklist_title}")
        
        # Method 1: Look for 1001tracklists track items specifically
        # Based on actual HTML structure analysis
        track_items = soup.find_all('div', class_='tlpItem')
        
        for item in track_items:
            # Look for the track value span
            track_value_span = item.find('span', class_='trackValue')
            if track_value_span:
                # Extract all text and clean it up
                track_text = track_value_span.get_text(strip=True)
                
                # Fix common spacing issues in 1001tracklists data
                track_text = re.sub(r'&', ' & ', track_text)  # Fix "&" to " & "
                track_text = re.sub(r'-', ' - ', track_text)  # Fix "-" to " - "
                track_text = re.sub(r'\s+', ' ', track_text)  # Fix multiple spaces
                track_text = track_text.strip()
                
                # Parse the track text to extract artist and title
                # Pattern: "Artist - Title" or "Artist & Artist - Title (Remix info)"
                if ' - ' in track_text:
                    # Remove common extra info that might interfere
                    clean_text = re.sub(r'\(.*?\)', '', track_text)  # Remove remix info in parentheses
                    clean_text = re.sub(r'\[.*?\]', '', clean_text)  # Remove label info in brackets
                    clean_text = clean_text.strip()
                    
                    parts = clean_text.split(' - ', 1)
                    if len(parts) == 2:
                        artist = parts[0].strip()
                        title = parts[1].strip()
                        
                        if len(artist) > 0 and len(title) > 0:
                            tracks.append(f'{artist} {title}')
        
        # Method 2: Look for divs and spans with track data
        if not tracks:
            # Look for common track listing patterns
            track_elements = soup.find_all(['div', 'span', 'p', 'li'])
            
            for elem in track_elements:
                text = elem.get_text(strip=True)
                # Look for "Artist - Title" pattern
                if ' - ' in text and 5 < len(text) < 200:
                    # Skip obviously non-track content
                    if any(skip in text.lower() for skip in [
                        'download', 'subscribe', 'comment', 'share', 'upload', 
                        'genre:', 'bpm:', 'key:', 'time:', 'length:', 'duration:',
                        'http', 'www', '.com', 'follow', 'like', 'playlist'
                    ]):
                        continue
                    
                    # Look for pattern that suggests it's a track
                    if re.match(r'^[^-]+ - [^-]+$', text):
                        parts = text.split(' - ', 1)
                        if len(parts) == 2:
                            artist, title = parts
                            artist = artist.strip()
                            title = title.strip()
                            
                            # Basic validation
                            if (len(artist) > 0 and len(title) > 0 and 
                                len(artist) < 100 and len(title) < 100 and
                                not artist.lower().startswith('http') and
                                not title.lower().startswith('http')):
                                tracks.append(f'{artist} {title}')
        
        # Method 3: Parse all text and look for track patterns
        if not tracks:
            all_text = soup.get_text()
            lines = all_text.split('\n')
            
            for line in lines:
                line = line.strip()
                # Look for lines that match track pattern
                if ' - ' in line and 5 < len(line) < 200:
                    # Skip non-track lines
                    if any(skip in line.lower() for skip in [
                        'download', 'subscribe', 'comment', 'share', 'upload',
                        'genre:', 'bpm:', 'key:', 'tracklist', 'playlist',
                        'http', 'www', '.com', 'follow', 'like', '1001'
                    ]):
                        continue
                    
                    # Check if it looks like a track (simple heuristic)
                    if re.match(r'^[\w\s&.,-]+ - [\w\s&.,-]+$', line):
                        parts = line.split(' - ', 1)
                        if len(parts) == 2:
                            artist, title = parts
                            artist = artist.strip()
                            title = title.strip()
                            
                            if (len(artist) > 0 and len(title) > 0 and 
                                len(artist) < 100 and len(title) < 100):
                                tracks.append(f'{artist} {title}')
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tracks = []
        for track in tracks:
            if track not in seen:
                seen.add(track)
                unique_tracks.append(track)
        
        print(f"Found {len(unique_tracks)} tracks")
        
        return unique_tracks, tracklist_title
        
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return [], "Unknown Tracklist"
    except Exception as e:
        print(f"Error parsing tracklist: {e}")
        return [], "Unknown Tracklist"

def read_soulseek_credentials(path='soulseek_credentials.txt'):
    creds = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                creds[k.strip()] = v.strip()
    return creds.get('SOULSEEK_USER'), creds.get('SOULSEEK_PASS')

def flatten_directory(root_dir):
    """Move all music files from subfolders up to root_dir and remove empty subfolders."""
    music_exts = {'.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma', '.alac', '.aiff', '.ape', '.opus', '.wv', '.tta', '.ac3', '.dts', '.amr', '.3gp', '.mid', '.midi', '.mod', '.xm', '.it', '.s3m', '.mp2', '.mp1', '.au', '.ra', '.ram', '.m4b', '.m4p', '.mpga', '.spx', '.oga', '.caf', '.dsf', '.dff', '.tak', '.shn', '.aif', '.aifc', '.snd', '.kar'}
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in music_exts:
                src = os.path.join(dirpath, filename)
                dst = os.path.join(root_dir, filename)
                if src != dst:
                    # Avoid overwriting files with the same name
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dst):
                        dst = os.path.join(root_dir, f"{base}_{counter}{ext}")
                        counter += 1
                    shutil.move(src, dst)
        # Remove empty subfolders
        if dirpath != root_dir and not os.listdir(dirpath):
            os.rmdir(dirpath)

def main():
    parser = argparse.ArgumentParser(description="Download tracks from a 1001tracklists URL using Soulseek via sldl.exe.")
    parser.add_argument('tracklist_url', help="1001tracklists URL")
    parser.add_argument('-d', '--directory', required=True, help='Output directory for downloads')
    parser.add_argument('--pref-format', type=str, default='mp3,flac,wav', help='Preferred formats, comma-separated (default: mp3,flac,wav)')
    parser.add_argument('--min-bitrate', type=int, default=256, help='Minimum bitrate (default: 256)')
    parser.add_argument('--min-size', type=str, default='500K', help='Minimum file size (default: 500K)')
    parser.add_argument('--max-size', type=str, default='100M', help='Maximum file size (default: 100M)')
    args = parser.parse_args()

    # Read Soulseek credentials
    soulseek_user, soulseek_pass = read_soulseek_credentials()
    if not soulseek_user or not soulseek_pass:
        sys.exit("Soulseek credentials not found in soulseek_credentials.txt")

    # Fetch tracklist
    print(f"Fetching tracks from 1001tracklists URL: {args.tracklist_url}")
    tracks, tracklist_title = fetch_1001tracklists_tracks(args.tracklist_url)
    
    if not tracks:
        sys.exit("No tracks found in tracklist. Please check the URL or try a different tracklist.")
    
    print(f"Found {len(tracks)} tracks from: {tracklist_title}")
    for i, track in enumerate(tracks[:10]):  # Show first 10 tracks
        print(f"  {i+1}. {track}")
    if len(tracks) > 10:
        print(f"  ... and {len(tracks) - 10} more tracks")

    # Use tracklist title for folder name
    folder_name = sanitize_filename(tracklist_title)
    tracklist_root = os.path.join(args.directory, folder_name)
    os.makedirs(tracklist_root, exist_ok=True)
    
    # Write tracklist to file
    tracklist_path = os.path.join(tracklist_root, 'tracklist.txt')
    with open(tracklist_path, 'w', encoding='utf-8') as f:
        for track in tracks:
            f.write(f'"{track}"\n')
    print(f"Tracklist written to {tracklist_path}")

    # Build sldl.exe command
    sldl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sldl.exe')
    cmd = [
        sldl_path, tracklist_path,
        '--user', soulseek_user,
        '--pass', soulseek_pass,
        '--pref-format', args.pref_format,
        '--min-bitrate', str(args.min_bitrate),
        '--input-type', 'list',
        '-p', tracklist_root
    ]
    print(f"Running: {' '.join(cmd)}")

    # Run sldl.exe and report progress
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print("\n--- slsk-batchdl output ---")
    for line in proc.stdout:
        print(line, end="")
    proc.wait()
    print("--- slsk-batchdl finished ---\n")

    # Post-process: flatten directory
    flatten_directory(tracklist_root)
    print(f"Flattened directory: {tracklist_root}")

    # Check for not found tracks and write to not_found.txt
    downloaded_files = [f for f in os.listdir(tracklist_root) if os.path.isfile(os.path.join(tracklist_root, f))]
    downloaded_basenames = set(os.path.splitext(f)[0].lower() for f in downloaded_files)
    not_found = []
    for track in tracks:
        # Remove quotes and sanitize to match file naming
        base = sanitize_filename(track).lower()
        if base not in downloaded_basenames:
            not_found.append(track)
    
    not_found_path = os.path.join(tracklist_root, 'not_found.txt')
    with open(not_found_path, 'w', encoding='utf-8') as nf:
        for track in not_found:
            nf.write(track + '\n')
    
    if not_found:
        print(f"\nTracks not found (also written to {not_found_path}):")
        for track in not_found:
            print(f"  - {track}")
    else:
        print("\nAll tracks were found and downloaded.")

if __name__ == '__main__':
    main() 