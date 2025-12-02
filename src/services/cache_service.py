"""
Redis Cache Service for Adaptive Retrieval Layer
Provides caching for embeddings and query results to reduce latency and computational costs
"""

import redis
import json
import hashlib
from typing import Any, Optional, List, Dict
from datetime import datetime
from src.utils.logger import log


class CacheService:
    """Redis-based caching service for RAG system"""

    def __init__(
        self, host: str = "localhost", port: int = 6379, db: int = 0, ttl: int = 3600
    ):
        """
        Initialize Redis cache service

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            ttl: Time-to-live for cache entries in seconds (default: 1 hour)
        """
        self.host = host
        self.port = port
        self.db = db
        self.ttl = ttl
        self.client = None
        self._connect()

    def _connect(self):
        """Establish connection to Redis server"""
        try:
            self.client = redis.StrictRedis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.client.ping()
            log.info(f"✅ Connected to Redis at {self.host}:{self.port}")

        except redis.ConnectionError as e:
            log.error(f"❌ Failed to connect to Redis: {e}")
            log.warning("⚠️ Cache service will operate in no-cache mode")
            self.client = None

        except Exception as e:
            log.error(f"❌ Unexpected error connecting to Redis: {e}")
            self.client = None

    def _make_key(self, text: str) -> str:
        """
        Generate MD5 hash key from text to avoid special characters

        Args:
            text: Input text

        Returns:
            MD5 hash string
        """
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def is_connected(self) -> bool:
        """Check if Redis connection is active"""
        if self.client is None:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    # ==================== Embedding Cache Methods ====================

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Retrieve cached embedding for text

        Args:
            text: Input text

        Returns:
            Embedding vector as list of floats, or None if not cached
        """
        if not self.is_connected():
            return None

        try:
            key = f"embedding:{self._make_key(text)}"
            data = self.client.get(key)

            if data:
                log.debug(f"🎯 Cache HIT for embedding: {text[:50]}...")
                return json.loads(data)
            else:
                log.debug(f"❌ Cache MISS for embedding: {text[:50]}...")
                return None

        except Exception as e:
            log.error(f"❌ Error getting embedding from cache: {e}")
            return None

    def set_embedding(
        self, text: str, embedding: List[float], ttl: Optional[int] = None
    ) -> bool:
        """
        Store embedding in cache

        Args:
            text: Input text
            embedding: Embedding vector
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            key = f"embedding:{self._make_key(text)}"
            value = json.dumps(embedding)
            cache_ttl = ttl if ttl is not None else self.ttl

            self.client.setex(key, cache_ttl, value)
            log.debug(f"💾 Cached embedding: {text[:50]}...")
            return True

        except Exception as e:
            log.error(f"❌ Error setting embedding in cache: {e}")
            return False

    # ==================== Query Result Cache Methods ====================

    def get_query_result(self, query: str) -> Optional[Dict]:
        """
        Retrieve cached query result

        Args:
            query: Query text

        Returns:
            Query result dictionary, or None if not cached
        """
        if not self.is_connected():
            return None

        try:
            key = f"query:{self._make_key(query)}"
            data = self.client.get(key)

            if data:
                log.info(f"🎯 Cache HIT for query: {query[:50]}...")
                return json.loads(data)
            else:
                log.debug(f"❌ Cache MISS for query: {query[:50]}...")
                return None

        except Exception as e:
            log.error(f"❌ Error getting query result from cache: {e}")
            return None

    def set_query_result(
        self, query: str, results: Dict, ttl: Optional[int] = None
    ) -> bool:
        """
        Store query result in cache

        Args:
            query: Query text
            results: Query result dictionary
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            key = f"query:{self._make_key(query)}"
            value = json.dumps(results)
            cache_ttl = ttl if ttl is not None else self.ttl

            self.client.setex(key, cache_ttl, value)
            log.info(f"💾 Cached query result: {query[:50]}...")
            return True

        except Exception as e:
            log.error(f"❌ Error setting query result in cache: {e}")
            return False

    # ==================== Batch Operations ====================

    def get_embeddings_batch(
        self, texts: List[str]
    ) -> Dict[str, Optional[List[float]]]:
        """
        Retrieve multiple embeddings from cache

        Args:
            texts: List of input texts

        Returns:
            Dictionary mapping text to embedding (None if not cached)
        """
        if not self.is_connected():
            return {text: None for text in texts}

        results = {}
        try:
            # Use pipeline for efficient batch operations
            pipe = self.client.pipeline()
            keys = [f"embedding:{self._make_key(text)}" for text in texts]

            for key in keys:
                pipe.get(key)

            cached_data = pipe.execute()

            for text, data in zip(texts, cached_data):
                if data:
                    results[text] = json.loads(data)
                    log.debug(f"🎯 Batch cache HIT: {text[:30]}...")
                else:
                    results[text] = None

            hit_count = sum(1 for v in results.values() if v is not None)
            log.info(f"📦 Batch embedding cache: {hit_count}/{len(texts)} hits")

        except Exception as e:
            log.error(f"❌ Error in batch embedding retrieval: {e}")
            results = {text: None for text in texts}

        return results

    def set_embeddings_batch(
        self, text_embedding_pairs: List[tuple], ttl: Optional[int] = None
    ) -> int:
        """
        Store multiple embeddings in cache

        Args:
            text_embedding_pairs: List of (text, embedding) tuples
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            Number of successfully cached embeddings
        """
        if not self.is_connected():
            return 0

        try:
            cache_ttl = ttl if ttl is not None else self.ttl
            pipe = self.client.pipeline()
            count = 0

            for text, embedding in text_embedding_pairs:
                key = f"embedding:{self._make_key(text)}"
                value = json.dumps(embedding)
                pipe.setex(key, cache_ttl, value)
                count += 1

            pipe.execute()
            log.info(f"💾 Batch cached {count} embeddings")
            return count

        except Exception as e:
            log.error(f"❌ Error in batch embedding storage: {e}")
            return 0

    # ==================== Cache Management Methods ====================

    def clear_cache(self) -> bool:
        """
        Clear all cached data

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            self.client.flushdb()
            log.info("🗑️ All cache cleared successfully")
            return True

        except Exception as e:
            log.error(f"❌ Error clearing cache: {e}")
            return False

    def clear_embedding_cache(self) -> int:
        """
        Clear only embedding cache entries

        Returns:
            Number of keys deleted
        """
        if not self.is_connected():
            return 0

        try:
            pattern = "embedding:*"
            keys = self.client.keys(pattern)

            if keys:
                deleted = self.client.delete(*keys)
                log.info(f"🗑️ Cleared {deleted} embedding cache entries")
                return deleted
            else:
                log.info("ℹ️ No embedding cache entries to clear")
                return 0

        except Exception as e:
            log.error(f"❌ Error clearing embedding cache: {e}")
            return 0

    def clear_query_cache(self) -> int:
        """
        Clear only query result cache entries

        Returns:
            Number of keys deleted
        """
        if not self.is_connected():
            return 0

        try:
            pattern = "query:*"
            keys = self.client.keys(pattern)

            if keys:
                deleted = self.client.delete(*keys)
                log.info(f"🗑️ Cleared {deleted} query cache entries")
                return deleted
            else:
                log.info("ℹ️ No query cache entries to clear")
                return 0

        except Exception as e:
            log.error(f"❌ Error clearing query cache: {e}")
            return 0

    def delete_key(self, key: str) -> bool:
        """
        Delete a specific cache key

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            deleted = self.client.delete(key)
            if deleted:
                log.debug(f"🗑️ Deleted cache key: {key}")
                return True
            else:
                log.debug(f"ℹ️ Key not found: {key}")
                return False

        except Exception as e:
            log.error(f"❌ Error deleting key {key}: {e}")
            return False

    def set_ttl(self, key: str, ttl: int) -> bool:
        """
        Update TTL for an existing cache key

        Args:
            key: Cache key
            ttl: New time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            result = self.client.expire(key, ttl)
            if result:
                log.debug(f"⏱️ Updated TTL for {key} to {ttl}s")
                return True
            else:
                log.debug(f"ℹ️ Key not found: {key}")
                return False

        except Exception as e:
            log.error(f"❌ Error setting TTL for {key}: {e}")
            return False

    # ==================== Cache Statistics Methods ====================

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics

        Returns:
            Dictionary containing cache statistics
        """
        if not self.is_connected():
            return {
                "connected": False,
                "error": "Redis not connected",
            }

        try:
            info = self.client.info()

            # Count keys by pattern
            embedding_keys = len(self.client.keys("embedding:*"))
            query_keys = len(self.client.keys("query:*"))
            total_keys = self.client.dbsize()

            stats = {
                "connected": True,
                "redis_version": info.get("redis_version", "unknown"),
                "uptime_seconds": info.get("uptime_in_seconds", 0),
                "total_keys": total_keys,
                "embedding_keys": embedding_keys,
                "query_keys": query_keys,
                "memory_used_mb": round(info.get("used_memory", 0) / (1024 * 1024), 2),
                "memory_peak_mb": round(
                    info.get("used_memory_peak", 0) / (1024 * 1024), 2
                ),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0), info.get("keyspace_misses", 0)
                ),
                "connected_clients": info.get("connected_clients", 0),
                "evicted_keys": info.get("evicted_keys", 0),
                "expired_keys": info.get("expired_keys", 0),
            }

            log.info(
                f"📊 Cache stats: {total_keys} keys, {stats['hit_rate']:.1f}% hit rate"
            )
            return stats

        except Exception as e:
            log.error(f"❌ Error getting cache stats: {e}")
            return {
                "connected": False,
                "error": str(e),
            }

    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """
        Calculate cache hit rate percentage

        Args:
            hits: Number of cache hits
            misses: Number of cache misses

        Returns:
            Hit rate as percentage (0-100)
        """
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)

    def get_key_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific cache key

        Args:
            key: Cache key to inspect

        Returns:
            Dictionary with key information, or None if key doesn't exist
        """
        if not self.is_connected():
            return None

        try:
            if not self.client.exists(key):
                return None

            ttl = self.client.ttl(key)
            key_type = self.client.type(key)
            memory = (
                self.client.memory_usage(key)
                if hasattr(self.client, "memory_usage")
                else None
            )

            info = {
                "key": key,
                "type": key_type,
                "ttl_seconds": ttl,
                "exists": True,
            }

            if memory:
                info["memory_bytes"] = memory

            return info

        except Exception as e:
            log.error(f"❌ Error getting key info for {key}: {e}")
            return None

    def get_all_keys(self, pattern: str = "*") -> List[str]:
        """
        Get all cache keys matching a pattern

        Args:
            pattern: Redis key pattern (default: "*" for all keys)

        Returns:
            List of matching keys
        """
        if not self.is_connected():
            return []

        try:
            keys = self.client.keys(pattern)
            log.debug(f"🔍 Found {len(keys)} keys matching pattern '{pattern}'")
            return keys

        except Exception as e:
            log.error(f"❌ Error getting keys with pattern '{pattern}': {e}")
            return []

    # ==================== Health Check Methods ====================

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on cache service

        Returns:
            Dictionary with health status
        """
        health = {
            "service": "CacheService",
            "timestamp": self._get_timestamp(),
            "status": "unknown",
            "details": {},
        }

        try:
            if not self.is_connected():
                health["status"] = "unhealthy"
                health["details"]["error"] = "Redis not connected"
                return health

            # Test basic operations
            test_key = "health_check_test"
            test_value = "ok"

            # Test write
            self.client.setex(test_key, 10, test_value)

            # Test read
            retrieved = self.client.get(test_key)

            # Test delete
            self.client.delete(test_key)

            if retrieved == test_value:
                health["status"] = "healthy"
                health["details"]["connection"] = "ok"
                health["details"]["read_write"] = "ok"
                health["details"]["host"] = self.host
                health["details"]["port"] = self.port
                health["details"]["db"] = self.db
            else:
                health["status"] = "degraded"
                health["details"]["error"] = "Read/write test failed"

        except Exception as e:
            health["status"] = "unhealthy"
            health["details"]["error"] = str(e)
            log.error(f"❌ Health check failed: {e}")

        return health

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""

        return datetime.utcnow().isoformat() + "Z"

    # ==================== Context Manager Support ====================

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection"""
        self.close()

    def close(self):
        """Close Redis connection"""
        if self.client:
            try:
                self.client.close()
                log.info("🔌 Redis connection closed")
            except Exception as e:
                log.error(f"❌ Error closing Redis connection: {e}")

    def __repr__(self) -> str:
        """String representation of CacheService"""
        status = "connected" if self.is_connected() else "disconnected"
        return f"CacheService(host={self.host}, port={self.port}, db={self.db}, status={status})"
