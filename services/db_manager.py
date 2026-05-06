import redis
import json

class RedisManager:
    def __init__(self):
        # Connects to the Redis container started via Docker
        self.client = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def save_song(self, song_id, metadata, hashes):
        pipeline = self.client.pipeline()
        # Store metadata for retrieval during identification
        pipeline.set(f"meta:{song_id}", json.dumps(metadata))
        for h_val, offset in hashes:
            # sadd ensures we don't store exact duplicate hashes for the same offset
            pipeline.sadd(f"hash:{h_val}", f"{song_id}:{offset}")
        pipeline.execute()

    def query_hashes(self, hash_list):
        pipeline = self.client.pipeline()
        for h_val in hash_list:
            pipeline.smembers(f"hash:{h_val}")
        return pipeline.execute()