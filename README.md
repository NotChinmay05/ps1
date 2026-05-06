# Audio Identification & Source Detection System

## Team Information
- **Team Name**: [NULL]
- **Year**: [2]
- **All-Female Team**: [No]

## Architecture Overview

#### Our approach focuses on a decoupled, asynchronous pipeline that separates signal processing from high-speed data retrieval.

*   **Feature Extraction & Storage**: 
    *   The system uses **Librosa** to perform Short-Time Fourier Transforms (STFT), converting audio into the frequency domain to identify "peaks" in a spectrogram[cite: 1, 2].
    *   These peaks are converted into **Constellation Maps** and hashed into pairs to ensure time-invariance[cite: 1, 2].
    *   Fingerprints are stored in a **Redis Inverted Index**, mapping hash strings to a list of song IDs and their respective time offsets for $O(1)$ lookup speeds[cite: 1, 2].
    
*   **Matching Algorithm**:
    *   The engine utilizes **Time-Offset Alignment** to handle noisy or partial snippets[cite: 1].
    *   It calculates the temporal difference ($\Delta Offset = DB\_Time - Query\_Time$) for every matching hash[cite: 1, 2].
    *   A **Histogram Analysis** identifies the candidate with the highest density of matches at a consistent time delta, filtering out random noise matches[cite: 1, 2].

*   **Scalability**:
    *   **FastAPI** with `async/await` allows the system to handle thousands of concurrent I/O-bound requests without blocking the event loop[cite: 1, 2].
    *   **Redis Pipelining** is used during ingestion to batch process thousands of song fingerprints, eliminating individual network round-trip bottlenecks[cite: 1, 2].
    *   The **Abstract Factory Pattern** allows the extraction logic to be swapped or scaled horizontally without modifying the core API[cite: 1, 2].

*   **Latency & Accuracy Mechanisms**:
    *   **Low Latency**: Custom middleware tracks end-to-end request time, while Redis ensures sub-millisecond retrieval of candidate matches[cite: 1, 2].
    *   **High Accuracy**: A **Confidence Scoring** mechanism is implemented ($Score = \frac{Matches \ at \ Peak \ \Delta}{Total \ Hashes} \times 100$)[cite: 1, 2].
    *   A strict threshold (e.g., >15%) and a **Validation Pipeline** prevent false positives from silent files or samples shorter than 1 second[cite: 1, 2].

**Note:** Please do not change the format or spelling of anything in this README. The fields are extracted using a script, so any changes to the structure or formatting may break the extraction process.
