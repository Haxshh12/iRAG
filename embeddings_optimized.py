"""
High-performance embeddings with async support and batching
"""

import pandas as pd
import google.generativeai as genai
from typing import List, Optional, Callable
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import PerformanceConfig
from cache import CacheManager

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file. Please set it up.")

genai.configure(api_key=api_key)

embedding_model = "models/embedding-001"
max_tokens = 8000

# Global cache instance
embedding_cache = CacheManager(max_memory_mb=50) if PerformanceConfig.USE_EMBEDDING_CACHE else None


def split_text(text: str) -> List[str]:
    """Split the text into chunks based on character limit."""
    if not text or len(text.strip()) == 0:
        return []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=8050, 
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    try:
        texts = text_splitter.split_text(text)
        return [t for t in texts if t.strip()]
    except Exception as e:
        if not PerformanceConfig.VERBOSE:
            return [text] if text.strip() else []
        print(f"⚠️ Error splitting text: {str(e)}")
        return [text] if text.strip() else []


def reduce_df(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Reduce dataframe with character-based token estimation."""
    if df is None or df.empty:
        if PerformanceConfig.VERBOSE:
            print("⚠️ DataFrame is empty!")
        return None
    
    if 'Text' not in df.columns:
        print(f"❌ Error: 'Text' column not found. Available: {df.columns.tolist()}")
        return None
    
    try:
        # Character-based token estimation
        df["char_count"] = df["Text"].fillna("").apply(lambda x: len(str(x)))
        
        new_rows = []
        for index, row in df.iterrows():
            text = row.get("Text", "")
            if pd.isna(text) or text == "":
                if PerformanceConfig.VERBOSE:
                    print(f"⚠️ Skipping row {index}: empty")
                continue
                
            if row["char_count"] > max_tokens * 4:
                texts = split_text(str(text))
                for split_chunk in texts:
                    new_row = row.copy()
                    new_row["Text"] = split_chunk
                    new_rows.append(new_row)
            else:
                new_rows.append(row)
        
        if not new_rows:
            print("❌ No valid rows!")
            return None
        
        new_df = pd.DataFrame(new_rows)
        new_df.drop(columns=["char_count"], inplace=True)
        print(f"✓ Processed {len(df)} → {len(new_df)} rows")
        return new_df
    except Exception as e:
        print(f"❌ Error reducing DataFrame: {str(e)}")
        return None


def get_embedding(text: str, model: str = "models/embedding-001") -> Optional[List]:
    """
    Get embedding with caching support.
    """
    if not text or len(str(text).strip()) == 0:
        return None
    
    # Check cache first
    if embedding_cache:
        cached = embedding_cache.get_embedding_cache(text)
        if cached:
            return cached
    
    text_clean = str(text).replace("\n", " ").strip()
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            result = genai.embed_content(
                model=model,
                content=text_clean,
                task_type="RETRIEVAL_DOCUMENT"
            )
            emb = result.get('embedding')
            
            if emb:
                # Cache the embedding
                if embedding_cache:
                    embedding_cache.set_embedding_cache(text, emb)
                return emb
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                if PerformanceConfig.VERBOSE:
                    print(f"❌ Embedding failed: {str(e)}")
    
    return None


def batch_embed(texts: List[str], progress_callback: Optional[Callable] = None) -> List[Optional[List]]:
    """
    Batch embedding with threading for high performance.
    """
    embeddings = []
    
    if PerformanceConfig.MAX_WORKERS > 1:
        # Use thread pool for concurrent API calls
        with ThreadPoolExecutor(max_workers=PerformanceConfig.MAX_WORKERS) as executor:
            futures = {executor.submit(get_embedding, text): text for text in texts}
            
            for i, future in enumerate(as_completed(futures)):
                embeddings.append(future.result())
                if progress_callback:
                    progress_callback(i + 1, len(texts))
    else:
        # Sequential processing
        for i, text in enumerate(texts):
            embeddings.append(get_embedding(text))
            if progress_callback:
                progress_callback(i + 1, len(texts))
    
    return embeddings
