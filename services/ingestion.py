import librosa
from pathlib import Path


class IngestionEngine:
    def __init__(self, extractor, db_manager):
        self.extractor = extractor
        self.db_manager = db_manager

    def process_dataset(self, directory: str):
        path_dir = Path(directory)
        if not path_dir.exists():
            print(f"Directory {directory} not found.")
            return

        for genre_folder in path_dir.iterdir():
            if genre_folder.is_dir():
                genre = genre_folder.name
                for audio_file in genre_folder.glob("*.wav"):
                    try:
                        self._ingest_file(audio_file, genre)
                    except Exception as e:
                        print(f"Error ingesting {audio_file}: {e}")

    def _ingest_file(self, file_path, genre):
        song_id = file_path.stem
        duration = librosa.get_duration(path=str(file_path), sr=22050)
        hashes = self.extractor.extract_features(str(file_path))

        metadata = {"title": song_id, "genre": genre, "duration": duration}
        self.db_manager.save_song(song_id, metadata, hashes)
        print(f"Indexed: {song_id} [{genre}]")