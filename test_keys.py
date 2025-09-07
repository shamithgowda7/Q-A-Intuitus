#!/usr/bin/env python3
"""
Test script to verify API keys are loaded correctly from .env file
Run this before starting the main application to ensure your keys are working.
"""

from dotenv import load_dotenv
import os
import google.generativeai as genai

def test_api_keys():
    """Test if API keys are properly loaded from .env file"""
    print("🔑 Testing API Key Configuration...")
    print("=" * 50)
    
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # Get the API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        print(f"Gemini Key: ✅ Found")
        print(f"   Key starts with: {api_key[:10]}...")
        
        # Configure Gemini with API key
        genai.configure(api_key=api_key)
        
        # Test the API key by making a simple request
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello, Gemini!")
        print("✅ Gemini API key is configured and working! You can run the app.")
        print(f"   Test response: {response.text[:50]}...")
        return True
        
    except ValueError as e:
        print(f"❌ Configuration Error: {str(e)}")
        print("\n📝 To fix this:")
        print("1. Open the .env file")
        print("2. Add your Gemini API key: GEMINI_API_KEY=your-actual-key")
        print("3. Get your key from: https://makersuite.google.com/app/apikey")
        return False
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        print("   The API key might be invalid or there's a network issue.")
        return False

if __name__ == "__main__":
    test_api_keys()
