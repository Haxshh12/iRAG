import pandas as pd
import google.generativeai as genai
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file. Please set it up.")

genai.configure(api_key=api_key)

embedding_model = "models/embedding-001"
max_tokens = 8000
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def split_text(text: str) -> List[str]:
    """
    Split the text into chunks based on character limit.
    """
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
        return [t for t in texts if t.strip()]  # Filter empty strings
    except Exception as e:
        print(f"⚠️ Error while splitting text: {str(e)}")
        return [text] if text.strip() else []


def reduce_df(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    This method ensures that the request sent to Gemini API will not exceed its limit.
    If a row exceeds the token limit, it splits the text into chunks.
    Uses simple character-based estimation instead of tiktoken.
    """
    if df is None or df.empty:
        print("⚠️ DataFrame is empty!")
        return None
    
    if 'Text' not in df.columns:
        print("❌ Error: 'Text' column not found in DataFrame. Available columns:", df.columns.tolist())
        return None
    
    try:
        # Simple character-based token estimation (1 token ≈ 4 characters)
        df["char_count"] = df["Text"].fillna("").apply(lambda x: len(str(x)))
        
        new_rows = []
        for index, row in df.iterrows():
            text = row.get("Text", "")
            if pd.isna(text) or text == "":
                print(f"⚠️ Skipping row {index}: empty text")
                continue
                
            if row["char_count"] > max_tokens * 4:  # Rough estimate: 1 token ≈ 4 chars
                texts = split_text(str(text))
                for split_text_chunk in texts:
                    new_row = row.copy()
                    new_row["Text"] = split_text_chunk
                    new_rows.append(new_row)
            else:
                new_rows.append(row)
        
        if not new_rows:
            print("❌ No valid rows after processing!")
            return None
        
        new_df = pd.DataFrame(new_rows)
        new_df.drop(columns=["char_count"], inplace=True)
        print(f"✓ DataFrame reduced from {len(df)} to {len(new_df)} rows")
        return new_df
    except Exception as e:
        print(f"❌ Error while reducing DataFrame: {str(e)}")
        return None


def get_embedding(text: str, model: str = "models/embedding-001") -> Optional[List]:
    """
    Create embedding for a single string using Google Gemini API with retry logic.
    Returns None if embedding fails after max retries.
    """
    if not text or len(str(text).strip()) == 0:
        print("⚠️ Warning: Empty text provided for embedding")
        return None
    
    for attempt in range(MAX_RETRIES):
        try:
            text_clean = str(text).replace("\n", " ").strip()
            result = genai.embed_content(
                model=model,
                content=text_clean,
                task_type="RETRIEVAL_DOCUMENT"
            )
            emb = result.get('embedding')
            if emb:
                return emb
            else:
                print(f"⚠️ Attempt {attempt + 1}/{MAX_RETRIES}: No embedding returned")
        except Exception as e:
            error_msg = str(e)
            if attempt < MAX_RETRIES - 1:
                print(f"⚠️ Attempt {attempt + 1}/{MAX_RETRIES} failed: {error_msg}. Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ Failed to create embedding after {MAX_RETRIES} attempts: {error_msg}")
    
    return None