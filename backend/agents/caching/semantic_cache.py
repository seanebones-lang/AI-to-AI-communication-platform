"""
Semantic Caching System for Enterprise AI Platform
Implements intelligent response caching based on semantic similarity
"""

import asyncio
import hashlib
import json
import time
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import redis
import pickle

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    EXACT_MATCH = "exact_match"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    HYBRID = "hybrid"

class CachePolicy(Enum):
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"

@dataclass
class CacheEntry:
    key: str
    value: Any
    embedding: List[float]
    metadata: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl: Optional[timedelta] = None
    cost: float = 0.0
    relevance_score: float = 1.0

@dataclass
class CacheHit:
    entry: CacheEntry
    similarity_score: float
    hit_type: str  # "exact", "semantic", "fuzzy"
    response_time: float

class SemanticCacheManager:
    """
    Semantic Cache Manager for AI responses
    Implements intelligent caching based on semantic similarity
    """
    
    def __init__(self, redis_client: redis.Redis = None, 
                 embedding_service=None,
                 cache_policy: CachePolicy = CachePolicy.ADAPTIVE,
                 max_cache_size: int = 10000,
                 similarity_threshold: float = 0.85):
        
        self.redis_client = redis_client
        self.embedding_service = embedding_service
        self.cache_policy = cache_policy
        self.max_cache_size = max_cache_size
        self.similarity_threshold = similarity_threshold
        
        # In-memory cache for fast access
        self.cache_store: Dict[str, CacheEntry] = {}
        self.embedding_index: Dict[str, List[float]] = {}
        
        # Cache statistics
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "exact_hits": 0,
            "semantic_hits": 0,
            "total_requests": 0,
            "total_savings": 0.0
        }
        
        # Performance tracking
        self.response_times = []
        self.cost_savings = []
    
    async def get(self, query: str, context: Dict[str, Any] = None) -> Optional[CacheHit]:
        """
        Retrieve cached response for query
        Returns CacheHit if found, None if miss
        """
        start_time = time.time()
        self.cache_stats["total_requests"] += 1
        
        try:
            # Try exact match first
            exact_key = self._generate_exact_key(query, context)
            if exact_key in self.cache_store:
                entry = self.cache_store[exact_key]
                if await self._is_entry_valid(entry):
                    await self._update_entry_access(entry)
                    hit = CacheHit(
                        entry=entry,
                        similarity_score=1.0,
                        hit_type="exact",
                        response_time=time.time() - start_time
                    )
                    self.cache_stats["hits"] += 1
                    self.cache_stats["exact_hits"] += 1
                    return hit
            
            # Try semantic similarity match
            if self.embedding_service:
                semantic_hit = await self._find_semantic_match(query, context)
                if semantic_hit:
                    response_time = time.time() - start_time
                    semantic_hit.response_time = response_time
                    self.cache_stats["hits"] += 1
                    self.cache_stats["semantic_hits"] += 1
                    return semantic_hit
            
            # Cache miss
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get operation failed: {e}")
            return None
    
    async def put(self, query: str, response: Any, context: Dict[str, Any] = None,
                  ttl: Optional[timedelta] = None, cost: float = 0.0) -> bool:
        """
        Store response in cache
        """
        try:
            # Generate embedding for semantic similarity
            embedding = None
            if self.embedding_service:
                embedding = await self.embedding_service.generate_embedding(query)
            
            # Create cache entry
            entry = CacheEntry(
                key=self._generate_exact_key(query, context),
                value=response,
                embedding=embedding,
                metadata={
                    "query": query,
                    "context": context or {},
                    "response_type": type(response).__name__,
                    "response_size": len(str(response))
                },
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                ttl=ttl,
                cost=cost
            )
            
            # Store in cache
            await self._store_entry(entry)
            
            # Update embedding index
            if embedding:
                self.embedding_index[entry.key] = embedding
            
            # Update cost savings
            self.cache_stats["total_savings"] += cost
            
            logger.debug(f"Cached response for query: {query[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Cache put operation failed: {e}")
            return False
    
    async def _find_semantic_match(self, query: str, context: Dict[str, Any]) -> Optional[CacheHit]:
        """
        Find semantically similar cached response
        """
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            best_match = None
            best_similarity = 0.0
            
            # Search through embedding index
            for entry_key, cached_embedding in self.embedding_index.items():
                if entry_key not in self.cache_store:
                    continue
                
                entry = self.cache_store[entry_key]
                if not await self._is_entry_valid(entry):
                    continue
                
                # Calculate similarity
                similarity = self._cosine_similarity(query_embedding, cached_embedding)
                
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    # Apply context relevance filtering
                    if await self._is_context_relevant(entry, context):
                        best_similarity = similarity
                        best_match = entry
            
            if best_match:
                await self._update_entry_access(best_match)
                return CacheHit(
                    entry=best_match,
                    similarity_score=best_similarity,
                    hit_type="semantic",
                    response_time=0.0  # Will be set by caller
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Semantic match search failed: {e}")
            return None
    
    async def _is_entry_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid"""
        # Check TTL
        if entry.ttl:
            if datetime.now() - entry.created_at > entry.ttl:
                await self._remove_entry(entry.key)
                return False
        
        # Check relevance score (decay over time)
        if entry.relevance_score < 0.3:
            await self._remove_entry(entry.key)
            return False
        
        return True
    
    async def _is_context_relevant(self, entry: CacheEntry, context: Dict[str, Any]) -> bool:
        """Check if cached entry is relevant to current context"""
        if not context or not entry.metadata.get("context"):
            return True
        
        # Simple context matching - can be enhanced with more sophisticated logic
        entry_context = entry.metadata["context"]
        
        # Check for critical context mismatches
        critical_keys = ["user_id", "model_name", "security_level"]
        for key in critical_keys:
            if key in context and key in entry_context:
                if context[key] != entry_context[key]:
                    return False
        
        return True
    
    async def _update_entry_access(self, entry: CacheEntry):
        """Update entry access statistics"""
        entry.last_accessed = datetime.now()
        entry.access_count += 1
        
        # Update relevance score based on access pattern
        entry.relevance_score = self._calculate_relevance_score(entry)
    
    def _calculate_relevance_score(self, entry: CacheEntry) -> float:
        """Calculate relevance score for entry"""
        base_score = 1.0
        
        # Age decay
        age_hours = (datetime.now() - entry.created_at).total_seconds() / 3600
        age_decay = max(0.1, 1.0 - (age_hours / 24))  # Decay over 24 hours
        
        # Access frequency boost
        access_boost = min(2.0, 1.0 + (entry.access_count / 10))
        
        # Recency boost
        last_access_hours = (datetime.now() - entry.last_accessed).total_seconds() / 3600
        recency_boost = max(0.5, 1.0 - (last_access_hours / 12))  # Decay over 12 hours
        
        relevance_score = base_score * age_decay * access_boost * recency_boost
        return min(1.0, relevance_score)
    
    async def _store_entry(self, entry: CacheEntry):
        """Store entry in cache with eviction policy"""
        # Check cache size limit
        if len(self.cache_store) >= self.max_cache_size:
            await self._evict_entries()
        
        self.cache_store[entry.key] = entry
        
        # Store in Redis if available
        if self.redis_client:
            try:
                serialized_entry = pickle.dumps(entry)
                ttl_seconds = int(entry.ttl.total_seconds()) if entry.ttl else None
                await self.redis_client.setex(
                    f"cache:{entry.key}", 
                    ttl_seconds or 3600,  # Default 1 hour
                    serialized_entry
                )
            except Exception as e:
                logger.warning(f"Failed to store in Redis: {e}")
    
    async def _evict_entries(self):
        """Evict entries based on cache policy"""
        if self.cache_policy == CachePolicy.LRU:
            await self._evict_lru()
        elif self.cache_policy == CachePolicy.LFU:
            await self._evict_lfu()
        elif self.cache_policy == CachePolicy.TTL:
            await self._evict_expired()
        elif self.cache_policy == CachePolicy.ADAPTIVE:
            await self._evict_adaptive()
    
    async def _evict_lru(self):
        """Evict least recently used entries"""
        sorted_entries = sorted(
            self.cache_store.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove 10% of entries
        evict_count = max(1, len(sorted_entries) // 10)
        for key, _ in sorted_entries[:evict_count]:
            await self._remove_entry(key)
    
    async def _evict_lfu(self):
        """Evict least frequently used entries"""
        sorted_entries = sorted(
            self.cache_store.items(),
            key=lambda x: x[1].access_count
        )
        
        # Remove 10% of entries
        evict_count = max(1, len(sorted_entries) // 10)
        for key, _ in sorted_entries[:evict_count]:
            await self._remove_entry(key)
    
    async def _evict_expired(self):
        """Evict expired entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, entry in self.cache_store.items():
            if entry.ttl and current_time - entry.created_at > entry.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            await self._remove_entry(key)
    
    async def _evict_adaptive(self):
        """Adaptive eviction based on multiple factors"""
        # Score entries based on multiple factors
        entry_scores = []
        
        for key, entry in self.cache_store.items():
            score = self._calculate_eviction_score(entry)
            entry_scores.append((key, score))
        
        # Sort by score (lower score = more likely to evict)
        entry_scores.sort(key=lambda x: x[1])
        
        # Remove 10% of entries with lowest scores
        evict_count = max(1, len(entry_scores) // 10)
        for key, _ in entry_scores[:evict_count]:
            await self._remove_entry(key)
    
    def _calculate_eviction_score(self, entry: CacheEntry) -> float:
        """Calculate eviction score for entry (lower = more likely to evict)"""
        # Factors that make entry less likely to be evicted:
        # - High access count
        # - Recent access
        # - High cost (expensive to regenerate)
        # - High relevance score
        
        access_score = entry.access_count / 100.0  # Normalize
        recency_score = max(0, 1.0 - (datetime.now() - entry.last_accessed).total_seconds() / 3600)
        cost_score = min(1.0, entry.cost / 10.0)  # Normalize cost
        relevance_score = entry.relevance_score
        
        # Weighted combination
        total_score = (
            access_score * 0.3 +
            recency_score * 0.3 +
            cost_score * 0.2 +
            relevance_score * 0.2
        )
        
        return total_score
    
    async def _remove_entry(self, key: str):
        """Remove entry from cache"""
        if key in self.cache_store:
            del self.cache_store[key]
        
        if key in self.embedding_index:
            del self.embedding_index[key]
        
        # Remove from Redis
        if self.redis_client:
            try:
                await self.redis_client.delete(f"cache:{key}")
            except Exception as e:
                logger.warning(f"Failed to remove from Redis: {e}")
    
    def _generate_exact_key(self, query: str, context: Dict[str, Any] = None) -> str:
        """Generate exact cache key for query and context"""
        key_data = {
            "query": query,
            "context": context or {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = 0.0
        if self.cache_stats["total_requests"] > 0:
            hit_rate = self.cache_stats["hits"] / self.cache_stats["total_requests"]
        
        semantic_hit_rate = 0.0
        if self.cache_stats["hits"] > 0:
            semantic_hit_rate = self.cache_stats["semantic_hits"] / self.cache_stats["hits"]
        
        return {
            "cache_size": len(self.cache_store),
            "max_cache_size": self.max_cache_size,
            "hit_rate": round(hit_rate, 3),
            "semantic_hit_rate": round(semantic_hit_rate, 3),
            "total_requests": self.cache_stats["total_requests"],
            "total_hits": self.cache_stats["hits"],
            "total_misses": self.cache_stats["misses"],
            "exact_hits": self.cache_stats["exact_hits"],
            "semantic_hits": self.cache_stats["semantic_hits"],
            "total_cost_savings": round(self.cache_stats["total_savings"], 2),
            "average_response_time": round(
                np.mean(self.response_times) if self.response_times else 0, 3
            )
        }
    
    async def clear_cache(self):
        """Clear all cache entries"""
        self.cache_store.clear()
        self.embedding_index.clear()
        
        if self.redis_client:
            try:
                keys = await self.redis_client.keys("cache:*")
                if keys:
                    await self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Failed to clear Redis cache: {e}")
        
        logger.info("Cache cleared")

class IntelligentCacheOptimizer:
    """
    Intelligent cache optimization based on usage patterns
    """
    
    def __init__(self, cache_manager: SemanticCacheManager):
        self.cache_manager = cache_manager
        self.optimization_enabled = True
        self.optimization_interval = timedelta(hours=1)
        self.last_optimization = datetime.now()
    
    async def optimize_cache(self):
        """Run cache optimization"""
        if not self.optimization_enabled:
            return
        
        try:
            # Adjust similarity threshold based on hit rates
            await self._optimize_similarity_threshold()
            
            # Optimize cache size
            await self._optimize_cache_size()
            
            # Clean up stale entries
            await self._cleanup_stale_entries()
            
            self.last_optimization = datetime.now()
            logger.info("Cache optimization completed")
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
    
    async def _optimize_similarity_threshold(self):
        """Optimize similarity threshold based on performance"""
        stats = await self.cache_manager.get_cache_stats()
        
        # If hit rate is too low, lower threshold
        if stats["hit_rate"] < 0.3:
            self.cache_manager.similarity_threshold = max(0.7, self.cache_manager.similarity_threshold - 0.05)
        
        # If hit rate is too high with low semantic hit rate, raise threshold
        elif stats["hit_rate"] > 0.8 and stats["semantic_hit_rate"] < 0.2:
            self.cache_manager.similarity_threshold = min(0.95, self.cache_manager.similarity_threshold + 0.05)
    
    async def _optimize_cache_size(self):
        """Optimize cache size based on memory usage and performance"""
        # Implementation would depend on memory monitoring
        pass
    
    async def _cleanup_stale_entries(self):
        """Clean up stale entries based on access patterns"""
        current_time = datetime.now()
        stale_threshold = timedelta(days=7)
        
        stale_keys = []
        for key, entry in self.cache_manager.cache_store.items():
            if current_time - entry.last_accessed > stale_threshold:
                stale_keys.append(key)
        
        for key in stale_keys:
            await self.cache_manager._remove_entry(key)
        
        if stale_keys:
            logger.info(f"Cleaned up {len(stale_keys)} stale cache entries")
