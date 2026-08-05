# ZipLoot YouTube Video & MP3 Downloader Studio

A premium, lightweight, self-hosted web application to download YouTube videos in high-quality (up to 4K UHD) and extract high-fidelity MP3 audios with a single click.

## Features

- **High-Quality Video Downloads**: Supports all available YouTube resolutions (360p, 480p, 720p, 1080p, 1440p 2K, 2160p 4K).
- **HD Video Merging**: Automatically downloads and merges separate video & audio streams using local FFmpeg configuration.
- **High-Quality MP3 Extraction**: Extracts audio tracks and converts them directly to high-fidelity (192kbps) MP3 files.
- **Branding prefix**: Automatically prefixes downloaded filenames with `ZipLoot-`.
- **Ignore Playlists**: Prevents playlist spam downloads by default, downloading only the active video in the URL.
- **Real-Time Progress Tracking**: Live-polls download speed (MB/s), percent completed, and ETA without page refresh.
- **Premium Dark UI**: Built with a sleek HSL-custom glassmorphic theme, responsive layout, and beautiful hover animations.
- **1-Click Auto-Setup**: Includes virtual environment configurations and nightly-patched dependencies for immediate launch.

## 🚀 1-Click Launch Instructions

### Windows

1. Double-click the **`deploy_windows.bat`** file.
2. The setup script will automatically verify Python, create a virtual environment (`venv`), install dependencies, clear the cache, and start the local server.
3. Your browser will open **`http://localhost:5000`** automatically.

### Linux / macOS

1. Open your terminal in this directory.
2. Grant execution permissions to the setup script:
   ```bash
   chmod +x deploy_linux.sh
   ```
3. Run the script:
   ```bash
   ./deploy_linux.sh
   ```
4. The script will handle dependencies and launch the server. Open `http://localhost:5000` in your web browser.

## Requirements

- Python 3.8 or newer.
- Local FFmpeg installation (automatically resolved or configured during deployment).

---
Built with ⚡ by [ZipLoot](https://ziploot.vercel.app)

---

## 🌐 Discover More Free Tools on ZipLoot

Check out our full suite of automated web applications and developer tools at **[https://ziploot.app](https://ziploot.app)**:

- 🎥 **[Ad-Free Video Downloader](https://ziploot.app/addfree)** — Fast social video downloads with zero popups.
- 📄 **[Unlimited PDF Toolset](https://ziploot.app/pdf-toolset)** — Merge, split, compress, and edit PDFs in browser.
- 📹 **[YouTube Downloader](https://ziploot.app/youtube-downloader)** — Download high quality YouTube videos and audio for free.
- 🎨 **[Watermark Remover](https://ziploot.app/watermark-remover)** — Remove image watermarks automatically.
- 🌐 **[Image Translator](https://ziploot.app/image-translator)** — Translate text inside images online instantly.

---

*Maintained with ❤️ by the **[ZipLoot Team](https://ziploot.app)**.*
