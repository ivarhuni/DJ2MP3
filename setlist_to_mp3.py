#!/usr/bin/env python3
import re
import os
import sys
import argparse
import threading
import datetime
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
import yt_dlp

# Optional for ID3 tagging
try:
    from mutagen.easyid3 import EasyID3
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
    HAVE_MUTAGEN = True
except ImportError:
    HAVE_MUTAGEN = False

# Optional progress bar
try:
    from tqdm import tqdm
    HAVE_TQDM = True
except ImportError:
    HAVE_TQDM = False

# Blacklist terms in video titles
BLACKLIST_TERMS = ('live', 'dj set')

# Thread-safe structures
log_lock = threading.Lock()
summary = {'success': [], 'skipped': []}


def sanitize_tracklist(lines):
    """
    Clean and filter raw comment lines into 'Artist - Title' format.
    """
    cleaned, seen = [], set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Remove timestamps, numbering, bullets, dashes, noise
        line = re.sub(r"\[?\(?\d{1,2}:\d{2}(?::\d{2})?\)?\]?", "", line)
        line = re.sub(r"^\s*\d+[\.)]?\s*", "", line)
        line = re.sub(r"^[\-\*\•]\s*", "", line)
        line = re.sub(r"[–—―]", "-", line)
        line = re.sub(r"\[.*?\]|\(.*?\)", "", line)
        line = re.sub(r"\s{2,}", " ", line).strip()
        if ' - ' not in line:
            continue
        artist, title = [p.strip() for p in line.split(' - ', 1)]
        if len(artist) < 2 or len(title) < 2:
            continue
        if not re.search(r"[A-Za-z]", artist) or not re.search(r"[A-Za-z]", title):
            continue
        if any(w in title.lower() for w in ('intro','outro','mixout','timestamp','setlist')):
            continue
        key = f"{artist.lower()} - {title.lower()}"
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(f"{artist} - {title}")
    return cleaned


def process_track(index, track, args, ydl_opts, out_dir, log_path, total):
    """
    Handle a single track: search, filter, download, tag, and log.
    """
    # Search
    try:
        with yt_dlp.YoutubeDL({**ydl_opts, 'quiet': True}) as ydl:
            info = ydl.extract_info(f"ytsearch5:{track}", download=False)
    except Exception as e:
        reason = f"search error: {e}"
        with log_lock:
            summary['skipped'].append((track, reason))
        return
    entries = info.get('entries', [])
    filtered = []
    chosen = None
    for vid in entries:
        title = (vid.get('title') or '').lower()
        dur = vid.get('duration', 0)
        url = vid.get('webpage_url') or f"https://www.youtube.com/watch?v={vid.get('id')}"
        if dur < args.min_duration:
            filtered.append((url, 'too short'))
            continue
        if dur > args.max_duration:
            filtered.append((url, 'too long'))
            continue
        if any(term in title for term in BLACKLIST_TERMS):
            filtered.append((url, 'blacklisted'))
            continue
        chosen = vid
        break
    if not chosen:
        with log_lock:
            summary['skipped'].append((track, 'no valid match'))
            with open(log_path, 'a', encoding='utf-8') as log:
                log.write(f"\n[SKIPPED] {track}\n")
                for u, r in filtered:
                    log.write(f"  - {u} ({r})\n")
        return
    dl_url = chosen.get('webpage_url')
    safe = re.sub(r'[\\/*?:"<>|]', '_', track)
    out_template = os.path.join(out_dir, f"{index:02d} - {safe}.%(ext)s")
    # Download and convert
    try:
        with yt_dlp.YoutubeDL({**ydl_opts, 'outtmpl': out_template, 'quiet': False}) as ydl:
            ydl.download([dl_url])
    except Exception as e:
        with log_lock:
            summary['skipped'].append((track, f"download error: {e}"))
            with open(log_path, 'a', encoding='utf-8') as log:
                log.write(f"\n[FAILED] {track} - download error: {e}\n")
        return
    with log_lock:
        summary['success'].append((track, dl_url))
        with open(log_path, 'a', encoding='utf-8') as log:
            log.write(f"[SUCCESS] {track} -> {dl_url}\n")
    # Tag metadata
    if HAVE_MUTAGEN:
        mp3_path = os.path.join(out_dir, f"{index:02d} - {safe}.mp3")
        if os.path.isfile(mp3_path):
            try:
                artist, title = track.split(' - ', 1)
                tags = EasyID3(mp3_path)
                tags['artist'] = artist.strip()
                tags['title'] = title.strip()
                tags.save()
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser(description="Download MP3s from a YouTube comment tracklist.")
    parser.add_argument('comment_url', help="YouTube comment URL (with v and lc parameters)")
    parser.add_argument('-d', '--directory', required=True, help='Output directory')
    parser.add_argument('--min-duration', type=int, default=150, help='Minimum duration (s)')
    parser.add_argument('--max-duration', type=int, default=630, help='Maximum duration (s)')
    parser.add_argument('--workers', type=int, default=4, help='Concurrent downloads')
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
        sys.exit("No valid 'Artist - Title' entries found.")

    # Prepare output and log
    os.makedirs(args.directory, exist_ok=True)
    log_path = os.path.join(args.directory, 'download_log.txt')
    # Initialize log file
    with open(log_path, 'w', encoding='utf-8') as log:
        log.write("=== Download Log ===\n")
        log.write(f"Date: {datetime.datetime.now().isoformat()}\n")
        log.write(f"Source Comment: {args.comment_url}\n\n")

    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0'
        }]
    }

    # Concurrency
    print(f"Starting processing with {args.workers} workers...")
    executor = ThreadPoolExecutor(max_workers=args.workers)
    futures = []
    total = len(tracks)
    for idx, tr in enumerate(tracks, start=1):
        futures.append(executor.submit(process_track, idx, tr, args, ydl_opts, args.directory, log_path, total))

    # Progress indicator
    if HAVE_TQDM:
        for _ in tqdm(as_completed(futures), total=total, desc='Tracks'): pass
    else:
        for _ in as_completed(futures): pass

    executor.shutdown(wait=True)

    # Summary
    print(f"\nDone. {len(summary['success'])} succeeded, {len(summary['skipped'])} skipped.")
    if summary['skipped']:
        print("See download_log.txt for details on skipped tracks.")

if __name__ == '__main__':
    main()
```
