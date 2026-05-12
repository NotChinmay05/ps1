import os
import time
import tempfile
import shutil
import librosa
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.db_manager import RedisManager
from services.fingerprinter import ConstellationExtractor, MatchingEngine

ffmpeg_bin_path = os.path.join(os.getcwd(), "ffmpeg_bin")
if os.path.exists(ffmpeg_bin_path):
    os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

app = FastAPI(title="Audio Identification API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db = RedisManager()
extractor = ConstellationExtractor()
matcher = MatchingEngine(db)

@app.get("/health")
async def health():
    try:
        redis_ready = db.client.ping() if db.client else False
        song_keys = db.client.keys("meta:*") if redis_ready else []
        
        return {
            "status": "healthy",
            "songsLoaded": len(song_keys),
            "indexReady": redis_ready,
            "ffmpeg": "found" if shutil.which("ffmpeg") else "not_found"
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}

@app.post("/api/v1/identify")
async def identify(file: UploadFile = File(...)):
    start_time = time.time()
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    _, ext = os.path.splitext(file.filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext.lower()) as tmp:
        try:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File write error: {str(e)}")

    try:
        clip_duration = librosa.get_duration(path=tmp_path)
        features = extractor.extract_features(tmp_path)
        result = matcher.find_match(features)
        latency_ms = (time.time() - start_time) * 1000

        if result:
            return {
                "match": {
                    "songId": str(result.get("filename", "UNKNOWN")),
                    "title": str(result.get("filename", "Unknown Title")),
                    "artist": str(result.get("type", "Audio")),
                    "duration": f"{clip_duration:.2f}s"
                },
                "confidence": result.get("confidence", 0),
                "latency": latency_ms,
                "status": "matched"
            }
        
        return {
            "match": None,
            "latency": latency_ms,
            "status": "unknown"
        }

    except Exception as e:
        print(f"IDENTIFY ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
