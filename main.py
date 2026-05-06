import os
import time
import tempfile
import asyncio
import numpy as np
import librosa
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from services.fingerprinter import AudioFingerprinter
from services.db_manager import DBManager

app = FastAPI(title="Audio Identification API")

# Initialize our services
fingerprinter = AudioFingerprinter(sample_rate=11025)
db_manager = DBManager()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Custom latency tracking middleware.
    Measures the time it takes to process the request and adds it to the response headers.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Adding process time to headers
    response.headers["X-Process-Time"] = str(process_time)
    
    # You can also log the latency here if needed
    # print(f"Request: {request.method} {request.url.path} - Latency: {process_time:.4f}s")
    
    return response

@app.get("/health")
async def health_check():
    """
    Health check endpoint returning basic operational status.
    """
    # Mock database connection check
    db_status = "connected"
    
    return {
        "status": "operational",
        "database": db_status,
        "message": "Service is running."
    }

def process_audio_sync(tmp_path: str):
    """
    Synchronous blocking function to load audio and extract features.
    Designed to be run in a separate thread.
    """
    try:
        y, sr = librosa.load(tmp_path, sr=11025, mono=True)
    except Exception as e:
        raise ValueError(f"Invalid or unsupported audio format: {str(e)}")
        
    duration = librosa.get_duration(y=y, sr=sr)
    if duration < 1.0:
        raise ValueError("Audio snippet is too short. Minimum duration is 1 second.")
        
    if np.max(np.abs(y)) < 1e-4:
        raise ValueError("Audio snippet is completely silent.")
        
    features = fingerprinter.extract_features(y)
    return features.get("hashes", [])

@app.post("/api/v1/identify")
async def identify_audio(file: UploadFile = File(...)):
    """
    Endpoint to identify an uploaded audio snippet.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    # Read file asynchronously
    file_bytes = await file.read()
    
    # We use a temporary file because librosa relies on soundfile/audioread
    # which generally expect a file path for formats like MP3.
    _, ext = os.path.splitext(file.filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext or ".wav") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
        
    try:
        # Run heavy audio processing in a separate thread to keep the event loop fully asynchronous
        try:
            query_hashes = await asyncio.to_thread(process_audio_sync, tmp_path)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
            
        if not query_hashes:
            raise HTTPException(status_code=400, detail="Could not extract any features from the audio snippet.")
            
        # Perform Fuzzy Matching (Redis pipelined queries are very fast, but could also be threaded if needed)
        match_result = await asyncio.to_thread(db_manager.fuzzy_match, query_hashes)
        
        song_id = match_result.get("song_id")
        
        # Fetch metadata if a match was found
        metadata = {}
        if song_id:
            metadata = db_manager.redis_client.hgetall(f"song:{song_id}")
            
        return {
            "status": "success",
            "match": match_result,
            "metadata": metadata
        }
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
