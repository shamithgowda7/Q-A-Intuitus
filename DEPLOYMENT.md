# 🚀 Intuitas AI - Production Deployment Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Make sure your `.env` file contains:

```
GEMINI_API_KEY=your-actual-gemini-api-key
```

### 3. Run the Application

```bash
# Option 1: Direct Streamlit
streamlit run app.py

# Option 2: Production runner (recommended)
python run.py
```

## 🎯 Features

### **Normal Mode**

- General purpose chat with Gemini AI
- Document-aware conversations (when document is loaded)
- Interactive chat interface with message history
- Smart suggestive prompts

### **Study Mode**

- Educational Q&A with structured answers
- Study-focused prompts and explanations
- Key points and examples generation
- Learning-optimized responses

### **Research Mode**

- Document upload and analysis (PDF, HTML, MD, TXT)
- RAG-powered document Q&A
- Source citation and references
- Research dashboard with analytics
- Advanced document processing

### **Journal Mode**

- Personal journaling interface
- Entry management and organization
- Future: AI-powered insights and summaries

## 🔧 Technical Features

- **RAG Pipeline**: FAISS vector store with Gemini embeddings
- **Multi-modal Support**: PDF, HTML, Markdown, and text files
- **Session Management**: Persistent chat history and document state
- **Error Handling**: Comprehensive error management and user feedback
- **Production Ready**: Optimized for deployment with proper configuration

## 📁 File Structure

```
rag-doc-assistant/
├── app.py                 # Main Streamlit application
├── run.py                 # Production runner script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys)
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── backend/
│   ├── rag_pipeline.py   # RAG processing logic
│   ├── document_loader.py # Document processing utilities
│   ├── vectorstore_handler.py # Vector store operations
│   └── utils.py          # Utility functions
├── frontend/
│   └── components.py     # UI components
├── data/
│   ├── uploads/          # Uploaded documents
│   └── processed/        # Processed vector stores
└── tests/
    └── test_pipeline.py  # Test suite
```

## 🌐 Deployment Options

### Local Development

```bash
streamlit run app.py
```

### Production Server

```bash
python run.py
```

### Docker (Future Enhancement)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.headless", "true"]
```

## 🔒 Security Notes

- Never commit `.env` file to version control
- Use environment variables for API keys in production
- Consider rate limiting for production deployments
- Implement user authentication for multi-user scenarios

## 📊 Performance Optimization

- Vector stores are cached locally for faster retrieval
- Document processing is optimized for large files
- Session state management reduces redundant API calls
- Error handling prevents application crashes

## 🎨 Customization

- Modify `app.py` for UI changes
- Update `backend/rag_pipeline.py` for AI model changes
- Customize `.streamlit/config.toml` for styling
- Add new modes by extending the main application logic

---

**Ready for production! 🚀**
