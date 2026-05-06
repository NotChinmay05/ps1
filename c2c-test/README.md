# Audio Identification & Source Detection System

## Team Information
- **Team Name**: [NULL]
- **Year**: [2]
- **All-Female Team**: [No]

## Architecture Overview

#### Describe your approach here. Keep it short and clear.

    - [How does your system efficiently extract and store features (e.g., fingerprints, spectrograms) from the audio dataset?]
        - Each audio file is processed through a Short-Time Fourier Transform (STFT) to produce a spectrogram. From that spectrogram, only the high-energy local maxima (peaks) are kept — these are the points most likely to survive noise. Pairs of nearby peaks are combined into time-invariant hashes. These hashes are stored in Redis as an inverted index: each hash is a key pointing to a list of (song_id, timestamp) entries. Redis keeps everything in memory, so reads are O(1) regardless of dataset size.

    - [What matching algorithm or technique do you use to compare noisy/partial query snippets against the database?]
        - The query clip goes through the same STFT → peak detection → hashing pipeline as the dataset. Each query hash is looked up in Redis, returning a list of candidate (song_id, db_timestamp) pairs. For each candidate, the engine computes ΔOffset = db_timestamp − query_timestamp. The correct song will have hundreds of hashes that all share the same ΔOffset — this is called temporal coherence. A false match produces randomly scattered offsets. The song with the largest cluster of matching ΔOffsets wins, and the cluster size divided by total query hashes becomes the confidence score.

    - [How does your architecture handle scalability to support a few thousand songs and concurrent queries?]
        - Two things carry the load. First, Redis — all fingerprint data lives in memory with O(1) hash lookups, so adding more songs increases storage linearly but doesn't slow down individual queries. Second, FastAPI runs on Uvicorn with async request handling, meaning incoming queries don't block each other. Multiple identification requests run concurrently without queuing, and Redis connections are shared safely across async workers.

    - [What mechanisms are in place to ensure low latency and high accuracy despite noise or distortion in the input queries?]
        - Latency is kept low by the O(1) Redis lookup — the system never scans the full dataset. Only hashes that actually match get processed further, so computation scales with matches found, not total songs indexed. Accuracy under noise is handled by the peak-selection step: only the strongest spectral peaks are fingerprinted, and background noise rarely produces peaks at those exact frequency-time coordinates. The temporal coherence check then filters out any accidental hash collisions — random noise can match a few hashes by chance, but it cannot fake a coherent ΔOffset cluster. A configurable confidence threshold prevents low-cluster matches from being returned as false positives.

**Note:** Please do not change the format or spelling of anything in this README. The fields are extracted using a script, so any changes to the structure or formatting may break the extraction process.
