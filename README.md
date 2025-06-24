# DJ2MP3: Automated Tracklist Downloaders (Soulseek & YouTube)

## Run Examples

### 1. Download from a Spotify Playlist via Soulseek
```sh
python DJ2MP3_spotify_via_soulseek.py "https://open.spotify.com/playlist/4bGw0ncQRTMX891DizZDkr" -d soulseek_downloads
```

### 2. Download from a YouTube Tracklist Comment via Soulseek
```sh
python DJ2MP3_youtube_via_soulseek.py "https://www.youtube.com/watch?v=E-6LmxvUiMk&lc=UgxwA4LZra3oRGeF0St4AaABAg" -d soulseek_downloads
```

### 3. Download MP3s from a YouTube Tracklist Comment (YouTube only)
```sh
python DJ2MP3_youtube.py "https://www.youtube.com/watch?v=E-6LmxvUiMk&lc=UgxwA4LZra3oRGeF0St4AaABAg" -d downloads
```

---

## Options Table

| Script                        | Output Dir Option | Format Option         | Bitrate Option | Min/Max Size Option | Duration Option | Workers Option | Notes |
|-------------------------------|-------------------|----------------------|---------------|---------------------|-----------------|---------------|-------|
| DJ2MP3_spotify_via_soulseek   | `-d, --directory` | `--pref-format`      | `--min-bitrate`| `--min-size`, `--max-size` | -               | -             | Needs Spotify credentials |
| DJ2MP3_youtube_via_soulseek   | `-d, --directory` | `--pref-format`      | `--min-bitrate`| `--min-size`, `--max-size` | -               | -             | -     |
| DJ2MP3_youtube                | `-d, --directory` | -                    | -             | -                   | `--min-duration`, `--max-duration` | `--workers`    | Needs ffmpeg |

---

## Installation Instructions

### macOS

