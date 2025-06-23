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
The script successfully downloaded 17 out of 21 songs listed in the comment.

---

## Soulseek Batch Downloader Script (`DJ2MP3_soulseek.py`)

This script automates downloading tracks from a YouTube comment tracklist using Soulseek via the `slsk-batchdl` tool (`sldl.exe`).

### Requirements

- Python packages: `youtube-comment-downloader`, `yt-dlp`
- Soulseek batch downloader: [`sldl.exe`](https://github.com/0x7d/soulseek-dl/releases)
- **.NET Runtime:** `sldl.exe` requires the [.NET 6.0 or later Desktop Runtime](https://dotnet.microsoft.com/en-us/download/dotnet/6.0) (Windows, x64/x86)

#### Install Python dependencies
```sh
pip install youtube-comment-downloader yt-dlp
```

#### Install .NET Desktop Runtime (Windows)
1. Go to the [.NET 6.0 Desktop Runtime download page](https://dotnet.microsoft.com/en-us/download/dotnet/6.0).
2. Download and install the "Desktop Runtime" for your system (x64/x86).
3. After installation, you should be able to run `dotnet --version` in a new terminal.

#### Download `sldl.exe`
1. Go to the [slsk-batchdl releases page](https://github.com/0x7d/soulseek-dl/releases).
2. Download the latest `sldl.exe` and place it in your project directory (same folder as the Python script).

### Usage

```sh
python DJ2MP3_soulseek.py "<YouTube comment URL>" -d <output_directory>
```

- The script will create a subfolder named after the YouTube video title inside your chosen output directory.
- On first run, you will be prompted for your Soulseek username and password (these are stored securely by `sldl.exe`).
- All tracks will be downloaded into the video-named folder.

#### Example
```sh
python DJ2MP3_soulseek.py "https://www.youtube.com/watch?v=E-6LmxvUiMk&lc=UgxwA4LZra3oRGeF0St4AaABAg" -d soulseek_downloads
```

---