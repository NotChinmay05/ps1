import librosa
import numpy as np
import json
from scipy.ndimage import maximum_filter
from interfaces.extractor import BaseAudioExtractor


class ConstellationExtractor(BaseAudioExtractor):
    def extract_features(self, file_path):
        # Force 22050Hz Mono for consistency across ingestion and query
        y, sr = librosa.load(file_path, sr=22050, mono=True)
        S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
        peaks = self._get_peaks(S)
        return [(int(p[0]), int(p[1])) for p in peaks]

    def _get_peaks(self, S):
        struct = np.ones((30, 30))
        local_max = (maximum_filter(S, footprint=struct) == S)
        # 10% of max energy threshold to filter noise
        background = (S > np.max(S) * 0.1)
        detected_peaks = local_max & background
        freqs, times = np.where(detected_peaks)
        return list(zip(freqs, times))


class MatchingEngine:
    def __init__(self, db_manager):
        self.db = db_manager

    def find_match(self, query_hashes):
        if not query_hashes: return None

        raw_matches = self.db.query_hashes([h[0] for h in query_hashes])
        hits = {}  # (song_id, delta) -> count

        for i, song_hits in enumerate(raw_matches):
            query_time = query_hashes[i][1]
            for hit in song_hits:
                song_id, song_time = hit.split(":")
                delta = int(song_time) - int(query_time)
                hits[(song_id, delta)] = hits.get((song_id, delta), 0) + 1

        if not hits: return None

        best_match_key = max(hits, key=hits.get)
        match_count = hits[best_match_key]
        conf_score = (match_count / len(query_hashes)) * 100

        if conf_score < 5: return None

        # Retrieve metadata from Redis
        meta_raw = self.db.client.get(f"meta:{best_match_key[0]}")
        meta = json.loads(meta_raw) if meta_raw else {}

        return {
            "filename": best_match_key[0],
            "confidence": f"{conf_score:.2f}",
            "type": meta.get("genre", "Unknown"),
            "full_duration": f"{meta.get('duration', 0):.2f}"
        }