from services.ingestion import IngestionEngine
from services.fingerprinter import ConstellationExtractor
from services.db_manager import RedisManager

# Matches the folder name in image_955257.png
DATASET_DIRECTORY = "./data"

if __name__ == "__main__":
    db = RedisManager()
    ext = ConstellationExtractor()
    engine = IngestionEngine(ext, db)

    print(f"Cleaning database and starting ingestion from: {DATASET_DIRECTORY}")
    db.client.flushall()  # Wipe old data for a clean start
    engine.process_dataset(DATASET_DIRECTORY)
    print("Ingestion complete!")