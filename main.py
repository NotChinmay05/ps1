import os
import time
import tempfile
import librosa
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from services.db_manager import RedisManager
from services.fingerprinter import ConstellationExtractor, MatchingEngine

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

db = RedisManager()
extractor = ConstellationExtractor()
matcher = MatchingEngine(db)

@app.post("/api/v1/identify")
async def identify(file: UploadFile = File(...)):
    start_time = time.time()
    temp_path = None

    try:
        content = await file.read()
        base_filename = os.path.basename(file.filename) if file.filename else "audio.wav"
        _, ext = os.path.splitext(base_filename)        
        fd, temp_path = tempfile.mkstemp(
            prefix="temp_",
            suffix=ext if ext.lower() in ALLOWED_AUDIO_EXTENSIONS else ".wav",
            dir=tempfile.gettempdir()
        )
        
        with os.fdopen(fd, "wb") as f:
            f.write(content)

        clip_duration = librosa.get_duration(path=temp_path)
        features = extractor.extract_features(temp_path)
        result = matcher.find_match(features)

        latency = time.time() - start_time

        if result:
            return {
                "match": {
                    "songId": result.get("filename", "UNKNOWN"),
                    "title": result.get("filename", "Unknown Title"),
                    "artist": result.get("type", "Audio"),
                    "duration": f"{clip_duration:.2f}s"
                },
                "confidence": result.get("confidence", 0),
                "latency": latency * 1000, # Number for frontend
                "status": "matched"
            }

        return {
            "match": None,
            "latency": latency * 1000,
            "status": "unknown"
        }

    except Exception as e:
        print(f"Backend Error: {e}")
        return {"error": str(e)}

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/health")
async def health():
    try:
        db.client.ping()
        song_keys = db.client.keys("meta:*")
        return {
            "status": "healthy",
            "songsLoaded": len(song_keys),
            "indexReady": True
        }
    except Exception as e:
        return {"status": "offline", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
