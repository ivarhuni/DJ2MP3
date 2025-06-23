# Download MP3s from a YouTube Tracklist Comment

Download MP3s from a tracklist in a YouTube comment, with advanced filtering, max-duration exclusion, and concurrency.

## Project Purpose

This project automates the process of extracting and downloading individual tracks from DJ set videos as MP3 files. Most popular DJ sets on YouTube have a comment containing the full tracklist—simply provide the URL of that comment, and the script will attempt to locate and download each track as an MP3. While not flawless, the script achieves a high success rate and saves DJs and music enthusiasts significant manual effort.

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

## Example Usage

To download MP3s from a YouTube comment containing a tracklist, run:

```sh
python setlist_to_mp3.py "https://www.youtube.com/watch?v=E-6LmxvUiMk&lc=UgxwA4LZra3oRGeF0St4AaABAg" -d downloads
```

This will create a `downloads` directory in your project root and save the MP3s there.