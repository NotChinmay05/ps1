import os
import time
import tempfile
import librosa
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from services.db_manager import RedisManager
from services.fingerprinter import ConstellationExtractor, MatchingEngine

# --- 1. Environment & Path Setup ---
# This ensures FFmpeg (downloaded via build.sh) is accessible to librosa
ffmpeg_bin_path = os.path.join(os.getcwd(), "ffmpeg_bin")
if os.path.exists(ffmpeg_bin_path):
    os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

app = FastAPI()
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".webm", ".mp4"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
db = RedisManager()
extractor = ConstellationExtractor()
matcher = MatchingEngine(db)

@app.post("/api/v1/identify")
async def identify(file: UploadFile = File(...)):
    start_time = time.time()
    temp_path = None

    try:
        content = await file.read()
        base_filename = os.path.basename(file.filename) if file.filename else "upload"
        _, original_extension = os.path.splitext(base_filename)        
        fd, temp_path = tempfile.mkstemp(
            prefix="identify_",
            suffix=original_extension.lower() if original_extension.lower() in ALLOWED_AUDIO_EXTENSIONS else ".wav",
            dir=tempfile.gettempdir()
        )

        with os.fdopen(fd, "wb") as f:
            f.write(content)

        clip_duration = librosa.get_duration(path=temp_path)
        features = extractor.extract_features(temp_path)
        result = matcher.find_match(features)
        latency_ms = (time.time() - start_time) * 1000

        if result:
            return {
                "match": {
                    "filename": result.get("filename", "Unknown"),
                    "type": result.get("type", "Audio"),
                    "duration_sec": f"{clip_duration:.2f}"
                },
                "confidence": result.get("confidence", 0),
                "latency": latency_ms,
                "status": "success"
            }

        return {
            "match": None,
            "latency": latency_ms,
            "status": "no_match",
            "duration": f"{clip_duration:.2f}s"
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"error": str(e), "status": "failed"}

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

@app.get("/health")
async def health():
    try:
        db.client.ping()
        song_keys = db.client.keys("meta:*")
        
        return {
            "status": "healthy",
            "songs_loaded": len(song_keys),
            "ffmpeg": "found" if shutil.which("ffmpeg") else "not_found",
            "environment": "production" if os.getenv("REDIS_URL") else "development"
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}
