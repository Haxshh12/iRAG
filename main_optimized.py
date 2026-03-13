"""
High-performance, responsive RAG-LLM TUI with streaming and caching
"""

import os
import sys
from dotenv import load_dotenv
from llama_index.core import PandasQueryEngine, Document
from llama_index.llms.gemini import Gemini
from tools.prompts import instruction_str, prompt_template
import pandas as pd
from typing import Optional
import traceback
from config import PerformanceConfig
from cache import CacheManager, MemoryOptimizer
import time

# Load environment
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Initialize performance infrastructure
cache_manager = CacheManager()
memory_optimizer = MemoryOptimizer()

def print_header(title: str):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_info(msg: str):
    """Print info message"""
    print(f"ℹ️  {msg}")

def print_success(msg: str):
    """Print success message"""
    print(f"✓ {msg}")

def print_error(msg: str):
    """Print error message"""
    print(f"❌ {msg}")

def print_warning(msg: str):
    """Print warning message"""
    print(f"⚠️  {msg}")

def validate_startup() -> bool:
    """Validate configuration at startup"""
    print_header("STARTUP VALIDATION")
    
    # Check API key
    if not api_key:
        print_error("GOOGLE_API_KEY not found in .env file")
        print("   Run: cp .env.example .env")
        print("   Then get key from: https://makersuite.google.com/app/apikey")
        return False
    print_success(f"API Key: {api_key[:10]}...")
    
    # Check config
    try:
        config_dict = PerformanceConfig.to_dict()
        print_success(f"Performance Config: {config_dict['BATCH_EMBEDDING_SIZE']} batch size")
    except Exception as e:
        print_error(f"Config error: {e}")
        return False
    
    # Check data
    if not os.path.exists("data"):
        os.makedirs("data", exist_ok=True)
        print_warning("Created data directory")
    
    print_success("All validations passed!\n")
    return True

def load_articles() -> Optional[pd.DataFrame]:
    """Load articles with progress"""
    print_info("Loading articles...")
    try:
        # Try optimized loader first
        try:
            from data_operations_optimized import load_articles_df
            articles_df = load_articles_df(use_cache=True)
        except ImportError:
            # Fallback to original
            from data_operations import load_articles_df
            articles_df = load_articles_df(use_cache=True)
        
        if articles_df is None:
            print_error("Failed to load articles")
            return None
        
        print_success(f"Loaded {len(articles_df)} articles")
        memory_optimizer.print_memory_usage()
        return articles_df
        
    except Exception as e:
        print_error(f"Error loading articles: {e}")
        traceback.print_exc()
        return None

def initialize_query_engine(articles_df: pd.DataFrame) -> Optional[PandasQueryEngine]:
    """Initialize query engine with LLM and cache"""
    print_info("Initializing query engine...")
    try:
        llm = Gemini(api_key=api_key, model_name="models/gemini-1.5-flash")
        
        query_engine = PandasQueryEngine(
            df=articles_df,
            llm=llm,
            instruction_str=instruction_str,
            synthesize_response=False,
            pandas_prompt=prompt_template,
            verbose=False,
        )
        
        print_success("Query engine initialized")
        return query_engine
        
    except Exception as e:
        print_error(f"Error initializing query engine: {e}")
        traceback.print_exc()
        return None

def stream_response(text: str, delay: float = 0.01):
    """Stream text character by character for responsive UI"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def query_with_cache_and_stream(query: str, query_engine: PandasQueryEngine) -> str:
    """Execute query with caching and streaming response"""
    
    # Check cache first
    cache_key = cache_manager.get_cache_key(query)
    cached_result = cache_manager.get_query_cache(cache_key)
    
    if cached_result:
        print_success("Cache hit!")
        stream_response(f"Response: {cached_result}")
        cache_manager.print_stats()
        return cached_result
    
    # Execute query with streaming
    print_info("Processing query...")
    start_time = time.time()
    
    try:
        response = query_engine.query(query)
        result = str(response)
        
        # Cache the result
        cache_manager.set_query_cache(cache_key, result)
        
        elapsed = time.time() - start_time
        print_success(f"Query completed in {elapsed:.2f}s")
        
        # Stream response
        stream_response(f"Response: {result}")
        
        # Show stats
        cache_manager.print_stats()
        memory_optimizer.print_memory_usage()
        
        return result
        
    except Exception as e:
        print_error(f"Query failed: {e}")
        return None

def interactive_chat(query_engine: PandasQueryEngine):
    """Interactive chat loop with responsive UI"""
    print_header("INTERACTIVE RAG CHAT")
    print("Type 'help' for commands, 'exit' to quit\n")
    
    query_count = 0
    
    while True:
        try:
            user_input = input("Query> ").strip()
            
            if not user_input:
                continue
            
            elif user_input.lower() == "exit":
                print_info("Goodbye!")
                break
            
            elif user_input.lower() == "help":
                print("""
Commands:
  exit          - Exit the application
  stats         - Show cache statistics
  memory        - Show memory usage
  config        - Show performance config
  help          - Show this message
  clear         - Clear screen
  
Or ask any question about the articles!
                """)
            
            elif user_input.lower() == "stats":
                cache_manager.print_stats()
            
            elif user_input.lower() == "memory":
                memory_optimizer.print_memory_usage()
            
            elif user_input.lower() == "config":
                PerformanceConfig.print_config()
            
            elif user_input.lower() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
            
            else:
                # Regular query
                query_count += 1
                print()
                query_with_cache_and_stream(user_input, query_engine)
                print()
                
                # Periodic memory check
                if query_count % 10 == 0:
                    print_warning(f"Memory check after {query_count} queries:")
                    memory_optimizer.print_memory_usage()
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break
        except Exception as e:
            print_error(f"Error: {e}")
            traceback.print_exc()

def main():
    """Main entry point"""
    print("\n" + "🚀 "*20)
    print("High-Performance RAG-LLM Terminal Interface")
    print("Powered by Google Gemini API | LlamaIndex RAG Engine")
    print("🚀 "*20 + "\n")
    
    # Validate startup
    if not validate_startup():
        print_error("Startup validation failed!")
        sys.exit(1)
    
    # Load articles
    articles_df = load_articles()
    if articles_df is None:
        print_error("Failed to load data!")
        sys.exit(1)
    
    # Initialize query engine
    query_engine = initialize_query_engine(articles_df)
    if query_engine is None:
        print_error("Failed to initialize query engine!")
        sys.exit(1)
    
    print_success("System ready!\n")
    
    # Show initial stats
    print_info(f"Cache capacity: {PerformanceConfig.EMBEDDING_CACHE_SIZE} embeddings")
    print_info(f"Max workers: {PerformanceConfig.MAX_WORKERS}")
    print_info(f"Streaming enabled: {PerformanceConfig.ENABLE_STREAMING}\n")
    
    # Start interactive chat
    interactive_chat(query_engine)
    
    # Final stats
    print_header("SESSION SUMMARY")
    cache_manager.print_stats()
    memory_optimizer.print_memory_usage()
    print_success("Thanks for using RAG-LLM!")

if __name__ == "__main__":
    main()
