import os
import sys
import argparse
import subprocess
import re
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

def sanitize_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)

def fetch_spotify_tracks(playlist_url, sp):
    playlist_id = playlist_url.split("playlist/")[-1].split("?")[0]
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    for item in results['items']:
        track = item['track']
        artist = track['artists'][0]['name'] if track['artists'] else ''
        title = track['name']
        if artist and title:
            tracks.append(f'{artist} {title}')
    return tracks

def read_spotify_credentials(path='spotify_credentials.txt'):
    creds = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                creds[k.strip()] = v.strip()
    return creds.get('CLIENT_ID'), creds.get('CLIENT_SECRET')

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

    # Spotify API setup
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

    # Fetch playlist tracks
    print(f"Fetching tracks from Spotify playlist: {args.playlist_url}")
    tracks = fetch_spotify_tracks(args.playlist_url, sp)
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
        '--user', 'kaztro',
        '--pass', 'dvergur',
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

if __name__ == '__main__':
    main() 