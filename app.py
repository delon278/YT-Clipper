import os
import json
import subprocess
import threading
import time
import re
from pathlib import Path
from flask import Flask, request, jsonify, send_file, send_from_directory
import yt_dlp

app = Flask(__name__, static_folder='static')

DOWNLOADS_DIR = Path("/tmp/YTClipper/downloads")
CLIPS_DIR = Path("/tmp/YTClipper/clips")
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

COOKIES_FILE = Path("/app/cookies.txt")

progress_store = {}


@app.route('/')
def index():
    return send_file('static/index.html')


@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'error': 'Query vacía'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'default_search': 'ytsearch10',
        **({"cookiefile": str(COOKIES_FILE)} if COOKIES_FILE.exists() else {}),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch10:{query}", download=False)
            results = []
            for entry in info.get('entries', []):
                if entry:
                    results.append({
                        'id': entry.get('id'),
                        'title': entry.get('title', 'Sin título'),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'thumbnail': entry.get('thumbnail', ''),
                        'duration': entry.get('duration', 0),
                        'uploader': entry.get('uploader', 'Desconocido'),
                        'view_count': entry.get('view_count', 0),
                    })
            return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL vacía'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        **({"cookiefile": str(COOKIES_FILE)} if COOKIES_FILE.exists() else {}),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'id': info.get('id'),
                'title': info.get('title'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', ''),
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url', '').strip()
    video_id = data.get('video_id', 'video')
    task_id = data.get('task_id', str(time.time()))

    if not url:
        return jsonify({'error': 'URL vacía'}), 400

    progress_store[task_id] = {'status': 'downloading', 'progress': 0, 'filename': None, 'error': None}

    def run_download():
        output_template = str(DOWNLOADS_DIR / f"{video_id}.%(ext)s")

        def progress_hook(d):
            if d['status'] == 'downloading':
                pct = d.get('_percent_str', '0%').replace('%', '').strip()
                try:
                    progress_store[task_id]['progress'] = float(pct)
                except:
                    pass
            elif d['status'] == 'finished':
                progress_store[task_id]['progress'] = 100
                progress_store[task_id]['filename'] = d.get('filename', '')

        ydl_opts = {
            'format': 'bestvideo+bestaudio/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
            'merge_output_format': 'mp4',
            **({"cookiefile": str(COOKIES_FILE)} if COOKIES_FILE.exists() else {}),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp4'):
                    filename = str(Path(filename).with_suffix('.mp4'))
                progress_store[task_id]['filename'] = filename
                progress_store[task_id]['status'] = 'done'
        except Exception as e:
            progress_store[task_id]['status'] = 'error'
            progress_store[task_id]['error'] = str(e)

    threading.Thread(target=run_download, daemon=True).start()
    return jsonify({'task_id': task_id})


@app.route('/api/progress/<task_id>')
def get_progress(task_id):
    return jsonify(progress_store.get(task_id, {'status': 'unknown'}))


@app.route('/api/clip', methods=['POST'])
def clip():
    data = request.json
    filename = data.get('filename', '')
    start = data.get('start', '0')
    end = data.get('end', '')
    clip_name = data.get('clip_name', f'clip_{int(time.time())}')

    if not filename or not os.path.exists(filename):
        video_id = data.get('video_id', '')
        candidates = list(DOWNLOADS_DIR.glob(f"{video_id}*.mp4"))
        if candidates:
            filename = str(candidates[0])
        else:
            return jsonify({'error': 'Archivo no encontrado'}), 404

    safe_name = re.sub(r'[^\w\-]', '_', clip_name)
    output_path = str(CLIPS_DIR / f"{safe_name}.mp4")

    cmd = ['ffmpeg', '-y', '-i', filename, '-ss', str(start)]
    if end:
        duration = float(end) - float(start)
        cmd += ['-t', str(duration)]
    cmd += ['-c:v', 'libx264', '-c:a', 'aac', '-preset', 'fast', output_path]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            return jsonify({'error': result.stderr[-500:]}), 500
        return jsonify({'output': output_path, 'filename': f"{safe_name}.mp4"})
    except FileNotFoundError:
        return jsonify({'error': 'ffmpeg no está instalado. Instálalo con: brew install ffmpeg (Mac) o sudo apt install ffmpeg (Linux)'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download-clip/<filename>')
def download_clip(filename):
    return send_from_directory(str(CLIPS_DIR), filename, as_attachment=True)


@app.route('/api/download-video/<video_id>')
def download_video(video_id):
    candidates = list(DOWNLOADS_DIR.glob(f"{video_id}*.mp4"))
    if not candidates:
        return jsonify({'error': 'Video no encontrado'}), 404
    return send_file(str(candidates[0]), as_attachment=True)


@app.route('/api/stream-video/<filename>')
def stream_video(filename):
    """Serve a downloaded video for in-browser playback with range support."""
    import mimetypes
    from flask import Response
    filepath = DOWNLOADS_DIR / filename
    if not filepath.exists():
        return jsonify({'error': 'Video no encontrado'}), 404

    file_size = filepath.stat().st_size
    range_header = request.headers.get('Range', None)

    if range_header:
        byte_start, byte_end = 0, None
        match = re.search(r'bytes=(\d+)-(\d*)', range_header)
        if match:
            byte_start = int(match.group(1))
            byte_end = int(match.group(2)) if match.group(2) else file_size - 1
        byte_end = min(byte_end, file_size - 1)
        length = byte_end - byte_start + 1

        def generate():
            with open(filepath, 'rb') as f:
                f.seek(byte_start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(65536, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        rv = Response(generate(), 206, mimetype='video/mp4', direct_passthrough=True)
        rv.headers['Content-Range'] = f'bytes {byte_start}-{byte_end}/{file_size}'
        rv.headers['Accept-Ranges'] = 'bytes'
        rv.headers['Content-Length'] = length
        return rv
    else:
        return send_file(str(filepath), mimetype='video/mp4')


@app.route('/api/files')
def list_files():
    downloads = [{'name': f.name, 'size': f.stat().st_size, 'type': 'download'} for f in DOWNLOADS_DIR.glob('*.mp4')]
    clips = [{'name': f.name, 'size': f.stat().st_size, 'type': 'clip'} for f in CLIPS_DIR.glob('*.mp4')]
    return jsonify({'downloads': downloads, 'clips': clips})


if __name__ == '__main__':
    print("\n🎬 YTClipper iniciado")
    print(f"📁 Descargas: {DOWNLOADS_DIR}")
    print(f"✂️  Clips: {CLIPS_DIR}")
    print("🌐 Abre tu navegador en: http://localhost:5050\n")
    app.run(host='0.0.0.0', port=5050, debug=False)
