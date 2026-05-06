import numpy as np
import librosa
import scipy.ndimage
from typing import Any, Dict, List, Tuple

from interfaces.extractor import BaseAudioExtractor

class AudioFingerprinter(BaseAudioExtractor):
    """
    Concrete implementation of BaseAudioExtractor using librosa and scipy.
    Extracts a constellation map of spectrogram peaks and generates
    combinatorial hashes.
    """
    def __init__(self, sample_rate=22050, n_fft=2048, hop_length=512):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        
        # Peak finding parameters
        self.filter_size = (10, 10) # (freq_bins, time_frames)
        
        # Hashing parameters
        self.target_zone_size = 5   # How many peaks to look ahead
        self.target_zone_delay = 1  # Start looking ahead after this many peaks
        
    def extract_features(self, audio_data: Any) -> Dict[str, Any]:
        """
        Extract features from the provided audio data.
        
        Args:
            audio_data: The input audio data (file path as string).
            
        Returns:
            A dictionary containing the extracted hashes and peak count.
        """
        # 1. Load audio
        # If audio_data is a string, it's a file path. Otherwise, assume it's a pre-loaded numpy array.
        if isinstance(audio_data, (str, bytes)):
            y, sr = librosa.load(audio_data, sr=self.sample_rate, mono=True)
        else:
            y = audio_data
            
        # 2. Compute Spectrogram
        # STFT (Short-Time Fourier Transform) converts time-domain to time-frequency domain
        stft_matrix = librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length)
        
        # Get magnitude spectrogram
        spectrogram = np.abs(stft_matrix)
        
        # 3. Find Spectrogram Peaks (Constellation Map)
        # We use a maximum filter to find local maxima in the 2D spectrogram.
        # A point is a peak if its value equals the maximum in its neighborhood.
        local_max = scipy.ndimage.maximum_filter(spectrogram, size=self.filter_size) == spectrogram
        
        # Apply amplitude threshold to filter out background noise
        # Using a dynamic threshold (e.g., 75th percentile of amplitude)
        threshold = np.percentile(spectrogram, 75)
        background_threshold = spectrogram > threshold
        
        # The peaks are the intersection of local maxima and threshold
        peaks = local_max & background_threshold
        
        # Get coordinates of peaks: frequencies (rows) and times (columns)
        freq_indices, time_indices = np.where(peaks)
        
        # Pair them up and sort by time (to facilitate forward-looking hashes)
        # Convert to standard Python types to prevent downstream JSON serialization errors
        peak_list = list(zip(time_indices.tolist(), freq_indices.tolist()))
        peak_list.sort(key=lambda x: x[0])
        
        # 4. Generate Combinatorial Hashes
        hashes = self._generate_hashes(peak_list)
        
        return {
            "hashes": hashes,
            "peak_count": len(peak_list)
        }
        
    def _generate_hashes(self, peaks: List[Tuple[int, int]]) -> List[Tuple[str, int]]:
        """
        Generates combinatorial hashes from a list of peaks.
        
        For each peak (anchor), we look ahead at a 'target zone' of subsequent peaks.
        We form a hash using: (anchor_freq, target_freq, time_delta).
        
        Returns:
            List of tuples: (hash_string, anchor_time)
        """
        hashes = []
        for i in range(len(peaks)):
            anchor_time, anchor_freq = peaks[i]
            
            # Define the target zone for this anchor
            target_start = i + self.target_zone_delay
            target_end = min(len(peaks), target_start + self.target_zone_size)
            
            for j in range(target_start, target_end):
                target_time, target_freq = peaks[j]
                
                # Time delta between anchor and target
                time_delta = target_time - anchor_time
                
                # Create a simple string hash (e.g., "f1|f2|dt")
                # Using strings makes it easy to store as Redis keys
                hash_string = f"{anchor_freq}|{target_freq}|{time_delta}"
                
                hashes.append((hash_string, anchor_time))
                
        return hashes
