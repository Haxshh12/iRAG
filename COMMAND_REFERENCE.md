# Command Reference Guide

## Interactive Commands

When running `python main_optimized.py`, you can use these commands:

### Help & Information

#### `help`
Show all available commands
```
Query> help
Commands:
  exit          - Exit the application
  stats         - Show cache statistics
  memory        - Show memory usage
  config        - Show performance config
  help          - Show this message
  clear         - Clear screen
```

#### `config`
Display current performance settings
```
Query> config
Performance Configuration:
  BATCH_EMBEDDING_SIZE:      10
  EMBEDDING_CACHE_SIZE:       1000
  MAX_WORKERS:                4
  QUERY_CACHE_TTL:            3600
  CACHE_MEMORY_LIMIT_MB:      100
  ENABLE_STREAMING:           True
  SPARSE_LOADING:             True
```

### Performance Monitoring

#### `stats`
Show cache performance statistics
```
Query> stats
Cache Statistics:
  Hits:     42
  Misses:   18
  Hit Rate: 70.0%
  Memory:   24.5MB
```

**What it means:**
- **Hits:** Queries answered from cache (instant)
- **Misses:** Unique queries requiring API call
- **Hit Rate:** % of queries from cache
- **Memory:** Current cache memory usage

**Target ranges:**
- Hit Rate: 30-50% (good), >70% (excellent)
- Memory: <50MB (low), <200MB (normal), >500MB (too much)

#### `memory`
Show system memory usage
```
Query> memory
Memory Monitoring:
  RSS:      95.2MB
  VMS:      312MB
  % System: 3.7%
```

