# Download MP3s from a YouTube Tracklist Comment

Download MP3s from a tracklist in a YouTube comment, with advanced filtering, max-duration exclusion, and concurrency.

## Usage

**macOS/Linux:**
```sh
python3 script.py "<YouTube comment URL>" -d <output_directory> [options]
```

**Windows PowerShell:**
```sh
python script.py "<YouTube comment URL>" -d <output_directory> [options]
```

## Dependencies

- `youtube-comment-downloader`
- `yt-dlp`
- `mutagen`
- `tqdm`

Install with:
```sh
pip install youtube-comment-downloader yt-dlp mutagen tqdm
```

## ffmpeg (required)

Ensure ffmpeg is installed and in your system PATH:

- **macOS:**  
  `brew install ffmpeg`
- **Windows:**
    1. Download the static build from [ffmpeg.org](https://ffmpeg.org/download.html)
    2. Unzip to a folder, e.g. `C:\ffmpeg`
    3. In Windows Search, type "Environment Variables" → Edit system environment variables → Environment Variables.
    4. Under "System variables", select `Path`, click Edit → New, then add `C:\ffmpeg\bin` (or your chosen folder).
    5. Click OK to save; open a new PowerShell/Command Prompt to verify with `ffmpeg -version`.

## Options

- `-d, --directory`       Output directory (required)
- `--min-duration`        Minimum video duration in seconds (default: 150)
- `--max-duration`        Maximum video duration in seconds (default: 630)
- `--workers`             Number of concurrent downloads (default: 4) 