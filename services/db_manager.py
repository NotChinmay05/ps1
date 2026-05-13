import os
import redis
import json

print(f"!!! DEBUG: Redis library is loading from: {redis.__file__}")

class RedisManager:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Ensure the URL has a valid scheme
        if not redis_url.startswith(("redis://", "rediss://", "unix://")):
            redis_url = f"rediss://{redis_url}" if "upstash.io" in redis_url else f"redis://{redis_url}"

        if "upstash.io" in redis_url and redis_url.startswith("redis://"):
            redis_url = redis_url.replace("redis://", "rediss://", 1)
            
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
