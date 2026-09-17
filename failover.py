import os
import time
import asyncio
from upstash_redis import Redis

REDIS_URL = os.getenv("UPSTASH_REDIS_URL")
NODE_ID = os.getenv("NODE_ID", "PRIMARY_TERMUX")
LOCK_KEY = "fubuki_cluster_master_lock"
LEASE_TTL = 60  # seconds

class FailoverManager:
    def __init__(self):
        if not REDIS_URL:
            raise ValueError("UPSTASH_REDIS_URL is not set in environment.")
        self.redis = Redis.from_url(REDIS_URL)
        self.is_leader = False

    def acquire_lock(self):
        res = self.redis.set(LOCK_KEY, NODE_ID, ex=LEASE_TTL, nx=True)
        if res:
            self.is_leader = True
            return True
        
        current = self.redis.get(LOCK_KEY)
        if current == NODE_ID:
            self.redis.expire(LOCK_KEY, LEASE_TTL)
            self.is_leader = True
            return True
            
        self.is_leader = False
        return False

    def renew_lease(self):
        lua = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("expire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """
        res = self.redis.eval(lua, [LOCK_KEY], [NODE_ID, LEASE_TTL])
        if not res:
            self.is_leader = False
        return bool(res)

    def release_lock(self):
        lua = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        self.redis.eval(lua, [LOCK_KEY], [NODE_ID])
        self.is_leader = False
