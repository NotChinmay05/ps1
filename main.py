import os
import sys
import tempfile
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ffmpeg_bin_path = os.path.join(os.getcwd(), "ffmpeg_bin")
if os.path.exists(ffmpeg_bin_path):
    os.environ["PATH"] += os.pathsep + ffmpeg_bin_path
    print(f"DEBUG: Added {ffmpeg_bin_path} to PATH")
    
try:
    from services.db_manager import RedisManager
except ImportError as e:
    print(f"Import Error: {e}")

app = FastAPI(title="Audio Identification API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db = RedisManager()

@app.get("/health")
async def health():
    """Health check to verify the API and Redis are alive."""
    try:
        redis_status = "connected" if db.client.ping() else "disconnected"
    except Exception:
        redis_status = "error"
        
    return {
        "status": "healthy",
        "redis": redis_status,
        "ffmpeg": "found" if shutil.which("ffmpeg") else "not_found"
    }

@app.post("/api/v1/identify")
async def identify(file: UploadFile = File(...)):
    """
    Identifies audio files. 
    Uses /tmp to avoid permission issues and manual cleanup to save space.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
        try:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File write error: {str(e)}")

    try:
        return {
            "status": "success",
            "filename": file.filename,
            "message": "File received and processed"
        }

    except Exception as e:
        print(f"IDENTIFY ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing error")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
