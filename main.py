import os
import time
import tempfile
import librosa
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "mode": "production"}

@app.post("/api/v1/identify")
async def identify(file: UploadFile = File(...)):
    start_time = time.time()
    
    from services.db_manager import RedisManager
    from services.fingerprinter import ConstellationExtractor, MatchingEngine

    ffmpeg_bin_path = os.path.join(os.getcwd(), "ffmpeg_bin")
    if os.path.exists(ffmpeg_bin_path):
        os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

    db = RedisManager()
    extractor = ConstellationExtractor()
    matcher = MatchingEngine(db)

    suffix = os.path.splitext(file.filename)[1].lower() or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        duration = librosa.get_duration(path=tmp_path)
        features = extractor.extract_features(tmp_path)
        result = matcher.find_match(features)
        
        latency_ms = (time.time() - start_time) * 1000

        if result:
            return {
                "match": {
                    "songId": str(result.get("filename", "UNKNOWN")),
                    "title": str(result.get("filename", "Found Match")),
                    "artist": str(result.get("type", "Audio")),
                    "duration": f"{result.get('full_duration', duration)}s",
                    "genre": str(result.get("type", "Audio"))
                },
                "confidence": float(result.get("confidence", 0)),
                "latency": latency_ms,
                "status": "matched"
            }
        
        return {"match": None, "latency": latency_ms, "status": "unknown"}

    except Exception as e:
        print(f"PROCESS ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
