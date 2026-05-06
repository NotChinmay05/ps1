from abc import ABC, abstractmethod

class BaseAudioExtractor(ABC):
    @abstractmethod
    def extract_features(self, file_path: str):
        """Abstract method to extract fingerprints from audio."""
        pass