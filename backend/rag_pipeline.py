# backend/rag_pipeline.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from sentence_transformers import SentenceTransformer

# Load environment variables and configure Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Configure Gemini with API key
genai.configure(api_key=api_key)

# Use SentenceTransformers for embeddings (no cloud credentials needed)
from langchain.embeddings.base import Embeddings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import ssl

class LocalEmbeddings(Embeddings):
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalEmbeddings, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            try:
                # Try to load the model with proper parameters
                ssl._create_default_https_context = ssl._create_unverified_context
                
                # First try to load from Hugging Face with proper parameters
                self.model = SentenceTransformer(
                    "sentence-transformers/all-MiniLM-L6-v2",
                    trust_remote_code=True
                )
                print("✅ SentenceTransformer model loaded successfully from Hugging Face")
            except Exception as e:
                print(f"⚠️ Failed to load from Hugging Face: {e}")
                try:
                    # Try to load from local cache if available
                    local_model = r"C:\Users\PREETHI H M\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2"
                    self.model = SentenceTransformer(
                        local_model,
                        trust_remote_code=True
                    )
                    print("✅ SentenceTransformer model loaded successfully from local cache")
                except Exception as e2:
                    print(f"⚠️ Failed to load from local cache: {e2}")
                    print("🔄 Falling back to simple TF-IDF embeddings...")
                    self.model = None
                    self._init_tfidf()
            
            self._initialized = True
    
    def _init_tfidf(self):
        """Fallback to TF-IDF if SentenceTransformer fails"""
        self.tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
        self.fitted = False
    
    def embed_documents(self, texts):
        if self.model:
            return self.model.encode(texts).tolist()
        else:
            # TF-IDF fallback
            if not self.fitted:
                self.tfidf.fit(texts)
                self.fitted = True
            return self.tfidf.transform(texts).toarray().tolist()
    
    def embed_query(self, text):
        if self.model:
            return self.model.encode([text]).tolist()[0]
        else:
            # TF-IDF fallback
            if not self.fitted:
                return [0.0] * 1000
            return self.tfidf.transform([text]).toarray().tolist()[0]

# Create a global embeddings instance to avoid multiple initializations
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = LocalEmbeddings()
    return _embeddings

def build_and_persist_vectorstore(texts, persist_dir="data/processed/vectorstore"):
    os.makedirs(persist_dir, exist_ok=True)
    # Chunk
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = []
    for t in texts:
        docs.extend(splitter.split_text(t))

    # Use local embeddings to avoid cloud credentials
    embeddings = get_embeddings()
    vs = FAISS.from_texts(docs, embeddings)
    vs.save_local(persist_dir)
    return persist_dir


def load_vectorstore_and_qa(persist_dir="data/processed/vectorstore"):
    # Loads FAISS vectorstore and returns a tiny QA wrapper with Gemini
    # Use local embeddings to avoid cloud credentials
    embeddings = get_embeddings()
    vs = FAISS.load_local(persist_dir, embeddings, allow_dangerous_deserialization=True)
    retriever = vs.as_retriever(search_kwargs={"k": 4})

    # Chat model (Gemini) - using direct SDK
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    
    # Custom QA wrapper for direct Gemini integration
    class DirectGeminiQA:
        def __init__(self, model, retriever):
            self.model = model
            self.retriever = retriever
        
        def run(self, query):
            docs = self.retriever.invoke(query)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            prompt = f"""
            Based on the following context, please answer the question. If the answer is not in the context, say so.
            
            Context:
            {context}
            
            Question: {query}
            
            Answer:
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        
        def run_with_sources(self, query):
            docs = self.retriever.invoke(query)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            prompt = f"""
            Based on the following context, please answer the question. If the answer is not in the context, say so.
            
            Context:
            {context}
            
            Question: {query}
            
            Answer:
            """
            
            response = self.model.generate_content(prompt)
            sources = [{"text": doc.page_content, "metadata": doc.metadata} for doc in docs]
            return response.text, sources
    
    qa_chain = DirectGeminiQA(model, retriever)

    # Small helper that returns answer + raw sources when needed
    class QAWrapper:
        def __init__(self, chain, retriever):
            self.chain = chain
            self.retriever = retriever

        def run(self, query):
            return self.chain.run(query)

        def run_with_sources(self, query):
            docs = self.retriever.invoke(query)
            answer = self.chain.run(query)
            sources = [getattr(d, 'metadata', {}) for d in docs]
            return answer, sources

    return QAWrapper(qa_chain, retriever)
