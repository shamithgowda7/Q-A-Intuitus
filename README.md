# Intuitas AI - Intelligent Document Assistant

A production-ready AI-powered document analysis and Q&A system built with Streamlit, LangChain, and Google Gemini. Features multiple modes for different use cases including general chat, study assistance, research analysis, and journaling.

## Project Structure

```
rag-doc-assistant/
├── .env                     # Environment variables (API keys)
├── requirements.txt         # Python dependencies
├── app.py                  # Streamlit frontend entry point
├── backend/
│   ├── __init__.py
│   ├── rag_pipeline.py     # Core RAG pipeline logic
│   ├── document_loader.py  # Document processing utilities
│   ├── vectorstore_handler.py # Vector store operations
│   └── utils.py            # Utility functions
├── data/
│   ├── uploads/            # Uploaded documents
│   └── processed/          # Processed vector stores
├── frontend/
│   ├── __init__.py
│   └── components.py       # UI components
└── tests/
    └── test_pipeline.py    # Basic tests
```

## Setup Instructions

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys:**

   - Edit `.env` file
   - Add your OpenAI API key: `OPENAI_API_KEY="your-actual-key"`
   - Optionally add Gemini key: `GEMINI_API_KEY="your-gemini-key"`

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Usage

1. Upload a PDF, HTML, or Markdown document
2. The system will extract text and show a preview
3. Click "Build vectorstore from this document" to process it
4. Ask questions about the document content
5. Get AI-powered answers with source citations

## Features

- **Document Processing**: Supports PDF, HTML, and Markdown files
- **Text Chunking**: Intelligent text splitting for better retrieval
- **Vector Search**: FAISS-based similarity search
- **Source Citation**: Shows relevant document chunks used for answers
- **Streamlit UI**: Clean, interactive web interface

## Next Steps

- Swap to Gemini embeddings/LLM for different AI provider
- Add highlighting and follow-up chat memory
- Implement multi-file handling
- Add persistence with Chroma/Qdrant for production use

## Testing

Run the basic test:

```bash
pytest tests/test_pipeline.py
```

---

**Ready to hack! 🚀**
