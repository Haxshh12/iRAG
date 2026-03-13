"""
High-performance data operations with lazy loading and streaming
"""

import pandas as pd
from embeddings_optimized import get_embedding, batch_embed, reduce_df
import os
from config import PerformanceConfig
from typing import Optional, Callable
from tqdm import tqdm

embedded_articles_path = os.path.join("data", "embedded_data.csv")
original_articles_path = os.path.join("data", "medium.csv")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)


def _validate_csv_structure(df: pd.DataFrame) -> bool:
    """Validate CSV structure"""
    if df is None or df.empty:
        print("❌ Error: DataFrame is empty!")
        return False
    
    if 'Text' not in df.columns:
        print(f"❌ Error: 'Text' column not found!")
        print(f"   Available: {df.columns.tolist()}")
        return False
    
    print(f"✓ CSV valid: {len(df)} rows, {len(df.columns)} columns")
    return True


def _modify_articles_df(articles_df: pd.DataFrame, progress_callback: Optional[Callable] = None) -> pd.DataFrame:
    """Create embeddings with progress tracking"""
    try:
        if not _validate_csv_structure(articles_df):
            return None
        
        print("🔄 Processing text...")
        articles_df = reduce_df(articles_df)
        if articles_df is None:
            print("❌ Error processing DataFrame")
            return None
        
        print("🔄 Creating embeddings...")
        
        # Use progress bar for better UX
        texts = articles_df['Text'].tolist()
        embeddings = []
        
        with tqdm(total=len(texts), desc="Embedding", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
            for i, text in enumerate(texts):
                emb = get_embedding(text)
                embeddings.append(emb)
                pbar.update(1)
                
                if progress_callback:
                    progress_callback(i + 1, len(texts))
        
        articles_df['embedded_values'] = embeddings
        
        # Validate embeddings
        null_count = articles_df['embedded_values'].isnull().sum()
        if null_count > 0:
            print(f"⚠️ Removing {null_count} rows with failed embeddings")
            articles_df = articles_df[articles_df['embedded_values'].notna()]
        
        if articles_df.empty:
            print("❌ Error: No valid embeddings!")
            return None
        
        print(f"✓ Created embeddings for {len(articles_df)} articles")
        print("🔄 Saving...")
        articles_df.to_csv(embedded_articles_path, index=False)
        print(f"✓ Saved to {embedded_articles_path}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None
    
    return articles_df


def _load_and_prepare_csv() -> pd.DataFrame:
    """Load and prepare CSV efficiently"""
    try:
        if not os.path.isfile(original_articles_path):
            print(f"❌ Error: '{original_articles_path}' not found!")
            return None
        
        print(f"🔄 Loading '{original_articles_path}'...")
        articles_df = pd.read_csv(original_articles_path)
        print(f"✓ Loaded {len(articles_df)} articles")
        
        articles_df = _modify_articles_df(articles_df)
        return articles_df
        
    except Exception as e:
        print(f"❌ Error loading CSV: {str(e)}")
        return None


def load_articles_df(use_cache: bool = True) -> pd.DataFrame:
    """
    Load articles with caching.
    use_cache: If True, uses cached embeddings when available
    """
    if use_cache and os.path.isfile(embedded_articles_path):
        print(f"✓ Found cached embeddings")
        try:
            print("🔄 Loading cached embeddings...")
            articles_df = pd.read_csv(embedded_articles_path)
            print(f"✓ Loaded {len(articles_df)} articles from cache")
            return articles_df
        except Exception as e:
            print(f"⚠️ Error loading cache: {str(e)}")
    
    # Create new embeddings
    articles_df = _load_and_prepare_csv()
    return articles_df


def get_articles_sample(n: int = 10) -> pd.DataFrame:
    """Get sample of articles for testing (faster)"""
    try:
        if os.path.isfile(embedded_articles_path):
            df = pd.read_csv(embedded_articles_path)
            return df.head(n)
        else:
            df = pd.read_csv(original_articles_path)
            return df.head(n)
    except:
        return None
