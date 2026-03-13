import pandas as pd
from tools.embeddings import get_embedding, reduce_df
import os

embedded_articles_path = os.path.join("data", "embedded_data.csv")
original_articles_path = os.path.join("data", "medium.csv")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)


def _validate_csv_structure(df: pd.DataFrame) -> bool:
    '''
    Validate that the CSV has the required 'Text' column.
    '''
    if df is None or df.empty:
        print("❌ Error: DataFrame is empty!")
        return False
    
    if 'Text' not in df.columns:
        print(f"❌ Error: 'Text' column not found!")
        print(f"   Available columns: {df.columns.tolist()}")
        return False
    
    print(f"✓ CSV structure valid: {len(df)} rows, {len(df.columns)} columns")
    return True


def _modify_articles_df(articles_df: pd.DataFrame) -> pd.DataFrame:
    '''
    Create vector embeddings from the provided dataframe.
    The embeddings are created only for rows that don't exceed API limits.
    '''
    try:
        # Validate structure
        if not _validate_csv_structure(articles_df):
            return None
        
        # Reduce DataFrame
        print("🔄 Processing and reducing text...")
        articles_df = reduce_df(articles_df)
        if articles_df is None:
            print("❌ Error while processing DataFrame. Please check your data.")
            return None
        
        # Create embeddings
        print("🔄 Creating embeddings (this may take a while)...")
        articles_df['embedded_values'] = articles_df['Text'].apply(get_embedding)
        
        # Validate embeddings
        null_count = articles_df['embedded_values'].isnull().sum()
        if null_count > 0:
            print(f"⚠️ Warning: {null_count} rows have null embeddings. Removing them.")
            articles_df = articles_df[articles_df['embedded_values'].notna()]
        
        if articles_df.empty:
            print("❌ Error: No valid embeddings were created!")
            return None
        
        print(f"✓ Embeddings created for {len(articles_df)} articles")
        print("🔄 Saving to CSV...")
        articles_df.to_csv(embedded_articles_path, index=False)
        print(f"✓ Saved to {embedded_articles_path}")
        
    except Exception as e:
        print(f"❌ Error while modifying DataFrame: {str(e)}")
        return None
    
    return articles_df


def _load_and_prepare_csv() -> pd.DataFrame:
    '''
    Load CSV and apply embedding transformation.
    Follows DRY principle (Don't Repeat Yourself).
    '''
    try:
        if not os.path.isfile(original_articles_path):
            print(f"❌ Error: '{original_articles_path}' not found!")
            print("   Please ensure medium.csv exists in the data/ folder.")
            return None
        
        print(f"🔄 Loading '{original_articles_path}'...")
        articles_df = pd.read_csv(original_articles_path)
        print(f"✓ Loaded {len(articles_df)} articles")
        
        articles_df = _modify_articles_df(articles_df)
        return articles_df
        
    except Exception as e:
        print(f"❌ Error while loading CSV: {str(e)}")
        return None


def load_articles_df() -> pd.DataFrame:
    '''
    Load articles with embeddings. Uses cached embeddings if available.
    '''
    if os.path.isfile(embedded_articles_path):
        print(f"✓ Found existing embeddings at {embedded_articles_path}")
        response = input("Load cached embeddings? (Y/N) [default: Y]: ").strip().upper()
        
        if response != 'N':
            try:
                print("🔄 Loading cached embeddings...")
                articles_df = pd.read_csv(embedded_articles_path)
                print(f"✓ Loaded {len(articles_df)} articles from cache")
                return articles_df
            except Exception as e:
                print(f"⚠️ Error loading cache: {str(e)}. Creating new embeddings.")
    
    # Create new embeddings
    articles_df = _load_and_prepare_csv()
    return articles_df
