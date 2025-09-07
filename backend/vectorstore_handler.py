# backend/vectorstore_handler.py
import os
from langchain.vectorstores import FAISS


def save_faiss_local(vectorstore, persist_dir):
    os.makedirs(persist_dir, exist_ok=True)
    vectorstore.save_local(persist_dir)


def load_faiss_local(persist_dir, embeddings):
    return FAISS.load_local(persist_dir, embeddings)
