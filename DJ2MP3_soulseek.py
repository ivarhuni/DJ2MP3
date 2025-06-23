import re
import os
import sys
import argparse
import datetime
from urllib.parse import urlparse, parse_qs
import subprocess
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
import yt_dlp

# --- Tracklist Sanitization ---
def sanitize_tracklist(lines):
    """
    Clean and filter raw comment lines into 'Artist Title' format (no dash, just a space).
    Print why a line is skipped for debugging.
    """
    cleaned, seen = [], set()
    for line in lines:
        orig_line = line
        line = line.strip()
        if not line:
            print(f"[SKIP] Empty line: '{orig_line}'")
            continue
        # Remove timestamps, numbering, bullets, dashes, noise
        line = re.sub(r"\[?\(?\d{1,2}:\d{2}(?::\d{2})?\)?\]?", "", line)
        line = re.sub(r"^\s*\d+[\.)]?\s*", "", line)
        line = re.sub(r"^[\-\*\•]", "", line)  # Remove leading -, *, •
        line = re.sub(r"[–—―]", "-", line)
        line = re.sub(r"\[.*?\]|\(.*?\)", "", line)
        line = re.sub(r"\s{2,}", " ", line).strip()
        if '-' not in line:
            print(f"[SKIP] No dash: '{orig_line}' -> '{line}'")
            continue
        artist, title = [p.strip() for p in line.split('-', 1)]
        if len(artist) < 2 or len(title) < 2:
            print(f"[SKIP] Artist or title too short: '{orig_line}' -> '{artist}' | '{title}'")
            continue
        if not re.search(r"[A-Za-z]", artist) or not re.search(r"[A-Za-z]", title):
            print(f"[SKIP] No letters in artist or title: '{orig_line}' -> '{artist}' | '{title}'")
            continue
        key = f"{artist.lower()} {title.lower()}"
        if key in seen:
            print(f"[SKIP] Duplicate: '{orig_line}' -> '{artist} {title}'")
            continue
        seen.add(key)
        cleaned.append(f"{artist} {title}")
    return cleaned

def sanitize_filename(name):
    # Remove or replace characters not allowed in Windows folder names
    return re.sub(r'[\\/:*?"<>|]', '_', name)

# Note: Login is now handled by slsk-batchdl (sldl.exe) itself. On first run, it will prompt for Soulseek credentials and store them securely for future use.

def main():
    parser = argparse.ArgumentParser(description="Download tracks from Soulseek using slsk-batchdl based on a YouTube comment tracklist.")
    parser.add_argument('comment_url', help="YouTube comment URL (with v and lc parameters)")
    parser.add_argument('-d', '--directory', required=True, help='Output directory for downloads')
    parser.add_argument('--pref-format', type=str, default='flac,mp3,wav', help='Preferred formats, comma-separated (default: flac,mp3,wav)')
    parser.add_argument('--min-bitrate', type=int, default=256, help='Minimum bitrate (default: 256)')
    parser.add_argument('--min-size', type=str, default='500K', help='Minimum file size (default: 500K)')
    parser.add_argument('--max-size', type=str, default='100M', help='Maximum file size (default: 100M)')
    args = parser.parse_args()

    # Parse comment URL
    parsed = urlparse(args.comment_url)
    params = parse_qs(parsed.query)
    vid = params.get('v', [None])[0]
    cid = params.get('lc', [None])[0]
    if not vid or not cid:
        sys.exit("Invalid URL: must include v and lc parameters.")

    # Fetch comment text
    print(f"Fetching comment for video {vid}, comment {cid}...")
    downloader = YoutubeCommentDownloader()
    comment_text = None
    for c in downloader.get_comments_from_url(f"https://www.youtube.com/watch?v={vid}", SORT_BY_POPULAR):
        if c.get('cid') == cid:
            comment_text = c.get('text')
            break
    if not comment_text:
        sys.exit("Comment not found.")

    # Parse tracklist
    tracks = sanitize_tracklist(comment_text.splitlines())
    print(f"Parsed {len(tracks)} tracks from comment.")
    if not tracks:
        sys.exit("No valid 'Artist Title' entries found.")

    # Fetch YouTube video title for folder naming
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
        video_title = info.get('title', f'video_{vid}')
    folder_name = sanitize_filename(video_title)
    output_dir = os.path.join(args.directory, folder_name)
    os.makedirs(output_dir, exist_ok=True)
    tracklist_path = os.path.join(output_dir, 'tracklist.txt')
    with open(tracklist_path, 'w', encoding='utf-8') as f:
        for track in tracks:
            f.write(f'"{track}"\n')
    print(f"Tracklist written to {tracklist_path}")

    # Build sldl.exe command (only use supported arguments)
    sldl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sldl.exe')
    cmd = [
        sldl_path, tracklist_path,
        '--user', 'kaztro',
        '--pass', 'dvergur',
        '--pref-format', args.pref_format,
        '--min-bitrate', str(args.min_bitrate),
        '--input-type', 'list',
        '-p', output_dir
    ]
    print(f"Running: {' '.join(cmd)}")

    # Run sldl.exe and report progress
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print("\n--- slsk-batchdl output ---")
    status_dict = {track: {'status': 'Pending', 'details': ''} for track in tracks}
    for line in proc.stdout:
        print(line, end="")
        # Parse for status updates
        m = re.search(r"Downloaded: (.+)", line)
        if m:
            track = m.group(1).strip()
            status_dict[track] = {'status': 'Downloaded', 'details': ''}
        m = re.search(r"Failed: (.+)", line)
        if m:
            track = m.group(1).strip()
            status_dict[track] = {'status': 'Failed', 'details': ''}
        m = re.search(r"Waiting: (.+)", line)
        if m:
            track = m.group(1).strip()
            status_dict[track] = {'status': 'Waiting', 'details': ''}
    proc.wait()
    print("--- slsk-batchdl finished ---\n")

if __name__ == '__main__':
    main()
