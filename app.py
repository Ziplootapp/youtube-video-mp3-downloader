import os
import sys
import uuid
import threading
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

# Dynamically resolve FFmpeg binary location across all platforms and users
ffmpeg_dir = None
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    if ffmpeg_exe and os.path.exists(ffmpeg_exe):
        ffmpeg_dir = os.path.dirname(ffmpeg_exe)
except Exception:
    pass

if not ffmpeg_dir:
    for p in [r"C:\ffmpeg-shared\bin", r"C:\ffmpeg\bin"]:
        if os.path.exists(p):
            ffmpeg_dir = p
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
                
            speed_str = d.get('_speed_str', 'N/A').strip()
            eta_str = d.get('_eta_str', 'N/A').strip()
            
            DOWNLOAD_PROGRESS[task_id].update({
                "percent": percent_str,
                "speed": speed_str,
                "eta": eta_str
            })
            
        elif d['status'] == 'finished':
            DOWNLOAD_PROGRESS[task_id].update({
                "percent": "100%",
                "status": "processing"
            })

    # yt-dlp configurations
    ydl_opts = {
        'progress_hooks': [progress_hook],
        'ffmpeg_location': local_ffmpeg if os.path.exists(local_ffmpeg) else None,
        'quiet': True,
        'no_warnings': True,
        'js_runtimes': {'node': {}},
        'noplaylist': True,
        'extractor_args': {'youtube': {'player_client': ['ios', 'web', 'default']}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }
    
    if format_option == 'mp3':
        # Download best audio and extract to MP3
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
        # Download best video (height match) + best audio, merge to MP4
        # format_option can be 1080, 720, 480, 360
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
            "percent": "100%",
            "filename": final_filename
        })
    except Exception as e:
        print(f"Download thread error: {e}")
        DOWNLOAD_PROGRESS[task_id].update({
            "status": "failed",
            "error": str(e)
        })

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/downloads/<path:filename>")
def serve_download(filename):
    return send_from_directory(OUTPUT_DIR, filename)

@app.route("/favicon.svg")
def serve_favicon():
    return send_from_directory(".", "favicon.svg")

@app.route("/api/info", methods=["POST"])
def get_video_info():
    data = request.json or {}
    url = data.get("url", "").strip()
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
        
    ydl_opts = {
        'extract_flat': False,
        'skip_download': True,
        'js_runtimes': {'node': {}},
        'noplaylist': True,
        'extractor_args': {'youtube': {'player_client': ['ios', 'web', 'default']}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract available resolutions
            formats = info.get("formats", [])
            heights = set()
            for f in formats:
                h = f.get("height")
                if h and h in [360, 480, 720, 1080, 1440, 2160]:
                    heights.add(h)
            
            resolutions = sorted(list(heights), reverse=True)
            
            return jsonify({
                "status": "success",
                "title": info.get("title", "YouTube Video"),
                "thumbnail": info.get("thumbnail") or info.get("thumbnails", [{}])[-1].get("url"),
                "duration": info.get("duration", 0),
                "author": info.get("uploader", "Unknown Uploader"),
                "resolutions": resolutions
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
    
    # Start background download thread
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

if __name__ == "__main__":
    print("=======================================================")
    print("   ZipLoot Dedicated YouTube Video & MP3 Downloader")
    print("   Running on: http://localhost:5000")
    print("=======================================================")
    app.run(host="0.0.0.0", port=5000, debug=False)
