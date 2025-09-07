# 🚀 Quick Setup Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure API Keys

### Option A: Using OpenAI (Recommended for testing)

1. Get your OpenAI API key from: https://platform.openai.com/api-keys
2. Open the `.env` file in your project
3. Replace `"your-openai-key"` with your actual key:
   ```
   OPENAI_API_KEY="sk-your-actual-openai-key-here"
   ```

### Option B: Using Gemini

1. Get your Gemini API key from: https://makersuite.google.com/app/apikey
2. Open the `.env` file in your project
3. Replace `"your-gemini-key"` with your actual key:
   ```
   GEMINI_API_KEY="your-actual-gemini-key-here"
   ```

## Step 3: Test Your Configuration

```bash
python test_keys.py
```

This will verify your API keys are loaded correctly.

## Step 4: Run the Application

```bash
streamlit run app.py
```

## 🔧 Troubleshooting

### If you get "API Key not configured" error:

1. Make sure your `.env` file is in the project root directory
2. Check that your API key doesn't have extra spaces or quotes
3. Run `python test_keys.py` to debug

### If you get import errors:

1. Make sure you installed all dependencies: `pip install -r requirements.txt`
2. Check that you're in the correct directory

### Example .env file:

```
# Copy your keys here (do NOT commit to git)
OPENAI_API_KEY="sk-proj-abc123def456..."
GEMINI_API_KEY="AIzaSyBvOkBwqLrJh..."
```

## 🎯 Ready to Test!

Once your keys are configured, you can:

1. Upload a PDF, HTML, or Markdown document
2. Extract and preview the text
3. Build a vector store
4. Ask questions and get AI-powered answers!

---

**Need help?** Check the main README.md for more details.
