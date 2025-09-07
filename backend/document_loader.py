# backend/document_loader.py
import os
import uuid
import pdfplumber
import html2text
from bs4 import BeautifulSoup


def save_uploaded_file(uploaded_file, dest_folder="data/uploads"):
    os.makedirs(dest_folder, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
    path = os.path.join(dest_folder, filename)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def extract_text_from_pdf(path):
    text = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            # add small marker for page references
            text.append(f"\n\n[Page {i+1}]\n" + page_text)
    return "\n".join(text)


def extract_text_from_html(path):
    raw = open(path, "r", encoding="utf-8").read()
    # Try to clean up with BeautifulSoup then html2text
    soup = BeautifulSoup(raw, "html.parser")
    body = soup.get_text(separator="\n")
    return body
