#!/usr/bin/env python3
"""
QUICK START GUIDE for RAG-LLM (Gemini Edition)
==============================================

Follow these exact steps in order!
"""

# STEP 1: Get API Key
# Go to: https://makersuite.google.com/app/apikey
# Sign in with Google → Click "Create API Key" → Copy value

# STEP 2: Create .env file
# Create file: D:\RAG\RAG-LLM\.env
# Add this line (replace with your actual key):
# GOOGLE_API_KEY=your_actual_key_here

# STEP 3: Activate virtual environment
# Run in PowerShell:
# venv\Scripts\Activate.ps1

# STEP 4: Install dependencies
# Run in PowerShell:
# pip install -r requirements-minimal.txt

# STEP 5: Validate setup
# Run in PowerShell:
# python check_config.py
# Should show: ✅ All checks passed!

# STEP 6: Run the application
# Run in PowerShell:
# python main.py

# STEP 7: Ask questions!
# Example questions:
# - What is machine learning?
# - Summarize the article about neural networks
# - What are the main topics covered?

# Type 'q' to quit

"""
TROUBLESHOOTING
===============

❌ "GOOGLE_API_KEY not found"
→ Check your .env file exists and has the right key

❌ Module errors
→ Run: pip install -r requirements-minimal.txt

❌ 'Text' column not found
→ Make sure data/medium.csv has a 'Text' column

❌ AttributeError in query
→ Verify your data/medium.csv has proper structure

💡 HINTS
========
- First run takes longer (creates embeddings)
- Cached embeddings in data/embedded_data.csv
- Type 'help' in chat for tips
- Run check_config.py anytime to validate setup
"""

print(__doc__)
