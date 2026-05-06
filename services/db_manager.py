import redis
from typing import List, Tuple, Dict, Any
from collections import Counter

class DBManager:
    """
    Handles Redis connection and provides methods to store hashes 
    and perform fuzzy matching for audio identification.
    """
    def __init__(self, host="localhost", port=6379, db=0):
        """
        Initialize the Redis connection pool.
        We use decode_responses=True to automatically get strings instead of bytes.
        """
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def store_hashes(self, song_id: str, hashes: List[Tuple[str, int]], metadata: Dict[str, Any] = None):
        """
        Stores combinatorial hashes in Redis using pipelining for performance.
        Optionally stores song metadata (genre, duration, etc.).
        
        Args:
            song_id: Unique identifier for the song.
            hashes: List of tuples (hash_string, anchor_time).
            metadata: Optional dictionary of metadata to store.
        """
        pipeline = self.redis_client.pipeline()
        
        for hash_string, anchor_time in hashes:
            # We use Redis Sets. Key is the hash, value is "song_id:anchor_time"
            # This allows multiple songs (or different parts of the same song) 
            # to share the same hash without overwriting.
            value = f"{song_id}:{anchor_time}"
            pipeline.sadd(hash_string, value)
            
        if metadata:
            # Store metadata in a Redis Hash
            pipeline.hset(f"song:{song_id}", mapping=metadata)
            
        # Execute all commands in the pipeline in one network round-trip
        pipeline.execute()

    def fuzzy_match(self, query_hashes: List[Tuple[str, int]]) -> Dict[str, Any]:
        """
        Fuzzy Matching Engine.
        Finds the most likely song match by calculating Delta Offsets.
        
        Args:
            query_hashes: List of tuples (hash_string, query_anchor_time).
            
        Returns:
            Dict containing the best match song_id and confidence score.
        """
        if not query_hashes:
            return {"song_id": None, "confidence": 0.0, "message": "No query hashes provided"}

        pipeline = self.redis_client.pipeline()
        
        # Batch fetch all matches for the query hashes
        for hash_string, _ in query_hashes:
            pipeline.smembers(hash_string)
            
        results = pipeline.execute()
        
        # Histogram to count (song_id, delta_offset) occurrences
        delta_histogram = Counter()
        
        # Process the results
        for i, query_hash_data in enumerate(query_hashes):
            _, query_time = query_hash_data
            db_matches = results[i]
            
            for match in db_matches:
                # match is stored as "song_id:db_time"
                song_id, db_time_str = match.rsplit(":", 1)
                db_time = int(db_time_str)
                
                # Calculate Delta Offset: DB_Time - Query_Time
                # A true match will have many hashes yielding the same Delta Offset
                delta_offset = db_time - query_time
                
                # Increment the count for this specific offset alignment
                delta_histogram[(song_id, delta_offset)] += 1
                
        if not delta_histogram:
            return {"song_id": None, "confidence": 0.0, "message": "No matches found in DB"}
            
        # Find the highest peak in the histogram (most common offset alignment)
        best_match, max_count = delta_histogram.most_common(1)[0]
        best_song_id, best_delta_offset = best_match
        
        # Calculate Confidence Score
        # Confidence is proportional to the peak alignment count relative to query size
        total_query_peaks = len(query_hashes)
        confidence = max_count / total_query_peaks if total_query_peaks > 0 else 0.0
        
        return {
            "song_id": str(best_song_id) if best_song_id else None,
            "confidence": float(confidence),
            "delta_offset": int(best_delta_offset),
            "matches": int(max_count),
            "total_query_hashes": int(total_query_peaks)
        }
