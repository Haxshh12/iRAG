from tools.prompts import instruction_str, prompt_template, context
from dotenv import load_dotenv
from llama_index.core.query_engine import PandasQueryEngine as pqe
from llama_index.core.tools import QueryEngineTool, ToolMetadata
import google.generativeai as genai
from data_operations import load_articles_df
import os
import sys

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Validate API Key on startup
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ CRITICAL ERROR: GOOGLE_API_KEY not found in .env file!")
    print("   Create a .env file with: GOOGLE_API_KEY=your_key_here")
    print("   Get your key from: https://makersuite.google.com/app/apikey")
    sys.exit(1)

if api_key == "your_api_key_here":
    print("❌ CRITICAL ERROR: GOOGLE_API_KEY is still the placeholder value!")
    print("   Please replace 'your_api_key_here' with your actual API key in .env")
    sys.exit(1)

# Configure Gemini API
try:
    genai.configure(api_key=api_key)
    print("✓ Gemini API configured successfully")
except Exception as e:
    print(f"❌ Error configuring Gemini API: {str(e)}")
    sys.exit(1)

def query_agent(articles_df):
    '''
    Create an interactive chat agent that queries Medium articles using Gemini.
    '''
    if articles_df is None:
        print("❌ No data available. Cannot start query agent.")
        return
    
    if len(articles_df) == 0:
        print("❌ DataFrame is empty. Cannot start query agent.")
        return
    
    try:
        print(f"✓ Initializing query engine with {len(articles_df)} articles...")
        
        # Initialize query engine
        articles_query_engine = pqe(df=articles_df, verbose=False, instruction_str=instruction_str)
        articles_query_engine.update_prompts({"pandas_prompt": prompt_template})
        
        articles_metadata = ToolMetadata(
            name="articles_data",
            description="Provides information about Medium articles. Use detailed questions.",
        )

        query_engine_tools = [
            QueryEngineTool(
                query_engine=articles_query_engine,
                metadata=articles_metadata,
            ),
        ]

        # Initialize Gemini model
        print("✓ Initializing Gemini model...")
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=context
        )
        chat = model.start_chat()
        
        print("\n" + "="*60)
        print("💬 RAG Chat System Ready!")
        print("="*60)
        print("Ask questions about the Medium articles.")
        print("Type 'q' to quit, 'help' for tips.\n")
        
        while True:
            try:
                prompt = input("You: ").strip()
                
                if prompt.lower() == 'q':
                    print("✓ Goodbye!")
                    break
                
                if prompt.lower() == 'help':
                    print("\n📚 Tips:")
                    print("  - Ask specific questions about the articles")
                    print("  - Use keywords from article titles or topics")
                    print("  - Type 'q' to quit\n")
                    continue
                
                if not prompt:
                    print("⚠️ Please enter a question.\n")
                    continue
                
                print("\n🔄 Processing...", end="", flush=True)
                
                try:
                    # Query the data
                    result = articles_query_engine.query(prompt)
                    
                    # Convert result to string (handle object response)
                    if hasattr(result, 'response'):
                        result_text = str(result.response)
                    elif isinstance(result, str):
                        result_text = result
                    else:
                        result_text = str(result)
                    
                    # Build context for Gemini
                    full_prompt = (
                        f"Article Context:\n{result_text}\n\n"
                        f"User Question: {prompt}\n\n"
                        f"Provide a concise, helpful answer based on the articles."
                    )
                    
                    # Get response from Gemini
                    response = chat.send_message(full_prompt)
                    print(f"\r✓ Done!\n\nAssistant: {response.text}\n")
                    
                except Exception as e:
                    error_msg = str(e)
                    if "API_KEY_INVALID" in error_msg:
                        print(f"\r❌\n❌ API Key Error: Invalid or expired.")
                        print("   Please update your GOOGLE_API_KEY in .env file.\n")
                        break
                    elif "RESOURCE_EXHAUSTED" in error_msg:
                        print(f"\r❌\n⚠️ Rate limit reached. Please wait a moment and try again.\n")
                    else:
                        print(f"\r❌\n⚠️ Error processing query: {error_msg}\n")
                        
            except KeyboardInterrupt:
                print("\n\n✓ Interrupted. Goodbye!")
                break
                
    except Exception as e:
        print(f"❌ Fatal error in query agent: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    '''
    Main entry point for the RAG application.
    '''
    try:
        print("🚀 RAG-LLM System Starting...")
        print("="*60)
        
        # Load articles
        print("📂 Loading articles...")
        articles_df = load_articles_df()
        
        if articles_df is None:
            print("❌ Failed to load articles. Exiting.")
            sys.exit(1)
        
        print(f"✓ Successfully loaded {len(articles_df)} articles\n")
        
        # Start query agent
        query_agent(articles_df)
        
    except KeyboardInterrupt:
        print("\n\n✓ Application interrupted by user.")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()