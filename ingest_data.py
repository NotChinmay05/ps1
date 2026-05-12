import os
from services.ingestion import IngestionEngine
from services.fingerprinter import ConstellationExtractor
from services.db_manager import RedisManager

DATASET_DIRECTORY = os.path.join(os.path.dirname(__file__), "data")

if __name__ == "__main__":
    db = RedisManager()
    ext = ConstellationExtractor()
    engine = IngestionEngine(ext, db)

    print(f"Starting ingestion from: {DATASET_DIRECTORY}")
    engine.process_dataset(DATASET_DIRECTORY)
    print("Ingestion complete!")
