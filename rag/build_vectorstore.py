from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from rag.config import VECTORSTORE_PATH, EMBEDDING_MODEL
import pymupdf
import os
import shutil


def load_pdf(path):
    doc = pymupdf.open(path)
    text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]
        text += f"\nPage {page_num + 1} \n"
        text += page.get_text("text") + "\n"

    return text


def build_vectorstore(pdf_path, vectorstore_path=VECTORSTORE_PATH):
    print(f"Load PDF with PyMuPDF: {pdf_path}")
    full_text = load_pdf(pdf_path)

    print("Cut to chunks with better splitting...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_text(full_text)
    print(f"Created {len(chunks)} chunks")

    print("Create embeddings...")
    embedding = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"}
    )

    print("Create ChromaDB vectorstore...")
    if os.path.exists(vectorstore_path):
        shutil.rmtree(vectorstore_path)

    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embedding,
        persist_directory=vectorstore_path
    )

    os.makedirs(os.path.dirname(vectorstore_path), exist_ok=True)

    print(f"ChromaDB index saved to {vectorstore_path}!")
    print(
        f"Documents in collection: {vectorstore._collection.count() if hasattr(vectorstore, '_collection') else 'unknown'}")

    return vectorstore


def build_document_chunks(pdf_path):
    print(f"Processing PDF: {pdf_path}")

    try:
        full_text = load_pdf(pdf_path)

        text_length = len(full_text)
        print(f" PDF size: {text_length:,} characters")

        if text_length > 5_000_000:
            chunk_size = 400
            print("Using smaller chunk size (400) for large PDF")
        elif text_length > 2_000_000:
            chunk_size = 600
            print("Using medium chunk size (600) for large PDF")
        else:
            chunk_size = 800

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_size // 4,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
            length_function=len,
        )

        chunks = splitter.split_text(full_text)
        print(f"Created {len(chunks)} chunks from {os.path.basename(pdf_path)}")
        return chunks

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return []


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        build_vectorstore(sys.argv[1])
    else:
        print("Usage: python build_vectorstore.py <path_to_pdf>")