- **Install .NET Runtime:**
  ```sh
  brew install --cask dotnet-sdk
  ```
  Or download from the [.NET 6.0 Desktop Runtime download page](https://dotnet.microsoft.com/en-us/download/dotnet/6.0).

- **Install Python dependencies:**
  ```sh
  pip install spotipy youtube-comment-downloader yt-dlp mutagen tqdm
  ```

- **Install ffmpeg:**
  ```sh
  brew install ffmpeg
  ```
  Or see the [official ffmpeg download page](https://ffmpeg.org/download.html#build-mac) for other options.
  - After installation, verify with:
    ```sh
    ffmpeg -version
    ```
  - If you get a "command not found" error, ensure `/usr/local/bin` or `/opt/homebrew/bin` is in your PATH.

- **Download `sldl`:**
  - Go to the [slsk-batchdl releases page](https://github.com/fiso64/slsk-batchdl/releases).
  - Download the latest release for macOS and make it executable:
    ```sh
    chmod +x sldl-macos-*
    mv sldl-macos-* sldl
    ```
  - **Move the `sldl` binary into your project directory (the same folder as your Python scripts).**
    This ensures the script can find and run `sldl` without needing to specify a path.

### Windows

- **Install .NET Desktop Runtime:**
  - Download and install from the [.NET 6.0 Desktop Runtime download page](https://dotnet.microsoft.com/en-us/download/dotnet/6.0).
  - After installation, run `dotnet --version` in a new terminal to verify.

- **Install Python dependencies:**
  ```sh
  pip install spotipy youtube-comment-downloader yt-dlp mutagen tqdm
  ```

- **Install ffmpeg:**
  1. Download the static build from the [official ffmpeg website](https://ffmpeg.org/download.html#build-windows).
  2. Unzip the archive to a folder, e.g. `C:\ffmpeg`.
  3. Add `C:\ffmpeg\bin` to your system PATH:
     - Open Windows Search and type "Environment Variables".
     - Click "Edit the system environment variables".
     - In the System Properties window, click "Environment Variables...".
     - Under "System variables", select `Path` and click "Edit".
     - Click "New" and add the path to your ffmpeg `bin` folder (e.g. `C:\ffmpeg\bin`).
     - Click OK to save and close all dialogs.
  4. Open a new Command Prompt or PowerShell and verify with:
     ```sh
     ffmpeg -version
     ```
  - If you get a "not recognized as an internal or external command" error, double-check your PATH.

- **Download `sldl.exe`:**
  - Go to the [slsk-batchdl releases page](https://github.com/fiso64/slsk-batchdl/releases).
  - Download the latest `sldl.exe` and place it in your project directory.

---

## Implementation Details

### 1. `DJ2MP3_spotify_via_soulseek.py`
- **Purpose:** Downloads tracks from a Spotify playlist using Soulseek.
- **Requirements:** `spotipy`, `sldl`, .NET Runtime, Spotify API credentials.
- **Setup:**
  - Register a free app at the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).
  - Save your credentials in `spotify_credentials.txt`:
    ```
    CLIENT_ID=your_client_id_here
    CLIENT_SECRET=your_client_secret_here
    ```
- **Note:** The Spotify playlist must be **public** for this script to work. Private playlists are not supported with the current authentication method.
- **How it works:**
  1. Fetches all tracks from the Spotify playlist.
  2. Writes the tracklist to `<playlist_name>/tracklist.txt`.
  3. Downloads all tracks into `<playlist_name>/` using Soulseek.
- **Options:**
  - `-d, --directory` (required)
  - `--pref-format` (default: mp3,flac,wav)
  - `--min-bitrate` (default: 256)
  - `--min-size` (default: 500K)
  - `--max-size` (default: 100M)
- **Notes:**
  - You do **not** need to set a Redirect URI for this script (Client Credentials flow is used).
  - Your Spotify credentials are **never** committed to git (see `.gitignore`).
  - The script requires the same Soulseek and .NET setup as the YouTube version.

### 2. `DJ2MP3_youtube_via_soulseek.py`
- **Purpose:** Downloads tracks from a YouTube comment tracklist using Soulseek.
- **Requirements:** `youtube-comment-downloader`, `yt-dlp`, `sldl`, .NET Runtime.
- **How it works:**
  1. Extracts tracklist from a YouTube comment.
  2. Writes the tracklist to `<mix_name>/tracklist.txt`.
  3. Downloads all tracks into `<mix_name>/` using Soulseek.
- **Options:**
  - `-d, --directory` (required)
  - `--pref-format` (default: mp3,flac,wav)
  - `--min-bitrate` (default: 256)
  - `--min-size` (default: 500K)
  - `--max-size` (default: 100M)

### 3. `DJ2MP3_youtube.py`
- **Purpose:** Downloads MP3s directly from YouTube using a tracklist comment.
- **Requirements:** `youtube-comment-downloader`, `yt-dlp`, `mutagen`, `tqdm`, `ffmpeg`.
- **How it works:**
  1. Extracts tracklist from a YouTube comment.
  2. Downloads and converts each track to MP3.
  3. Saves all tracks in the specified output directory.
- **Options:**
  - `-d, --directory` (required)
  - `--min-duration` (default: 150)
  - `--max-duration` (default: 630)
  - `--workers` (default: 4)

---

## sldl (Soulseek Batch Downloader) Documentation

- See the [slsk-batchdl releases page](https://github.com/fiso64/slsk-batchdl/releases) for the latest downloads and usage instructions.
- On first run, you will be prompted for your Soulseek username and password (these are stored securely by `sldl`).
- All tracks will be downloaded into the folder you specify with `-d` and the script will create a subfolder named after the playlist or mix.

---

## Troubleshooting
- If you get an authentication error, double-check your `spotify_credentials.txt`.
- If no tracks are found, make sure the playlist is public and the URL is correct.
- For Soulseek download issues, see the `sldl` documentation and ensure your credentials are correct.

### Soulseek Credentials

You must supply your Soulseek username and password in a file named `soulseek_credentials.txt` in the project directory. This file should contain:

```
SOULSEEK_USER=your_soulseek_username
SOULSEEK_PASS=your_soulseek_password
```

This file is automatically gitignored and will not be committed to your repository.

Both Soulseek scripts (`DJ2MP3_spotify_via_soulseek.py` and `DJ2MP3_youtube_via_soulseek.py`) will read your credentials from this file.