**What it means:**
- **RSS:** Physical memory actually used
- **VMS:** Virtual memory (can be larger, don't worry)
- **% System:** Percentage of total system memory
- **Healthy:** < 10% system memory usage

### Cache & Data Operations

#### `clear`
Clear the terminal screen
```
Query> clear
[Terminal cleared]
```

### Exit & Cleanup

#### `exit`
Gracefully shut down the application
```
Query> exit
✓ Goodbye!

============================================================
  SESSION SUMMARY
============================================================
Cache Statistics:
  Hits:     42
  Misses:   18
  Hit Rate: 70.0%
  Memory:   24.5MB

Memory Monitoring:
  RSS:      95.2MB
  VMS:      312MB
  % System: 3.7%

✓ Thanks for using RAG-LLM!
```

The application:
1. Saves cache to disk
2. Displays final statistics
3. Cleans up resources
4. Exits gracefully

## Query Patterns

### Direct Questions
```
Query> What are the main topics in the articles?
```
Returns a synthesized answer based on article content.

### Specific Information
```
Query> How many articles mention machine learning?
```
Performs semantic search and counts results.

### Comparative Queries
```
Query> Compare topics A and B in the articles
```
Finds relevant sections and creates comparison.

### Complex Analysis
```
Query> What patterns do you see in the data regarding X?
```
Uses Gemini to analyze and identify patterns.

## Output Interpretation

### Response Flow

```
Query> Your question here
i️ ️Processing query...
Response: [Character streaming starts...]
The answer appears character by character...
✓ Query completed in 2.34s
Cache Statistics:
  Hits:     1
  Misses:   0
  Hit Rate: 100.0%
  Memory:   15.2MB
Query>
```

**Indicators explained:**
- `ℹ️  Processing query...` - API call in progress
- `✓ Query completed in 2.34s` - Success! Shows response time
- `Cache Statistics:` - Performance metrics
  - Hit Rate 100% = Answer was cached (very fast)
  - Hit Rate 0% = New query (first time)

### Error Messages

#### `❌ Error: API Key not found`
**Fix:** Create `.env` file with `GOOGLE_API_KEY=<key>`

#### `❌ Query failed: API Error`
**Fix:** Check API key validity at https://makersuite.google.com/app/apikey

#### `❌ Failed to load articles`
**Fix:** Ensure `data/medium.csv` exists

#### `⚠️  Removing X rows with failed embeddings`
**Normal:** System automatically handles bad embeddings

## Configuration Changes

### How to Modify Settings

1. **Edit `config.py`** before running:
```python
# Change any of these values
PerformanceConfig.MAX_WORKERS = 2         # Fewer parallel calls
PerformanceConfig.CACHE_MEMORY_LIMIT_MB = 50  # Less memory
PerformanceConfig.BATCH_EMBEDDING_SIZE = 5    # Smaller batches
```

2. **Run the system:**
```bash
python main_optimized.py
```

3. **Verify settings in interactive session:**
```
Query> config
# Should show your modified values
```

### Common Tuning Scenarios

**Scenario: "My computer is running slow"**
```python
PerformanceConfig.MAX_WORKERS = 2
PerformanceConfig.BATCH_EMBEDDING_SIZE = 5
```

**Scenario: "I want maximum speed"**
```python
PerformanceConfig.MAX_WORKERS = 8
PerformanceConfig.BATCH_EMBEDDING_SIZE = 20
```

**Scenario: "I want minimum memory usage"**
```python
PerformanceConfig.EMBEDDING_CACHE_SIZE = 100
PerformanceConfig.CACHE_MEMORY_LIMIT_MB = 25
PerformanceConfig.MAX_WORKERS = 1
```

**Scenario: "I keep getting API rate limits"**
```python
PerformanceConfig.MAX_WORKERS = 1  # Sequential
# Add delay in embeddings_optimized.py
```

## Performance Metrics

### Response Time Categories

| Time | Category | User Experience |
|------|----------|-----------------|
| < 1ms | Cached | Instant (magic) |
| 1-2s | API (fast) | Responsive |
| 2-5s | API (normal) | Acceptable |
| 5-10s | API (slow) | Noticeable wait |
| > 10s | API (very slow) | User frustrated |

**Quick optimization:**
- If most queries < 2s: You're good! ✅
- If most queries > 5s: Try `MAX_WORKERS = 8`
- If memory grows fast: Reduce `CACHE_MEMORY_LIMIT_MB`

### Cache Hit Rate Targets

| Hit Rate | Interpretation | Action |
|----------|----------------|--------|
| 0-10% | Each query unique | Normal for exploration |
| 10-40% | Some repetition | Good for typical use |
| 40-70% | Regular patterns | Very good! |
| 70%+ | Frequent repeats | Excellent! |

**Tips to improve hit rate:**
- Ask similar questions multiple times
- Use exact phrasing
- Build context through series of queries

## Troubleshooting Commands

### Verify System Health

1. **Start fresh test:**
```bash
python main_optimized.py
```

2. **Run command sequence:**
```
Query> config          # Show settings
Query> stats           # Show initial stats (should be 0/0)
Query> memory          # Show memory
Query> What is this data about?  # Simple query
Query> stats           # Stats should change
Query> What is this data about?  # Repeat query
Query> stats           # Should show cache hit
Query> exit            # Clean shutdown
```

### Debug Information

Enable verbose logging in `config.py`:
```python
# Add this for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
```

Then run and look for detailed logs:
```
DEBUG:config:PerformanceConfig loaded
DEBUG:cache:Cache hit for key: abc123...
DEBUG:embeddings:Batch embedding 10 texts...
```

### Check Specific Operations

**Test cache directly:**
```python
from cache import CacheManager
cm = CacheManager()
cm.set_query_cache("test_key", "test_value")
print(cm.get_query_cache("test_key"))  # Should print test_value
```

**Test embedding:**
```python
from embeddings_optimized import get_embedding
emb = get_embedding("sample text")
print(f"Embedding shape: {len(emb)}")  # Should be 768
```

**Test data loading:**
```python
from data_operations_optimized import load_articles_df
df = load_articles_df()
print(f"Loaded {len(df)} articles")
```

## API Interaction

### When Connected to API

The system makes API calls to Google Gemini when:
1. User asks a **new unique query**
2. Query **cache has expired** (default 1 hour)
3. Cache is **explicitly cleared**

### API Call Sequence

```
User Query
  ↓
Hash query text
  ↓
Check cache
  ↓ HIT (< 1ms)
Return cached result
  ↓
  ↓ MISS
Send to Google Gemini API
  ↓
Google processes query (5-10s)
  ↓
Stream response to user
  ↓
Cache result
  ↓
Return to user
```

### Cost Considerations (Free Tier)

- **Gemini Free:** 60 requests/minute
- **Cached query:** No API cost (instant)
- **Typical session:** 20-30 unique queries (~3 API calls due to caching)

**Cost optimization:**
- Use cache effectively (hit rate > 30%)
- Ask similar questions (builds cache)
- Batch similar topics together

## Advanced Usage

### Batch Query Mode (Custom)

Create `batch_queries.py`:
```python
from main_optimized import query_with_cache_and_stream, initialize_query_engine
from data_operations_optimized import load_articles_df

df = load_articles_df()
engine = initialize_query_engine(df)

queries = [
    "What is topic A?",
    "What is topic B?",
    "Compare A and B",
]

for q in queries:
    print(f"\nQ: {q}")
    query_with_cache_and_stream(q, engine)
```

Run: `python batch_queries.py`

### Real-Time Monitoring

While system is running in one terminal, open another:
```bash
python -c "
from cache import CacheManager
import time

cm = CacheManager()
while True:
    cm.print_stats()
    time.sleep(5)
    print('---')
"
```

This shows cache statistics updating in real-time as user queries!

## Summary

**Most Used Commands:**
1. **Any question** → Direct query
2. `stats` → Check cache performance
3. `memory` → Check system resources
4. `help` → Show all commands
5. `exit` → Quit gracefully

**Pro Tip:** Type `stats` between queries to watch cache hit rate improve! ⚡

---

**Last Updated:** 2024 | **System Version:** 1.0
