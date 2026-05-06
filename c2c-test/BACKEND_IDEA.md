# Audio Identification Engine (Production-Grade)

This project is a high-performance, asynchronous audio fingerprinting system designed for the **Code2Create Challenge**. It identifies audio snippets by matching them against a dataset of copyright-free tracks, even in the presence of significant background noise or distortion[cite: 1].

---

## ## Key Functionalities
*   **Dynamic Dataset Ingestion**: Automatically crawls `./dataset/{genre}/{filename}` to build a searchable database with metadata (Genre, Title, Duration)[cite: 1].
*   **Robust Audio Fingerprinting**: Utilizes **Constellation Mapping** (spectrogram peak detection) to create digital signatures resistant to environmental noise[cite: 1].
*   **Fuzzy Matching Engine**: Employs a **Time-Offset ($\Delta$ Offset)** alignment algorithm to find the most likely match from 3–10 second partial snippets[cite: 1].
*   **High Concurrency**: Built with **FastAPI** and **Redis** to handle multiple simultaneous identification requests in near real-time[cite: 1].
*   **Confidence Scoring**: Provides a mathematical certainty metric for every match, preventing false positives via an adjustable threshold[cite: 1].
*   **Real-time Telemetry**: Integrated middleware for monitoring system latency and health status[cite: 1].

---

## ## Technical Approach
The system follows a modular architecture based on the **Abstract Factory** design pattern to ensure scalability and maintainability[cite: 1].

### ### 1. Feature Extraction (The "Black Box")
Instead of matching raw audio, the system converts files into a **Constellation Map**[cite: 1].
*   **STFT**: Audio is processed via Short-Time Fourier Transform[cite: 1].
*   **Peak Filtering**: Local maxima (high-energy points) are identified in the spectrogram. These peaks are the most likely elements to survive background noise[cite: 1].
*   **Hashing**: These peaks are paired to create time-invariant hashes[cite: 1].

### ### 2. Fast Retrieval & Storage
*   **Inverted Index**: Hashes are stored in **Redis** as keys, pointing to a list of songs and the specific timestamps where that hash occurs[cite: 1].
*   **$O(1)$ Lookup**: Using Redis ensures that searching for a snippet takes milliseconds, even with thousands of songs in the index[cite: 1].

### ### 3. Robust Matching Algorithm
To identify a song, the engine looks for **Temporal Coherence**:
*   For every matching hash found in the DB, it calculates: $\Delta Offset = DB\_Time - Query\_Time$[cite: 1].
*   In a correct match, hundreds of hashes will share the *same* $\Delta$ Offset (forming a cluster)[cite: 1].
*   In a false match, the offsets will be randomly scattered[cite: 1].

---

## ## System Architecture

*   **Backend**: Python 3.13+, FastAPI, Uvicorn[cite: 1].
*   **Data Processing**: Librosa, NumPy, SciPy[cite: 1].
*   **Database**: Redis (In-memory storage)[cite: 1].
*   **Frontend**: React (JSX) with Axios for asynchronous file handling[cite: 1].

---

## ## Setup & Execution

### ### Prerequisites
*   Python 3.13+
*   Redis Server (running on `localhost:6379`)
*   FFmpeg (required by Librosa for audio decoding)

### ### Installation
1.  **Clone the repository** and navigate to the project root.
2.  **Activate Virtual Environment**:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    ```
3.  **Install Dependencies**:
    ```bash
    pip install fastapi uvicorn librosa numpy scipy redis
    ```

### ### Running the Application
1.  **Ingest the Dataset**:
    Place your audio files in `./dataset/{genre}/` and run the ingestion script to populate Redis[cite: 1].
2.  **Start the Backend**:
    ```bash
    uvicorn main:app --reload
    
```
3.  **Launch the Frontend**:
    Run your React development server to interact with the UI[cite: 1].

---

## ## API Documentation
*   `POST /api/v1/identify`: Upload an audio file to receive the predicted match and confidence score[cite: 1].
*   `GET /health`: Check system status and the total number of indexed tracks[cite: 1].