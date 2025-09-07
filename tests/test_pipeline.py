# tests/test_pipeline.py
from backend.rag_pipeline import build_and_persist_vectorstore, load_vectorstore_and_qa


def test_basic_rag(tmp_path):
    texts = ["This is a short doc. Supervised learning uses labels."]
    persist_dir = str(tmp_path / "vs")
    build_and_persist_vectorstore(texts, persist_dir=persist_dir)
    qa = load_vectorstore_and_qa(persist_dir=persist_dir)
    answer = qa.run("What is supervised learning?")
    assert "labels" in answer.lower()
