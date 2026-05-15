# Audio Identification & Source Detection System
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
---

## 🎵 What is this app? (Beginner's Guide)

Think of this project as your very own **Shazam**! It's a lightning-fast music recognition engine. You can give it a short, noisy audio snippet, and it will match it against a database to find out exactly what song it is. 
Unfortunately this being a very small scale project, this can only recognise and celar out the distorted clips of the audio it has been trained on. As there is no ML involved here currently, but we are bringing out the feature very soon.

Instead of just comparing audio files side-by-side (which is slow and breaks if there is background noise), it uses math to create an "acoustic fingerprint"—a constellation of sound peaks. It then searches our database for a matching constellation to find your song in milliseconds!

## 🌍 Try it Live!

The application is fully deployed and accessible from anywhere:

- **🎨 Frontend (Vercel)**: — *Head here to upload your audio snippets!*
- **⚙️ Backend API (Render)**:
- **🗄️ Database (Upstash)**: Our backend connects securely to a cloud-hosted Redis instance for sub-millisecond lookups.

## 🛠️ Implementation Overview

- **The Frontend (`c2c-test` folder)**: A sleek, modern React application built with Next.js. It gives you a beautiful workspace to upload audio snippets, visualizes the matching process, and displays the confidence score and latency details.
- **The Backend (Root folder)**: A Python-based **FastAPI** server running inside a **Docker** container. This is the "brain" that receives your snippet, extracts the audio features using libraries like `librosa`, and scores the matches.
- **The Database**: We use **Redis** because finding matching fingerprints requires thousands of lookups per second. Redis keeps everything in memory, ensuring the app feels completely instant.

## 💻 How to Run Locally

Want to tinker with the code? You can run both the frontend and backend on your own machine!

### 1. Start the Backend
You can run the backend easily using Docker:
```bash
# Build the Docker image
docker build -t audio-matcher .

# Run the container (make sure to provide your Upstash Redis URL or any other redis db url might be local also!)
docker run -p 8000:8000 -e REDIS_URL="rediss://your-upstash-redis-url:port" audio-matcher
```

*(Alternatively, you can run it natively using Python by installing `pip install -r requirements.txt`, making sure `ffmpeg` is installed on your system, and running `uvicorn main:app --reload`)*.

### 2. Start the Frontend
Open a new terminal and navigate to the frontend folder:
```bash
cd c2c-test

# Install dependencies
npm install

# Start the development server
npm run dev
```
Open `http://localhost:3000` in your browser, and you're good to go!
