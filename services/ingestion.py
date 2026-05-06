import os
import sys
import logging
import librosa
from pathlib import Path

# Fix imports if running as script directly without module context
if __name__ == "__main__":
    # Add parent directory to sys.path so we can import services
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.fingerprinter import AudioFingerprinter
from services.db_manager import DBManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def ingest_dataset(root_dir: str):
    """
    Traverses the local directory structure to find audio files,
    extracts features, and stores them in Redis.
    """
    root_path = Path(root_dir)
    if not root_path.exists() or not root_path.is_dir():
        logger.error(f"Directory not found: {root_dir}")
        return

    # Initialize components
    # We standardize to 11025Hz to save memory, as specified.
    target_sr = 11025
    fingerprinter = AudioFingerprinter(sample_rate=target_sr)
    db_manager = DBManager()

    logger.info(f"Starting ingestion from: {root_path.absolute()}")
    
    total_processed = 0
    total_skipped = 0

    # Traverse directory structure
    for dirpath, dirnames, filenames in os.walk(root_path):
        current_dir = Path(dirpath)
        
        # Genre is the name of the immediate parent folder of the audio files
        # If audio files are in the root directory, genre is 'unknown'
        if current_dir == root_path:
            genre = "unknown"
        else:
            genre = current_dir.name
            
        for filename in filenames:
            file_path = current_dir / filename
            
            # Skip hidden files or obvious non-audio files like .DS_Store
            if filename.startswith('.'):
                continue
                
            song_id = file_path.stem # Filename without extension
            
            try:
                # 1. Load the file
                # librosa standardizes the sample rate here
                y, sr = librosa.load(str(file_path), sr=target_sr, mono=True)
                
                # 2. Calculate duration
                duration = librosa.get_duration(y=y, sr=sr)
                
                # 3. Extract features
                # Pass the pre-loaded numpy array to the fingerprinter
                features = fingerprinter.extract_features(y)
                hashes = features.get("hashes", [])
                
                if not hashes:
                    logger.warning(f"No features extracted for {filename}. Skipping.")
                    total_skipped += 1
                    continue
                    
                # 4. Store metadata and hashes
                metadata = {
                    "genre": genre,
                    "duration": duration,
                    "filename": filename,
                    "original_path": str(file_path)
                }
                
                # Use Redis pipelining under the hood via DBManager
                db_manager.store_hashes(song_id=song_id, hashes=hashes, metadata=metadata)
                
                total_processed += 1
                logger.info(f"Ingested [{genre}] {song_id}: {len(hashes)} hashes, {duration:.2f}s")
                
            except Exception as e:
                # Skip corrupted or non-audio files
                logger.warning(f"Skipped {filename}: {str(e)}")
                total_skipped += 1

    logger.info("Ingestion Complete.")
    logger.info(f"Total processed: {total_processed}")
    logger.info(f"Total skipped: {total_skipped}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python services/ingestion.py <path_to_dataset>")
        sys.exit(1)
        
    dataset_path = sys.argv[1]
    ingest_dataset(dataset_path)
