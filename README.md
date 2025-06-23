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

## Example Usage

To download MP3s from a YouTube comment containing a tracklist, run:

```sh
python setlist_to_mp3.py "https://www.youtube.com/watch?v=E-6LmxvUiMk&lc=UgxwA4LZra3oRGeF0St4AaABAg" -d downloads
```

This will create a `downloads` directory in your project root and save the MP3s there.

### URL Explanation

- **Main URL:**
  - `https://www.youtube.com/watch?v=E-6LmxvUiMk`
  - This is the URL for the YouTube video itself.

- **Comment URL (Required by the Program):**
  - `https://www.youtube.com/watch?v=E-6LmxvUiMk&lc=UgxwA4LZra3oRGeF0St4AaABAg`
  - This URL points to a specific comment on the video, identified by the `lc` parameter.
    - `v=E-6LmxvUiMk` is the video ID.
    - `lc=UgxwA4LZra3oRGeF0St4AaABAg` is the comment ID.

**The program requires the comment URL** because it extracts the tracklist from a specific comment, not from the video description or other comments. The `lc` parameter is essential for identifying and fetching the correct comment. 