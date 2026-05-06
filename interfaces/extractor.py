from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAudioExtractor(ABC):
    """
    Abstract base class for extracting features from audio data.
    """
    
    @abstractmethod
    def extract_features(self, audio_data: Any) -> Dict[str, Any]:
        """
        Extract features from the provided audio data.
        
        Args:
            audio_data: The input audio data (e.g., raw bytes, numpy array, or file path).
            
        Returns:
            A dictionary or object containing the extracted features.
        """
        pass
