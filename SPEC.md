# Project: Audio Identification Engine (Production-Grade)

## Architecture Overview
An asynchronous, highly concurrent FastAPI backend backed by Redis. It utilizes an Abstract Factory pattern for feature extraction to allow swapping fingerprinting algorithms. The system includes robust dynamic data ingestion, fuzzy matching via time-offset alignment, and integrated latency/health telemetry.

## Core Tech Stack
*   **API & Concurrency:** FastAPI (Python), utilizing async/await for non-blocking concurrent queries.
*   **Audio Processing:** Librosa, Numpy, Scipy.
*   **Storage & Fast Retrieval:** Redis (In-memory hash-based lookup).
*   **Metrics:** Custom FastAPI Middleware for latency tracking.

## Module Mapping & Data Flow

### Module 1: The Abstraction & Dynamic Ingestion (Issues 1, 3, 4, 11)
*   **`interfaces/extractor.py`**: Defines an abstract base class `BaseAudioExtractor`.
*   **`services/fingerprinter.py`**: Concrete class implementing baseline fingerprinting (Constellation Maps via Librosa).
*   **`services/ingestion.py` (Dynamic Parser)**: 
    *   Traverses `dataset/{genre}/{filename}.wav`.
    *   Dynamically extracts `genre` from folder name and `song_id` from filename.
    *   Calculates `duration` via `librosa`. Uses fallback strings for `title` and `artist`.
    *   Uses strict `try/except` blocks to gracefully skip and log corrupt or hidden system files.

### Module 2: Fast Retrieval & Memory Optimization (Issues 2, 6, 15)
*   **Redis Schema (`services/db_manager.py`)**:
    *   *Hash Index*: Key = `hash_string`, Value = `List[(song_id, time_offset)]`. (Inverted index for fast retrieval).
    *   *Metadata Index*: Key = `song_id`, Value = `JSON(metadata)`.
    *   *Optimization*: Uses Redis pipelining for batch inserts during ingestion to eliminate I/O bottlenecks.

### Module 3: The Query & Matching Engine (Issues 5, 7, 8, 9, 12)
*   **Validation Pipeline**: Inspects incoming 3-10s queries. Cleanly rejects silent files or files < 1 second with a `400 Bad Request`.
*   **Fuzzy Matching Engine**:
    *   Finds matching hashes in Redis.
    *   Calculates $\Delta Offset = DB\_Time - Query\_Time$.
    *   Groups by `song_id` and $\Delta Offset$. The `song_id` with the highest density of matches at a consistent time delta wins.
*   **Confidence Scoring**: Calculates `Score = (Matches at Peak Delta) / (Total Hashes in Query) * 100`. Establishes a threshold (e.g., > 15%) to prevent false positives.

### Module 4: API, Telemetry, and Testing (Issues 10, 13, 14, 18)
*   **Endpoints (`main.py`)**:
    *   `POST /api/v1/identify`: The main concurrent query endpoint handling `multipart/form-data`.
    *   `GET /health`: Health and status check returning DB connection status and loaded track count.
*   **Middleware**: Intercepts requests to calculate and log end-to-end latency time.
*   **`tests/evaluator.py`**: Standalone script looping through a test set, calculating accuracy, false positives, and false negatives.