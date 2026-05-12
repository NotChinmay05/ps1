import os
import time
import tempfile
import librosa
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ffmpeg_bin_path = os.path.join(os.getcwd(), "ffmpeg_bin")
if os.path.exists(ffmpeg_bin_path):
    os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = None
extractor = None
matcher = None

def get_services():
    """Load services only when needed to save startup memory."""
    global db, extractor, matcher
    if db is None:
        from services.db_manager import RedisManager
        from services.fingerprinter import ConstellationExtractor, MatchingEngine
        db = RedisManager()
        extractor = ConstellationExtractor()
        matcher = MatchingEngine(db)
    return db, extractor, matcher

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "audio-engine"}

@app.post("/api/v1/identify")
async def identify(file: UploadFile = File(...)):
    start_time = time.time()
    
    try:
        service_db, service_extractor, service_matcher = get_services()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service Init Failed: {str(e)}")

    suffix = os.path.splitext(file.filename)[1].lower() or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        features = service_extractor.extract_features(tmp_path)
        result = service_matcher.find_match(features)
        latency_ms = (time.time() - start_time) * 1000

        if result:
            return {
                "match": {
                    "songId": str(result.get("filename", "UNKNOWN")),
                    "title": str(result.get("filename", "Unknown Title")),
                    "artist": "Identified Song",
                    "duration": "N/A"
                },
                "confidence": result.get("confidence", 0),
                "latency": latency_ms,
                "status": "matched"
            }
        
        return {"match": None, "latency": latency_ms, "status": "unknown"}

    except Exception as e:
        print(f"CRASH: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
