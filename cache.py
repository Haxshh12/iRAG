"""
High-performance caching system for RAG-LLM
Reduces redundant API calls and improves response times
"""

import json
import hashlib
import time
from typing import Dict, Any, Optional, Tuple
from collections import OrderedDict
import psutil
import os

class CacheManager:
    """
    Intelligent caching system with memory management
    - Query result caching
    - Embedding caching
    - LRU eviction policy
    """
    
    def __init__(self, max_memory_mb: int = 100):
        self.query_cache: OrderedDict = OrderedDict()
        self.embedding_cache: Dict = {}
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory = 0
        self.hits = 0
        self.misses = 0
    
    @staticmethod
    def _hash_query(query: str) -> str:
        """Create hash for query caching"""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    @staticmethod
    def _estimate_size(obj: Any) -> int:
        """Rough estimate of object memory size in bytes"""
        try:
            return len(json.dumps(obj, default=str).encode('utf-8'))
        except:
            return 1000  # Default estimate
    
    def get_query_cache(self, query: str) -> Optional[Tuple[str, float]]:
        """Retrieve cached query result if available and not expired"""
        cache_key = self._hash_query(query)
        
        if cache_key not in self.query_cache:
            self.misses += 1
            return None
        
        result, timestamp, ttl = self.query_cache[cache_key]
        
        # Check if cache expired
        if time.time() - timestamp > ttl:
            del self.query_cache[cache_key]
            self.misses += 1
            return None
        
        # Move to end (LRU)
        self.query_cache.move_to_end(cache_key)
        self.hits += 1
        return result
    
    def set_query_cache(self, query: str, result: str, ttl: int = 3600):
        """Cache a query result with TTL"""
        cache_key = self._hash_query(query)
        
        # Check memory limits
        result_size = self._estimate_size(result)
        while self.current_memory + result_size > self.max_memory_bytes and self.query_cache:
            # Evict oldest entry
            old_key, (_, _, old_result) = self.query_cache.popitem(last=False)
            self.current_memory -= self._estimate_size(old_result)
        
        self.query_cache[cache_key] = (result, time.time(), ttl)
        self.current_memory += result_size
    
    def get_embedding_cache(self, text: str) -> Optional[list]:
        """Get cached embedding"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.embedding_cache:
            self.hits += 1
            return self.embedding_cache[text_hash]
        self.misses += 1
        return None
    
    def set_embedding_cache(self, text: str, embedding: list):
        """Cache an embedding"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        self.embedding_cache[text_hash] = embedding
    
    def clear_old_queries(self, ttl: int = 3600):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            k for k, (_, timestamp, entry_ttl) in self.query_cache.items()
            if current_time - timestamp > entry_ttl
        ]
        for key in expired_keys:
            del self.query_cache[key]
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "queries_cached": len(self.query_cache),
            "embeddings_cached": len(self.embedding_cache),
            "cache_hits": self.hits,
            "cache_misses": self.misses,
            "hit_rate_percent": f"{hit_rate:.1f}%",
            "memory_used_mb": f"{self.current_memory / (1024*1024):.2f}",
        }
    
    def print_stats(self):
        """Display cache statistics"""
        stats = self.get_stats()
        print("\n📊 Cache Statistics:")
        print("=" * 50)
        for key, value in stats.items():
            print(f"  {key:<25} : {value}")
        print("=" * 50)


class MemoryOptimizer:
    """Monitor and optimize memory usage"""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get current memory usage"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / (1024 * 1024),  # Resident Set Size
            "vms_mb": memory_info.vms / (1024 * 1024),  # Virtual Memory Size
            "percent": process.memory_percent(),
        }
    
    @staticmethod
    def print_memory_usage():
        """Display memory usage"""
        stats = MemoryOptimizer.get_memory_usage()
        print(f"💾 Memory: {stats['rss_mb']:.1f}MB ({stats['percent']:.1f}%)")
