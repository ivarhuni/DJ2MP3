# Soulseek Batch Downloader Script (`DJ2MP3_spotify_via_soulseek.py`)

This script automates downloading tracks from a **Spotify playlist** using Soulseek via the `slsk-batchdl` tool ([sldl](https://github.com/fiso64/slsk-batchdl)).

---

## Requirements

- Python packages: `spotipy`
- Soulseek batch downloader: [`sldl`](https://github.com/fiso64/slsk-batchdl)
- **.NET Runtime:** `sldl` requires the .NET 6.0 or later Desktop Runtime (Windows/macOS)
- **Spotify API credentials:**
    - Register a free app at the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
    - Copy your Client ID and Client Secret into a file named `spotify_credentials.txt` in this directory:
      ```
      CLIENT_ID=your_client_id_here
      CLIENT_SECRET=your_client_secret_here
      ```

#### Install Python dependencies
```sh
pip install spotipy
```

---

## Usage

```sh
python DJ2MP3_spotify_via_soulseek.py <spotify_playlist_url> -d <output_directory>
```

- The script will create a subfolder named after the Spotify playlist inside your chosen output directory.
- All tracks will be downloaded into the playlist-named folder.
- Your Spotify credentials are read from `spotify_credentials.txt` (which is gitignored for safety).

#### Example
```sh
python DJ2MP3_spotify_via_soulseek.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" -d soulseek_downloads
```

---

## Options

- `-d, --directory`       Output directory (required)
- `--pref-format`         Preferred formats, comma-separated (default: mp3,flac,wav)
- `--min-bitrate`         Minimum bitrate (default: 256)
- `--min-size`            Minimum file size (default: 500K)
- `--max-size`            Maximum file size (default: 100M)

**These options work exactly the same as in `DJ2MP3_soulseek.py`.**

---

## How it works

1. Fetches all tracks from the given Spotify playlist (as "Artist Title").
2. Writes the tracklist to a file, one track per line, each in double quotes.
3. Calls `sldl.exe` to search and download each track from Soulseek, using your preferred format and bitrate settings.

---

## Notes
- You do **not** need to set a Redirect URI for this script (Client Credentials flow is used).
- Your Spotify credentials are **never** committed to git (see `.gitignore`).
- The script requires the same Soulseek and .NET setup as the YouTube version.

---

## Troubleshooting
- If you get an authentication error, double-check your `spotify_credentials.txt`.
- If no tracks are found, make sure the playlist is public and the URL is correct.
- For Soulseek download issues, see the `sldl` documentation and ensure your credentials are correct. 