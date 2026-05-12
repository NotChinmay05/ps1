import redis
import json
import os

class RedisManager:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = redis.Redis.from_url(
            redis_url, 
            decode_responses=True,
            socket_timeout=5,
            retry_on_timeout=True
        )

    def save_song(self, song_id, metadata, hashes):
        pipeline = self.client.pipeline()
        pipeline.set(f"meta:{song_id}", json.dumps(metadata))
        for h_val, offset in hashes:
            pipeline.sadd(f"hash:{h_val}", f"{song_id}:{offset}")
        pipeline.execute()

    def query_hashes(self, hash_list):
        pipeline = self.client.pipeline()
        for h_val in hash_list:
            pipeline.smembers(f"hash:{h_val}")
        return pipeline.execute()
