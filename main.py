import os
import time
import librosa
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from services.db_manager import RedisManager
from services.fingerprinter import ConstellationExtractor, MatchingEngine

app = FastAPI()

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
    filename = os.path.basename(file.filename)
    temp_path = os.path.join(os.getcwd(), f"temp_{filename}")

    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        clip_duration = librosa.get_duration(path=temp_path)
        features = extractor.extract_features(temp_path)
        result = matcher.find_match(features)
        
        latency = time.time() - start_time

        if result:
            return {
                "match": True,
                "confidence": result["confidence"],
                "latency": f"{latency*1000:.2f}",
                "duration": f"{clip_duration:.2f}s",
                "type": result["type"],
                "filename": result["filename"]
            }

        return {
            "match": False,
            "latency": f"{latency:.4f}s",
            "duration": f"{clip_duration:.2f}s"
        }
    
    except Exception as e:
        return {"error": str(e)}
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/health")
async def health():
    try:
        db.client.ping()
        song_keys = db.client.keys("meta:*")
        song_count = len(song_keys)
        
        return {
            "status": "online", 
            "songs_indexed": song_count,
            "environment": "production" if os.getenv("REDIS_URL") else "development"
        }
    except Exception as e:
        return {"status": "offline", "error": str(e)}
