import os
import sys
import argparse
import subprocess
import re
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import shutil

def sanitize_filename(name):
    # Replace all problematic characters (including slashes, backslashes, and whitespace at ends) with underscores
    return re.sub(r'[\\/:*?"<>|\s]+', '_', name).strip('_')

def fetch_spotify_tracks_with_dash_fallback(playlist_url, sp):
    playlist_id = playlist_url.split("playlist/")[-1].split("?")[0]
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    for item in results['items']:
        track = item['track']
        artist = track['artists'][0]['name'] if track['artists'] else ''
        title = track['name']
        if artist and title:
            search_entry = f'{artist} {title}'
            # Try original search
            found = sp.search(q=search_entry, type='track', limit=1)['tracks']['items']
            if found:
                tracks.append(search_entry)
            elif '-' in search_entry:
                fallback = search_entry.replace('-', '').replace('  ', ' ').strip()
                found_fallback = sp.search(q=fallback, type='track', limit=1)['tracks']['items']
                if found_fallback:
                    tracks.append(fallback)
    return tracks

def read_spotify_credentials(path='spotify_credentials.txt'):
    creds = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                creds[k.strip()] = v.strip()
    return creds.get('CLIENT_ID'), creds.get('CLIENT_SECRET')

def read_soulseek_credentials(path='soulseek_credentials.txt'):
    creds = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                creds[k.strip()] = v.strip()
    return creds.get('SOULSEEK_USER'), creds.get('SOULSEEK_PASS')

def write_tracklist_with_dash_fallback(tracks, path):
    """
    Write tracklist to file. If a track contains '-' and is not found, also try without the dash.
    """
    written = set()
    with open(path, 'w', encoding='utf-8') as f:
        for track in tracks:
            f.write(f'"{track}"\n')
            written.add(track)
            # If the track contains a dash, add a fallback without the dash (if not already present)
            if '-' in track:
                fallback = track.replace('-', '').replace('  ', ' ').strip()
                if fallback and fallback not in written:
                    f.write(f'"{fallback}"\n')
                    written.add(fallback)

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
    parser = argparse.ArgumentParser(description="Download tracks from a Spotify playlist using Soulseek via sldl.exe.")
    parser.add_argument('playlist_url', help="Spotify playlist URL")
    parser.add_argument('-d', '--directory', required=True, help='Output directory for downloads')
    parser.add_argument('--pref-format', type=str, default='mp3,flac,wav', help='Preferred formats, comma-separated (default: mp3,flac,wav)')
    parser.add_argument('--min-bitrate', type=int, default=256, help='Minimum bitrate (default: 256)')
    parser.add_argument('--min-size', type=str, default='500K', help='Minimum file size (default: 500K)')
    parser.add_argument('--max-size', type=str, default='100M', help='Maximum file size (default: 100M)')
    args = parser.parse_args()

    # Read Spotify credentials
    client_id, client_secret = read_spotify_credentials()
    if not client_id or not client_secret:
        sys.exit("Spotify credentials not found in spotify_credentials.txt")

    # Read Soulseek credentials
    soulseek_user, soulseek_pass = read_soulseek_credentials()
    if not soulseek_user or not soulseek_pass:
        sys.exit("Soulseek credentials not found in soulseek_credentials.txt")

    # Spotify API setup
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

    # Fetch playlist tracks
    print(f"Fetching tracks from Spotify playlist: {args.playlist_url}")
    tracks = fetch_spotify_tracks_with_dash_fallback(args.playlist_url, sp)
    print(f"Fetched {len(tracks)} tracks from playlist.")
    if not tracks:
        sys.exit("No tracks found in playlist.")

    # Use playlist name for folder
    playlist = sp.playlist(args.playlist_url.split("playlist/")[-1].split("?")[0])
    folder_name = sanitize_filename(playlist['name'])
    playlist_root = os.path.join(args.directory, folder_name)
    os.makedirs(playlist_root, exist_ok=True)
    tracklist_path = os.path.join(playlist_root, 'tracklist.txt')
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
        '-p', playlist_root
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
    flatten_directory(playlist_root)
    print(f"Flattened directory: {playlist_root}")

    # Check for not found tracks and write to not_found.txt
    downloaded_files = [f for f in os.listdir(playlist_root) if os.path.isfile(os.path.join(playlist_root, f))]
    downloaded_basenames = set(os.path.splitext(f)[0].lower() for f in downloaded_files)
    not_found = []
    for track in tracks:
        # Remove quotes and sanitize to match file naming
        base = sanitize_filename(track).lower()
        if base not in downloaded_basenames:
            not_found.append(track)
    not_found_path = os.path.join(playlist_root, 'not_found.txt')
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