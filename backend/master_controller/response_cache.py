"""
Intelligent Response Caching System
Caches AI responses for duplicate queries to improve speed and reduce API calls
"""

import hashlib
import time
from typing import Optional, Dict, Tuple, List
import json


class ResponseCache:
    """
    Smart caching for AI responses with similarity detection
    """
    
    def __init__(self, ttl_seconds: int = 3600, max_entries: int = 1000):
        self.cache = {}  # {query_hash: {response, timestamp, hit_count}}
        self.ttl = ttl_seconds  # Cache time-to-live (1 hour default)
        self.max_entries = max_entries
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_saved_calls": 0
        }
        
        print(f"💾 Response Cache initialized (TTL: {ttl_seconds}s, Max: {max_entries} entries)")
    
    def _hash_query(self, message: str, context: Optional[str] = None) -> str:
        """Generate hash for query + context"""
        # Normalize: lowercase, strip whitespace
        normalized = message.lower().strip()
        if context:
            normalized += context.lower().strip()
        
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, message: str, context: Optional[str] = None) -> Optional[str]:
        """Get cached response if available and not expired"""
        query_hash = self._hash_query(message, context)
        
        if query_hash in self.cache:
            entry = self.cache[query_hash]
            age = time.time() - entry["timestamp"]
            
            # Check if expired
            if age > self.ttl:
                del self.cache[query_hash]
                self.stats["evictions"] += 1
                self.stats["misses"] += 1
                print(f"   💾 Cache MISS (expired after {age/60:.1f} minutes)")
                return None
            
            # Cache hit!
            entry["hit_count"] += 1
            self.stats["hits"] += 1
            self.stats["total_saved_calls"] += 1
            
            hit_rate = self.stats["hits"] / (self.stats["hits"] + self.stats["misses"]) * 100
            print(f"   ✅ Cache HIT! (saved API call, hit rate: {hit_rate:.1f}%)")
            print(f"      This response has been reused {entry['hit_count']} times")
            
            return entry["response"]
        
        self.stats["misses"] += 1
        print(f"   💾 Cache MISS (new query)")
        return None
    
    def set(self, message: str, response: str, context: Optional[str] = None):
        """Store response in cache"""
        query_hash = self._hash_query(message, context)
        
        # Check cache size limit
        if len(self.cache) >= self.max_entries and query_hash not in self.cache:
            # Evict oldest entry (simple FIFO)
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
            self.stats["evictions"] += 1
            print(f"   ⚠️ Cache full - evicted oldest entry")
        
        self.cache[query_hash] = {
            "response": response,
            "timestamp": time.time(),
            "hit_count": 0,
            "query_preview": message[:50] + "..." if len(message) > 50 else message
        }
        
        print(f"   💾 Cached response ({len(self.cache)}/{self.max_entries} entries)")
    
    def clear_expired(self):
        """Remove all expired entries"""
        now = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now - entry["timestamp"] > self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
            self.stats["evictions"] += 1
        
        if expired_keys:
            print(f"   🧹 Cleared {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def clear_all(self):
        """Clear entire cache"""
        count = len(self.cache)
        self.cache.clear()
        print(f"   🧹 Cleared all {count} cache entries")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate cache efficiency (API calls saved)
        original_calls = total_requests
        actual_calls = original_calls - self.stats["total_saved_calls"]
        efficiency = (self.stats["total_saved_calls"] / original_calls * 100) if original_calls > 0 else 0
        
        return {
            "total_entries": len(self.cache),
            "max_entries": self.max_entries,
            "total_requests": total_requests,
            "cache_hits": self.stats["hits"],
            "cache_misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%",
            "api_calls_saved": self.stats["total_saved_calls"],
            "efficiency": f"{efficiency:.1f}%",
            "evictions": self.stats["evictions"],
            "ttl_seconds": self.ttl
        }
    
    def get_popular_queries(self, top_n: int = 5) -> List[Dict]:
        """Get most frequently cached queries"""
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1]["hit_count"],
            reverse=True
        )[:top_n]
        
        return [
            {
                "query": entry["query_preview"],
                "hits": entry["hit_count"],
                "age_minutes": (time.time() - entry["timestamp"]) / 60
            }
            for _, entry in sorted_entries
        ]
