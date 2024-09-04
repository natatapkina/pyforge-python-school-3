import json

from redis import Redis

from log import logger


class RedisCacheBackend:
    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client

    def __call__(self):
        return self

    def get_cached_result(self, key: str):
        logger.info(f'Retrieving data from cache using key {key}.')
        result = self.redis_client.get(key)
        if result:
            return json.loads(result)
        return None

    def set_cache(self, key: str, value: dict, expiration: int = 60):
        logger.info(f'Saving data to cache using key {key}.')
        self.redis_client.setex(key, expiration, json.dumps(value))

    def del_cache(self, key: str):
        logger.info(f'Deleting data from cache using key {key}.')
        self.redis_client.delete(key)
