# Soulseek Batch Downloader Script (`DJ2MP3_soulseek.py`)

This script automates downloading tracks from a YouTube comment tracklist using Soulseek via the `slsk-batchdl` tool ([sldl](https://github.com/fiso64/slsk-batchdl)).

### Requirements

- Python packages: `youtube-comment-downloader`, `yt-dlp`
- Soulseek batch downloader: [`sldl`](https://github.com/fiso64/slsk-batchdl)
- **.NET Runtime:** `sldl` requires the .NET 6.0 or later Desktop Runtime (Windows/macOS)

#### Install Python dependencies (all platforms)
```sh
pip install youtube-comment-downloader yt-dlp
```

### Platform-specific Installation

#### **Windows**
1. **Install .NET Desktop Runtime:**
    - Go to the [.NET 6.0 Desktop Runtime download page](https://dotnet.microsoft.com/en-us/download/dotnet/6.0).
    - Download and install the "Desktop Runtime" for your system (x64/x86).
    - After installation, you should be able to run `dotnet --version` in a new terminal.
2. **Download `sldl.exe`:**
    - Go to the [slsk-batchdl releases page](https://github.com/fiso64/slsk-batchdl/releases).
    - Download the latest `sldl.exe` and place it in your project directory (same folder as the Python script).

#### **macOS**
1. **Install .NET Runtime:**
    - The recommended way is via Homebrew:
      ```sh
      brew install --cask dotnet-sdk
      ```
    - Or download the installer from the [.NET 6.0 Desktop Runtime download page](https://dotnet.microsoft.com/en-us/download/dotnet/6.0).
    - After installation, you should be able to run `dotnet --version` in a new terminal.
2. **Download and install `sldl`:**
    - Go to the [slsk-batchdl releases page](https://github.com/fiso64/slsk-batchdl/releases).
    - Download the latest release for macOS. If a native `sldl` binary is available (e.g. `sldl-macos-x64` or `sldl-macos-arm64`), download it and make it executable:
      ```sh
      chmod +x sldl-macos-*
      mv sldl-macos-* sldl
      ```
    - If only a `.zip` or `.tar.gz` is provided, extract it and move the `sldl` binary to your project directory.
    - If there is no native macOS binary, download the `sldl.dll` file and run it using the .NET runtime:
      ```sh
      dotnet sldl.dll <args>
      ```
    - Place the `sldl` binary (or `sldl.dll`) in your project directory (same folder as the Python script).
    - You can test the installation by running:
      ```sh
      ./sldl --help
      # or, if using the DLL:
      dotnet sldl.dll --help
      ```

### Usage

```sh
python DJ2MP3_soulseek.py "<YouTube comment URL>" -d <output_directory>
```

- The script will create a subfolder named after the YouTube video title inside your chosen output directory.
- On first run, you will be prompted for your Soulseek username and password (these are stored securely by `sldl`).
- All tracks will be downloaded into the video-named folder.

#### Example
```sh
python DJ2MP3_soulseek.py "https://www.youtube.com/watch?v=E-6LmxvUiMk&lc=UgxwA4LZra3oRGeF0St4AaABAg" -d soulseek_downloads
```

---

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