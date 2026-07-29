import os
import sys
import uuid
import threading
import subprocess
import webbrowser

# Auto-install dependencies if missing on any machine automatically
required_packages = {
    'flask': 'flask',
    'yt_dlp': 'yt-dlp',
    'imageio_ffmpeg': 'imageio-ffmpeg'
}

for module_name, package_name in required_packages.items():
    try:
        __import__(module_name)
    except ImportError:
        print(f"[AUTO-SETUP] Package '{package_name}' not found. Installing automatically...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package_name}", "--pre"])
        except Exception as e:
            print(f"[WARNING] Could not auto-install {package_name}: {e}")

from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

# Dynamically resolve FFmpeg binary location across all platforms and users
ffmpeg_exe_path = None
ffmpeg_dir = None

try:
    import imageio_ffmpeg
    import shutil
    raw_exe = imageio_ffmpeg.get_ffmpeg_exe()
    if raw_exe and os.path.exists(raw_exe):
        ffmpeg_dir = os.path.dirname(raw_exe)
        target_name = "ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg"
        target_path = os.path.join(ffmpeg_dir, target_name)
        if not os.path.exists(target_path):
            try:
                shutil.copy2(raw_exe, target_path)
            except Exception:
                pass
        ffmpeg_exe_path = target_path if os.path.exists(target_path) else raw_exe
except Exception:
    pass

if not ffmpeg_dir:
    for p in [r"C:\ffmpeg-shared\bin", r"C:\ffmpeg\bin"]:
        if os.path.exists(p):
            ffmpeg_dir = p
            t_exe = os.path.join(p, "ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg")
            if os.path.exists(t_exe):
                ffmpeg_exe_path = t_exe
            break

if ffmpeg_dir and os.path.exists(ffmpeg_dir):
    if hasattr(os, 'add_dll_directory'):
        try:
            os.add_dll_directory(ffmpeg_dir)
        except Exception:
            pass
    os.environ["PATH"] = ffmpeg_dir + os.path.pathsep + os.environ.get("PATH", "")

app = Flask(__name__, static_folder=".")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Global dict to store download progress in real-time
DOWNLOAD_PROGRESS = {}

def get_clean_title(title):
    clean = "".join(c for c in title if c.isalnum() or c in "._- ").strip()
    return f"ZipLoot-{clean}"

def run_download_thread(task_id, url, format_option, title):
    DOWNLOAD_PROGRESS[task_id] = {
        "status": "downloading",
        "percent": "0%",
        "speed": "N/A",
        "eta": "N/A",
        "filename": None,
        "error": None
    }
    
    clean_title = get_clean_title(title)
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            
            if total_bytes:
                percent = int((downloaded / total_bytes) * 100)
                percent_str = f"{percent}%"
            else:
                percent_str = d.get('_percent_str', '0%').strip()
                
            DOWNLOAD_PROGRESS[task_id].update({
                "percent": percent_str,
                "speed": d.get('_speed_str', 'N/A').strip(),
                "eta": d.get('_eta_str', 'N/A').strip()
            })
        elif d['status'] == 'finished':
            DOWNLOAD_PROGRESS[task_id].update({
                "percent": "100%",
                "status": "processing"
            })

    # yt-dlp Options
    ydl_opts = {
        'progress_hooks': [progress_hook],
        'ffmpeg_location': ffmpeg_exe_path or ffmpeg_dir,
        'quiet': True,
        'no_warnings': True,
        'js_runtimes': {'node': {}},
        'noplaylist': True,
        'extractor_args': {'youtube': {'player_client': ['ios', 'web', 'default']}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }
    
    if format_option == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(OUTPUT_DIR, f"{clean_title}.%(ext)s"),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
        final_filename = f"{clean_title}.mp3"
    else:
        ydl_opts.update({
            'format': f"bestvideo[height<={format_option}]+bestaudio/best",
            'outtmpl': os.path.join(OUTPUT_DIR, f"{clean_title}.%(ext)s"),
            'merge_output_format': 'mp4',
        })
        final_filename = f"{clean_title}.mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        DOWNLOAD_PROGRESS[task_id].update({
            "status": "completed",
            "filename": final_filename
        })
    except Exception as e:
        DOWNLOAD_PROGRESS[task_id].update({
            "status": "failed",
            "error": str(e)
        })

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/downloads/<filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

@app.route("/api/info", methods=["POST"])
def get_info():
    data = request.json or {}
    url = data.get("url", "").strip()
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
        
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'js_runtimes': {'node': {}},
        'noplaylist': True,
        'extractor_args': {'youtube': {'player_client': ['ios', 'web', 'default']}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats_available = []
            if 'formats' in info:
                heights = set()
                for f in info['formats']:
                    h = f.get('height')
                    if h and h not in heights:
                        heights.add(h)
                formats_available = sorted(list(heights), reverse=True)

            return jsonify({
                "title": info.get("title", "YouTube Video"),
                "thumbnail": info.get("thumbnail", ""),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader") or info.get("channel") or "ZipLoot Channel",
                "author": info.get("uploader") or info.get("channel") or "ZipLoot Channel",
                "formats": formats_available,
                "resolutions": formats_available if formats_available else [1080, 720, 480, 360]
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.json or {}
    url = data.get("url", "").strip()
    format_option = data.get("format", "720").strip() # 1080, 720, 480, 360 or mp3
    title = data.get("title", "video").strip()
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
        
    task_id = str(uuid.uuid4())[:8]
    
    thread = threading.Thread(
        target=run_download_thread,
        args=(task_id, url, format_option, title)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "status": "success",
        "task_id": task_id
    })

@app.route("/api/progress/<task_id>", methods=["GET"])
def get_progress(task_id):
    progress = DOWNLOAD_PROGRESS.get(task_id)
    if not progress:
        return jsonify({"error": "Task not found"}), 404
        
    return jsonify(progress)

def open_browser():
    webbrowser.open("http://localhost:5000")

if __name__ == "__main__":
    print("=======================================================")
    print("   ZipLoot Dedicated YouTube Video & MP3 Downloader")
    print("   Running on: http://localhost:5000")
    print("=======================================================")
    threading.Timer(1.2, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
