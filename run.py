#!/usr/bin/env python3
"""
Production runner for Intuitas AI
"""
import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import streamlit
        import langchain
        import google.generativeai
        print("✅ All requirements satisfied")
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has valid API key"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    try:
        from dotenv import load_dotenv
        import os
        import google.generativeai as genai
        
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found in .env file")
            return False
        
        # Test the API key
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Test")
        print("✅ Gemini API key configured and working")
        return True
        
    except Exception as e:
        print(f"❌ API key test failed: {str(e)}")
        return False

def main():
    """Main entry point"""
    print("🚀 Starting Intuitas AI...")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    print("✅ Environment ready")
    print("🌐 Starting Streamlit server...")
    
    # Run Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down Intuitas AI...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
