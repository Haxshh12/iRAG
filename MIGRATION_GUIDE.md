# Migration Guide: OpenAI to Gemini

This document outlines the changes made to migrate from OpenAI to Google Gemini API.

## What Changed

### 1. Dependencies
**Removed:**
- `openai` - OpenAI Python client
- `llama-index-agent-openai` - OpenAI-specific agent
- `llama-index-embeddings-openai` - OpenAI embeddings
- `llama-index-llms-openai` - OpenAI LLM integration
- `tiktoken` - OpenAI tokenizer (needs Rust compiler)

**Added:**
- `google-generativeai` - Gemini API client

### 2. API Key Configuration
**Before (OpenAI):**
```
OPENAI_API_KEY=sk-...
```

**After (Gemini):**
```
GOOGLE_API_KEY=AIza...
```

Get your free key: https://makersuite.google.com/app/apikey

### 3. Embedding Model
**Before:**
```python
from openai import OpenAI
client = OpenAI(api_key=...)
embedding = client.embeddings.create(
    input=text,
    model="text-embedding-3-large"
)
```

**After:**
```python
import google.generativeai as genai
genai.configure(api_key=...)
result = genai.embed_content(
    content=text,
    model="models/embedding-001",
    task_type="RETRIEVAL_DOCUMENT"
)
```

### 4. LLM Model
**Before:**
```python
from llama_index.llms.openai import OpenAI
llm = OpenAI(model="gpt-4", temperature=0.1)
agent = ReActAgent.from_tools(tools, llm=llm)
```

**After:**
```python
import google.generativeai as genai
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=context
)
chat = model.start_chat()
response = chat.send_message(prompt)
```

### 5. Token Counting
**Before:**
```python
import tiktoken
encoding = tiktoken.get_encoding("cl100k_base")
tokens = len(encoding.encode(text))
```

**After:**
```python
# Simple character-based estimation
tokens_estimate = len(text) // 4  # 1 token ≈ 4 characters
```

## Improvements Made

### ✅ Resilience Features Added
1. **Startup Validation**
   - Checks API key is valid on startup
   - Validates all required files exist
   - Confirms data structure before processing

2. **Retry Logic**
   - Automatic retries for failed API calls
   - Exponential backoff to prevent rate limiting
   - Graceful degradation on persistent failures

3. **Better Error Messages**
   - Clear, actionable error descriptions
   - Guidance on how to fix issues
   - Progress indicators during long operations

4. **Data Validation**
   - Checks for required 'Text' column
   - Handles NULL/empty values
   - Validates CSV structure before processing

### 🎯 Performance Optimization
1. **Removed Heavy Dependencies**
   - No more matplotlib/Gradio bloat
   - Faster installation (no compilation needed)
   - Smaller memory footprint

2. **Smarter Text Processing**
   - Character-based token estimation (no Rust compiler needed)
   - Better text chunking preservation
   - Reduced API call overhead

### 🛠️ New Tools
1. **Configuration Checker** (`check_config.py`)
   - Validates entire setup before running
   - Diagnoses common issues
   - Clear remediation steps

2. **Comprehensive Documentation**
   - Detailed README with troubleshooting
   - This migration guide
   - Inline code comments

## Cost Comparison

### OpenAI (GPT-4)
- Embeddings: $0.02 per 1M tokens
- Query: $0.03 per 1K tokens (input) + $0.06 per 1K tokens (output)
- **Annual cost for 10,000 queries: ~$500+**

### Google Gemini (Free Tier)
- Embeddings: FREE (60 req/min)
- Generative: FREE (15 req/min)
- **Annual cost for 10,000 queries: $0** (until you exceed free tier)

## Steps to Upgrade

If you're upgrading from the old OpenAI version:

### 1. Backup Your Data
```bash
cp data/embedded_data.csv data/embedded_data.csv.backup
```

### 2. Get New Dependencies
```bash
pip uninstall -y openai tiktoken llama-index-agent-openai llama-index-llms-openai llama-index-embeddings-openai
pip install -r requirements-minimal.txt
```

### 3. Update .env
```bash
# Old
OPENAI_API_KEY=sk-...

# New
GOOGLE_API_KEY=AIza...
```

### 4. Re-generate Embeddings
```bash
rm data/embedded_data.csv  # Optional: regenerate embeddings
python main.py
```

### 5. Validate Setup
```bash
python check_config.py
```

## API Limits & Rate Limiting

### Gemini Free Tier
- Embeddings: 60 requests per minute
- Generative models: 15 requests per minute

The system automatically:
- Detects rate limiting errors
- Waits before retrying (exponential backoff)
- Informs you if limits are exceeded

### Upgrading to Paid Tier
When ready to scale, enable billing in Google Cloud Console for higher limits.

## Rollback (if needed)

If you need to go back to OpenAI:

```bash
git checkout requirements.txt main.py data_operations.py tools/
pip install -r requirements.txt
```

## FAQ

**Q: Is Gemini API truly free?**
A: Yes, with generous free tier (60 req/min for embeddings, 15 req/min for generative). No billing required unless you exceed these limits.

**Q: Will my old embeddings still work?**
A: No, embeddings from OpenAI are incompatible with Gemini. You'll need to regenerate them using `python main.py`.

**Q: Can I use the old `requirements.txt`?**
A: Not recommended. Use `requirements-minimal.txt` which has correct dependencies.

**Q: Do I need Rust compiler?**
A: No! The new version doesn't require Rust, making setup much simpler.

**Q: What if I exceed the free tier?**
A: The system will inform you with a clear error. You can either wait for the rate limit window to reset or enable paid tier.

## Support

- Configuration issues? Run `python check_config.py`
- Need help? Check the README.md for troubleshooting
- Have questions? Review the inline code comments

Happy migrating! 🚀
