# Performance Configuration for RAG-LLM
# Tuning parameters for optimal resource usage

class PerformanceConfig:
    """High-performance configuration settings"""
    
    # ===== EMBEDDING OPTIMIZATION =====
    BATCH_EMBEDDING_SIZE = 10  # Process embeddings in batches
    EMBEDDING_CACHE_SIZE = 1000  # Max embeddings to keep in memory cache
    USE_EMBEDDING_CACHE = True  # Enable embedding caching
    
    # ===== MEMORY OPTIMIZATION =====
    SPARSE_LOADING = True  # Load data lazily, only what's needed
    DATAFRAME_CHUNK_SIZE = 100  # Process dataframe in chunks
    CLEANUP_INTERVAL = 50  # Clean memory every N queries
    
    # ===== CONCURRENCY =====
    MAX_WORKERS = 4  # Thread pool workers
    USE_ASYNC = True  # Enable async operations
    
    # ===== STREAMING & RESPONSE =====
    ENABLE_STREAMING = True  # Stream responses as they're generated
    STREAM_CHUNK_SIZE = 50  # Characters per stream chunk
    
    # ===== API OPTIMIZATION =====
    RETRY_BACKOFF = 1.5  # Exponential backoff multiplier
    TIMEOUT_SECONDS = 30  # API timeout
    CONNECTION_POOL_SIZE = 5  # Reuse connections
    
    # ===== SEARCH OPTIMIZATION =====
    TOP_K_RESULTS = 5  # Return top K relevant articles
    MIN_SIMILARITY_SCORE = 0.3  # Only return relevant results
    
    # ===== CACHING =====
    ENABLE_QUERY_CACHE = True  # Cache similar query results
    QUERY_CACHE_TTL = 3600  # Cache for 1 hour
    CACHE_MEMORY_LIMIT_MB = 100  # Max cache size
    
    # ===== LOGGING =====
    VERBOSE = False  # Less logging = better performance
    LOG_LEVEL = "WARNING"  # Only show errors/warnings
    
    @classmethod
    def to_dict(cls):
        """Convert config to dictionary"""
        return {key: getattr(cls, key) for key in dir(cls) 
                if not key.startswith('_') and key.isupper()}
    
    @classmethod
    def print_config(cls):
        """Display current configuration"""
        print("⚙️  Performance Configuration:")
        print("=" * 50)
        for key, value in cls.to_dict().items():
            print(f"  {key:<30} = {value}")
        print("=" * 50)
